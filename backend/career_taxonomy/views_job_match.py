from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cvs.models import CV

from cv_analysis.services.ats_analyzer import analyze_ats

from .models import Role
from .services.candidate_intelligence import (
    build_candidate_intelligence,
)
from .services.job_intelligence import (
    build_job_intelligence,
)
from .services.personalized_roadmap import (
    build_personalized_roadmap,
)


class CareerTaxonomyJobMatchView(APIView):
    """
    Career Intelligence endpoint used by the existing frontend:

        POST /api/career-taxonomy/job-match/

    Input:
        {
            "cv_id": 1,
            "job_description": "..."
        }

    Response:
        {
            "analysis": {
                "job_match": {...},
                "application_readiness": {...},
                "candidate_profile": {...},
                "job_skills": [...],
                "detected_roles": [...],
                "roadmap": {
                    "status": "success",
                    "role": {...},
                    "total_phases": 0,
                    "total_hours": 0,
                    "phases": [...]
                }
            }
        }
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        cv_id = request.data.get(
            "cv_id"
        )

        job_description = str(
            request.data.get(
                "job_description"
            )
            or ""
        ).strip()

        # ---------------------------------------------------------
        # Validate input
        # ---------------------------------------------------------
        if not cv_id:
            return Response(
                {
                    "detail": "cv_id is required."
                },
                status=400,
            )

        if len(job_description) < 30:
            return Response(
                {
                    "detail": (
                        "Please provide a complete job description "
                        "of at least 30 characters."
                    )
                },
                status=400,
            )

        # ---------------------------------------------------------
        # Get CV belonging to authenticated user
        # ---------------------------------------------------------
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
                status=404,
            )

        # ---------------------------------------------------------
        # ATS analysis
        # ---------------------------------------------------------
        ats_result = analyze_ats(
            parsed_data=cv.parsed_data,
            extracted_text=cv.extracted_text,
        )

        ats_score = ats_result.get(
            "score",
            0,
        )

        # ---------------------------------------------------------
        # Candidate Intelligence
        #
        # This is the normalized candidate profile used by the
        # Career Intelligence platform.
        # ---------------------------------------------------------
        candidate_profile = (
            build_candidate_intelligence(
                parsed_data=cv.parsed_data,
                extracted_text=(
                    cv.extracted_text or ""
                ),
            )
        )

        # ---------------------------------------------------------
        # Existing Job Intelligence
        #
        # Keep the existing matching behavior and response fields.
        # ---------------------------------------------------------
        intelligence = (
            build_job_intelligence(
                cv=cv,
                job_description=job_description,
                ats_score=ats_score,
            )
        )

        job_skills = intelligence.get(
            "job_skills",
            [],
        )

        detected_roles = intelligence.get(
            "detected_roles",
            [],
        )

        job_match = intelligence.get(
            "job_match",
            {},
        )

        application_readiness = (
            intelligence.get(
                "application_readiness",
                {},
            )
        )

        # ---------------------------------------------------------
        # Personalized Roadmap
        #
        # build_job_intelligence() already identifies the best role
        # and the candidate's matched / partial / missing skills.
        #
        # Here we adapt those results to the richer
        # build_personalized_roadmap() engine.
        # ---------------------------------------------------------
        roadmap = {
            "status": "success",
            "role": None,
            "total_phases": 0,
            "total_hours": 0,
            "phases": [],
        }

        matched_role = job_match.get(
            "role"
        )

        if (
            isinstance(
                matched_role,
                dict,
            )
            and matched_role.get("id")
        ):
            role_id = matched_role.get(
                "id"
            )

            role = (
                Role.objects
                .filter(
                    id=role_id,
                    is_active=True,
                )
                .select_related(
                    "track",
                    "track__category",
                )
                .prefetch_related(
                    "role_skills__skill",
                    "roadmap_phases__steps__skill",
                )
                .first()
            )

            if role is not None:
                skill_match = job_match.get(
                    "skill_match",
                    {},
                )

                missing = skill_match.get(
                    "missing",
                    [],
                )

                partial = skill_match.get(
                    "partial",
                    [],
                )

                priority_missing = job_match.get(
                    "priority_missing_skills",
                    [],
                )

                # -------------------------------------------------
                # Normalize missing skills
                # -------------------------------------------------
                missing_skills = []

                for item in missing:
                    skill_id = item.get(
                        "skill_id"
                    )

                    if not skill_id:
                        continue

                    missing_skills.append(
                        {
                            "skill_id": skill_id,
                            "name": item.get(
                                "name",
                                "",
                            ),
                            "slug": item.get(
                                "slug",
                                "",
                            ),
                            "importance": item.get(
                                "importance"
                            ),
                            "weight": item.get(
                                "weight",
                                0,
                            ),
                            "minimum_level": item.get(
                                "minimum_level"
                            ),
                        }
                    )

                # -------------------------------------------------
                # Normalize improvement skills
                #
                # Partial/non-required skills are treated as
                # skills that need improvement.
                # -------------------------------------------------
                improvement_skills = []

                for item in partial:
                    skill_id = item.get(
                        "skill_id"
                    )

                    if not skill_id:
                        continue

                    improvement_skills.append(
                        {
                            "skill_id": skill_id,
                            "name": item.get(
                                "name",
                                "",
                            ),
                            "slug": item.get(
                                "slug",
                                "",
                            ),
                            "importance": item.get(
                                "importance"
                            ),
                            "weight": item.get(
                                "weight",
                                0,
                            ),
                            "minimum_level": item.get(
                                "minimum_level"
                            ),
                        }
                    )

                # -------------------------------------------------
                # Normalize priority skills
                # -------------------------------------------------
                priority_skills = []

                for item in priority_missing:
                    skill_id = item.get(
                        "skill_id"
                    )

                    if not skill_id:
                        continue

                    priority_skills.append(
                        {
                            "skill_id": skill_id,
                            "name": item.get(
                                "name",
                                "",
                            ),
                            "slug": item.get(
                                "slug",
                                "",
                            ),
                            "importance": item.get(
                                "importance"
                            ),
                            "weight": item.get(
                                "weight",
                                0,
                            ),
                            "minimum_level": item.get(
                                "minimum_level"
                            ),
                        }
                    )

                # -------------------------------------------------
                # Deduplicate skill collections
                # -------------------------------------------------
                def unique_skill_items(
                    items,
                ):
                    result = []
                    seen = set()

                    for item in items:
                        skill_id = item.get(
                            "skill_id"
                        )

                        if not skill_id:
                            continue

                        if skill_id in seen:
                            continue

                        seen.add(
                            skill_id
                        )

                        result.append(
                            item
                        )

                    return result

                missing_skills = (
                    unique_skill_items(
                        missing_skills
                    )
                )

                improvement_skills = (
                    unique_skill_items(
                        improvement_skills
                    )
                )

                priority_skills = (
                    unique_skill_items(
                        priority_skills
                    )
                )

                # -------------------------------------------------
                # Build personalized roadmap
                # -------------------------------------------------
                roadmap_skill_gap = {
                    "missing_skills": missing_skills,
                    "improvement_skills": (
                        improvement_skills
                    ),
                    "priority_skills": (
                        priority_skills
                    ),
                }

                roadmap = (
                    build_personalized_roadmap(
                        role=role,
                        skill_gap=roadmap_skill_gap,
                    )
                )

        # ---------------------------------------------------------
        # Build public-facing candidate profile
        #
        # Keep the complete normalized intelligence profile available
        # to the frontend, while also preserving useful CV metadata.
        # ---------------------------------------------------------
        candidate_profile_response = {
            **candidate_profile,
            "cv_id": cv.id,
            "cv_title": cv.title,
            "ats_score": ats_score,
            "ats_status": ats_result.get(
                "status",
                "Unknown",
            ),
        }

        # ---------------------------------------------------------
        # Final response
        # ---------------------------------------------------------
        return Response(
            {
                "analysis": {
                    "job_match": job_match,
                    "application_readiness": (
                        application_readiness
                    ),
                    "candidate_profile": (
                        candidate_profile_response
                    ),
                    "job_skills": job_skills,
                    "detected_roles": detected_roles,
                    "roadmap": roadmap,
                }
            }
        )