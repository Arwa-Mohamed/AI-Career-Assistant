from django.conf import settings
from django.db import models


class CV(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cvs",
    )

    title = models.CharField(max_length=150, default="My CV")
    file = models.FileField(upload_to="cvs/")

    extracted_text = models.TextField(blank=True)

    parsed_data = models.JSONField(
        default=dict,
        blank=True,
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"