SECRET_KEY = "asdasd"

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": "mem_db"}}


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django_cognito_saml",
]

MIDDLEWARE = ["django.contrib.sessions.middleware.SessionMiddleware"]


ROOT_URLCONF = "django_cognito_saml.urls"


COGNITO_CONFIG = dict(
    CLIENT_ID="client_id",
    CLIENT_SECRET="client_secret",
    ENDPOINT="https://fake_cognito.com",
    JWKS_URI="http://cognito-idp.ap-southeast-2.amazonaws.com:443/ap-southeast-some_endpoint/.well-known/jwks.json",  # noqa
    REDIRECT_URI="https://test_redirect.com/",
    RESPONSE_HOOK="",
)

AUTHENTICATION_BACKENDS = ("django_cognito_saml.backends.CognitoUserBackend",)
