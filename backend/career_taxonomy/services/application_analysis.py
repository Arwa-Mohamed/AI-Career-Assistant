from __future__ import annotations

from .candidate_intelligence import (
    build_candidate_intelligence,
)
from .career_readiness import (
    calculate_career_readiness,
)
from .job_matching_engine import (
    calculate_job_match,
)


def analyze_application_match(
    *,
    parsed_data,
    extracted_text: str,
    job_description: str,
    cv_score: float | None = None,
) -> dict:
    """
    Full application-specific analysis.

    This compares one candidate against one specific job.
    """

    candidate_profile = (
        build_candidate_intelligence(
            parsed_data=parsed_data,
            extracted_text=extracted_text,
        )
    )

    job_match = calculate_job_match(
        job_description=job_description,
        candidate_profile=candidate_profile,
    )

    application_score = (
        job_match.get(
            "score",
            0,
        )
    )

    readiness = calculate_career_readiness(
        cv_score=cv_score,
        career_fit=application_score,
        skill_coverage=job_match[
            "skill_match"
        ].get(
            "score",
            0,
        ),
        required_skill_coverage=job_match[
            "skill_match"
        ].get(
            "required_skill_coverage",
            0,
        ),
    )

    return {
        "status": "success",

        "candidate_profile": candidate_profile,

        "job_match": job_match,

        "application_readiness": readiness,
    }