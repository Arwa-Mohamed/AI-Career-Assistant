from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cvs.models import CV
from job_matching.serializers import JobAnalysisSerializer

from .models import JobAnalysis
from .services.job_matcher import calculate_job_match
from rest_framework import generics


class JobMatchView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = JobAnalysisSerializer

    def post(self, request, cv_id):
        job_description = request.data.get(
            "job_description"
        )

        if not job_description:
            return Response(
                {
                    "detail": "job_description is required."
                },
                status=400,
            )

        try:
            cv = CV.objects.get(
                id=cv_id,
                user=request.user,
            )
        except CV.DoesNotExist:
            return Response(
                {"detail": "CV not found."},
                status=404,
            )

        if not cv.extracted_text:
            return Response(
                {
                    "detail": (
                        "CV text has not been extracted yet."
                    )
                },
                status=400,
            )

        cv_skills = cv.parsed_data.get(
            "skills",
            [],
        )

        result = calculate_job_match(
            cv.extracted_text,
            cv_skills,
            job_description,
        )

        analysis = JobAnalysis.objects.create(
            user=request.user,
            cv=cv,
            job_description=job_description,
            semantic_similarity=result[
                "semantic_similarity"
            ],
            semantic_score=result[
                "semantic_score"
            ],
            skill_match_score=result[
                "skill_match_score"
            ],
            final_match_score=result[
                "final_match_score"
            ],
            required_skills=result[
                "required_skills"
            ],
            matched_skills=result[
                "matched_skills"
            ],
            missing_skills=result[
                "missing_skills"
            ],
        )

        return Response({
            "id": analysis.id,
            "cv_id": cv.id,
            "job_description": analysis.job_description,
            "semantic_similarity": analysis.semantic_similarity,
            "semantic_score": analysis.semantic_score,
            "required_skills": analysis.required_skills,
            "matched_skills": analysis.matched_skills,
            "missing_skills": analysis.missing_skills,
            "skill_match_score": analysis.skill_match_score,
            "final_match_score": analysis.final_match_score,
            "created_at": analysis.created_at,
        })
        
class JobAnalysisListView(generics.ListAPIView):
    serializer_class = JobAnalysisSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return JobAnalysis.objects.filter(
            user=self.request.user
        ).select_related(
            "cv"
        ).order_by("-created_at")