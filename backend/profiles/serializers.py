from pathlib import Path

from rest_framework import serializers

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )

    account_full_name = serializers.SerializerMethodField()

    class Meta:
        model = Profile

        fields = [
            "id",
            "username",
            "email",
            "account_full_name",
            "full_name",
            "phone",
            "location",
            "bio",
            "career_goal",
            "linkedin_url",
            "profile_image",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "username",
            "email",
            "account_full_name",
            "created_at",
            "updated_at",
        ]


    def validate_profile_image(self, value):
        extension = Path(value.name).suffix.lower()

        allowed_extensions = {
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
        }

        if extension not in allowed_extensions:
            raise serializers.ValidationError(
                "Only JPG, JPEG, PNG, and WEBP images are allowed."
            )

        max_size = 2 * 1024 * 1024

        if value.size > max_size:
            raise serializers.ValidationError(
                "Profile image size must not exceed 2 MB."
            )

        return value

    def get_account_full_name(self, obj):
        user = obj.user

        full_name = ""

        try:
            full_name = user.get_full_name()
        except AttributeError:
            full_name = ""

        return (
            full_name.strip()
            if full_name
            else ""
        )