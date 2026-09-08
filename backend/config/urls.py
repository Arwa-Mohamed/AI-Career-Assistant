from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from core.views import health_check


urlpatterns = [
    # Admin
    path(
        "admin/",
        admin.site.urls,
    ),

    # django-allauth
    path(
        "accounts/",
        include("allauth.urls"),
    ),

    # Health check
    path(
        "api/health/",
        health_check,
    ),

    # Authentication
    path(
        "api/auth/",
        include("accounts.urls"),
    ),

    # Profile
    path(
        "api/profile/",
        include("profiles.urls"),
    ),

    # CVs
    path(
        "api/cvs/",
        include("cvs.urls"),
    ),

    # CV Analysis
    path(
        "api/cv-analysis/",
        include("cv_analysis.urls"),
    ),

    # Job Matching
    path(
        "api/job-matching/",
        include("job_matching.urls"),
    ),

    # Skill Gap
    path(
        "api/skill-gap/",
        include("skill_gap.urls"),
    ),

    # Dashboard
    path(
        "api/dashboard/",
        include("dashboard.urls"),
    ),

    # Chatbot
    path(
        "api/chatbot/",
        include("chatbot.urls"),
    ),

    # Interviews
    path(
        "api/interviews/",
        include("interviews.urls"),
    ),

    # Career Projects
    path(
        "api/projects/",
        include("career_projects.urls"),
    ),

    path(
       "api/career-taxonomy/",
       include("career_taxonomy.urls"),
    ),
]


# Media files during development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )