from django.urls import path

from .views_job_match import (
    CareerTaxonomyJobMatchView,
)
from .views import (
    CategoryListView,
    RoleDetailView,
    RoleListView,
    SkillListView,
    TrackDetailView,
    TrackListView,
)


urlpatterns = [
    path(
        "categories/",
        CategoryListView.as_view(),
        name="category-list",
    ),

    path(
        "tracks/",
        TrackListView.as_view(),
        name="track-list",
    ),

    path(
        "tracks/<slug:slug>/",
        TrackDetailView.as_view(),
        name="track-detail",
    ),

    path(
        "roles/",
        RoleListView.as_view(),
        name="role-list",
    ),

    path(
        "roles/<slug:slug>/",
        RoleDetailView.as_view(),
        name="role-detail",
    ),

    path(
        "skills/",
        SkillListView.as_view(),
        name="skill-list",
    ),

    
     path(
        "job-match/",
        CareerTaxonomyJobMatchView.as_view(),
        name="career-taxonomy-job-match",
    ),
    
]