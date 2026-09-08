from django.db import models

from cvs.models import CV


class CVAnalysis(models.Model):
    cv = models.OneToOneField(
        CV,
        on_delete=models.CASCADE,
        related_name="analysis",
    )

    score = models.PositiveIntegerField(default=0)

    breakdown = models.JSONField(default=dict, blank=True)

    sections = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Analysis for CV #{self.cv.id}"