from django.urls import path

from .views import (
    CareerProjectListCreateView,
    CareerProjectDetailView,
    CareerProjectRecommendationsView,
)


urlpatterns = [
    path(
        "",
        CareerProjectListCreateView.as_view(),
        name="career-project-list",
    ),

    path(
        "recommendations/",
        CareerProjectRecommendationsView.as_view(),
        name="career-project-recommendations",
    ),

    path(
        "<int:project_id>/",
        CareerProjectDetailView.as_view(),
        name="career-project-detail",
    ),
]