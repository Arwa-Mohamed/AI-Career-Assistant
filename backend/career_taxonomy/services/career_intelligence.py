from __future__ import annotations

from django.db.models import Prefetch

from career_taxonomy.models import Role, RoleSkill

from .candidate_intelligence import (
    build_candidate_intelligence,
)
from .career_detection import (
    detect_career_roles,
)
from .career_readiness import (
    calculate_career_readiness,
)
from .personalized_roadmap import (
    build_personalized_roadmap,
)
from .skill_gap_engine import (
    calculate_skill_gap,
)


# ============================================================
# Role Loading
# ============================================================

def get_intelligence_roles():
    """
    Load all active roles required by Career Intelligence.

    Everything needed by the intelligence pipeline is
    prefetched here to avoid N+1 database queries.
    """

    role_skills = (
        RoleSkill.objects
        .select_related("skill")
        .filter(
            role__is_active=True,
            skill__is_active=True,
        )
        .order_by(
            "-weight",
            "skill__name",
        )
    )

    return list(
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
            Prefetch(
                "role_skills",
                queryset=role_skills,
            ),
            "roadmap_phases__steps__skill",
        )
    )


# ============================================================
# Role Lookup
# ============================================================

def _build_role_map(roles):
    """
    Build role_id -> Role map.
    """

    return {
        role.id: role
        for role in roles
    }


# ============================================================
# Career Intelligence
# ============================================================

def analyze_candidate_career(
    *,
    parsed_data,
    extracted_text: str = "",
    cv_score: float | None = None,
    top_n: int = 5,
) -> dict:
    """
    Complete Career Intelligence pipeline.

    Pipeline:

        Raw CV
          ↓
        Canonical Candidate Profile
          ↓
        Taxonomy Skill Normalization
          ↓
        Career Detection
          ↓
        Best Role
          ↓
        Skill Gap
          ↓
        Personalized Roadmap
          ↓
        Career Readiness
    """

    # --------------------------------------------------------
    # 1. Candidate Intelligence
    # --------------------------------------------------------

    candidate_profile = build_candidate_intelligence(
        parsed_data=parsed_data,
        extracted_text=extracted_text,
    )

    # --------------------------------------------------------
    # 2. Load taxonomy intelligence
    # --------------------------------------------------------

    roles = get_intelligence_roles()

    if not roles:
        return {
            "status": "no_roles",
            "candidate_profile": candidate_profile,
            "career_detection": {
                "status": "no_roles",
                "best_role": None,
                "top_roles": [],
                "count": 0,
            },
            "skill_gap": None,
            "roadmap": None,
            "career_readiness": None,
        }

    # --------------------------------------------------------
    # 3. Career Detection
    # --------------------------------------------------------

    detection = detect_career_roles(
        roles=roles,
        candidate_profile=candidate_profile,
        top_n=top_n,
    )

    best_role = detection.get(
        "best_role"
    )

    # --------------------------------------------------------
    # 4. No confident role
    # --------------------------------------------------------

    if not best_role:
        return {
            "status": "insufficient_evidence",

            "candidate_profile": candidate_profile,

            "career_detection": detection,

            "skill_gap": None,

            "roadmap": None,

            "career_readiness": calculate_career_readiness(
                cv_score=cv_score,
                career_fit=0,
                skill_coverage=0,
                projects=0,
                interview_readiness=0,
                profile_completeness=_calculate_profile_completeness(
                    candidate_profile
                ),
            ),
        }

    # --------------------------------------------------------
    # 5. Resolve ORM Role
    # --------------------------------------------------------

    role_map = _build_role_map(
        roles
    )

    role_id = best_role.get(
        "role_id"
    )

    role = role_map.get(
        role_id
    )

    if role is None:
        return {
            "status": "role_resolution_failed",
            "candidate_profile": candidate_profile,
            "career_detection": detection,
            "skill_gap": None,
            "roadmap": None,
            "career_readiness": None,
        }

    # --------------------------------------------------------
    # 6. Skill Gap
    # --------------------------------------------------------

    skill_gap = calculate_skill_gap(
        role,
        candidate_profile,
    )

    # --------------------------------------------------------
    # 7. Personalized Roadmap
    # --------------------------------------------------------

    roadmap = build_personalized_roadmap(
        role,
        skill_gap,
    )

    # --------------------------------------------------------
    # 8. Career Readiness
    # --------------------------------------------------------

    skill_coverage = float(
        skill_gap.get(
            "score",
            0,
        )
        or 0
    )

    required_coverage = float(
        skill_gap.get(
            "required_skill_coverage",
            0,
        )
        or 0
    )

    career_fit = float(
        best_role.get(
            "score",
            0,
        )
        or 0
    )

    projects_score = _calculate_project_score(
        candidate_profile
    )

    profile_completeness = (
        _calculate_profile_completeness(
            candidate_profile
        )
    )

    career_readiness = calculate_career_readiness(
        cv_score=cv_score,
        career_fit=career_fit,
        skill_coverage=skill_coverage,
        projects=projects_score,
        interview_readiness=None,
        profile_completeness=profile_completeness,
        required_skill_coverage=required_coverage,
    )

    # --------------------------------------------------------
    # 9. Unified result
    # --------------------------------------------------------

    return {
        "status": "success",

        "candidate_profile": candidate_profile,

        "career_detection": detection,

        "primary_role": best_role,

        "skill_gap": skill_gap,

        "roadmap": roadmap,

        "career_readiness": career_readiness,
    }


# ============================================================
# Profile Completeness
# ============================================================

def _calculate_profile_completeness(
    candidate_profile: dict,
) -> float:
    """
    Estimate profile completeness from canonical profile.
    """

    if not candidate_profile:
        return 0.0

    checks = {
        "summary": bool(
            candidate_profile.get(
                "summary"
            )
        ),

        "target_role": bool(
            candidate_profile.get(
                "target_role"
            )
        ),

        "skills": bool(
            candidate_profile.get(
                "skills"
            )
        ),

        "experience": bool(
            candidate_profile.get(
                "experience"
            )
        ),

        "education": bool(
            candidate_profile.get(
                "education"
            )
        ),

        "projects": bool(
            candidate_profile.get(
                "projects"
            )
        ),

        "certifications": bool(
            candidate_profile.get(
                "certifications"
            )
        ),

        "languages": bool(
            candidate_profile.get(
                "languages"
            )
        ),
    }

    completed = sum(
        1
        for value in checks.values()
        if value
    )

    return round(
        (
            completed
            / len(checks)
        )
        * 100,
        2,
    )


# ============================================================
# Project Score
# ============================================================

def _calculate_project_score(
    candidate_profile: dict,
) -> float:
    """
    Estimate practical project evidence.

    This is intentionally conservative.
    """

    projects = candidate_profile.get(
        "projects"
    ) or []

    if not projects:
        return 0.0

    if isinstance(projects, (list, tuple)):
        project_count = len(projects)
    else:
        project_count = 1

    if project_count >= 5:
        return 100.0

    if project_count == 4:
        return 90.0

    if project_count == 3:
        return 80.0

    if project_count == 2:
        return 65.0

    return 40.0