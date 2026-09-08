from django.urls import path

from .views import CVAnalysisView


urlpatterns = [
    path(
        "<int:cv_id>/",
        CVAnalysisView.as_view(),
        name="cv-analysis",
    ),
]