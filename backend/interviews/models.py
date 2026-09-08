from django.conf import settings
from django.db import models

from cvs.models import CV
from job_matching.models import JobAnalysis


class InterviewSession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="interview_sessions",
    )

    cv = models.ForeignKey(
        CV,
        on_delete=models.CASCADE,
        related_name="interview_sessions",
    )

    job_analysis = models.ForeignKey(
        JobAnalysis,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="interview_sessions",
    )

    role = models.CharField(max_length=200, blank=True)

    status = models.CharField(
        max_length=30,
        default="active",
    )
    
    final_score = models.FloatField(default=0)

    total_questions = models.PositiveIntegerField(default=0)

    completed_at = models.DateTimeField(
     null=True,
     blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - Interview #{self.id}"


class InterviewQuestion(models.Model):
    session = models.ForeignKey(
        InterviewSession,
        on_delete=models.CASCADE,
        related_name="questions",
    )

    question_text = models.TextField()

    category = models.CharField(
        max_length=50,
        default="technical",
    )

    order = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Q{self.order} - Interview #{self.session.id}"


class InterviewAnswer(models.Model):
    question = models.OneToOneField(
        InterviewQuestion,
        on_delete=models.CASCADE,
        related_name="answer",
    )

    answer_text = models.TextField()

    score = models.FloatField(default=0)

    feedback = models.TextField(blank=True)

    improved_answer = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answer - Q{self.question.order}"