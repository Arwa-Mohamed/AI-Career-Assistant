from io import BytesIO
from pathlib import Path
from tempfile import NamedTemporaryFile
from xml.sax.saxutils import escape

from django.http import FileResponse

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import (
    FormParser,
    MultiPartParser,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CV
from .serializers import CVSerializer
from .utils.extractor import extract_text
from .utils.parser import parse_cv


# =========================================================
# CV LIST / CREATE
# =========================================================


class CVListCreateView(
    generics.ListCreateAPIView
):
    serializer_class = CVSerializer

    permission_classes = [
        IsAuthenticated
    ]

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    def get_queryset(self):
        return (
            CV.objects.filter(
                user=self.request.user
            )
            .order_by("-uploaded_at")
        )

    def perform_create(
        self,
        serializer,
    ):
        uploaded_file = (
            serializer.validated_data.get("file")
        )

        if uploaded_file is None:
            raise ValidationError(
                {
                    "file": (
                        "A CV file is required."
                    )
                }
            )

        suffix = (
            Path(uploaded_file.name)
            .suffix
            .lower()
        )

        temp_path = None

        try:
            # =================================================
            # TEMPORARY FILE FOR PARSING
            # =================================================
            #
            # Vercel deployment filesystem is read-only.
            # /tmp is writable during the request and is used
            # only as temporary working space.
            #

            with NamedTemporaryFile(
                mode="wb",
                suffix=suffix,
                delete=False,
            ) as temp_file:

                for chunk in uploaded_file.chunks():
                    temp_file.write(chunk)

                temp_path = temp_file.name

            # Reset uploaded file pointer before saving
            # through the configured CV storage backend.
            try:
                uploaded_file.seek(0)
            except Exception:
                pass

            # =================================================
            # TEXT EXTRACTION
            # =================================================

            try:
                extracted_text = extract_text(
                    temp_path
                )
            except Exception:
                extracted_text = ""

            # =================================================
            # CV PARSING
            # =================================================

            try:
                parsed_data = parse_cv(
                    extracted_text
                )
            except Exception:
                parsed_data = {}

            if not isinstance(
                parsed_data,
                dict,
            ):
                parsed_data = {}

            parsed_data.setdefault(
                "projects",
                [],
            )

            # =================================================
            # SAVE CV FILE
            # =================================================
            #
            # Local:
            #     media/cvs/
            #
            # Vercel:
            #     Vercel Blob
            #

            try:
                cv = serializer.save(
                    user=self.request.user
                )
            except Exception as exc:
                raise ValidationError(
                    {
                        "file": (
                            "The CV could not be stored. "
                            "Please try again."
                        )
                    }
                ) from exc

            # =================================================
            # SAVE PARSED INFORMATION
            # =================================================

            cv.extracted_text = (
                extracted_text
            )

            cv.parsed_data = (
                parsed_data
            )

            cv.save(
                update_fields=[
                    "extracted_text",
                    "parsed_data",
                    "updated_at",
                ]
            )

        finally:
            # =================================================
            # REMOVE TEMPORARY FILE
            # =================================================

            if temp_path:
                try:
                    Path(temp_path).unlink(
                        missing_ok=True
                    )
                except Exception:
                    pass


# =========================================================
# CV DETAIL
# =========================================================


class CVDetailView(
    generics.RetrieveDestroyAPIView
):
    serializer_class = CVSerializer

    permission_classes = [
        IsAuthenticated
    ]

    def get_queryset(self):
        return CV.objects.filter(
            user=self.request.user
        )


# =========================================================
# CV ANALYSIS
# =========================================================


class CVAnalysisView(
    APIView
):
    permission_classes = [
        IsAuthenticated
    ]

    def get(
        self,
        request,
        cv_id,
    ):
        try:
            cv = CV.objects.get(
                id=cv_id,
                user=request.user,
            )
        except CV.DoesNotExist:
            return Response(
                {
                    "detail": "CV not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "id": cv.id,
                "title": cv.title,
                "parsed_data": (
                    cv.parsed_data
                    or {}
                ),
                "text_length": len(
                    cv.extracted_text
                    or ""
                ),
            }
        )


# =========================================================
# ADD PROJECT TO CV
# =========================================================


class AddProjectToCVView(
    APIView
):
    permission_classes = [
        IsAuthenticated
    ]

    def post(
        self,
        request,
        cv_id,
        project_id,
    ):
        try:
            cv = CV.objects.get(
                id=cv_id,
                user=request.user,
            )
        except CV.DoesNotExist:
            return Response(
                {
                    "detail": "CV not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            from career_projects.models import (
                CareerProject,
            )

            project = CareerProject.objects.get(
                id=project_id,
                user=request.user,
            )

        except ImportError:
            return Response(
                {
                    "detail": (
                        "Career projects app is "
                        "not configured."
                    )
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        except CareerProject.DoesNotExist:
            return Response(
                {
                    "detail": "Project not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if project.status != "completed":
            return Response(
                {
                    "detail": (
                        "Only completed projects "
                        "can be added to a CV."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        parsed_data = (
            cv.parsed_data
            if isinstance(
                cv.parsed_data,
                dict,
            )
            else {}
        )

        projects = parsed_data.get(
            "projects",
            [],
        )

        if not isinstance(
            projects,
            list,
        ):
            projects = []

        already_added = any(
            str(
                item.get(
                    "source_project_id",
                    "",
                )
            )
            == str(project.id)
            for item in projects
            if isinstance(
                item,
                dict,
            )
        )

        if already_added:
            return Response(
                {
                    "detail": (
                        "This project is already "
                        "added to the CV."
                    ),
                    "parsed_data": parsed_data,
                },
                status=status.HTTP_200_OK,
            )

        project_data = {
            "source_project_id": project.id,
            "title": getattr(
                project,
                "title",
                "",
            ),
            "description": getattr(
                project,
                "description",
                "",
            ),
            "target_role": getattr(
                project,
                "target_role",
                "",
            ),
            "skills": (
                getattr(
                    project,
                    "skills",
                    [],
                )
                or []
            ),
            "objectives": (
                getattr(
                    project,
                    "objectives",
                    [],
                )
                or []
            ),
            "github_url": (
                getattr(
                    project,
                    "github_url",
                    "",
                )
                or ""
            ),
            "demo_url": (
                getattr(
                    project,
                    "demo_url",
                    "",
                )
                or ""
            ),
            "difficulty": (
                getattr(
                    project,
                    "difficulty",
                    "",
                )
                or ""
            ),
            "completed_at": (
                project.completed_at.isoformat()
                if getattr(
                    project,
                    "completed_at",
                    None,
                )
                else None
            ),
        }

        projects.append(
            project_data
        )

        parsed_data["projects"] = (
            projects
        )

        cv.parsed_data = (
            parsed_data
        )

        cv.save(
            update_fields=[
                "parsed_data",
                "updated_at",
            ]
        )

        return Response(
            {
                "message": (
                    "Project added to CV "
                    "successfully."
                ),
                "project": project_data,
                "cv_id": cv.id,
                "parsed_data": parsed_data,
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# REMOVE PROJECT FROM CV
# =========================================================


class RemoveProjectFromCVView(
    APIView
):
    permission_classes = [
        IsAuthenticated
    ]

    def delete(
        self,
        request,
        cv_id,
        project_id,
    ):
        try:
            cv = CV.objects.get(
                id=cv_id,
                user=request.user,
            )
        except CV.DoesNotExist:
            return Response(
                {
                    "detail": "CV not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        parsed_data = (
            cv.parsed_data
            if isinstance(
                cv.parsed_data,
                dict,
            )
            else {}
        )

        projects = parsed_data.get(
            "projects",
            [],
        )

        if not isinstance(
            projects,
            list,
        ):
            projects = []

        original_count = len(
            projects
        )

        projects = [
            item
            for item in projects
            if not (
                isinstance(
                    item,
                    dict,
                )
                and str(
                    item.get(
                        "source_project_id",
                        "",
                    )
                )
                == str(project_id)
            )
        ]

        if len(projects) == original_count:
            return Response(
                {
                    "detail": (
                        "Project is not attached "
                        "to this CV."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        parsed_data["projects"] = (
            projects
        )

        cv.parsed_data = (
            parsed_data
        )

        cv.save(
            update_fields=[
                "parsed_data",
                "updated_at",
            ]
        )

        return Response(
            {
                "message": (
                    "Project removed from CV "
                    "successfully."
                ),
                "cv_id": cv.id,
                "parsed_data": parsed_data,
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# GENERATED CV PDF HELPERS
# =========================================================


def _clean_text(
    value,
):
    return str(
        value or ""
    ).strip()


def _as_list(
    value,
):
    return (
        value
        if isinstance(
            value,
            list,
        )
        else []
    )


def _escape(
    value,
):
    return escape(
        _clean_text(value)
    )


def _field(
    item,
    keys,
    default="",
):
    if not isinstance(
        item,
        dict,
    ):
        return default

    for key in keys:
        value = item.get(key)

        if (
            value is not None
            and _clean_text(value)
        ):
            return value

    return default


def _unique_strings(
    values,
):
    result = []
    seen = set()

    for value in _as_list(values):
        text = _clean_text(value)

        if not text:
            continue

        key = text.casefold()

        if key in seen:
            continue

        seen.add(key)
        result.append(text)

    return result


def _normalize_experience(
    values,
):
    result = []

    for item in _as_list(values):
        if isinstance(
            item,
            str,
        ):
            if item.strip():
                result.append(
                    {
                        "job_title": item.strip(),
                        "company": "",
                        "duration": "",
                        "description": "",
                    }
                )
            continue

        if not isinstance(
            item,
            dict,
        ):
            continue

        result.append(
            {
                "job_title": _clean_text(
                    _field(
                        item,
                        [
                            "job_title",
                            "title",
                            "position",
                            "role",
                        ],
                    )
                ),
                "company": _clean_text(
                    _field(
                        item,
                        [
                            "company",
                            "organization",
                            "employer",
                        ],
                    )
                ),
                "duration": _clean_text(
                    _field(
                        item,
                        [
                            "duration",
                            "date",
                            "period",
                            "year",
                        ],
                    )
                ),
                "description": _clean_text(
                    _field(
                        item,
                        [
                            "description",
                            "responsibilities",
                            "details",
                        ],
                    )
                ),
            }
        )

    return result


def _normalize_education(
    values,
):
    result = []

    for item in _as_list(values):
        if isinstance(
            item,
            str,
        ):
            if item.strip():
                result.append(
                    {
                        "degree": item.strip(),
                        "institution": "",
                        "year": "",
                        "description": "",
                    }
                )
            continue

        if not isinstance(
            item,
            dict,
        ):
            continue

        result.append(
            {
                "degree": _clean_text(
                    _field(
                        item,
                        [
                            "degree",
                            "title",
                            "program",
                            "qualification",
                        ],
                    )
                ),
                "institution": _clean_text(
                    _field(
                        item,
                        [
                            "institution",
                            "university",
                            "school",
                            "college",
                        ],
                    )
                ),
                "year": _clean_text(
                    _field(
                        item,
                        [
                            "year",
                            "date",
                            "period",
                        ],
                    )
                ),
                "description": _clean_text(
                    _field(
                        item,
                        [
                            "description",
                            "details",
                        ],
                    )
                ),
            }
        )

    return result


def _normalize_certifications(
    values,
):
    result = []

    for item in _as_list(values):
        if isinstance(
            item,
            str,
        ):
            name = item.strip()

            if name:
                result.append(
                    {
                        "name": name,
                        "issuer": "",
                        "year": "",
                    }
                )

            continue

        if not isinstance(
            item,
            dict,
        ):
            continue

        name = _clean_text(
            _field(
                item,
                [
                    "name",
                    "title",
                    "certificate",
                    "certification",
                ],
            )
        )

        if not name:
            continue

        result.append(
            {
                "name": name,
                "issuer": _clean_text(
                    _field(
                        item,
                        [
                            "issuer",
                            "organization",
                            "provider",
                            "institution",
                        ],
                    )
                ),
                "year": _clean_text(
                    _field(
                        item,
                        [
                            "year",
                            "date",
                            "period",
                        ],
                    )
                ),
            }
        )

    return result


def _normalize_projects(
    values,
):
    result = []

    for item in _as_list(values):
        if not isinstance(
            item,
            dict,
        ):
            continue

        title = _clean_text(
            _field(
                item,
                [
                    "title",
                    "name",
                ],
            )
        )

        if not title:
            continue

        skills = _unique_strings(
            _field(
                item,
                [
                    "skills",
                    "technologies",
                    "tech_stack",
                ],
                [],
            )
        )

        objectives = _unique_strings(
            _field(
                item,
                [
                    "objectives",
                    "outcomes",
                    "highlights",
                ],
                [],
            )
        )

        result.append(
            {
                "title": title,
                "target_role": _clean_text(
                    _field(
                        item,
                        [
                            "target_role",
                            "role",
                        ],
                    )
                ),
                "description": _clean_text(
                    _field(
                        item,
                        [
                            "description",
                        ],
                    )
                ),
                "skills": skills,
                "objectives": objectives,
                "github_url": _clean_text(
                    _field(
                        item,
                        [
                            "github_url",
                            "github",
                        ],
                    )
                ),
                "demo_url": _clean_text(
                    _field(
                        item,
                        [
                            "demo_url",
                            "demo",
                            "live_url",
                        ],
                    )
                ),
            }
        )

    return result


def _template_config(
    template,
):
    template = (
        _clean_text(
            template
        ).lower()
        or "modern"
    )

    configs = {
        "modern": {
            "accent": "#4F46E5",
            "section": "#4338CA",
            "rule": 1.5,
        },
        "ats": {
            "accent": "#111827",
            "section": "#111827",
            "rule": 1.0,
        },
        "executive": {
            "accent": "#0F172A",
            "section": "#0F172A",
            "rule": 1.8,
        },
        "minimal": {
            "accent": "#475467",
            "section": "#475467",
            "rule": 0.8,
        },
    }

    return configs.get(
        template,
        configs["modern"],
    )


# =========================================================
# GENERATED CV PDF
# =========================================================


class GenerateCVPDFView(
    APIView
):
    permission_classes = [
        IsAuthenticated
    ]

    def post(
        self,
        request,
    ):
        data = request.data

        name = _clean_text(
            data.get(
                "name",
                "",
            )
        )

        title = _clean_text(
            data.get(
                "title",
                "",
            )
        )

        email = _clean_text(
            data.get(
                "email",
                request.user.email or "",
            )
        )

        phone = _clean_text(
            data.get(
                "phone",
                "",
            )
        )

        location = _clean_text(
            data.get(
                "location",
                "",
            )
        )

        linkedin = _clean_text(
            data.get(
                "linkedin",
                "",
            )
        )

        github = _clean_text(
            data.get(
                "github",
                "",
            )
        )

        portfolio = _clean_text(
            data.get(
                "portfolio",
                "",
            )
        )

        summary = _clean_text(
            data.get(
                "summary",
                "",
            )
        )

        selected_cv_id = data.get(
            "cv_id"
        )

        template = _clean_text(
            data.get(
                "template",
                "modern",
            )
        ).lower()

        if template not in {
            "modern",
            "ats",
            "executive",
            "minimal",
        }:
            template = "modern"

        sections = data.get(
            "sections",
            {},
        )

        if not isinstance(
            sections,
            dict,
        ):
            sections = {}

        show_summary = sections.get(
            "summary",
            True,
        )

        show_skills = sections.get(
            "skills",
            True,
        )

        show_experience = sections.get(
            "experience",
            True,
        )

        show_education = sections.get(
            "education",
            True,
        )

        show_certifications = sections.get(
            "certifications",
            True,
        )

        show_projects = sections.get(
            "projects",
            True,
        )

        show_achievements = sections.get(
            "achievements",
            True,
        )

        show_languages = sections.get(
            "languages",
            True,
        )

        show_links = sections.get(
            "links",
            True,
        )

        if not name:
            name = (
                request.user.get_full_name()
                or request.user.username
                or "Candidate"
            )

        parsed_data = {}

        if selected_cv_id:
            try:
                cv = CV.objects.get(
                    id=selected_cv_id,
                    user=request.user,
                )

                if isinstance(
                    cv.parsed_data,
                    dict,
                ):
                    parsed_data = (
                        cv.parsed_data
                    )

            except CV.DoesNotExist:
                parsed_data = {}

        # =====================================================
        # OPTIONAL STRUCTURED CONTENT
        # =====================================================

        content = data.get(
            "content",
            {},
        )

        if not isinstance(
            content,
            dict,
        ):
            content = {}

        # =====================================================
        # PROJECT FALLBACK
        # =====================================================

        try:
            from career_projects.models import (
                CareerProject,
            )

            completed_projects = (
                CareerProject.objects.filter(
                    user=request.user,
                    status="completed",
                ).order_by(
                    "-completed_at",
                    "-id",
                )
            )

        except Exception:
            completed_projects = []

        fallback_projects = []

        for project in completed_projects:
            fallback_projects.append(
                {
                    "title": getattr(
                        project,
                        "title",
                        "",
                    ),
                    "target_role": getattr(
                        project,
                        "target_role",
                        "",
                    )
                    or "",
                    "description": getattr(
                        project,
                        "description",
                        "",
                    )
                    or "",
                    "skills": getattr(
                        project,
                        "skills",
                        [],
                    )
                    or [],
                    "objectives": getattr(
                        project,
                        "objectives",
                        [],
                    )
                    or [],
                    "github_url": getattr(
                        project,
                        "github_url",
                        "",
                    )
                    or "",
                    "demo_url": getattr(
                        project,
                        "demo_url",
                        "",
                    )
                    or "",
                }
            )

        # =====================================================
        # SKILLS
        # =====================================================

        if "skills" in content:
            clean_skills = _unique_strings(
                content.get(
                    "skills",
                    [],
                )
            )
        else:
            raw_skills = []

            raw_skills.extend(
                _as_list(
                    parsed_data.get(
                        "skills",
                        [],
                    )
                )
            )

            raw_skills.extend(
                _as_list(
                    parsed_data.get(
                        "technical_skills",
                        [],
                    )
                )
            )

            for project in fallback_projects:
                raw_skills.extend(
                    _as_list(
                        project.get(
                            "skills",
                            [],
                        )
                    )
                )

            clean_skills = _unique_strings(
                raw_skills
            )

        # =====================================================
        # EXPERIENCE
        # =====================================================

        if "experience" in content:
            experience = (
                _normalize_experience(
                    content.get(
                        "experience",
                        [],
                    )
                )
            )
        else:
            experience = (
                _normalize_experience(
                    parsed_data.get(
                        "experience",
                        [],
                    )
                )
            )

        # =====================================================
        # EDUCATION
        # =====================================================

        if "education" in content:
            education = (
                _normalize_education(
                    content.get(
                        "education",
                        [],
                    )
                )
            )
        else:
            education = (
                _normalize_education(
                    parsed_data.get(
                        "education",
                        [],
                    )
                )
            )

        # =====================================================
        # CERTIFICATIONS
        # =====================================================

        if "certifications" in content:
            certifications = (
                _normalize_certifications(
                    content.get(
                        "certifications",
                        [],
                    )
                )
            )
        else:
            certifications = (
                _normalize_certifications(
                    parsed_data.get(
                        "certifications",
                        [],
                    )
                )
            )

            if not certifications:
                certifications = (
                    _normalize_certifications(
                        parsed_data.get(
                            "training",
                            [],
                        )
                    )
                )

        # =====================================================
        # PROJECTS
        # =====================================================

        if "projects" in content:
            projects = (
                _normalize_projects(
                    content.get(
                        "projects",
                        [],
                    )
                )
            )
        else:
            projects = (
                _normalize_projects(
                    parsed_data.get(
                        "projects",
                        [],
                    )
                )
            )

            if not projects:
                projects = (
                    _normalize_projects(
                        fallback_projects
                    )
                )

        # =====================================================
        # ACHIEVEMENTS
        # =====================================================

        if "achievements" in content:
            achievements = _unique_strings(
                content.get(
                    "achievements",
                    [],
                )
            )
        else:
            achievements = _unique_strings(
                parsed_data.get(
                    "achievements",
                    [],
                )
            )

        # =====================================================
        # LANGUAGES
        # =====================================================

        if "languages" in content:
            languages = _unique_strings(
                content.get(
                    "languages",
                    [],
                )
            )
        else:
            languages = _unique_strings(
                parsed_data.get(
                    "languages",
                    [],
                )
            )

        # =====================================================
        # LINKS
        # =====================================================

        links_payload = content.get(
            "links",
            {},
        )

        if not isinstance(
            links_payload,
            dict,
        ):
            links_payload = {}

        linkedin = _clean_text(
            links_payload.get(
                "linkedin",
                linkedin,
            )
        )

        github = _clean_text(
            links_payload.get(
                "github",
                github,
            )
        )

        portfolio = _clean_text(
            links_payload.get(
                "portfolio",
                portfolio,
            )
        )

        # =====================================================
        # PDF SETUP
        # =====================================================

        template_config = _template_config(
            template
        )

        accent_color = colors.HexColor(
            template_config["accent"]
        )

        section_color = colors.HexColor(
            template_config["section"]
        )

        buffer = BytesIO()

        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=17 * mm,
            leftMargin=17 * mm,
            topMargin=15 * mm,
            bottomMargin=15 * mm,
            title=f"{name} - CV",
            author="AI Career Assistant",
        )

        styles = getSampleStyleSheet()

        name_style = ParagraphStyle(
            "CVName",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=28,
            textColor=colors.HexColor(
                "#111827"
            ),
            spaceAfter=4,
        )

        title_style = ParagraphStyle(
            "CVTitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=15,
            textColor=colors.HexColor(
                "#4B5563"
            ),
            spaceAfter=6,
        )

        contact_style = ParagraphStyle(
            "Contact",
            parent=styles["Normal"],
            fontSize=8.3,
            leading=11.5,
            textColor=colors.HexColor(
                "#4B5563"
            ),
            alignment=TA_LEFT,
        )

        section_style = ParagraphStyle(
            "Section",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            textColor=section_color,
            spaceBefore=13,
            spaceAfter=6,
        )

        body_style = ParagraphStyle(
            "Body",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=8.8,
            leading=13,
            textColor=colors.HexColor(
                "#374151"
            ),
            spaceAfter=4,
        )

        entry_title_style = ParagraphStyle(
            "EntryTitle",
            parent=body_style,
            fontName="Helvetica-Bold",
            fontSize=9,
            textColor=colors.HexColor(
                "#111827"
            ),
        )

        small_style = ParagraphStyle(
            "Small",
            parent=body_style,
            fontSize=7.8,
            leading=11,
            textColor=colors.HexColor(
                "#6B7280"
            ),
        )

        bullet_style = ParagraphStyle(
            "Bullet",
            parent=body_style,
            leftIndent=10,
            firstLineIndent=-6,
            fontSize=8.2,
            leading=12,
            spaceAfter=2,
        )

        skill_style = ParagraphStyle(
            "Skill",
            parent=body_style,
            fontSize=8.0,
            leading=11,
            textColor=colors.HexColor(
                "#4B5563"
            ),
        )

        story = []

        # =====================================================
        # HEADER
        # =====================================================

        header_left = [
            Paragraph(
                _escape(name),
                name_style,
            ),
            Paragraph(
                _escape(
                    title
                    or "Professional"
                ),
                title_style,
            ),
        ]

        contact_lines = []

        for value in [
            email,
            phone,
            location,
            linkedin,
            github,
            portfolio,
        ]:
            if value:
                contact_lines.append(
                    _escape(value)
                )

        contact_paragraphs = [
            Paragraph(
                line,
                contact_style,
            )
            for line in contact_lines
        ]

        if not contact_paragraphs:
            contact_paragraphs = [
                Paragraph(
                    "",
                    contact_style,
                )
            ]

        header_table = Table(
            [
                [
                    header_left,
                    contact_paragraphs,
                ]
            ],
            colWidths=[
                105 * mm,
                65 * mm,
            ],
        )

        header_table.setStyle(
            TableStyle(
                [
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        0,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        0,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        0,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        0,
                    ),
                ]
            )
        )

        story.append(
            header_table
        )

        story.append(
            Spacer(
                1,
                5,
            )
        )

        story.append(
            HRFlowable(
                width="100%",
                thickness=template_config[
                    "rule"
                ],
                color=accent_color,
            )
        )

        # =====================================================
        # SUMMARY
        # =====================================================

        if (
            show_summary
            and summary
        ):
            story.append(
                Paragraph(
                    "PROFESSIONAL SUMMARY",
                    section_style,
                )
            )

            story.append(
                Paragraph(
                    _escape(summary),
                    body_style,
                )
            )

        # =====================================================
        # SKILLS
        # =====================================================

        if (
            show_skills
            and clean_skills
        ):
            story.append(
                Paragraph(
                    "TECHNICAL SKILLS",
                    section_style,
                )
            )

            skill_text = " • ".join(
                _escape(skill)
                for skill in clean_skills
            )

            story.append(
                Paragraph(
                    skill_text,
                    skill_style,
                )
            )

        # =====================================================
        # EXPERIENCE
        # =====================================================

        if (
            show_experience
            and experience
        ):
            story.append(
                Paragraph(
                    "EXPERIENCE",
                    section_style,
                )
            )

            for item in experience:
                entry = []

                job_title = (
                    item.get(
                        "job_title"
                    )
                    or "Professional Experience"
                )

                company = item.get(
                    "company",
                    "",
                )

                duration = item.get(
                    "duration",
                    "",
                )

                description = (
                    item.get(
                        "description",
                        "",
                    )
                    or ""
                )

                heading_text = _escape(
                    job_title
                )

                if company:
                    heading_text += (
                        " — "
                        + _escape(company)
                    )

                entry.append(
                    Paragraph(
                        heading_text,
                        entry_title_style,
                    )
                )

                if duration:
                    entry.append(
                        Paragraph(
                            _escape(
                                duration
                            ),
                            small_style,
                        )
                    )

                if description:
                    description_lines = [
                        part.strip()
                        for part in description.replace(
                            "•",
                            "\n",
                        ).splitlines()
                        if part.strip()
                    ]

                    if len(
                        description_lines
                    ) > 1:
                        for bullet in description_lines:
                            entry.append(
                                Paragraph(
                                    "• "
                                    + _escape(
                                        bullet
                                    ),
                                    bullet_style,
                                )
                            )
                    else:
                        entry.append(
                            Paragraph(
                                _escape(
                                    description
                                ),
                                body_style,
                            )
                        )

                story.append(
                    KeepTogether(entry)
                )

        # =====================================================
        # EDUCATION
        # =====================================================

        if (
            show_education
            and education
        ):
            story.append(
                Paragraph(
                    "EDUCATION",
                    section_style,
                )
            )

            for item in education:
                entry = []

                degree = (
                    item.get(
                        "degree"
                    )
                    or "Education"
                )

                institution = (
                    item.get(
                        "institution"
                    )
                    or ""
                )

                year = (
                    item.get(
                        "year"
                    )
                    or ""
                )

                description = (
                    item.get(
                        "description",
                        "",
                    )
                    or ""
                )

                heading_text = _escape(
                    degree
                )

                if institution:
                    heading_text += (
                        " — "
                        + _escape(
                            institution
                        )
                    )

                entry.append(
                    Paragraph(
                        heading_text,
                        entry_title_style,
                    )
                )

                if year:
                    entry.append(
                        Paragraph(
                            _escape(year),
                            small_style,
                        )
                    )

                if description:
                    entry.append(
                        Paragraph(
                            _escape(
                                description
                            ),
                            body_style,
                        )
                    )

                story.append(
                    KeepTogether(entry)
                )

        # =====================================================
        # CERTIFICATIONS
        # =====================================================

        if (
            show_certifications
            and certifications
        ):
            story.append(
                Paragraph(
                    "CERTIFICATIONS & TRAINING",
                    section_style,
                )
            )

            for item in certifications:
                entry = []

                name_value = item.get(
                    "name",
                    "",
                )

                issuer = item.get(
                    "issuer",
                    "",
                )

                year = item.get(
                    "year",
                    "",
                )

                heading_text = _escape(
                    name_value
                )

                if issuer:
                    heading_text += (
                        " — "
                        + _escape(
                            issuer
                        )
                    )

                if year:
                    heading_text += (
                        f" ({_escape(year)})"
                    )

                entry.append(
                    Paragraph(
                        heading_text,
                        entry_title_style,
                    )
                )

                story.append(
                    KeepTogether(entry)
                )

        # =====================================================
        # PROJECTS
        # =====================================================

        if (
            show_projects
            and projects
        ):
            story.append(
                Paragraph(
                    "SELECTED PROJECTS",
                    section_style,
                )
            )

            for project in projects:
                project_story = []

                project_title = (
                    project.get(
                        "title",
                        "",
                    )
                    or "Project"
                )

                target_role = (
                    project.get(
                        "target_role",
                        "",
                    )
                    or ""
                )

                description = (
                    project.get(
                        "description",
                        "",
                    )
                    or ""
                )

                skills = _unique_strings(
                    project.get(
                        "skills",
                        [],
                    )
                )

                objectives = _unique_strings(
                    project.get(
                        "objectives",
                        [],
                    )
                )

                github_url = _clean_text(
                    project.get(
                        "github_url",
                        "",
                    )
                )

                demo_url = _clean_text(
                    project.get(
                        "demo_url",
                        "",
                    )
                )

                project_story.append(
                    Paragraph(
                        _escape(
                            project_title
                        ),
                        entry_title_style,
                    )
                )

                if target_role:
                    project_story.append(
                        Paragraph(
                            _escape(
                                target_role
                            ),
                            small_style,
                        )
                    )

                if description:
                    project_story.append(
                        Paragraph(
                            _escape(
                                description
                            ),
                            body_style,
                        )
                    )

                for objective in objectives[:4]:
                    project_story.append(
                        Paragraph(
                            "• "
                            + _escape(
                                objective
                            ),
                            bullet_style,
                        )
                    )

                if skills:
                    project_story.append(
                        Paragraph(
                            "Tech: "
                            + " • ".join(
                                _escape(
                                    skill
                                )
                                for skill in skills
                            ),
                            small_style,
                        )
                    )

                links = []

                if github_url:
                    links.append(
                        "GitHub: "
                        + _escape(
                            github_url
                        )
                    )

                if demo_url:
                    links.append(
                        "Demo: "
                        + _escape(
                            demo_url
                        )
                    )

                if links:
                    project_story.append(
                        Paragraph(
                            " | ".join(links),
                            small_style,
                        )
                    )

                story.append(
                    KeepTogether(
                        project_story
                    )
                )

        # =====================================================
        # ACHIEVEMENTS
        # =====================================================

        if (
            show_achievements
            and achievements
        ):
            story.append(
                Paragraph(
                    "ACHIEVEMENTS",
                    section_style,
                )
            )

            for achievement in achievements:
                story.append(
                    Paragraph(
                        "• "
                        + _escape(
                            achievement
                        ),
                        bullet_style,
                    )
                )

        # =====================================================
        # LANGUAGES
        # =====================================================

        if (
            show_languages
            and languages
        ):
            story.append(
                Paragraph(
                    "LANGUAGES",
                    section_style,
                )
            )

            story.append(
                Paragraph(
                    " • ".join(
                        _escape(language)
                        for language in languages
                    ),
                    body_style,
                )
            )

        # =====================================================
        # LINKS
        # =====================================================

        if (
            show_links
            and (
                linkedin
                or github
                or portfolio
            )
        ):
            story.append(
                Paragraph(
                    "PROFESSIONAL LINKS",
                    section_style,
                )
            )

            links = []

            if linkedin:
                links.append(
                    "LinkedIn: "
                    + _escape(linkedin)
                )

            if github:
                links.append(
                    "GitHub: "
                    + _escape(github)
                )

            if portfolio:
                links.append(
                    "Portfolio: "
                    + _escape(portfolio)
                )

            story.append(
                Paragraph(
                    "<br/>".join(links),
                    body_style,
                )
            )

        # =====================================================
        # BUILD PDF
        # =====================================================

        document.build(story)

        buffer.seek(0)

        safe_name = (
            name.replace("/", "_")
            .replace("\\", "_")
            .replace(" ", "_")
            .strip("_")
            or "Candidate"
        )

        filename = (
            f"{safe_name}_CV.pdf"
        )

        return FileResponse(
            buffer,
            as_attachment=True,
            filename=filename,
            content_type="application/pdf",
        )