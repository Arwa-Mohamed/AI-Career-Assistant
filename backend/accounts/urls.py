from django.urls import path

from .views import (
    ChangeEmailView,
    ChangePasswordView,
    DeleteAccountView,
    EmailStatusView,
    LoginView,
    MeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RefreshView,
    RegisterView,
    ResendEmailVerificationView,
    SocialLoginExchangeView,
    social_login_success,
)


urlpatterns = [
    # =========================================================
    # Authentication
    # =========================================================

    path(
        "register/",
        RegisterView.as_view(),
        name="register",
    ),

    path(
        "login/",
        LoginView.as_view(),
        name="login",
    ),

    path(
        "refresh/",
        RefreshView.as_view(),
        name="refresh",
    ),

    # =========================================================
    # Password Reset
    # =========================================================

    path(
        "password/reset/",
        PasswordResetRequestView.as_view(),
        name="password-reset-request",
    ),

    path(
        "password/reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),

    # =========================================================
    # Current User
    # =========================================================

    path(
        "me/",
        MeView.as_view(),
        name="me",
    ),

    # =========================================================
    # Email Verification
    # =========================================================

    path(
        "email/status/",
        EmailStatusView.as_view(),
        name="email-status",
    ),

    path(
        "email/resend/",
        ResendEmailVerificationView.as_view(),
        name="email-resend",
    ),

    path(
        "email/change/",
        ChangeEmailView.as_view(),
        name="email-change",
    ),

    # =========================================================
    # Password Change
    # =========================================================

    path(
        "password/change/",
        ChangePasswordView.as_view(),
        name="password-change",
    ),

    # =========================================================
    # Account Management
    # =========================================================

    path(
        "account/delete/",
        DeleteAccountView.as_view(),
        name="account-delete",
    ),

    # =========================================================
    # Social Authentication
    # =========================================================

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