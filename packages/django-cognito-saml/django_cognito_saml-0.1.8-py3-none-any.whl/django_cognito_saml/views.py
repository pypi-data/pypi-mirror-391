import json
import time
import urllib
from typing import Dict, Optional
from urllib.parse import urlencode

import jwt
from django.conf import settings
from django.contrib import auth
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse

from .conf import conf
from .utils import generate_return_uri, generate_state, get_cognito_callback_url


def cognito_login(request: "HttpRequest") -> "HttpResponse":
    """Redirect users to the cognito hosted login view.

    Encoded within the state is a redirect (utilizing the bouncer).

    Post login; users are directed to "cognito_callback"
    """
    state = generate_state(request)

    params = {
        "client_id": conf.COGNITO_CLIENT_ID,
        "response_type": "code",
        "scope": "openid",
        "redirect_uri": conf.COGNITO_REDIRECT_URI or get_cognito_callback_url(request),
        "state": state,
    }

    request.session["state"] = state
    request.session["next"] = generate_return_uri(request)

    redirect_url = f"{conf.COGNITO_AUTH_ENDPOINT}?{urlencode(params)}"
    return HttpResponseRedirect(redirect_url)


JWKS_CLIENT = jwt.PyJWKClient(
    conf.COGNITO_JWKS_URI, cache_keys=True, cache_jwk_set=True, lifespan=60 * 60
)


def _decode_jwt(token: str) -> Dict:
    # Fetch JWT token via authorization code flow
    jwt_signing_key = JWKS_CLIENT.get_signing_key_from_jwt(token)

    return jwt.decode(
        token,
        jwt_signing_key.key,
        algorithms=["RS256"],
        audience=conf.COGNITO_CLIENT_ID,
    )


def _exchange_code_for_jwt(request: HttpRequest, code: str) -> Optional[Dict]:
    # Fetch JWT token via authorization code flow
    # Creating a payload to fetch JWT tokens from cognito
    data = {
        "code": code,
        "client_id": conf.COGNITO_CLIENT_ID,
        "client_secret": conf.COGNITO_CLIENT_SECRET,
        "redirect_uri": conf.COGNITO_REDIRECT_URI or get_cognito_callback_url(request),
        "grant_type": "authorization_code",
    }

    encoded_data = urllib.parse.urlencode(data).encode("utf-8")

    cognito_request = urllib.request.Request(conf.COGNITO_TOKEN_ENDPOINT, encoded_data)
    cognito_response = urllib.request.urlopen(cognito_request)

    status_code = cognito_response.status

    if status_code != 200:
        return None

    return json.loads(cognito_response.read())


def cognito_callback(request: "HttpRequest") -> "HttpResponse":
    if not request.GET.get("code"):
        return JsonResponse({"detail": "Code parameter missing"}, status=401)

    if not request.GET.get("state"):
        return JsonResponse({"detail": "State parameter missing"}, status=401)

    if request.GET.get("state") != request.session.get("state"):
        return JsonResponse({"detail": "Invalid state parameter"}, status=401)

    cognito_data = _exchange_code_for_jwt(request, code=request.GET["code"])
    if not cognito_data:
        return JsonResponse({"detail": "Invalid token response"}, status=401)

    try:
        decoded_jwt_token = _decode_jwt(cognito_data["id_token"])
    except jwt.ImmatureSignatureError:
        # The token provided by AWS requires a second to be active :(
        time.sleep(1)
        decoded_jwt_token = _decode_jwt(cognito_data["id_token"])

    # Authenticate user
    user = auth.authenticate(request=request, cognito_jwt=decoded_jwt_token)

    if not user:
        return JsonResponse({"detail": "User account not found"}, status=404)

    auth.login(request, user)

    # Redirect
    redirect = request.session.get("next", None)
    redirect_default = settings.LOGIN_REDIRECT_URL
    response = HttpResponseRedirect(redirect or redirect_default)

    # Post response hook
    response = conf.response_hook(
        request, response, user=user, cognito_jwt=decoded_jwt_token
    )
    return response
