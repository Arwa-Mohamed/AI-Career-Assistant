from __future__ import annotations

import re
from typing import Any, Iterable


# ============================================================
# Text Utilities
# ============================================================

def _normalize(value: Any) -> str:
    """
    Normalize any value into searchable lowercase text.
    """
    if value is None:
        return ""

    if isinstance(value, (list, tuple, set)):
        value = " ".join(str(item) for item in value)

    if isinstance(value, dict):
        value = " ".join(
            f"{key} {val}"
            for key, val in value.items()
        )

    text = str(value).lower()

    text = re.sub(r"[\r\n\t]+", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def _flatten_strings(value: Any) -> list[str]:
    """
    Recursively flatten nested structures into strings.
    """
    result: list[str] = []

    if value is None:
        return result

    if isinstance(value, str):
        value = value.strip()

        if value:
            result.append(value)

        return result

    if isinstance(value, dict):
        for key, val in value.items():
            result.extend(_flatten_strings(key))
            result.extend(_flatten_strings(val))

        return result

    if isinstance(value, (list, tuple, set)):
        for item in value:
            result.extend(_flatten_strings(item))

        return result

    result.append(str(value))

    return result


def _contains_term(text: str, term: str) -> bool:
    """
    Boundary-aware term matching.
    """

    text = _normalize(text)
    term = _normalize(term)

    if not text or not term:
        return False

    escaped = re.escape(term)

    return bool(
        re.search(
            rf"(?<!\w){escaped}(?!\w)",
            text,
            flags=re.IGNORECASE,
        )
    )


# ============================================================
# Candidate Profile Helpers
# ============================================================

def _candidate_skills(candidate_profile: dict) -> list[dict]:
    """
    Get normalized taxonomy skills from canonical candidate profile.
    """

    skills = candidate_profile.get("skills") or []

    if not isinstance(skills, list):
        return []

    return [
        skill
        for skill in skills
        if isinstance(skill, dict)
    ]


def _candidate_skill_ids(candidate_profile: dict) -> set[int]:
    """
    Return canonical taxonomy skill IDs.
    """

    skill_ids = set()

    for skill in _candidate_skills(candidate_profile):
        skill_id = skill.get("skill_id")

        if skill_id is not None:
            try:
                skill_ids.add(int(skill_id))
            except (TypeError, ValueError):
                continue

    return skill_ids


def _candidate_skill_names(candidate_profile: dict) -> set[str]:
    """
    Return normalized canonical skill names.
    """

    names = set()

    for skill in _candidate_skills(candidate_profile):
        name = skill.get("name")

        if name:
            names.add(_normalize(name))

    return names


def _candidate_skill_aliases(candidate_profile: dict) -> set[str]:
    """
    Return aliases detected for candidate skills.
    """

    aliases = set()

    for skill in _candidate_skills(candidate_profile):
        for alias in skill.get("matched_aliases", []) or []:
            normalized = _normalize(alias)

            if normalized:
                aliases.add(normalized)

    return aliases


def _candidate_search_text(candidate_profile: dict) -> str:
    """
    Build searchable candidate text from canonical profile.

    This is only used as supporting evidence.
    The normalized taxonomy skills remain the primary signal.
    """

    values = [
        candidate_profile.get("summary", ""),
        candidate_profile.get("target_role", ""),
        candidate_profile.get("raw_text", ""),
    ]

    for field in (
        "experience",
        "projects",
        "education",
        "certifications",
        "languages",
    ):
        values.extend(
            _flatten_strings(
                candidate_profile.get(field, [])
            )
        )

    values.extend(
        _flatten_strings(
            candidate_profile.get("skills_raw", [])
        )
    )

    return _normalize(" ".join(values))


def _candidate_titles(candidate_profile: dict) -> list[str]:
    """
    Extract possible target/current role titles.
    """

    titles = []

    target_role = candidate_profile.get("target_role")

    if target_role:
        titles.extend(_flatten_strings(target_role))

    # Some parsers may expose title-like information
    for key in (
        "title",
        "current_title",
        "job_title",
        "desired_role",
        "target_roles",
    ):
        if candidate_profile.get(key):
            titles.extend(
                _flatten_strings(
                    candidate_profile[key]
                )
            )

    # De-duplicate while preserving order.
    seen = set()
    result = []

    for title in titles:
        normalized = _normalize(title)

        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(title)

    return result


# ============================================================
# Role Helpers
# ============================================================

def _role_title_terms(role) -> list[str]:
    """
    Build title evidence terms from Role.
    """

    terms = []

    if getattr(role, "name", None):
        terms.append(role.name)

    terms.extend(
        _flatten_strings(
            getattr(role, "typical_titles", None) or []
        )
    )

    # De-duplicate.
    normalized_seen = set()
    result = []

    for term in terms:
        normalized = _normalize(term)

        if normalized and normalized not in normalized_seen:
            normalized_seen.add(normalized)
            result.append(term)

    return result


def _role_search_text(role) -> str:
    """
    Build role-specific searchable text.
    """

    values = [
        getattr(role, "name", ""),
        getattr(role, "description", ""),
    ]

    values.extend(
        _flatten_strings(
            getattr(role, "typical_titles", None) or []
        )
    )

    values.extend(
        _flatten_strings(
            getattr(role, "responsibilities", None) or []
        )
    )

    values.extend(
        _flatten_strings(
            getattr(role, "interview_topics", None) or []
        )
    )

    values.extend(
        _flatten_strings(
            getattr(role, "project_types", None) or []
        )
    )

    return _normalize(" ".join(values))


# ============================================================
# Title Scoring
# ============================================================

def _score_title_evidence(
    candidate_profile: dict,
    role,
) -> dict:
    """
    Score explicit candidate target/current titles against a role.
    """

    candidate_titles = _candidate_titles(candidate_profile)

    if not candidate_titles:
        return {
            "score": 0.0,
            "matched_titles": [],
        }

    role_terms = _role_title_terms(role)

    if not role_terms:
        return {
            "score": 0.0,
            "matched_titles": [],
        }

    matched_titles = []

    for candidate_title in candidate_titles:
        candidate_normalized = _normalize(candidate_title)

        for role_term in role_terms:
            role_normalized = _normalize(role_term)

            if not role_normalized:
                continue

            # Exact phrase match.
            if _contains_term(
                candidate_normalized,
                role_normalized,
            ):
                matched_titles.append(
                    {
                        "candidate_title": candidate_title,
                        "matched_role_title": role_term,
                        "match_type": "exact",
                    }
                )
                break

            # Token overlap for titles such as:
            # "Junior Backend Engineer"
            # vs "Backend Developer"
            candidate_tokens = {
                token
                for token in candidate_normalized.split()
                if len(token) > 2
            }

            role_tokens = {
                token
                for token in role_normalized.split()
                if len(token) > 2
            }

            if candidate_tokens and role_tokens:
                overlap = len(
                    candidate_tokens.intersection(role_tokens)
                ) / max(
                    len(role_tokens),
                    1,
                )

                if overlap >= 0.5:
                    matched_titles.append(
                        {
                            "candidate_title": candidate_title,
                            "matched_role_title": role_term,
                            "match_type": "partial",
                            "overlap": round(overlap, 3),
                        }
                    )
                    break

    if not matched_titles:
        return {
            "score": 0.0,
            "matched_titles": [],
        }

    has_exact = any(
        item["match_type"] == "exact"
        for item in matched_titles
    )

    score = 1.0 if has_exact else 0.65

    return {
        "score": score,
        "matched_titles": matched_titles,
    }


# ============================================================
# Skill Scoring
# ============================================================

def _score_role_skills(
    role,
    candidate_profile: dict,
) -> dict:
    """
    Score candidate against RoleSkill requirements.

    Important:
    - Uses already-prefetched role_skills.
    - Uses canonical taxonomy skill IDs as primary evidence.
    - Does not perform database queries.
    """

    candidate_skill_ids = _candidate_skill_ids(
        candidate_profile
    )

    candidate_skill_names = _candidate_skill_names(
        candidate_profile
    )

    candidate_aliases = _candidate_skill_aliases(
        candidate_profile
    )

    candidate_text = _candidate_search_text(
        candidate_profile
    )

    role_skills = list(
        role.role_skills.all()
    )

    if not role_skills:
        return {
            "score": 0.0,
            "required_coverage": 0.0,
            "matched_skills": [],
            "partial_skills": [],
            "missing_skills": [],
            "matched_evidence": [],
            "matched_weight": 0.0,
            "total_weight": 0.0,
        }

    matched_skills = []
    partial_skills = []
    missing_skills = []
    matched_evidence = []

    total_weight = 0.0
    matched_weight = 0.0
    required_total = 0.0
    required_matched = 0.0

    for role_skill in role_skills:

        skill = role_skill.skill

        if not skill or not skill.is_active:
            continue

        weight = float(
            role_skill.weight or 1
        )

        importance = role_skill.importance

        # Importance multiplier.
        importance_multiplier = {
            "required": 1.5,
            "important": 1.0,
            "optional": 0.5,
        }.get(
            importance,
            1.0,
        )

        effective_weight = (
            weight * importance_multiplier
        )

        total_weight += effective_weight

        if importance == "required":
            required_total += effective_weight

        skill_id = skill.id
        skill_name = _normalize(skill.name)

        aliases = [
            _normalize(alias)
            for alias in (
                skill.aliases or []
            )
            if _normalize(alias)
        ]

        # ----------------------------------------------------
        # 1. Exact canonical taxonomy match
        # ----------------------------------------------------

        if skill_id in candidate_skill_ids:

            candidate_skill = next(
                (
                    item
                    for item in _candidate_skills(
                        candidate_profile
                    )
                    if item.get("skill_id") == skill_id
                ),
                {},
            )

            confidence = float(
                candidate_skill.get(
                    "confidence",
                    0.95,
                )
                or 0.95
            )

            confidence = max(
                0.0,
                min(
                    confidence,
                    1.0,
                ),
            )

            matched_skills.append(
                {
                    "skill_id": skill.id,
                    "skill": skill.name,
                    "importance": importance,
                    "weight": weight,
                    "confidence": round(
                        confidence,
                        3,
                    ),
                    "minimum_level": role_skill.minimum_level,
                }
            )

            matched_evidence.append(
                {
                    "skill": skill.name,
                    "source": "canonical_taxonomy",
                    "confidence": round(
                        confidence,
                        3,
                    ),
                }
            )

            matched_weight += (
                effective_weight * confidence
            )

            if importance == "required":
                required_matched += (
                    effective_weight * confidence
                )

            continue

        # ----------------------------------------------------
        # 2. Name / alias fallback
        # ----------------------------------------------------

        matched_alias = None

        if skill_name in candidate_skill_names:
            matched_alias = skill.name

        else:
            for alias in aliases:
                if alias in candidate_aliases:
                    matched_alias = alias
                    break

        if matched_alias:

            confidence = 0.85

            matched_skills.append(
                {
                    "skill_id": skill.id,
                    "skill": skill.name,
                    "importance": importance,
                    "weight": weight,
                    "confidence": confidence,
                    "minimum_level": role_skill.minimum_level,
                }
            )

            matched_evidence.append(
                {
                    "skill": skill.name,
                    "source": "normalized_name_or_alias",
                    "matched_alias": matched_alias,
                    "confidence": confidence,
                }
            )

            matched_weight += (
                effective_weight * confidence
            )

            if importance == "required":
                required_matched += (
                    effective_weight * confidence
                )

            continue

        # ----------------------------------------------------
        # 3. Raw CV supporting evidence
        # ----------------------------------------------------

        matched_raw = False

        if skill_name and _contains_term(
            candidate_text,
            skill_name,
        ):
            matched_raw = True
            evidence_term = skill.name

        else:
            evidence_term = None

            for alias in aliases:
                if _contains_term(
                    candidate_text,
                    alias,
                ):
                    matched_raw = True
                    evidence_term = alias
                    break

        if matched_raw:

            confidence = 0.60

            partial_skills.append(
                {
                    "skill_id": skill.id,
                    "skill": skill.name,
                    "importance": importance,
                    "weight": weight,
                    "confidence": confidence,
                    "minimum_level": role_skill.minimum_level,
                    "evidence": evidence_term,
                }
            )

            matched_evidence.append(
                {
                    "skill": skill.name,
                    "source": "raw_cv_text",
                    "matched_term": evidence_term,
                    "confidence": confidence,
                }
            )

            matched_weight += (
                effective_weight * confidence
            )

            if importance == "required":
                required_matched += (
                    effective_weight * confidence
                )

            continue

        # ----------------------------------------------------
        # 4. Missing
        # ----------------------------------------------------

        missing_skills.append(
            {
                "skill_id": skill.id,
                "skill": skill.name,
                "importance": importance,
                "weight": weight,
                "minimum_level": role_skill.minimum_level,
            }
        )

    if total_weight > 0:
        score = (
            matched_weight / total_weight
        ) * 100
    else:
        score = 0.0

    if required_total > 0:
        required_coverage = (
            required_matched / required_total
        ) * 100
    else:
        required_coverage = 100.0

    return {
        "score": round(
            min(score, 100.0),
            2,
        ),
        "required_coverage": round(
            min(required_coverage, 100.0),
            2,
        ),
        "matched_skills": matched_skills,
        "partial_skills": partial_skills,
        "missing_skills": missing_skills,
        "matched_evidence": matched_evidence,
        "matched_weight": round(
            matched_weight,
            3,
        ),
        "total_weight": round(
            total_weight,
            3,
        ),
    }


# ============================================================
# Match Reason
# ============================================================

def _build_match_reason(
    skill_result: dict,
    title_result: dict,
) -> str:
    """
    Generate a human-readable explanation.
    """

    matched = skill_result.get(
        "matched_skills",
        [],
    )

    partial = skill_result.get(
        "partial_skills",
        [],
    )

    missing = skill_result.get(
        "missing_skills",
        [],
    )

    title_matches = title_result.get(
        "matched_titles",
        [],
    )

    parts = []

    if title_matches:
        parts.append(
            "Strong title alignment"
        )

    if matched:
        parts.append(
            f"{len(matched)} relevant skills matched"
        )

    if partial:
        parts.append(
            f"{len(partial)} skills supported by CV evidence"
        )

    if missing:
        parts.append(
            f"{len(missing)} skills still missing"
        )

    if not parts:
        return "Limited evidence for this role"

    return " • ".join(parts)


# ============================================================
# Career Detection
# ============================================================

def detect_career_roles(
    *,
    roles: Iterable,
    candidate_profile: dict,
    top_n: int = 5,
) -> dict:
    """
    Detect the best career roles for a candidate.

    This is intentionally database-agnostic.

    `roles` must be a prefetched iterable from
    `get_intelligence_roles()`.

    `candidate_profile` must be the canonical candidate
    intelligence profile.

    Returns:
        {
            "status": "success",
            "best_role": {...},
            "top_roles": [...],
            "count": int,
        }
    """

    if not candidate_profile:
        return {
            "status": "insufficient_evidence",
            "best_role": None,
            "top_roles": [],
            "count": 0,
        }

    roles = list(roles or [])

    if not roles:
        return {
            "status": "no_roles",
            "best_role": None,
            "top_roles": [],
            "count": 0,
        }

    results = []

    for role in roles:

        skill_result = _score_role_skills(
            role,
            candidate_profile,
        )

        title_result = _score_title_evidence(
            candidate_profile,
            role,
        )

        skill_score = float(
            skill_result.get(
                "score",
                0,
            )
        )

        title_score = float(
            title_result.get(
                "score",
                0,
            )
        )

        # ----------------------------------------------------
        # Main scoring model
        #
        # Skills = 78%
        # Explicit title = 22%
        # ----------------------------------------------------

        final_score = (
            skill_score * 0.78
        ) + (
            title_score * 100 * 0.22
        )

        final_score = max(
            0.0,
            min(
                final_score,
                100.0,
            ),
        )

        # Confidence is slightly more conservative
        # than raw score.
        confidence = final_score

        matched_skill_count = len(
            skill_result.get(
                "matched_skills",
                [],
            )
        )

        partial_skill_count = len(
            skill_result.get(
                "partial_skills",
                [],
            )
        )

        required_skill_count = (
            matched_skill_count
            + partial_skill_count
            + len(
                [
                    item
                    for item in skill_result.get(
                        "missing_skills",
                        [],
                    )
                    if item.get("importance") == "required"
                ]
            )
        )

        result = {
            "role_id": role.id,
            "role": role.name,
            "role_slug": role.slug,

            "track": role.track.name
            if role.track
            else None,

            "track_slug": role.track.slug
            if role.track
            else None,

            "category": (
                role.track.category.name
                if role.track
                and role.track.category
                else None
            ),

            "category_slug": (
                role.track.category.slug
                if role.track
                and role.track.category
                else None
            ),

            "score": round(
                final_score,
                2,
            ),

            "confidence": round(
                confidence,
                2,
            ),

            "title_match": round(
                title_score * 100,
                2,
            ),

            "skill_score": round(
                skill_score,
                2,
            ),

            "required_skill_coverage": skill_result.get(
                "required_coverage",
                0,
            ),

            "matched_skills": skill_result.get(
                "matched_skills",
                [],
            ),

            "partial_skills": skill_result.get(
                "partial_skills",
                [],
            ),

            "missing_skills": skill_result.get(
                "missing_skills",
                [],
            ),

            "matched_evidence": skill_result.get(
                "matched_evidence",
                [],
            ),

            "matched_titles": title_result.get(
                "matched_titles",
                [],
            ),

            "matched_skill_count": matched_skill_count,

            "partial_skill_count": partial_skill_count,

            "required_skill_count": required_skill_count,

            "match_reason": _build_match_reason(
                skill_result,
                title_result,
            ),
        }

        results.append(result)

    # Highest score first.
    results.sort(
        key=lambda item: (
            item["score"],
            item["required_skill_coverage"],
            item["skill_score"],
        ),
        reverse=True,
    )

    top_n = max(
        int(top_n or 5),
        1,
    )

    results = results[:top_n]

    if not results:
        status = "insufficient_evidence"
        best_role = None
    else:
        status = "success"
        best_role = results[0]

    return {
        "status": status,
        "best_role": best_role,
        "top_roles": results,
        "count": len(results),
    }