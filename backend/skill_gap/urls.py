from django.urls import path

from .views import SkillGapView


urlpatterns = [
    path(
        "<int:job_analysis_id>/",
        SkillGapView.as_view(),
        name="skill-gap",
    ),
]