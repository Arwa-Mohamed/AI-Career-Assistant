from rest_framework import serializers

from .models import (
    Category,
    Role,
    RoleSkill,
    RoadmapPhase,
    RoadmapStep,
    Skill,
    Track,
)


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = [
            "id",
            "name",
            "slug",
            "skill_type",
            "category",
            "description",
            "aliases",
        ]


class RoleSkillSerializer(serializers.ModelSerializer):
    skill = SkillSerializer(
        read_only=True,
    )

    class Meta:
        model = RoleSkill
        fields = [
            "id",
            "skill",
            "importance",
            "weight",
            "minimum_level",
            "evidence_types",
            "notes",
        ]


class RoadmapStepSerializer(serializers.ModelSerializer):
    skill = SkillSerializer(
        read_only=True,
    )

    class Meta:
        model = RoadmapStep
        fields = [
            "id",
            "title",
            "description",
            "step_number",
            "skill",
            "resource_type",
            "estimated_hours",
            "completion_criteria",
            "is_required",
        ]


class RoadmapPhaseSerializer(serializers.ModelSerializer):
    steps = RoadmapStepSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = RoadmapPhase
        fields = [
            "id",
            "title",
            "description",
            "phase_number",
            "estimated_weeks",
            "is_required",
            "steps",
        ]


class RoleListSerializer(serializers.ModelSerializer):
    track_name = serializers.CharField(
        source="track.name",
        read_only=True,
    )

    category_name = serializers.CharField(
        source="track.category.name",
        read_only=True,
    )

    class Meta:
        model = Role
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "track_name",
            "category_name",
            "average_experience_years_min",
            "average_experience_years_max",
        ]


class RoleDetailSerializer(serializers.ModelSerializer):
    track_name = serializers.CharField(
        source="track.name",
        read_only=True,
    )

    category_name = serializers.CharField(
        source="track.category.name",
        read_only=True,
    )

    skills = serializers.SerializerMethodField()
    roadmap = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "responsibilities",
            "typical_titles",
            "career_levels",
            "interview_topics",
            "project_types",
            "certifications",
            "average_experience_years_min",
            "average_experience_years_max",
            "track_name",
            "category_name",
            "skills",
            "roadmap",
        ]

    def get_skills(self, obj):
        return RoleSkillSerializer(
            obj.role_skills.select_related(
                "skill"
            ).all(),
            many=True,
        ).data

    def get_roadmap(self, obj):
        phases = (
            obj.roadmap_phases
            .prefetch_related(
                "steps__skill"
            )
            .all()
        )

        return RoadmapPhaseSerializer(
            phases,
            many=True,
        ).data


class TrackListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source="category.name",
        read_only=True,
    )

    roles_count = serializers.IntegerField(
        source="roles.count",
        read_only=True,
    )

    class Meta:
        model = Track
        fields = [
            "id",
            "name",
            "slug",
            "short_description",
            "description",
            "category_name",
            "roles_count",
        ]


class TrackDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source="category.name",
        read_only=True,
    )

    roles = RoleListSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Track
        fields = [
            "id",
            "name",
            "slug",
            "short_description",
            "description",
            "icon",
            "category_name",
            "roles",
        ]


class CategorySerializer(serializers.ModelSerializer):
    tracks = TrackListSerializer(
        many=True,
        read_only=True,
    )

    tracks_count = serializers.IntegerField(
        source="tracks.count",
        read_only=True,
    )

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "icon",
            "tracks_count",
            "tracks",
        ]