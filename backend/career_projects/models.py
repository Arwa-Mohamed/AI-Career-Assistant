from django.conf import settings
from django.db import models


class CareerProject(models.Model):

    STATUS_CHOICES = [
        ("not_started", "Not Started"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
    ]

    DIFFICULTY_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="career_projects",
    )

    title = models.CharField(
        max_length=255
    )

    description = models.TextField(
        blank=True
    )

    target_role = models.CharField(
        max_length=255,
        blank=True
    )

    skills = models.JSONField(
        default=list,
        blank=True
    )

    objectives = models.JSONField(
        default=list,
        blank=True
    )

    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default="beginner",
    )

    estimated_days = models.PositiveIntegerField(
        default=7
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="not_started",
    )

    progress = models.PositiveIntegerField(
        default=0
    )

    github_url = models.URLField(
        blank=True
    )

    demo_url = models.URLField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        ordering = [
            "-created_at"
        ]

    def __str__(self):
        return (
            f"{self.title} - "
            f"{self.user.username}"
        )