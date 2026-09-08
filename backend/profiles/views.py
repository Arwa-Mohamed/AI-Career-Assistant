from rest_framework import generics
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework.permissions import IsAuthenticated

from .models import Profile
from .serializers import ProfileSerializer


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self):
        user = self.request.user

        profile, created = Profile.objects.get_or_create(
            user=user
        )

        if created:
            account_full_name = ""

            try:
                account_full_name = (
                    user.get_full_name()
                    or ""
                ).strip()
            except AttributeError:
                account_full_name = ""

            if not profile.full_name:
                profile.full_name = (
                    account_full_name
                    or user.username
                    or ""
                )

                profile.save(
                    update_fields=[
                        "full_name",
                        "updated_at",
                    ]
                )

        return profile
    
    def patch(self, request, *args, **kwargs):
        print("===== PROFILE PATCH DATA =====")
        print("FILES:", request.FILES)
        print("DATA:", request.data)

        response = super().patch(request, *args, **kwargs)

        print("STATUS:", response.status_code)
        print("RESPONSE DATA:", response.data)

        print("==============================")

        return response