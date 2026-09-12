from django.conf import settings
from django.db import models
from cloudinary.models import CloudinaryField


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    full_name = models.CharField(
        max_length=150,
        blank=True,
    )

    phone = models.CharField(
        max_length=30,
        blank=True,
    )

    location = models.CharField(
        max_length=150,
        blank=True,
    )

    bio = models.TextField(
        blank=True,
    )

    career_goal = models.CharField(
        max_length=200,
        blank=True,
    )

    linkedin_url = models.URLField(
        blank=True,
    )

    profile_image = CloudinaryField(
        "profile_image",
        folder="ai-career-assistant/profile_photos",
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return (
            self.full_name
            or self.user.username
        )