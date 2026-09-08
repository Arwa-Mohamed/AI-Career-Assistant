from django.urls import path

from .views import (
    JobAnalysisListView,
    JobMatchView,
)


urlpatterns = [
    path(
        "<int:cv_id>/",
        JobMatchView.as_view(),
        name="job-match",
    ),

    path(
        "history/",
        JobAnalysisListView.as_view(),
        name="job-analysis-history",
    ),
]