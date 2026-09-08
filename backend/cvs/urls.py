from django.urls import path

from .views import (
    CVListCreateView,
    CVDetailView,
    CVAnalysisView,
    AddProjectToCVView,
    RemoveProjectFromCVView,
    GenerateCVPDFView,
)

from .tailored_views import (
    TailorCVView,
    TailoredCVPDFView,
)


urlpatterns = [
    path(
        "",
        CVListCreateView.as_view(),
        name="cv-list-create",
    ),

    path(
        "generate-pdf/",
        GenerateCVPDFView.as_view(),
        name="generate-cv-pdf",
    ),

    path(
        "tailor/",
        TailorCVView.as_view(),
        name="tailor-cv",
    ),

    path(
        "tailor/generate-pdf/",
        TailoredCVPDFView.as_view(),
        name="tailored-cv-pdf",
    ),

    path(
        "<int:pk>/",
        CVDetailView.as_view(),
        name="cv-detail",
    ),

    path(
        "<int:cv_id>/analysis/",
        CVAnalysisView.as_view(),
        name="cv-analysis",
    ),

    path(
        "<int:cv_id>/projects/<int:project_id>/",
        AddProjectToCVView.as_view(),
        name="add-project-to-cv",
    ),

    path(
        "<int:cv_id>/projects/<int:project_id>/remove/",
        RemoveProjectFromCVView.as_view(),
        name="remove-project-from-cv",
    ),
]