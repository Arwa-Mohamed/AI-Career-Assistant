from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cvs.models import CV
from job_matching.models import JobAnalysis
from profiles.models import Profile

from skill_gap.services.skill_gap_service import (
    calculate_skill_gap,
)
from skill_gap.services.roadmap import (
    generate_learning_roadmap,
)


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # =========================================
        # Profile
        # =========================================

        profile = (
            Profile.objects
            .filter(user=user)
            .first()
        )

        profile_data = {
            "full_name": (
                profile.full_name
                if profile
                else ""
            ),
            "phone": (
                profile.phone
                if profile
                else ""
            ),
            "location": (
                profile.location
                if profile
                else ""
            ),
            "bio": (
                profile.bio
                if profile
                else ""
            ),
            "career_goal": (
                profile.career_goal
                if profile
                else ""
            ),
            "linkedin_url": (
                profile.linkedin_url
                if profile
                else ""
            ),
        }

        # =========================================
        # Latest CV
        # =========================================

        latest_cv = (
            CV.objects
            .filter(user=user)
            .order_by("-uploaded_at")
            .first()
        )

        cv_data = None
        cv_score = 0

        if latest_cv:
            cv_data = {
                "id": latest_cv.id,
                "title": latest_cv.title,
                "uploaded_at": (
                    latest_cv.uploaded_at
                ),
                "parsed_data": (
                    latest_cv.parsed_data
                    or {}
                ),
                "extracted_text_length": len(
                    latest_cv.extracted_text
                    or ""
                ),
            }

            # CV Analysis
            if hasattr(latest_cv, "analysis"):
                cv_score = (
                    latest_cv.analysis.score
                )

        # =========================================
        # Job Analyses
        # =========================================

        job_analyses = list(
            JobAnalysis.objects
            .filter(user=user)
            .order_by("-created_at")[:5]
        )

        latest_job = (
            job_analyses[0]
            if job_analyses
            else None
        )

        # =========================================
        # Skill Gap
        # =========================================

        skill_gap_data = None

        if latest_job and latest_cv:
            parsed_data = (
                latest_cv.parsed_data
                or {}
            )

            current_skills = (
                parsed_data.get(
                    "skills",
                    []
                )
            )

            result = calculate_skill_gap(
                current_skills,
                latest_job.required_skills,
            )

            skill_gap_data = {
                "gap_score": result[
                    "gap_score"
                ],
                "current_skills": current_skills,
                "required_skills": (
                    latest_job.required_skills
                ),
                "matched_skills": result[
                    "matched_skills"
                ],
                "missing_skills": result[
                    "missing_skills"
                ],
                "learning_roadmap": (
                    generate_learning_roadmap(
                        result[
                            "missing_skills"
                        ]
                    )
                ),
            }

        # =========================================
        # Job History
        # =========================================

        job_history = [
            {
                "id": job.id,
                "cv_id": job.cv_id,
                "score": (
                    job.final_match_score
                ),
                "created_at": (
                    job.created_at
                ),
            }
            for job in job_analyses
        ]

        # =========================================
        # Final Response
        # =========================================

        return Response({
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },

            "profile": profile_data,

            "cv": cv_data,

            "cv_score": cv_score,

            "latest_job_match": (
                latest_job.final_match_score
                if latest_job
                else 0
            ),

            "skill_gap": skill_gap_data,

            "job_history": job_history,
        })