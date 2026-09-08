from .embedding_service import calculate_similarity
from .skill_matcher import (
    compare_skills,
    extract_job_skills,
)


def calculate_job_match(
    cv_text,
    cv_skills,
    job_description,
):
    semantic_similarity = calculate_similarity(
        cv_text,
        job_description,
    )

    semantic_score = max(
        0,
        min(semantic_similarity, 1),
    ) * 100

    job_skills = extract_job_skills(
        job_description
    )

    skill_result = compare_skills(
        cv_skills,
        job_skills,
    )

    final_score = (
        semantic_score * 0.6
        + skill_result["skill_match_score"] * 0.4
    )

    return {
        "semantic_similarity": round(
            semantic_similarity,
            4,
        ),
        "semantic_score": round(
            semantic_score,
            2,
        ),
        "required_skills": job_skills,
        "matched_skills": skill_result[
            "matched_skills"
        ],
        "missing_skills": skill_result[
            "missing_skills"
        ],
        "skill_match_score": skill_result[
            "skill_match_score"
        ],
        "final_match_score": round(
            final_score,
            2,
        ),
    }