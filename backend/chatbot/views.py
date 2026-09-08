from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cvs.models import CV
from profiles.models import Profile
from job_matching.models import JobAnalysis
from skill_gap.services.skill_gap_service import (
    calculate_skill_gap,
)
from skill_gap.services.roadmap import (
    generate_learning_roadmap,
)

from .models import ChatMessage, ChatSession
from .services.ai_service import generate_career_response


class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        message = str(
            request.data.get(
                "message",
                "",
            )
        ).strip()

        session_id = request.data.get(
            "session_id"
        )

        if not message:
            return Response(
                {
                    "detail": "message is required."
                },
                status=400,
            )

        # =====================================================
        # GET OR CREATE CHAT SESSION
        # =====================================================

        if session_id:
            try:
                session = ChatSession.objects.get(
                    id=session_id,
                    user=request.user,
                )
            except ChatSession.DoesNotExist:
                return Response(
                    {
                        "detail": (
                            "Chat session not found."
                        )
                    },
                    status=404,
                )
        else:
            session = ChatSession.objects.create(
                user=request.user,
                title=message[:50],
            )

        # =====================================================
        # PREVIOUS MESSAGES
        # =====================================================

        previous_messages = (
            ChatMessage.objects
            .filter(session=session)
            .order_by("-created_at")[:10]
        )

        previous_messages = list(
            reversed(
                list(previous_messages)
            )
        )

        chat_history = [
            {
                "role": msg.role,
                "content": msg.content,
            }
            for msg in previous_messages
        ]

        # =====================================================
        # USER PROFILE
        # =====================================================

        profile = (
            Profile.objects
            .filter(user=request.user)
            .first()
        )

        profile_data = {
            "username": (
                request.user.username
                or ""
            ),
            "email": (
                getattr(
                    request.user,
                    "email",
                    "",
                )
                or ""
            ),
            "full_name": (
                (
                    profile.full_name
                    if profile
                    else ""
                )
                or getattr(
                    request.user,
                    "get_full_name",
                    lambda: "",
                )()
                or request.user.username
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

        # =====================================================
        # LATEST CV
        # =====================================================

        latest_cv = (
            CV.objects
            .filter(user=request.user)
            .order_by("-uploaded_at")
            .first()
        )

        cv_data = {}

        if latest_cv:
            cv_data = {
                "id": latest_cv.id,
                "title": latest_cv.title,
                "parsed_data": (
                    latest_cv.parsed_data
                    if isinstance(
                        latest_cv.parsed_data,
                        dict,
                    )
                    else {}
                ),
            }

        # =====================================================
        # LATEST JOB ANALYSIS
        # =====================================================

        latest_job = (
            JobAnalysis.objects
            .filter(user=request.user)
            .order_by("-created_at")
            .first()
        )

        job_data = {}

        if latest_job:
            job_data = {
                "id": latest_job.id,
                "job_description": (
                    latest_job.job_description
                ),
                "final_match_score": (
                    latest_job.final_match_score
                ),
                "required_skills": (
                    latest_job.required_skills
                ),
                "matched_skills": (
                    latest_job.matched_skills
                ),
                "missing_skills": (
                    latest_job.missing_skills
                ),
            }

        # =====================================================
        # SKILL GAP
        # =====================================================

        skill_gap_data = {}

        if latest_cv and latest_job:
            parsed_data = (
                latest_cv.parsed_data
                if isinstance(
                    latest_cv.parsed_data,
                    dict,
                )
                else {}
            )

            current_skills = (
                parsed_data.get(
                    "skills",
                    [],
                )
            )

            if not isinstance(
                current_skills,
                list,
            ):
                current_skills = []

            required_skills = (
                latest_job.required_skills
                or []
            )

            if not isinstance(
                required_skills,
                list,
            ):
                required_skills = []

            gap = calculate_skill_gap(
                current_skills,
                required_skills,
            )

            skill_gap_data = {
                **gap,
                "learning_roadmap": (
                    generate_learning_roadmap(
                        gap.get(
                            "missing_skills",
                            [],
                        )
                    )
                ),
            }

        # =====================================================
        # SAVE USER MESSAGE
        # =====================================================

        ChatMessage.objects.create(
            session=session,
            role="user",
            content=message,
        )

        # =====================================================
        # GENERATE AI RESPONSE
        # =====================================================

        try:
            answer = generate_career_response(
                user_message=message,
                profile_data=profile_data,
                cv_data=cv_data,
                job_data=job_data,
                skill_gap_data=skill_gap_data,
                chat_history=chat_history,
            )

        except Exception:
            # Defensive fallback at the API boundary.
            answer = (
                "I’m temporarily unable to connect "
                "to the AI service. Please try again "
                "in a moment. You can also continue using "
                "your CV, job matching, projects, and "
                "interview tools while the AI service is unavailable."
            )

        if not answer:
            answer = (
                "I’m sorry, I couldn’t generate an answer "
                "right now. Please try again."
            )

        # =====================================================
        # SAVE ASSISTANT MESSAGE
        # =====================================================

        ChatMessage.objects.create(
            session=session,
            role="assistant",
            content=answer,
        )

        # =====================================================
        # RESPONSE
        # =====================================================

        return Response(
            {
                "session_id": session.id,
                "message": answer,
            },
            status=200,
        )