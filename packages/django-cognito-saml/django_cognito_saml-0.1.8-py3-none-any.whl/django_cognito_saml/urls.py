from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.cognito_login, name="cognito_login"),
    path("cognito/callback/", views.cognito_callback, name="cognito_callback"),
]
