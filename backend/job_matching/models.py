from django.conf import settings
from django.db import models

from cvs.models import CV


class JobAnalysis(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="job_analyses",
    )

    cv = models.ForeignKey(
        CV,
        on_delete=models.CASCADE,
        related_name="job_analyses",
    )

    job_description = models.TextField()

    semantic_similarity = models.FloatField(default=0)
    semantic_score = models.FloatField(default=0)

    skill_match_score = models.FloatField(default=0)
    final_match_score = models.FloatField(default=0)

    required_skills = models.JSONField(
        default=list,
        blank=True,
    )

    matched_skills = models.JSONField(
        default=list,
        blank=True,
    )

    missing_skills = models.JSONField(
        default=list,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"CV {self.cv.id} - "
            f"{self.final_match_score}%"
        )