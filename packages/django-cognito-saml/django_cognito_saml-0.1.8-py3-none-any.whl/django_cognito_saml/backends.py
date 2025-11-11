from logging import getLogger
from typing import Any, Optional

from django.contrib.auth.backends import RemoteUserBackend
from django.contrib.auth.models import AbstractBaseUser
from django.http import HttpRequest

from django_cognito_saml.conf import COGNITO_GROUPS_SESSION_KEY, conf

logger = getLogger("django_cognito_saml")


class CognitoUserBackend(RemoteUserBackend):
    """
    This backend is to be used in conjunction with the ``RemoteUserMiddleware``
    found in the middleware module of this package, and is used when the server
    is handling authentication outside of Django.

    By default, the ``authenticate`` method creates ``User`` objects for
    usernames that don't already exist in the database.  Subclasses can disable
    this behavior by setting the ``create_unknown_user`` attribute to
    ``False``.

    Override configure_user for post login customization

    """

    # Change this to False if you do not want to create a remote user.
    create_unknown_user = True

    cognito_jwt: dict

    def authenticate(  # type: ignore[override]
        self, request: HttpRequest, cognito_jwt: dict[str, Any], **kwargs: Any
    ) -> Optional[AbstractBaseUser]:
        self.cognito_jwt = cognito_jwt
        remote_user = cognito_jwt["email"]
        return super().authenticate(request, remote_user=remote_user, **kwargs)

    def configure_user(  # type: ignore[override]
        self, request: HttpRequest, user: AbstractBaseUser, **kwargs: Any
    ) -> AbstractBaseUser:
        """
        Configure a user after creation and return the updated user.

        By default, return the user unmodified.
        """
        return user


class SuperUserBackend(CognitoUserBackend):
    """
    This backend creates users and adds them as superusers
    """

    # Change this to False if you do not want to create a remote user.
    create_unknown_user = True

    cognito_jwt: dict

    def authenticate(  # type: ignore[override]
        self, request: HttpRequest, cognito_jwt: dict[str, Any], **kwargs: Any
    ) -> Optional[AbstractBaseUser]:
        url = request.build_absolute_uri("/")

        # Extracting email
        email = cognito_jwt.get("email")

        # Parsing email
        unparsed_groups = cognito_jwt.get("custom:groups", "")
        if "[" in unparsed_groups:
            groups = unparsed_groups.removeprefix("[").removesuffix("]").split(",")
        else:
            groups = [unparsed_groups.strip()]

        groups += cognito_jwt.get("cognito:groups", [])

        # Checking if user has access.
        if conf.COGNITO_REQUIRED_GROUPS:
            if not set(groups).issuperset(set(conf.COGNITO_REQUIRED_GROUPS)):
                msg = (
                    f"COGNITO_SSO_FAILURE: {email} logged into "
                    f"{url} but was not in groups: {conf.COGNITO_REQUIRED_GROUPS}"
                )
                logger.info(msg)
                return None

        user = super().authenticate(request, cognito_jwt=cognito_jwt, **kwargs)

        if user:
            request.session[COGNITO_GROUPS_SESSION_KEY] = groups
            msg = (
                f"COGNITO_SSO_LOGIN: {email} logged into "
                f"{url} with groups: {groups}"
            )
            logger.info(msg)

        return user

    def configure_user(  # type: ignore[override]
        self,
        request: HttpRequest,
        user: AbstractBaseUser,
        created: bool = True,
        **kwargs: Any,
    ) -> AbstractBaseUser:
        """
        Configure a user after creation and return the updated user.

        By default, return the user unmodified.
        """

        if created:
            user.set_unusable_password()
            user.email = self.cognito_jwt["email"]  # type: ignore [attr-defined]
            user.first_name = self.cognito_jwt.get("given_name") or ""  # type: ignore
            user.last_name = self.cognito_jwt.get("family_name") or ""  # type: ignore
            user.is_superuser = True  # type: ignore [attr-defined]
            user.is_staff = True  # type: ignore [attr-defined]
            user.save()
        return user


class DisallowUnknownUserSuperUserBackend(SuperUserBackend):
    """Same backend as `SuperUserBackend` but does not create
    users if they don't already exist.
    """

    create_unknown_user = False
