from django.conf import settings
from django.db import models

from cvs.models import CV
from job_matching.models import JobAnalysis


class SkillGapAnalysis(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="skill_gap_analyses",
    )

    cv = models.ForeignKey(
        CV,
        on_delete=models.CASCADE,
        related_name="skill_gap_analyses",
    )

    job_analysis = models.ForeignKey(
        JobAnalysis,
        on_delete=models.CASCADE,
        related_name="skill_gap_analyses",
    )

    current_skills = models.JSONField(
        default=list,
        blank=True,
    )

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

    gap_score = models.FloatField(default=0)

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"Job Analysis {self.job_analysis.id}"
        )