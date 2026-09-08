from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from job_matching.models import JobAnalysis

from .models import SkillGapAnalysis
from .services.skill_gap_service import calculate_skill_gap
from .services.roadmap import (
    generate_learning_roadmap,
)

class SkillGapView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, job_analysis_id):
        try:
            job_analysis = JobAnalysis.objects.get(
                id=job_analysis_id,
                user=request.user,
            )
        except JobAnalysis.DoesNotExist:
            return Response(
                {"detail": "Job analysis not found."},
                status=404,
            )

        cv = job_analysis.cv

        current_skills = cv.parsed_data.get(
            "skills",
            [],
        )

        required_skills = (
            job_analysis.required_skills
        )

        result = calculate_skill_gap(
            current_skills,
            required_skills,
        )
        
        roadmap = generate_learning_roadmap(
    result["missing_skills"]
        )

        analysis = SkillGapAnalysis.objects.create(
            user=request.user,
            cv=cv,
            job_analysis=job_analysis,
            current_skills=current_skills,
            required_skills=required_skills,
            matched_skills=result["matched_skills"],
            missing_skills=result["missing_skills"],
            gap_score=result["gap_score"],
        )

        return Response({
            "id": analysis.id,
            "cv_id": cv.id,
            "job_analysis_id": job_analysis.id,
            "current_skills": analysis.current_skills,
            "required_skills": analysis.required_skills,
            "matched_skills": analysis.matched_skills,
            "missing_skills": analysis.missing_skills,
            "gap_score": analysis.gap_score,
            "learning_roadmap": roadmap,
        })