from django.db.models import Count, Q
from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import (
    Category,
    Role,
    Skill,
    Track,
)
from .serializers import (
    CategorySerializer,
    RoleDetailSerializer,
    RoleListSerializer,
    SkillSerializer,
    TrackDetailSerializer,
    TrackListSerializer,
)


class CategoryListView(generics.ListAPIView):
    permission_classes = [
        AllowAny
    ]

    serializer_class = CategorySerializer

    def get_queryset(self):
        return (
            Category.objects
            .filter(is_active=True)
            .prefetch_related(
                "tracks__roles"
            )
            .annotate(
                tracks_count=Count(
                    "tracks",
                    filter=Q(
                        tracks__is_active=True
                    ),
                    distinct=True,
                )
            )
            .order_by(
                "display_order",
                "name",
            )
        )


class TrackListView(generics.ListAPIView):
    permission_classes = [
        AllowAny
    ]

    serializer_class = TrackListSerializer

    def get_queryset(self):
        queryset = (
            Track.objects
            .filter(
                is_active=True,
                category__is_active=True,
            )
            .select_related("category")
            .annotate(
                roles_count=Count(
                    "roles",
                    filter=Q(
                        roles__is_active=True
                    ),
                    distinct=True,
                )
            )
        )

        category = self.request.query_params.get(
            "category"
        )

        search = self.request.query_params.get(
            "search"
        )

        if category:
            queryset = queryset.filter(
                category__slug=category
            )

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(
                    description__icontains=search
                )
                | Q(
                    short_description__icontains=search
                )
            )

        return queryset.order_by(
            "category__display_order",
            "display_order",
            "name",
        )


class TrackDetailView(generics.RetrieveAPIView):
    permission_classes = [
        AllowAny
    ]

    serializer_class = TrackDetailSerializer

    queryset = (
        Track.objects
        .filter(
            is_active=True,
            category__is_active=True,
        )
        .select_related("category")
        .prefetch_related("roles")
    )

    lookup_field = "slug"


class RoleListView(generics.ListAPIView):
    permission_classes = [
        AllowAny
    ]

    serializer_class = RoleListSerializer

    def get_queryset(self):
        queryset = (
            Role.objects
            .filter(
                is_active=True,
                track__is_active=True,
                track__category__is_active=True,
            )
            .select_related(
                "track",
                "track__category",
            )
        )

        track = self.request.query_params.get(
            "track"
        )

        category = self.request.query_params.get(
            "category"
        )

        search = self.request.query_params.get(
            "search"
        )

        if track:
            queryset = queryset.filter(
                track__slug=track
            )

        if category:
            queryset = queryset.filter(
                track__category__slug=category
            )

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(
                    description__icontains=search
                )
                | Q(
                    typical_titles__icontains=search
                )
            )

        return queryset.order_by(
            "track__category__display_order",
            "track__display_order",
            "display_order",
            "name",
        )


class RoleDetailView(generics.RetrieveAPIView):
    permission_classes = [
        AllowAny
    ]

    serializer_class = RoleDetailSerializer

    queryset = (
        Role.objects
        .filter(
            is_active=True,
            track__is_active=True,
            track__category__is_active=True,
        )
        .select_related(
            "track",
            "track__category",
        )
        .prefetch_related(
            "role_skills__skill",
            "roadmap_phases__steps__skill",
        )
    )

    lookup_field = "slug"


class SkillListView(generics.ListAPIView):
    permission_classes = [
        AllowAny
    ]

    serializer_class = SkillSerializer

    def get_queryset(self):
        queryset = Skill.objects.filter(
            is_active=True
        )

        search = self.request.query_params.get(
            "search"
        )

        skill_type = self.request.query_params.get(
            "type"
        )

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(
                    aliases__icontains=search
                )
            )

        if skill_type:
            queryset = queryset.filter(
                skill_type=skill_type
            )

        return queryset.order_by(
            "name"
        )