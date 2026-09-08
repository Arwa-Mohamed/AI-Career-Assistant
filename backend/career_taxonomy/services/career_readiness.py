from __future__ import annotations


# ============================================================
# Default Weights
# ============================================================

DEFAULT_WEIGHTS = {
    "cv_score": 0.25,
    "career_fit": 0.25,
    "skill_coverage": 0.20,
    "projects": 0.15,
    "interview_readiness": 0.10,
    "profile_completeness": 0.05,
}


# ============================================================
# Utilities
# ============================================================

def clamp(
    value: float,
    minimum: float = 0.0,
    maximum: float = 100.0,
) -> float:
    return max(
        minimum,
        min(
            float(value or 0),
            maximum,
        ),
    )


# ============================================================
# Labels
# ============================================================

def get_readiness_label(
    score: float,
) -> str:

    score = clamp(score)

    if score >= 85:
        return "Highly Ready"

    if score >= 70:
        return "Ready with Minor Gaps"

    if score >= 55:
        return "Almost Ready"

    if score >= 40:
        return "Needs Preparation"

    return "Early Stage"


def get_readiness_description(
    score: float,
) -> str:

    score = clamp(score)

    if score >= 85:
        return (
            "The candidate is highly prepared for this career path "
            "and can confidently target relevant opportunities."
        )

    if score >= 70:
        return (
            "The candidate is generally ready, with a few gaps "
            "that should be improved while applying."
        )

    if score >= 55:
        return (
            "The candidate has a reasonable foundation but should "
            "strengthen several important areas before relying heavily "
            "on applications."
        )

    if score >= 40:
        return (
            "The candidate needs focused preparation to become "
            "competitive for this career path."
        )

    return (
        "The candidate is still at an early stage and should build "
        "core skills, evidence, and practical experience."
    )


# ============================================================
# Application Verdict
# ============================================================

def get_application_verdict(
    score: float,
    required_skill_coverage: float = 0.0,
) -> str:

    score = clamp(score)

    required_skill_coverage = clamp(
        required_skill_coverage
    )

    if (
        score >= 80
        and required_skill_coverage >= 80
    ):
        return "Apply Now"

    if (
        score >= 65
        and required_skill_coverage >= 60
    ):
        return "Apply While Improving"

    return "Prepare Before Applying"


# ============================================================
# Career Readiness
# ============================================================

def calculate_career_readiness(
    *,
    cv_score: float | None = None,
    career_fit: float | None = None,
    skill_coverage: float | None = None,
    projects: float | None = None,
    interview_readiness: float | None = None,
    profile_completeness: float | None = None,
    required_skill_coverage: float | None = None,
    weights: dict | None = None,
) -> dict:
    """
    Calculate overall career readiness.

    Missing components are excluded and remaining weights
    are normalized automatically.
    """

    weights = (
        weights
        or DEFAULT_WEIGHTS.copy()
    )

    values = {
        "cv_score": cv_score,
        "career_fit": career_fit,
        "skill_coverage": skill_coverage,
        "projects": projects,
        "interview_readiness": interview_readiness,
        "profile_completeness": profile_completeness,
    }

    normalized_values = {}

    active_weight_total = 0.0

    for key, value in values.items():

        if value is None:
            continue

        normalized_values[key] = clamp(
            value
        )

        active_weight_total += float(
            weights.get(
                key,
                0,
            )
        )

    # No measurable signals.
    if active_weight_total <= 0:
        score = 0.0

    else:

        weighted_sum = 0.0

        for key, value in normalized_values.items():

            weighted_sum += (
                value
                * float(
                    weights.get(
                        key,
                        0,
                    )
                )
            )

        score = (
            weighted_sum
            / active_weight_total
        )

    score = round(
        clamp(score),
        2,
    )

    if required_skill_coverage is None:

        # If no explicit required coverage is available,
        # use the general skill coverage.
        required_skill_coverage = (
            skill_coverage
            if skill_coverage is not None
            else 0
        )

    required_skill_coverage = round(
        clamp(
            required_skill_coverage
        ),
        2,
    )

    label = get_readiness_label(
        score
    )

    return {
        "score": score,

        "label": label,

        "description": get_readiness_description(
            score
        ),

        "application_verdict": get_application_verdict(
            score,
            required_skill_coverage,
        ),

        "required_skill_coverage": (
            required_skill_coverage
        ),

        "components": {
            key: round(
                value,
                2,
            )
            for key, value in normalized_values.items()
        },

        "weights": {
            key: value
            for key, value in weights.items()
            if key in normalized_values
        },

        "status": "success",
    }