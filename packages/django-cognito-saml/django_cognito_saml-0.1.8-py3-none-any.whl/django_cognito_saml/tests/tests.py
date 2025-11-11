import base64
import json
import unittest.mock
from typing import Any, Dict, cast
from urllib.parse import parse_qs, urlparse

import jwt
import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.http import HttpRequest, HttpResponse
from django.test import override_settings
from django.test.client import Client
from django.urls import reverse

from django_cognito_saml.backends import CognitoUserBackend


@pytest.mark.django_db
class TestRedirect:
    def test_redirect_is_correct(self, client: Client) -> None:
        response = client.get(reverse("cognito_login"))

        assert response.status_code == 302

        parse_result = urlparse(response.url)  # type: ignore

        assert parse_result.path == "/oauth2/authorize"
        assert parse_result.scheme == "https"

        query = parse_qs(parse_result.query)
        assert query["client_id"] == [settings.COGNITO_CONFIG["CLIENT_ID"]]
        assert query["response_type"] == [
            "code"
        ], "We only allow authorization code flow"
        assert query["scope"] == ["openid"]
        assert query["redirect_uri"] == [settings.COGNITO_CONFIG["REDIRECT_URI"]]

        state = json.loads(base64.b64decode(query["state"][0]).decode("utf-8"))

        assert state["redirect_uri"].endswith(reverse("cognito_callback"))
        assert state["key"]


@pytest.mark.django_db
class TestCallback:
    def test_callback_errors_when_state_parameter_is_missing(
        self, client: Client
    ) -> None:
        # Initial fetch to set key state
        response = client.get(reverse("cognito_callback"), data={"code": "fake_code"})

        assert response.status_code == 401
        assert response.json()["detail"] == "State parameter missing"

    def test_callback_errors_whencode_parameter_is_missing(
        self, client: Client
    ) -> None:
        # Initial fetch to set key state
        response = client.get(reverse("cognito_callback"), data={})

        assert response.status_code == 401
        assert response.json()["detail"] == "Code parameter missing"

    def test_callback_errors_state_parameter_does_not_equal_session_state(
        self, client: Client
    ) -> None:
        # Initial fetch to set key state
        response = client.get(
            reverse("cognito_callback"), data={"code": "code", "state": "state"}
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid state parameter"

    def get_cognito_callback(self, client: Client, jwt_payload: Dict) -> HttpResponse:
        encoded_jwt = jwt.encode(
            jwt_payload,
            "some_jwt_secret",
            algorithm="HS256",
        )
        with unittest.mock.patch(
            "django_cognito_saml.views._decode_jwt"
        ) as mock_decode_jwt:
            mock_decode_jwt.return_value = jwt_payload

            with unittest.mock.patch(
                "django_cognito_saml.views._exchange_code_for_jwt"
            ) as mock_exchange_code_for_jwt:
                mock_exchange_code_for_jwt.return_value = {
                    "id_token": encoded_jwt,
                    "access_token": encoded_jwt,
                }

                # 1) Login and get redirected
                login_response_url: str = client.get(
                    reverse("cognito_login")
                ).url  # type:ignore
                state = parse_qs(urlparse(login_response_url).query)["state"][0]
                assert isinstance(state, str)

                # 2) Visit the callback url
                ret = client.get(
                    reverse("cognito_callback"),
                    data={"code": "fake_code", "state": state},
                )
        return cast(HttpResponse, ret)

    def test_successful_callback(self, client: Client) -> None:
        jwt_payload = {"email": "william.chu@uptickhq.com"}

        response = self.get_cognito_callback(client, jwt_payload)

        assert response.status_code == 302

        assert client.session["_auth_user_id"] == "1"

    @override_settings(
        COGNITO_CONFIG={
            **settings.COGNITO_CONFIG,
            **{"RESPONSE_HOOK": "django_cognito_saml.tests.tests.hook_override"},
        }
    )
    def test_response_hook(self, client: Client) -> None:
        jwt_payload = {"email": "william.chu@uptickhq.com"}

        response = self.get_cognito_callback(client, jwt_payload)

        assert response.status_code == 302
        assert response.cookies["lol"].value == "test"

    @override_settings(
        AUTHENTICATION_BACKENDS=["django_cognito_saml.tests.tests.CustomBackend"]
    )
    def test_custom_backend_auth(self, client: Client) -> None:
        jwt_payload = {"email": "william.chu@uptickhq.com", "first_name": "wombat"}

        response = self.get_cognito_callback(client, jwt_payload)

        assert response.status_code == 302

        UserModel = get_user_model()
        user = UserModel.objects.get()
        assert user.get_username() == "william.chu@uptickhq.com"
        assert user.first_name == "wombat"  # type: ignore


def hook_override(
    request: HttpRequest,
    response: HttpResponse,
    user: AbstractBaseUser,
    cognito_jwt: dict[str, Any],
) -> HttpResponse:
    response.set_cookie("lol", "test")
    return response


class CustomBackend(CognitoUserBackend):
    create_unknown_user = True

    def configure_user(  # type: ignore[override]
        self, request: HttpRequest, user: AbstractBaseUser, created=True
    ) -> AbstractBaseUser:
        """
        Configure a user after creation and return the updated user.

        By default, return the user unmodified.
        """
        user.first_name = self.cognito_jwt["first_name"]  # type: ignore
        user.save()
        return user
