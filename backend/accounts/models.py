from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username
    
import secrets

from django.conf import settings
from django.db import models
from django.utils import timezone


class SocialLoginCode(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    code = models.CharField(
        max_length=128,
        unique=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    used = models.BooleanField(
        default=False,
    )

    def is_valid(self):
        age = (
            timezone.now() - self.created_at
        ).total_seconds()

        return (
            not self.used
            and age <= 60
        )

    @staticmethod
    def generate_code():
        return secrets.token_urlsafe(48)