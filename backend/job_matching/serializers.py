from rest_framework import serializers

from .models import JobAnalysis


class JobAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobAnalysis
        fields = [
            "id",
            "cv",
            "job_description",
            "semantic_similarity",
            "semantic_score",
            "skill_match_score",
            "final_match_score",
            "required_skills",
            "matched_skills",
            "missing_skills",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "semantic_similarity",
            "semantic_score",
            "skill_match_score",
            "final_match_score",
            "required_skills",
            "matched_skills",
            "missing_skills",
        ]