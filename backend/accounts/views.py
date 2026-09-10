import os

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator

from allauth.account.models import EmailAddress

from rest_framework import generics, serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .models import SocialLoginCode
from .serializers import RegisterSerializer


User = get_user_model()


# =========================================================
# Register
# =========================================================

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


# =========================================================
# Login / Refresh JWT
# =========================================================

class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code != status.HTTP_200_OK:
            return response

        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.user
        except Exception:
            return Response(
                {"detail": "Invalid login credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        email_address = (
            EmailAddress.objects
            .filter(
                user=user,
                email__iexact=user.email,
            )
            .first()
        )

        if email_address is None:
            return Response(
                {
                    "detail": (
                        "Please verify your email before signing in."
                    ),
                    "email_verification_required": True,
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if not email_address.verified:
            return Response(
                {
                    "detail": (
                        "Please verify your email before signing in."
                    ),
                    "email_verification_required": True,
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        return response


class RefreshView(TokenRefreshView):
    permission_classes = [AllowAny]


# =========================================================
# Current User
# =========================================================

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {
                "id": request.user.id,
                "username": request.user.username,
                "email": request.user.email,
            }
        )


# =========================================================
# Password Reset Request
# =========================================================

class PasswordResetRequestView(APIView):
    """
    Sends a password reset link to the user's email.

    The response is intentionally generic so that the API does
    not reveal whether a specific email address has an account.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        email = (
            request.data.get("email", "")
            .strip()
            .lower()
        )

        if not email:
            return Response(
                {
                    "detail": "Please enter your email address."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        email_field = serializers.EmailField()

        try:
            email = email_field.run_validation(email)
        except serializers.ValidationError:
            return Response(
                {
                    "detail": "Please enter a valid email address."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = (
            User.objects
            .filter(
                email__iexact=email,
                is_active=True,
            )
            .first()
        )

        generic_response = Response(
            {
                "detail": (
                    "If an account exists with this email, "
                    "a password reset link has been sent."
                )
            },
            status=status.HTTP_200_OK,
        )

        if user is None:
            return generic_response

        frontend_url = os.getenv(
            "FRONTEND_URL",
            "http://localhost:5173",
        ).rstrip("/")

        uid = urlsafe_base64_encode(
            force_bytes(user.pk)
        )

        token = default_token_generator.make_token(user)

        reset_url = (
            f"{frontend_url}"
            f"/reset-password/{uid}/{token}"
        )

        subject = "Reset your AI Career Assistant password"

        message = (
            "Hello,\n\n"
            "We received a request to reset the password "
            "for your AI Career Assistant account.\n\n"
            "Open the following link to create a new password:\n\n"
            f"{reset_url}\n\n"
            "This link is valid only for a limited time and "
            "will become invalid after the password is changed.\n\n"
            "If you did not request a password reset, "
            "you can safely ignore this email.\n\n"
            "AI Career Assistant"
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=None,
            recipient_list=[email],
            fail_silently=False,
        )

        return generic_response


# =========================================================
# Password Reset Confirm
# =========================================================

class PasswordResetConfirmView(APIView):
    """
    Validates the uid/token and sets the user's new password.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        uid_value = (
            request.data.get("uid", "")
            .strip()
        )

        token = (
            request.data.get("token", "")
            .strip()
        )

        new_password = request.data.get(
            "new_password",
            "",
        )

        confirm_password = request.data.get(
            "confirm_password",
            "",
        )

        if not uid_value:
            return Response(
                {"detail": "Password reset user ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not token:
            return Response(
                {"detail": "Password reset token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not new_password:
            return Response(
                {"detail": "New password is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not confirm_password:
            return Response(
                {"detail": "Password confirmation is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if new_password != confirm_password:
            return Response(
                {"detail": "New passwords do not match."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            uid = force_str(
                urlsafe_base64_decode(uid_value)
            )
            user = User.objects.get(
                pk=uid,
                is_active=True,
            )
        except (
            TypeError,
            ValueError,
            OverflowError,
            User.DoesNotExist,
        ):
            return Response(
                {
                    "detail": (
                        "This password reset link is invalid "
                        "or has expired."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not default_token_generator.check_token(
            user,
            token,
        ):
            return Response(
                {
                    "detail": (
                        "This password reset link is invalid "
                        "or has expired."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(
                new_password,
                user,
            )
        except DjangoValidationError as exc:
            return Response(
                {
                    "detail": list(exc.messages)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save(update_fields=["password"])

        return Response(
            {
                "detail": (
                    "Your password has been reset successfully. "
                    "You can now sign in with your new password."
                )
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# Email Status
# =========================================================

class EmailStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        email = (
            request.user.email or ""
        ).strip().lower()

        email_address = (
            EmailAddress.objects
            .filter(
                user=request.user,
                email__iexact=email,
            )
            .order_by(
                "-primary",
                "-id",
            )
            .first()
        )

        return Response(
            {
                "email": email,
                "verified": bool(
                    email_address
                    and email_address.verified
                ),
                "primary": bool(
                    email_address
                    and email_address.primary
                ),
            }
        )


# =========================================================
# Change Password
# =========================================================

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        current_password = request.data.get(
            "current_password",
            "",
        )

        new_password = request.data.get(
            "new_password",
            "",
        )

        confirm_password = request.data.get(
            "confirm_password",
            "",
        )

        if (
            not current_password
            or not new_password
            or not confirm_password
        ):
            return Response(
                {
                    "detail": (
                        "All password fields are required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not request.user.check_password(
            current_password
        ):
            return Response(
                {
                    "detail": (
                        "Current password is incorrect."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if new_password != confirm_password:
            return Response(
                {
                    "detail": (
                        "New passwords do not match."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(
                new_password,
                request.user,
            )
        except DjangoValidationError as exc:
            return Response(
                {
                    "detail": list(exc.messages)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.user.set_password(new_password)

        request.user.save(
            update_fields=["password"]
        )

        # Issue fresh JWTs so the user remains signed in.
        refresh = RefreshToken.for_user(
            request.user
        )

        return Response(
            {
                "detail": (
                    "Password changed successfully."
                ),
                "access": str(
                    refresh.access_token
                ),
                "refresh": str(refresh),
            }
        )


# =========================================================
# Change Email
# =========================================================

class ChangeEmailView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        new_email = (
            request.data.get(
                "new_email"
            ) or ""
        ).strip().lower()

        if not new_email:
            return Response(
                {
                    "detail": (
                        "New email is required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        email_serializer = serializers.EmailField()

        try:
            new_email = email_serializer.run_validation(
                new_email
            )
        except serializers.ValidationError:
            return Response(
                {
                    "detail": (
                        "Please enter a valid email address."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        current_email = (
            request.user.email or ""
        ).strip().lower()

        if new_email.lower() == current_email:
            return Response(
                {
                    "detail": (
                        "This is already your current email."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            request.user.__class__.objects
            .filter(email__iexact=new_email)
            .exclude(pk=request.user.pk)
            .exists()
        ):
            return Response(
                {
                    "detail": (
                        "An account with this email "
                        "already exists."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            EmailAddress.objects
            .filter(email__iexact=new_email)
            .exclude(user=request.user)
            .exists()
        ):
            return Response(
                {
                    "detail": (
                        "An account with this email "
                        "already exists."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Remove previous unconfirmed addresses
        # created by earlier change-email attempts.
        EmailAddress.objects.filter(
            user=request.user,
            verified=False,
        ).delete()

        EmailAddress.objects.add_email(
            request=request,
            user=request.user,
            email=new_email,
            confirm=True,
            signup=False,
        )

        return Response(
            {
                "detail": (
                    "A verification email has been sent "
                    "to your new email address."
                ),
                "email": new_email,
            }
        )


# =========================================================
# Resend Email Verification
# =========================================================

class ResendEmailVerificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        email = (
            request.user.email or ""
        ).strip().lower()

        email_address = (
            EmailAddress.objects
            .filter(
                user=request.user,
                email__iexact=email,
            )
            .first()
        )

        if (
            email_address
            and email_address.verified
        ):
            return Response(
                {
                    "detail": (
                        "Your email is already verified."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if email_address is None:
            EmailAddress.objects.add_email(
                request=request,
                user=request.user,
                email=email,
                confirm=True,
                signup=False,
            )
        else:
            email_address.delete()

            EmailAddress.objects.add_email(
                request=request,
                user=request.user,
                email=email,
                confirm=True,
                signup=False,
            )

        return Response(
            {
                "detail": (
                    "A verification email has been sent."
                )
            }
        )


# =========================================================
# Delete Account
# =========================================================

class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user

        current_password = (
            request.data.get("current_password") or ""
        ).strip()

        # For normal username/password accounts, require the
        # current password as an additional confirmation.
        if user.has_usable_password():
            if not current_password:
                return Response(
                    {
                        "detail": (
                            "Current password is required "
                            "to delete your account."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not user.check_password(current_password):
                return Response(
                    {
                        "detail": (
                            "Current password is incorrect."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        user.delete()

        return Response(
            {
                "detail": (
                    "Your account has been permanently deleted."
                )
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# Social Login Success
# =========================================================

def social_login_success(request):
    frontend_url = os.getenv(
        "FRONTEND_URL",
        "http://localhost:5173",
    ).rstrip("/")

    user = request.user

    if not user.is_authenticated:
        return redirect(
            f"{frontend_url}/login"
        )

    code = SocialLoginCode.objects.create(
        user=user,
        code=SocialLoginCode.generate_code(),
    )

    return redirect(
        f"{frontend_url}/social-callback"
        f"?code={code.code}"
    )


# =========================================================
# Exchange Social Code -> JWT
# =========================================================

class SocialLoginExchangeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        code_value = request.data.get(
            "code"
        )

        if not code_value:
            return Response(
                {
                    "detail": "Code is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            code = (
                SocialLoginCode.objects
                .select_related("user")
                .get(code=code_value)
            )
        except SocialLoginCode.DoesNotExist:
            return Response(
                {
                    "detail": (
                        "Invalid login code."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not code.is_valid():
            return Response(
                {
                    "detail": (
                        "Login code has expired "
                        "or has already been used."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        refresh = RefreshToken.for_user(
            code.user
        )

        access_token = refresh.access_token

        code.used = True

        code.save(
            update_fields=["used"]
        )

        return Response(
            {
                "access": str(access_token),
                "refresh": str(refresh),
            }
        )