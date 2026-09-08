from typing import Any

from .canonical_profile import (
    build_canonical_candidate_profile,
)
from .skill_normalization import (
    extract_taxonomy_skills,
)


def build_candidate_intelligence(
    parsed_data: Any,
    extracted_text: str = "",
) -> dict:
    """
    Creates the normalized candidate representation used
    by the rest of the Career Intelligence platform.
    """

    profile = build_canonical_candidate_profile(
        parsed_data=parsed_data,
        extracted_text=extracted_text,
    )

    searchable_text_parts = [
        profile.get("raw_text", ""),
        profile.get("summary", ""),
        profile.get("target_role", ""),
        *profile.get("skills_raw", []),
        *profile.get("experience", []),
        *profile.get("education", []),
        *profile.get("projects", []),
        *profile.get("certifications", []),
        *profile.get("languages", []),
    ]

    searchable_text = " ".join(
        str(part)
        for part in searchable_text_parts
        if part
    )

    normalized_skills = extract_taxonomy_skills(
        text=searchable_text,
        parsed_skills=profile.get(
            "skills_raw",
            [],
        ),
    )

    profile["skills"] = normalized_skills

    profile["skill_count"] = len(
        normalized_skills
    )

    return profile