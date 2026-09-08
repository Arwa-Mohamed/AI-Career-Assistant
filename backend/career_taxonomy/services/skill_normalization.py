from __future__ import annotations

import re
from functools import lru_cache
from typing import Any

from career_taxonomy.models import Skill


def normalize_text(value: Any) -> str:
    if value is None:
        return ""

    text = str(value).lower()

    text = text.replace(
        "&",
        " and ",
    )

    text = re.sub(
        r"[^a-z0-9+#.\-/ ]+",
        " ",
        text,
    )

    return " ".join(
        text.split()
    ).strip()


def _normalize_aliases(
    skill: Skill,
) -> list[str]:
    aliases = [
        skill.name,
    ]

    if isinstance(
        skill.aliases,
        list,
    ):
        aliases.extend(
            str(alias)
            for alias in skill.aliases
            if alias
        )

    elif isinstance(
        skill.aliases,
        dict,
    ):
        aliases.extend(
            str(key)
            for key in skill.aliases.keys()
            if key
        )

        aliases.extend(
            str(value)
            for value in skill.aliases.values()
            if value
        )

    normalized = []

    for alias in aliases:
        value = normalize_text(alias)

        if value:
            normalized.append(value)

    return list(
        dict.fromkeys(normalized)
    )


@lru_cache(maxsize=1)
def build_skill_index() -> tuple:
    """
    Cached taxonomy index.

    The cache can later be replaced with Redis for multi-worker deployment.
    """

    skills = list(
        Skill.objects
        .filter(is_active=True)
        .only(
            "id",
            "name",
            "slug",
            "aliases",
            "skill_type",
        )
    )

    index = []

    for skill in skills:
        aliases = _normalize_aliases(skill)

        index.append(
            {
                "id": skill.id,
                "name": skill.name,
                "slug": skill.slug,
                "skill_type": skill.skill_type,
                "aliases": aliases,
            }
        )

    index.sort(
        key=lambda item: max(
            (
                len(alias)
                for alias in item["aliases"]
            ),
            default=0,
        ),
        reverse=True,
    )

    return tuple(index)


def clear_skill_index_cache() -> None:
    """
    Call after changing taxonomy skills in admin/importers.
    """

    build_skill_index.cache_clear()


def phrase_exists(
    text: str,
    phrase: str,
) -> bool:
    if not text or not phrase:
        return False

    pattern = (
        rf"(?<![a-z0-9+#.\-/])"
        rf"{re.escape(phrase)}"
        rf"(?![a-z0-9+#.\-/])"
    )

    return bool(
        re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )
    )


def extract_taxonomy_skills(
    text: str,
    parsed_skills: list[Any] | None = None,
) -> list[dict]:
    """
    Convert raw CV language into canonical taxonomy skills.
    """

    raw_text = normalize_text(text)

    explicit_skills = normalize_text(
        " ".join(
            str(item)
            for item in (
                parsed_skills or []
            )
            if item
        )
    )

    searchable_text = " ".join(
        value
        for value in (
            raw_text,
            explicit_skills,
        )
        if value
    )

    if not searchable_text:
        return []

    results = []

    for skill in build_skill_index():
        matched_aliases = [
            alias
            for alias in skill["aliases"]
            if phrase_exists(
                searchable_text,
                alias,
            )
        ]

        if not matched_aliases:
            continue

        longest_match = max(
            (
                len(alias)
                for alias in matched_aliases
            ),
            default=1,
        )

        # Confidence is a heuristic for now.
        # Later it can incorporate occurrence count,
        # project evidence and experience duration.
        confidence = min(
            0.98,
            round(
                0.60
                + (
                    min(longest_match, 30)
                    / 100
                ),
                2,
            ),
        )

        results.append(
            {
                "skill_id": skill["id"],
                "name": skill["name"],
                "slug": skill["slug"],
                "skill_type": skill["skill_type"],
                "matched_aliases": matched_aliases,
                "confidence": confidence,
                "evidence": {
                    "source": "cv",
                    "explicit_section": any(
                        phrase_exists(
                            explicit_skills,
                            alias,
                        )
                        for alias in matched_aliases
                    ),
                },
            }
        )

    return results