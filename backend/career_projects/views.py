from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CareerProject
from cvs.models import CV
from job_matching.models import JobAnalysis
from skill_gap.services.skill_gap_service import calculate_skill_gap

from .services import generate_project_recommendations


class CareerProjectListCreateView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        projects = CareerProject.objects.filter(
            user=request.user
        )

        data = [
            self.serialize_project(project)
            for project in projects
        ]

        return Response(data)

    def post(self, request):

        data = request.data

        title = data.get("title")

        if not title:
            return Response(
                {
                    "detail": "Project title is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        project = CareerProject.objects.create(
            user=request.user,

            title=title,

            description=data.get(
                "description",
                "",
            ),

            target_role=data.get(
                "target_role",
                "",
            ),

            skills=data.get(
                "skills",
                [],
            ),

            objectives=data.get(
                "objectives",
                [],
            ),

            difficulty=data.get(
                "difficulty",
                "beginner",
            ),

            estimated_days=data.get(
                "estimated_days",
                7,
            ),
        )

        return Response(
            self.serialize_project(project),
            status=status.HTTP_201_CREATED,
        )

    @staticmethod
    def serialize_project(project):

        return {
            "id": project.id,
            "title": project.title,
            "description": project.description,
            "target_role": project.target_role,
            "skills": project.skills,
            "objectives": project.objectives,
            "difficulty": project.difficulty,
            "estimated_days": project.estimated_days,
            "status": project.status,
            "progress": project.progress,
            "github_url": project.github_url,
            "demo_url": project.demo_url,
            "created_at": project.created_at,
            "completed_at": project.completed_at,
        }


class CareerProjectDetailView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get_object(
        self,
        request,
        project_id,
    ):

        try:
            return CareerProject.objects.get(
                id=project_id,
                user=request.user,
            )

        except CareerProject.DoesNotExist:
            return None

    def patch(
        self,
        request,
        project_id,
    ):

        project = self.get_object(
            request,
            project_id,
        )

        if not project:
            return Response(
                {
                    "detail": "Project not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data

        if "status" in data:

            new_status = data["status"]

            valid_statuses = {
                "not_started",
                "in_progress",
                "completed",
            }

            if new_status not in valid_statuses:
                return Response(
                    {
                        "detail":
                            "Invalid project status."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            project.status = new_status

            if new_status == "not_started":
                project.progress = 0
                project.completed_at = None

            elif new_status == "in_progress":

                if project.progress == 0:
                    project.progress = 25

                project.completed_at = None

            elif new_status == "completed":

                project.progress = 100

                project.completed_at = (
                    timezone.now()
                )

        if "progress" in data:

            try:
                progress = int(
                    data["progress"]
                )
            except (
                TypeError,
                ValueError,
            ):
                return Response(
                    {
                        "detail":
                            "Progress must be a number."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not 0 <= progress <= 100:
                return Response(
                    {
                        "detail":
                            "Progress must be between 0 and 100."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            project.progress = progress

            if progress == 0:
                project.status = (
                    "not_started"
                )
                project.completed_at = None

            elif progress == 100:
                project.status = (
                    "completed"
                )

                project.completed_at = (
                    timezone.now()
                )

            else:
                project.status = (
                    "in_progress"
                )

                project.completed_at = None

        if "github_url" in data:
            project.github_url = (
                data["github_url"]
                or ""
            )

        if "demo_url" in data:
            project.demo_url = (
                data["demo_url"]
                or ""
            )

        project.save()

        return Response(
            CareerProjectListCreateView
            .serialize_project(project)
        )

    def delete(
        self,
        request,
        project_id,
    ):

        project = self.get_object(
            request,
            project_id,
        )

        if not project:
            return Response(
                {
                    "detail":
                        "Project not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        project.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class CareerProjectRecommendationsView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        latest_cv = (
            CV.objects
            .filter(user=request.user)
            .order_by("-uploaded_at")
            .first()
        )

        latest_job = (
            JobAnalysis.objects
            .filter(user=request.user)
            .order_by("-created_at")
            .first()
        )

        if not latest_cv:
            return Response({
                "recommendations": [],
                "message": (
                    "Upload a CV before generating "
                    "project recommendations."
                ),
            })

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

        # ---------------------------------------------------------
        # CASE 1: A job analysis exists.
        # Keep the existing job-specific behavior.
        # ---------------------------------------------------------
        if latest_job:
            required_skills = (
                latest_job.required_skills
                or []
            )

            gap_result = calculate_skill_gap(
                current_skills,
                required_skills,
            )

            target_role = (
                getattr(
                    latest_job,
                    "target_role",
                    "",
                )
                or parsed_data.get(
                    "target_role",
                    "",
                )
                or parsed_data.get(
                    "career_goal",
                    "",
                )
                or "Career Development"
            )

            recommendations = (
                generate_project_recommendations(
                    gap_result["missing_skills"],
                    target_role,
                )
            )

            return Response({
                "target_role": target_role,
                "source": "job_analysis",
                "recommendation_mode": "job_specific",
                "missing_skills":
                    gap_result["missing_skills"],
                "recommendations":
                    recommendations,
                "message": (
                    "These projects are tailored to your CV, target role, "
                    "and the skill gaps found in the job you analyzed."
                ),
            })

        # ---------------------------------------------------------
        # CASE 2: No job analysis exists.
        # Generate career-oriented project ideas from the CV.
        # The job is optional now.
        # ---------------------------------------------------------
        target_role = (
            parsed_data.get(
                "target_role",
                "",
            )
            or parsed_data.get(
                "career_goal",
                "",
            )
            or parsed_data.get(
                "role",
                "",
            )
            or "Career Development"
        )

        recommendations = (
            generate_project_recommendations(
                [],
                target_role,
            )
        )

        return Response({
            "target_role": target_role,
            "source": "cv_profile",
            "recommendation_mode": "career_based",
            "missing_skills": [],
            "recommendations": recommendations,
            "message": (
                "These projects are based on your CV and career goals. "
                "Analyze a job to unlock more personalized, job-specific "
                "project recommendations."
            ),
        })
