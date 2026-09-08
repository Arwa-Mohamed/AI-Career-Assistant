from __future__ import annotations

from typing import Any

from .job_description_parser import (
    extract_job_sections,
    infer_skill_importance,
)
from .skill_normalization import (
    build_skill_index,
    normalize_text,
)


IMPORTANCE_WEIGHT = {
    "required": 1.5,
    "important": 1.0,
    "preferred": 0.5,
}


def detect_job_skills(
    job_description: str,
) -> list[dict]:
    """
    Detect canonical taxonomy skills from a job description.
    """

    normalized_job = normalize_text(
        job_description
    )

    if not normalized_job:
        return []

    detected = {}

    for taxonomy_skill in build_skill_index():
        matched_aliases = []

        for alias in taxonomy_skill[
            "aliases"
        ]:
            if not alias:
                continue

            if alias in normalized_job:
                matched_aliases.append(
                    alias
                )

        if not matched_aliases:
            continue

        best_alias = max(
            matched_aliases,
            key=len,
        )

        importance = (
            infer_skill_importance(
                job_description,
                best_alias,
            )
        )

        detected[
            taxonomy_skill["id"]
        ] = {
            "skill_id": taxonomy_skill["id"],
            "name": taxonomy_skill["name"],
            "slug": taxonomy_skill["slug"],
            "skill_type": taxonomy_skill[
                "skill_type"
            ],
            "importance": importance,
            "matched_aliases": (
                matched_aliases
            ),
        }

    return sorted(
        detected.values(),
        key=lambda item: (
            -IMPORTANCE_WEIGHT.get(
                item["importance"],
                1.0,
            ),
            item["name"].lower(),
        ),
    )


def calculate_skill_match(
    job_skills: list[dict],
    candidate_profile: dict,
) -> dict:
    """
    Compare canonical job requirements with candidate skills.
    """

    candidate_skills = {
        item["skill_id"]: item
        for item in candidate_profile.get(
            "skills",
            [],
        )
        if item.get("skill_id")
    }

    total_weight = 0.0
    matched_weight = 0.0

    matched = []
    missing = []
    partial = []

    for job_skill in job_skills:
        importance = job_skill[
            "importance"
        ]

        weight = IMPORTANCE_WEIGHT.get(
            importance,
            1.0,
        )

        total_weight += weight

        candidate_skill = candidate_skills.get(
            job_skill["skill_id"]
        )

        if not candidate_skill:
            missing.append(
                {
                    **job_skill,
                    "candidate_confidence": 0,
                    "status": "missing",
                }
            )

            continue

        confidence = float(
            candidate_skill.get(
                "confidence",
                0.5,
            )
        )

        confidence = min(
            max(
                confidence,
                0,
            ),
            1,
        )

        achieved = (
            weight
            * confidence
        )

        matched_weight += achieved

        if confidence >= 0.80:
            status = "matched"

            matched.append(
                {
                    **job_skill,
                    "candidate_confidence": confidence,
                    "status": status,
                }
            )

        else:
            status = "partial"

            partial.append(
                {
                    **job_skill,
                    "candidate_confidence": confidence,
                    "status": status,
                }
            )

    score = (
        matched_weight
        / total_weight
        * 100
        if total_weight
        else 0
    )

    required_skills = [
        item
        for item in job_skills
        if item["importance"] == "required"
    ]

    required_matched = [
        item
        for item in matched
        if item["importance"] == "required"
    ]

    required_partial = [
        item
        for item in partial
        if item["importance"] == "required"
    ]

    required_coverage = (
        (
            len(required_matched)
            + (
                len(required_partial)
                * 0.5
            )
        )
        / len(required_skills)
        * 100
        if required_skills
        else 100
    )

    return {
        "score": round(
            min(
                max(
                    score,
                    0,
                ),
                100,
            ),
            2,
        ),
        "required_skill_coverage": round(
            min(
                max(
                    required_coverage,
                    0,
                ),
                100,
            ),
            2,
        ),
        "matched": matched,
        "partial": partial,
        "missing": missing,
    }


def calculate_title_match(
    job_title: str,
    target_role: str,
    cv_text: str,
) -> float:
    """
    Calculate a modest title/alignment signal.
    """

    title = normalize_text(
        job_title
    )

    target = normalize_text(
        target_role
    )

    cv_text_normalized = normalize_text(
        cv_text
    )

    if not title:
        return 0

    if target and (
        title in target
        or target in title
    ):
        return 100

    if title in cv_text_normalized:
        return 80

    title_tokens = {
        token
        for token in title.split()
        if len(token) >= 3
    }

    if not title_tokens:
        return 0

    matching_tokens = [
        token
        for token in title_tokens
        if token in cv_text_normalized
    ]

    return (
        len(matching_tokens)
        / len(title_tokens)
        * 100
    )


def calculate_job_match(
    *,
    job_description: str,
    candidate_profile: dict,
) -> dict:
    """
    Main Job Description Intelligence engine.
    """

    sections = extract_job_sections(
        job_description
    )

    job_title = sections.get(
        "title",
        "",
    )

    job_skills = detect_job_skills(
        job_description
    )

    skill_match = calculate_skill_match(
        job_skills=job_skills,
        candidate_profile=candidate_profile,
    )

    title_match = calculate_title_match(
        job_title=job_title,
        target_role=candidate_profile.get(
            "target_role",
            "",
        ),
        cv_text=candidate_profile.get(
            "raw_text",
            "",
        ),
    )

    # Weighted job-specific score.
    #
    # Skills remain the dominant factor.
    final_score = (
        skill_match["score"]
        * 0.75
        + title_match
        * 0.15
        + skill_match[
            "required_skill_coverage"
        ]
        * 0.10
    )

    final_score = round(
        min(
            max(
                final_score,
                0,
            ),
            100,
        ),
        2,
    )

    if (
        final_score >= 85
        and skill_match[
            "required_skill_coverage"
        ] >= 80
    ):
        verdict = {
            "status": "strong_match",
            "label": "Strong Match",
            "can_apply": True,
            "description": (
                "Your profile is strongly aligned "
                "with this job."
            ),
        }

    elif (
        final_score >= 70
        and skill_match[
            "required_skill_coverage"
        ] >= 60
    ):
        verdict = {
            "status": "good_match",
            "label": "Good Match",
            "can_apply": True,
            "description": (
                "You have a good foundation for this job, "
                "with some gaps to improve."
            ),
        }

    elif (
        final_score >= 50
    ):
        verdict = {
            "status": "partial_match",
            "label": "Partial Match",
            "can_apply": False,
            "description": (
                "You have relevant overlap, but several "
                "important requirements are still missing."
            ),
        }

    else:
        verdict = {
            "status": "low_match",
            "label": "Low Match",
            "can_apply": False,
            "description": (
                "This job currently has substantial gaps "
                "relative to your profile."
            ),
        }

    priority_missing = sorted(
        skill_match["missing"],
        key=lambda item: (
            -IMPORTANCE_WEIGHT.get(
                item["importance"],
                1.0,
            ),
            item["name"].lower(),
        ),
    )

    return {
        "status": "success",

        "job": {
            "title": job_title,
        },

        "job_skills": job_skills,

        "score": final_score,

        "skill_match": skill_match,

        "title_match": round(
            title_match,
            2,
        ),

        "priority_missing_skills": (
            priority_missing[:10]
        ),

        "verdict": verdict,

        "sections": {
            "responsibilities": sections.get(
                "responsibilities",
                [],
            ),
            "requirements": sections.get(
                "requirements",
                [],
            ),
            "preferred": sections.get(
                "preferred",
                [],
            ),
        },
    }