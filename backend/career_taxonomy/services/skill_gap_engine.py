from __future__ import annotations

from decimal import Decimal
from typing import Any


IMPORTANCE_MULTIPLIERS = {
    "required": 1.5,
    "important": 1.0,
    "optional": 0.5,
}


def clamp(
    value: float,
    minimum: float = 0.0,
    maximum: float = 100.0,
) -> float:
    return round(
        min(
            max(
                value,
                minimum,
            ),
            maximum,
        ),
        2,
    )


def estimate_skill_level(
    confidence: float,
) -> int:
    """
    Temporary evidence-based skill level.

    V1:
        confidence -> level

    V2:
        CV evidence + projects + experience + assessments.
    """

    confidence = min(
        max(
            float(confidence or 0),
            0,
        ),
        1,
    )

    if confidence >= 0.90:
        return 5

    if confidence >= 0.80:
        return 4

    if confidence >= 0.65:
        return 3

    if confidence >= 0.50:
        return 2

    return 1


def calculate_skill_gap(
    role: Any,
    candidate_profile: dict,
) -> dict:
    """
    Universal skill-gap engine for any Role in the taxonomy.
    """

    candidate_skills = {
        item["skill_id"]: item
        for item in candidate_profile.get(
            "skills",
            [],
        )
        if item.get("skill_id")
    }

    role_skills = list(
        role.role_skills.all()
    )

    if not role_skills:
        return {
            "status": "no_taxonomy_data",
            "role": {
                "id": role.id,
                "name": role.name,
            },
            "score": 0,
            "required_skill_coverage": 0,
            "strong_skills": [],
            "improvement_skills": [],
            "missing_skills": [],
            "priority_skills": [],
            "summary": {
                "total": 0,
                "required": 0,
                "important": 0,
                "optional": 0,
                "matched": 0,
                "needs_improvement": 0,
                "missing": 0,
            },
        }

    total_weight = 0.0
    achieved_weight = 0.0

    strong_skills = []
    improvement_skills = []
    missing_skills = []

    for role_skill in role_skills:
        skill = role_skill.skill

        weight = float(
            role_skill.weight or Decimal("1")
        )

        weight = max(
            weight,
            1.0,
        )

        importance = (
            role_skill.importance
        )

        multiplier = IMPORTANCE_MULTIPLIERS.get(
            importance,
            1.0,
        )

        effective_weight = (
            weight
            * multiplier
        )

        total_weight += effective_weight

        required_level = min(
            max(
                int(
                    role_skill.minimum_level
                    or 1
                ),
                1,
            ),
            5,
        )

        candidate_skill = candidate_skills.get(
            skill.id
        )

        if not candidate_skill:
            missing_skills.append(
                {
                    "skill_id": skill.id,
                    "skill": skill.name,
                    "slug": skill.slug,
                    "importance": importance,
                    "required_level": required_level,
                    "estimated_level": 0,
                    "confidence": 0,
                    "level_gap": required_level,
                    "status": "missing",
                }
            )

            continue

        confidence = min(
            max(
                float(
                    candidate_skill.get(
                        "confidence",
                        0.5,
                    )
                ),
                0,
            ),
            1,
        )

        estimated_level = estimate_skill_level(
            confidence
        )

        base_payload = {
            "skill_id": skill.id,
            "skill": skill.name,
            "slug": skill.slug,
            "importance": importance,
            "required_level": required_level,
            "estimated_level": estimated_level,
            "confidence": confidence,
            "level_gap": max(
                required_level
                - estimated_level,
                0,
            ),
        }

        if estimated_level >= required_level:
            achieved_weight += effective_weight

            strong_skills.append(
                {
                    **base_payload,
                    "status": "strong",
                }
            )

        else:
            partial_ratio = (
                estimated_level
                / required_level
            )

            achieved_weight += (
                effective_weight
                * partial_ratio
            )

            improvement_skills.append(
                {
                    **base_payload,
                    "status": "improve",
                }
            )

    score = (
        achieved_weight
        / total_weight
        * 100
        if total_weight
        else 0
    )

    score = clamp(score)

    required_items = [
        item
        for item in role_skills
        if item.importance == "required"
    ]

    required_matched = [
        item
        for item in strong_skills
        if item["importance"] == "required"
    ]

    required_coverage = (
        len(required_matched)
        / len(required_items)
        * 100
        if required_items
        else 100
    )

    priority_candidates = []

    for item in missing_skills:
        importance_priority = {
            "required": 100,
            "important": 70,
            "optional": 40,
        }.get(
            item["importance"],
            30,
        )

        priority_candidates.append(
            {
                **item,
                "priority_score": (
                    importance_priority
                    + (
                        item["level_gap"]
                        * 10
                    )
                ),
            }
        )

    for item in improvement_skills:
        importance_priority = {
            "required": 80,
            "important": 55,
            "optional": 30,
        }.get(
            item["importance"],
            20,
        )

        priority_candidates.append(
            {
                **item,
                "priority_score": (
                    importance_priority
                    + (
                        item["level_gap"]
                        * 8
                    )
                ),
            }
        )

    priority_candidates.sort(
        key=lambda item: (
            -item["priority_score"],
            -item["level_gap"],
            item["skill"].lower(),
        )
    )

    priority_skills = [
        {
            key: value
            for key, value in item.items()
            if key != "priority_score"
        }
        for item in priority_candidates[:10]
    ]

    return {
        "status": "success",
        "role": {
            "id": role.id,
            "name": role.name,
            "slug": role.slug,
            "track": role.track.name,
            "track_slug": role.track.slug,
            "category": role.track.category.name,
            "category_slug": role.track.category.slug,
        },
        "score": score,
        "required_skill_coverage": clamp(
            required_coverage
        ),
        "strong_skills": strong_skills,
        "improvement_skills": improvement_skills,
        "missing_skills": missing_skills,
        "priority_skills": priority_skills,
        "summary": {
            "total": len(role_skills),
            "required": sum(
                item.importance == "required"
                for item in role_skills
            ),
            "important": sum(
                item.importance == "important"
                for item in role_skills
            ),
            "optional": sum(
                item.importance == "optional"
                for item in role_skills
            ),
            "matched": len(
                strong_skills
            ),
            "needs_improvement": len(
                improvement_skills
            ),
            "missing": len(
                missing_skills
            ),
        },
    }