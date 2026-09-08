from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    RegisterView,
    MeView,
    social_login_success,
    SocialLoginExchangeView,
)


urlpatterns = [
    # Normal authentication
    path(
        "register/",
        RegisterView.as_view(),
        name="register",
    ),

    path(
        "login/",
        TokenObtainPairView.as_view(),
        name="login",
    ),

    path(
        "refresh/",
        TokenRefreshView.as_view(),
        name="refresh",
    ),

    path(
        "me/",
        MeView.as_view(),
        name="me",
    ),

    # Google / GitHub authentication
    path(
        "social/success/",
        social_login_success,
        name="social-login-success",
    ),

    path(
        "social/exchange/",
        SocialLoginExchangeView.as_view(),
        name="social-login-exchange",
    ),
]