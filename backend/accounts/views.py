from django.shortcuts import redirect

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import SocialLoginCode
from .serializers import RegisterSerializer


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


class RefreshView(TokenRefreshView):
    permission_classes = [AllowAny]


# =========================================================
# Current User
# =========================================================

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
        })


# =========================================================
# Social Login Success
# =========================================================

def social_login_success(request):
    """
    Called by django-allauth after successful
    Google/GitHub authentication.

    Creates a short-lived, one-time code that
    React exchanges for SimpleJWT tokens.
    """

    user = request.user

    if not user.is_authenticated:
        return redirect(
            "http://localhost:5173/login"
        )

    code = SocialLoginCode.objects.create(
        user=user,
        code=SocialLoginCode.generate_code(),
    )

    return redirect(
        "http://localhost:5173/social-callback"
        f"?code={code.code}"
    )


# =========================================================
# Exchange Social Code -> JWT
# =========================================================

class SocialLoginExchangeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        code_value = request.data.get("code")

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
                    "detail": "Invalid login code."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Code is valid only once and for a short time.
        if not code.is_valid():
            return Response(
                {
                    "detail": "Login code has expired or has already been used."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        refresh = RefreshToken.for_user(
            code.user
        )

        access_token = refresh.access_token

        # Mark code as used before returning tokens.
        code.used = True
        code.save(
            update_fields=["used"]
        )

        return Response({
            "access": str(access_token),
            "refresh": str(refresh),
        })