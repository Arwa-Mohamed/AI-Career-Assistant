from django.contrib import admin

from .models import CareerProject


@admin.register(CareerProject)
class CareerProjectAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "user",
        "target_role",
        "difficulty",
        "status",
        "progress",
        "created_at",
    )

    list_filter = (
        "status",
        "difficulty",
    )

    search_fields = (
        "title",
        "target_role",
        "user__username",
    )