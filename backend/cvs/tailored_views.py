import re
from io import BytesIO
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

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CV


def normalize_text(value):
    if value is None:
        return ""

    return re.sub(
        r"[^a-zA-Z0-9+#.\- ]+",
        " ",
        str(value).lower(),
    ).strip()


def extract_words(text):
    normalized = normalize_text(text)

    words = set()

    for word in normalized.split():
        cleaned = word.strip(".,:;()[]{}")

        if len(cleaned) >= 2:
            words.add(cleaned)

    return words


def calculate_overlap(text_a, text_b):
    words_a = extract_words(text_a)
    words_b = extract_words(text_b)

    if not words_b:
        return 0

    return len(
        words_a.intersection(words_b)
    )


def safe_text(value):
    """
    Escape text before passing it to ReportLab Paragraph.
    """
    if value is None:
        return ""

    return escape(str(value))


def get_profile_data(user):
    """
    Safely retrieve profile information if the profiles
    app exposes a related Profile model.
    """
    data = {
        "name": (
            user.get_full_name()
            or user.username
            or "Candidate"
        ),
        "email": user.email or "",
        "phone": "",
        "location": "",
        "linkedin": "",
        "career_goal": "",
        "bio": "",
    }

    try:
        from profiles.models import Profile

        profile = (
            Profile.objects.filter(
                user=user
            ).first()
        )

        if profile:
            data["name"] = (
                getattr(
                    profile,
                    "full_name",
                    "",
                )
                or data["name"]
            )

            data["phone"] = (
                getattr(
                    profile,
                    "phone",
                    "",
                )
                or ""
            )

            data["location"] = (
                getattr(
                    profile,
                    "location",
                    "",
                )
                or ""
            )

            data["linkedin"] = (
                getattr(
                    profile,
                    "linkedin_url",
                    "",
                )
                or ""
            )

            data["career_goal"] = (
                getattr(
                    profile,
                    "career_goal",
                    "",
                )
                or ""
            )

            data["bio"] = (
                getattr(
                    profile,
                    "bio",
                    "",
                )
                or ""
            )

    except Exception:
        pass

    return data


class TailorCVView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        job_title = str(
            request.data.get(
                "job_title",
                "",
            )
        ).strip()

        job_description = str(
            request.data.get(
                "job_description",
                "",
            )
        ).strip()

        required_skills = request.data.get(
            "required_skills",
            [],
        )

        cv_id = request.data.get(
            "cv_id"
        )

        if not job_title:
            return Response(
                {
                    "detail": (
                        "Job title is required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not job_description:
            return Response(
                {
                    "detail": (
                        "Job description is required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(
            required_skills,
            list,
        ):
            required_skills = []

        # --------------------------------------------------
        # Load CV
        # --------------------------------------------------

        cv = None

        if cv_id:
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

        if cv is None:
            cv = (
                CV.objects.filter(
                    user=request.user
                )
                .order_by("-uploaded_at")
                .first()
            )

        if cv is None:
            return Response(
                {
                    "detail": (
                        "Please upload a CV before "
                        "tailoring it."
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

        # --------------------------------------------------
        # Candidate skills
        # --------------------------------------------------

        candidate_skills = []

        parsed_skills = parsed_data.get(
            "skills",
            [],
        )

        technical_skills = parsed_data.get(
            "technical_skills",
            [],
        )

        if isinstance(
            parsed_skills,
            list,
        ):
            candidate_skills.extend(
                parsed_skills
            )

        if isinstance(
            technical_skills,
            list,
        ):
            candidate_skills.extend(
                technical_skills
            )

        candidate_skills = [
            str(skill).strip()
            for skill in candidate_skills
            if str(skill).strip()
        ]

        candidate_skills = list(
            dict.fromkeys(
                candidate_skills
            )
        )

        # --------------------------------------------------
        # Detect required skills
        # --------------------------------------------------

        job_text = (
            f"{job_title} {job_description}"
        )

        job_words = extract_words(
            job_text
        )

        detected_skills = []

        for skill in required_skills:
            skill_text = str(
                skill
            ).strip()

            if skill_text:
                detected_skills.append(
                    skill_text
                )

        common_skills = [
            "python",
            "java",
            "javascript",
            "typescript",
            "react",
            "react.js",
            "node",
            "node.js",
            "django",
            "flask",
            "fastapi",
            "sql",
            "postgresql",
            "mysql",
            "mongodb",
            "docker",
            "git",
            "github",
            "html",
            "css",
            "bootstrap",
            "machine learning",
            "deep learning",
            "artificial intelligence",
            "ai",
            "nlp",
            "tensorflow",
            "pytorch",
            "scikit-learn",
            "rest api",
            "rest",
            "api",
            "aws",
            "azure",
            "linux",
            "c++",
            "c#",
            "data structures",
            "algorithms",
            "communication",
            "problem solving",
            "teamwork",
        ]

        for skill in common_skills:
            normalized_skill = normalize_text(
                skill
            )

            if (
                normalized_skill
                and normalized_skill in job_words
            ):
                detected_skills.append(
                    skill
                )

        detected_skills = list(
            dict.fromkeys(
                detected_skills
            )
        )

        # --------------------------------------------------
        # Match skills
        # --------------------------------------------------

        matched_skills = []
        missing_skills = []

        for required_skill in detected_skills:
            required_normalized = normalize_text(
                required_skill
            )

            matched = False

            for candidate_skill in candidate_skills:
                candidate_normalized = normalize_text(
                    candidate_skill
                )

                if (
                    required_normalized
                    == candidate_normalized
                    or required_normalized
                    in candidate_normalized
                    or candidate_normalized
                    in required_normalized
                ):
                    matched = True
                    break

            if matched:
                matched_skills.append(
                    required_skill
                )
            else:
                missing_skills.append(
                    required_skill
                )

        # --------------------------------------------------
        # Completed projects
        # --------------------------------------------------

        try:
            from career_projects.models import CareerProject

            completed_projects = list(
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

        project_results = []

        for project in completed_projects:
            project_skills = (
                getattr(
                    project,
                    "skills",
                    [],
                )
                or []
            )

            project_text_parts = [
                getattr(
                    project,
                    "title",
                    "",
                ),
                getattr(
                    project,
                    "description",
                    "",
                ),
                getattr(
                    project,
                    "target_role",
                    "",
                ),
            ]

            if isinstance(
                project_skills,
                list,
            ):
                project_text_parts.extend(
                    project_skills
                )

            project_text = " ".join(
                str(part)
                for part in project_text_parts
                if part
            )

            score = calculate_overlap(
                project_text,
                job_text,
            )

            for required_skill in detected_skills:
                if normalize_text(
                    required_skill
                ) in normalize_text(
                    project_text
                ):
                    score += 2

            project_results.append(
                {
                    "id": project.id,
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
                    "skills": project_skills,
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
                    "relevance_score": score,
                }
            )

        project_results.sort(
            key=lambda item: item[
                "relevance_score"
            ],
            reverse=True,
        )

        recommended_projects = (
            project_results[:3]
        )

        # --------------------------------------------------
        # Match score
        # --------------------------------------------------

        total_required = len(
            detected_skills
        )

        if total_required > 0:
            skill_match_score = round(
                (
                    len(matched_skills)
                    / total_required
                )
                * 100
            )
        else:
            skill_match_score = 50

        project_bonus = 0

        if recommended_projects:
            top_score = recommended_projects[
                0
            ]["relevance_score"]

            if top_score >= 8:
                project_bonus = 10

            elif top_score >= 4:
                project_bonus = 5

        overall_score = min(
            100,
            skill_match_score
            + project_bonus,
        )

        # --------------------------------------------------
        # Tailored summary
        # --------------------------------------------------

        top_skills = matched_skills[:5]

        if top_skills:
            skill_sentence = ", ".join(
                top_skills
            )

            tailored_summary = (
                f"Motivated {job_title} candidate "
                f"with hands-on experience in "
                f"{skill_sentence}. "
                f"Experienced in building practical "
                f"software solutions and completing "
                f"real-world projects, with a strong "
                f"focus on applying technical skills "
                f"to business and user needs."
            )
        else:
            tailored_summary = (
                f"Motivated candidate targeting "
                f"a {job_title} position, with "
                f"hands-on experience through "
                f"practical projects and a strong "
                f"commitment to continuous learning "
                f"and professional development."
            )

        return Response(
            {
                "job": {
                    "title": job_title,
                    "description": job_description,
                },

                "cv": {
                    "id": cv.id,
                    "title": cv.title,
                },

                "match": {
                    "score": overall_score,
                    "skill_match_score": skill_match_score,
                    "matched_skills": matched_skills,
                    "missing_skills": missing_skills,
                },

                "skills": {
                    "candidate_skills": candidate_skills,
                    "required_skills": detected_skills,
                    "matched_skills": matched_skills,
                    "missing_skills": missing_skills,
                },

                "recommended_projects": (
                    recommended_projects
                ),

                "tailored_summary": tailored_summary,

                "candidate_context": (
                    request.user.get_full_name()
                    or request.user.username
                    or "Candidate"
                ),
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# TAILORED CV PDF
# =========================================================

class TailoredCVPDFView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        job_title = str(
            request.data.get(
                "job_title",
                "",
            )
        ).strip()

        tailored_summary = str(
            request.data.get(
                "tailored_summary",
                "",
            )
        ).strip()

        matched_skills = request.data.get(
            "matched_skills",
            [],
        )

        recommended_project_ids = (
            request.data.get(
                "recommended_project_ids",
                [],
            )
        )

        cv_id = request.data.get(
            "cv_id"
        )

        if not job_title:
            return Response(
                {
                    "detail": (
                        "Job title is required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(
            matched_skills,
            list,
        ):
            matched_skills = []

        if not isinstance(
            recommended_project_ids,
            list,
        ):
            recommended_project_ids = []

        # --------------------------------------------------
        # Load selected CV
        # --------------------------------------------------

        cv = None

        if cv_id:
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

        if cv is None:
            cv = (
                CV.objects.filter(
                    user=request.user
                )
                .order_by("-uploaded_at")
                .first()
            )

        if cv is None:
            return Response(
                {
                    "detail": (
                        "Please upload a CV first."
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

        experience = parsed_data.get(
            "experience",
            [],
        )

        education = parsed_data.get(
            "education",
            [],
        )

        if not isinstance(
            experience,
            list,
        ):
            experience = []

        if not isinstance(
            education,
            list,
        ):
            education = []

        # --------------------------------------------------
        # Profile
        # --------------------------------------------------

        profile = get_profile_data(
            request.user
        )

        # --------------------------------------------------
        # Projects
        # --------------------------------------------------

        selected_projects = []

        try:
            from career_projects.models import CareerProject

            queryset = CareerProject.objects.filter(
                user=request.user,
                status="completed",
            )

            if recommended_project_ids:
                ordered_projects = []

                for project_id in (
                    recommended_project_ids
                ):
                    try:
                        project = queryset.get(
                            id=int(project_id)
                        )
                        ordered_projects.append(
                            project
                        )
                    except (
                        CareerProject.DoesNotExist,
                        ValueError,
                        TypeError,
                    ):
                        continue

                selected_projects = (
                    ordered_projects
                )

            if not selected_projects:
                selected_projects = list(
                    queryset.order_by(
                        "-completed_at",
                        "-id",
                    )[:3]
                )

        except Exception:
            selected_projects = []

        # --------------------------------------------------
        # Build PDF
        # --------------------------------------------------

        buffer = BytesIO()

        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=17 * mm,
            leftMargin=17 * mm,
            topMargin=15 * mm,
            bottomMargin=15 * mm,
            title=f"{profile['name']} - Tailored CV",
            author="AI Career Assistant",
        )

        styles = getSampleStyleSheet()

        name_style = ParagraphStyle(
            "TailoredName",
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
            "TailoredTitle",
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
            "TailoredContact",
            parent=styles["Normal"],
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor(
                "#4B5563"
            ),
        )

        section_style = ParagraphStyle(
            "TailoredSection",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            textColor=colors.HexColor(
                "#111827"
            ),
            spaceBefore=13,
            spaceAfter=6,
        )

        body_style = ParagraphStyle(
            "TailoredBody",
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
            "TailoredEntryTitle",
            parent=body_style,
            fontName="Helvetica-Bold",
            fontSize=9,
            textColor=colors.HexColor(
                "#111827"
            ),
        )

        small_style = ParagraphStyle(
            "TailoredSmall",
            parent=body_style,
            fontSize=8,
            leading=11,
            textColor=colors.HexColor(
                "#6B7280"
            ),
        )

        story = []

        # --------------------------------------------------
        # Header
        # --------------------------------------------------

        header_left = [
            Paragraph(
                safe_text(
                    profile["name"]
                ),
                name_style,
            ),

            Paragraph(
                safe_text(
                    job_title
                    or profile["career_goal"]
                    or "Professional"
                ),
                title_style,
            ),
        ]

        contact_lines = []

        for value in [
            profile["email"],
            profile["phone"],
            profile["location"],
        ]:
            if value:
                contact_lines.append(
                    Paragraph(
                        safe_text(value),
                        contact_style,
                    )
                )

        if not contact_lines:
            contact_lines.append(
                Paragraph(
                    "",
                    contact_style,
                )
            )

        header_table = Table(
            [
                [
                    header_left,
                    contact_lines,
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

        story.append(header_table)

        story.append(
            Spacer(
                1,
                5,
            )
        )

        story.append(
            HRFlowable(
                width="100%",
                thickness=1.4,
                color=colors.HexColor(
                    "#111827"
                ),
            )
        )

        # --------------------------------------------------
        # Target Position
        # --------------------------------------------------

        story.append(
            Paragraph(
                "TARGET POSITION",
                section_style,
            )
        )

        story.append(
            Paragraph(
                safe_text(job_title),
                entry_title_style,
            )
        )

        # --------------------------------------------------
        # Tailored Summary
        # --------------------------------------------------

        if tailored_summary:
            story.append(
                Paragraph(
                    "PROFESSIONAL SUMMARY",
                    section_style,
                )
            )

            story.append(
                Paragraph(
                    safe_text(
                        tailored_summary
                    ),
                    body_style,
                )
            )

        # --------------------------------------------------
        # Matched Skills
        # --------------------------------------------------

        clean_matched_skills = []

        for skill in matched_skills:
            skill = str(skill).strip()

            if (
                skill
                and skill
                not in clean_matched_skills
            ):
                clean_matched_skills.append(
                    skill
                )

        if clean_matched_skills:
            story.append(
                Paragraph(
                    "RELEVANT SKILLS",
                    section_style,
                )
            )

            skills_text = " • ".join(
                safe_text(skill)
                for skill
                in clean_matched_skills
            )

            story.append(
                Paragraph(
                    skills_text,
                    body_style,
                )
            )

        # --------------------------------------------------
        # Experience
        # --------------------------------------------------

        if experience:
            story.append(
                Paragraph(
                    "EXPERIENCE",
                    section_style,
                )
            )

            for item in experience:
                if not isinstance(
                    item,
                    dict,
                ):
                    continue

                job_item_title = (
                    item.get(
                        "job_title"
                    )
                    or item.get(
                        "title"
                    )
                    or item.get(
                        "position"
                    )
                    or "Professional Experience"
                )

                company = (
                    item.get(
                        "company"
                    )
                    or item.get(
                        "organization"
                    )
                    or ""
                )

                duration = (
                    item.get(
                        "duration"
                    )
                    or item.get(
                        "date"
                    )
                    or item.get(
                        "period"
                    )
                    or ""
                )

                description = item.get(
                    "description",
                    "",
                )

                entry = []

                heading = safe_text(
                    job_item_title
                )

                if company:
                    heading += (
                        f" — {safe_text(company)}"
                    )

                entry.append(
                    Paragraph(
                        heading,
                        entry_title_style,
                    )
                )

                if duration:
                    entry.append(
                        Paragraph(
                            safe_text(
                                duration
                            ),
                            small_style,
                        )
                    )

                if description:
                    entry.append(
                        Paragraph(
                            safe_text(
                                description
                            ),
                            body_style,
                        )
                    )

                story.append(
                    KeepTogether(entry)
                )

        # --------------------------------------------------
        # Education
        # --------------------------------------------------

        if education:
            story.append(
                Paragraph(
                    "EDUCATION",
                    section_style,
                )
            )

            for item in education:
                if not isinstance(
                    item,
                    dict,
                ):
                    continue

                degree = (
                    item.get(
                        "degree"
                    )
                    or item.get(
                        "title"
                    )
                    or "Education"
                )

                institution = (
                    item.get(
                        "institution"
                    )
                    or item.get(
                        "university"
                    )
                    or item.get(
                        "school"
                    )
                    or ""
                )

                year = (
                    item.get(
                        "year"
                    )
                    or item.get(
                        "date"
                    )
                    or ""
                )

                heading = safe_text(
                    degree
                )

                if institution:
                    heading += (
                        f" — {safe_text(institution)}"
                    )

                entry = [
                    Paragraph(
                        heading,
                        entry_title_style,
                    )
                ]

                if year:
                    entry.append(
                        Paragraph(
                            safe_text(year),
                            small_style,
                        )
                    )

                description = item.get(
                    "description",
                    "",
                )

                if description:
                    entry.append(
                        Paragraph(
                            safe_text(
                                description
                            ),
                            body_style,
                        )
                    )

                story.append(
                    KeepTogether(entry)
                )

        # --------------------------------------------------
        # Selected Projects
        # --------------------------------------------------

        if selected_projects:
            story.append(
                Paragraph(
                    "RELEVANT PROJECTS",
                    section_style,
                )
            )

            for project in selected_projects:
                project_title = (
                    getattr(
                        project,
                        "title",
                        "",
                    )
                    or "Project"
                )

                description = (
                    getattr(
                        project,
                        "description",
                        "",
                    )
                    or ""
                )

                target_role = (
                    getattr(
                        project,
                        "target_role",
                        "",
                    )
                    or ""
                )

                skills = (
                    getattr(
                        project,
                        "skills",
                        [],
                    )
                    or []
                )

                objectives = (
                    getattr(
                        project,
                        "objectives",
                        [],
                    )
                    or []
                )

                github_url = (
                    getattr(
                        project,
                        "github_url",
                        "",
                    )
                    or ""
                )

                demo_url = (
                    getattr(
                        project,
                        "demo_url",
                        "",
                    )
                    or ""
                )

                entry = []

                entry.append(
                    Paragraph(
                        safe_text(
                            project_title
                        ),
                        entry_title_style,
                    )
                )

                if target_role:
                    entry.append(
                        Paragraph(
                            safe_text(
                                target_role
                            ),
                            small_style,
                        )
                    )

                if description:
                    entry.append(
                        Paragraph(
                            safe_text(
                                description
                            ),
                            body_style,
                        )
                    )

                if isinstance(
                    objectives,
                    list,
                ) and objectives:
                    objective_text = (
                        "Key Outcomes: "
                        + " • ".join(
                            safe_text(item)
                            for item in objectives
                        )
                    )

                    entry.append(
                        Paragraph(
                            objective_text,
                            small_style,
                        )
                    )

                if isinstance(
                    skills,
                    list,
                ) and skills:
                    skills_text = (
                        "Tech: "
                        + " • ".join(
                            safe_text(skill)
                            for skill in skills
                        )
                    )

                    entry.append(
                        Paragraph(
                            skills_text,
                            small_style,
                        )
                    )

                links = []

                if github_url:
                    links.append(
                        "GitHub: "
                        + safe_text(
                            github_url
                        )
                    )

                if demo_url:
                    links.append(
                        "Demo: "
                        + safe_text(
                            demo_url
                        )
                    )

                if links:
                    entry.append(
                        Paragraph(
                            " | ".join(links),
                            small_style,
                        )
                    )

                story.append(
                    KeepTogether(entry)
                )

        # --------------------------------------------------
        # Links
        # --------------------------------------------------

        if (
            profile["linkedin"]
            or profile["email"]
        ):
            story.append(
                Paragraph(
                    "PROFESSIONAL LINKS",
                    section_style,
                )
            )

            links = []

            if profile["linkedin"]:
                links.append(
                    "LinkedIn: "
                    + safe_text(
                        profile["linkedin"]
                    )
                )

            if profile["email"]:
                links.append(
                    "Email: "
                    + safe_text(
                        profile["email"]
                    )
                )

            story.append(
                Paragraph(
                    "<br/>".join(links),
                    body_style,
                )
            )

        # --------------------------------------------------
        # Build
        # --------------------------------------------------

        document.build(story)

        buffer.seek(0)

        filename = (
            f"{profile['name'].replace(' ', '_')}"
            f"_Tailored_CV.pdf"
        )

        return FileResponse(
            buffer,
            as_attachment=True,
            filename=filename,
            content_type="application/pdf",
        )