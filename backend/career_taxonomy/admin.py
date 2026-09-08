from django.contrib import admin

from .models import (
    Category,
    Role,
    RoleSkill,
    RoadmapPhase,
    RoadmapStep,
    Skill,
    Track,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "slug",
        "display_order",
        "is_active",
    ]

    list_filter = [
        "is_active",
    ]

    search_fields = [
        "name",
        "description",
    ]

    prepopulated_fields = {
        "slug": ("name",),
    }

    ordering = [
        "display_order",
        "name",
    ]


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "category",
        "display_order",
        "is_active",
    ]

    list_filter = [
        "category",
        "is_active",
    ]

    search_fields = [
        "name",
        "description",
        "short_description",
    ]

    prepopulated_fields = {
        "slug": ("name",),
    }

    ordering = [
        "category",
        "display_order",
        "name",
    ]


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "skill_type",
        "category",
        "is_active",
    ]

    list_filter = [
        "skill_type",
        "is_active",
    ]

    search_fields = [
        "name",
        "aliases",
        "description",
    ]

    prepopulated_fields = {
        "slug": ("name",),
    }


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "track",
        "average_experience_years_min",
        "average_experience_years_max",
        "is_active",
    ]

    list_filter = [
        "track",
        "track__category",
        "is_active",
    ]

    search_fields = [
        "name",
        "description",
        "typical_titles",
    ]

    prepopulated_fields = {
        "slug": ("name",),
    }

    ordering = [
        "track",
        "display_order",
        "name",
    ]


@admin.register(RoleSkill)
class RoleSkillAdmin(admin.ModelAdmin):
    list_display = [
        "role",
        "skill",
        "importance",
        "weight",
        "minimum_level",
    ]

    list_filter = [
        "importance",
        "skill__skill_type",
        "role__track",
    ]

    search_fields = [
        "role__name",
        "skill__name",
        "notes",
    ]

    ordering = [
        "-weight",
    ]


@admin.register(RoadmapPhase)
class RoadmapPhaseAdmin(admin.ModelAdmin):
    list_display = [
        "role",
        "phase_number",
        "title",
        "estimated_weeks",
        "is_required",
    ]

    list_filter = [
        "is_required",
        "role__track",
    ]

    search_fields = [
        "role__name",
        "title",
        "description",
    ]

    ordering = [
        "role",
        "phase_number",
    ]


@admin.register(RoadmapStep)
class RoadmapStepAdmin(admin.ModelAdmin):
    list_display = [
        "phase",
        "step_number",
        "title",
        "skill",
        "estimated_hours",
        "is_required",
    ]

    list_filter = [
        "is_required",
        "resource_type",
    ]

    search_fields = [
        "phase__role__name",
        "phase__title",
        "title",
        "description",
        "skill__name",
    ]

    ordering = [
        "phase",
        "step_number",
    ]