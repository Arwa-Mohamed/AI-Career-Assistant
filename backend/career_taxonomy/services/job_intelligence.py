import re
from typing import Any, Dict, Iterable, List, Optional

from career_taxonomy.models import Role, RoleSkill, Skill
from .canonical_profile import build_canonical_candidate_profile


WORD_RE = re.compile(r"\b[\w+#./-]+\b", re.UNICODE)


def normalize_text(value: Any) -> str:
    if value is None:
        return ""

    text = str(value).lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def skill_terms(skill: Skill) -> List[str]:
    terms = [skill.name]

    aliases = (
        skill.aliases
        if isinstance(skill.aliases, list)
        else []
    )

    terms.extend(
        str(item)
        for item in aliases
        if item
    )

    cleaned: List[str] = []
    seen = set()

    for term in terms:
        normalized = normalize_text(term)

        if normalized and normalized not in seen:
            seen.add(normalized)
            cleaned.append(normalized)

    return cleaned


def contains_term(
    text: str,
    term: str,
) -> bool:
    term = normalize_text(term)

    if not text or not term:
        return False

    escaped = re.escape(term)

    return re.search(
        rf"(?<![a-z0-9])"
        rf"{escaped}"
        rf"(?![a-z0-9])",
        text,
        flags=re.IGNORECASE,
    ) is not None


def candidate_text(cv: Any) -> str:
    """
    Legacy/fallback candidate text extraction.

    This is intentionally kept for backward compatibility with older CVs.
    Career Intelligence should prefer candidate_profile when available.
    """
    if cv is None:
        return ""

    pieces = [
        cv.extracted_text or ""
    ]

    parsed = (
        cv.parsed_data
        if isinstance(cv.parsed_data, dict)
        else {}
    )

    for key in (
        "summary",
        "objective",
        "experience",
        "education",
        "projects",
        "skills",
        "certifications",
        "training",
        "languages",
    ):
        value = parsed.get(key)

        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    pieces.extend(
                        str(v)
                        for v in item.values()
                        if isinstance(
                            v,
                            (str, int, float),
                        )
                    )
                elif item is not None:
                    pieces.append(str(item))

        elif value is not None:
            pieces.append(str(value))

    return normalize_text(
        " ".join(pieces)
    )


def _candidate_profile_text(
    candidate_profile: Optional[Dict[str, Any]],
) -> str:
    """
    Build searchable candidate text from the canonical profile.

    This is the preferred source for Career Intelligence.
    """

    if not isinstance(candidate_profile, dict):
        return ""

    pieces: List[str] = []

    for key in (
        "raw_text",
        "summary",
        "target_role",
        "experience",
        "education",
        "projects",
        "certifications",
        "languages",
        "skills_raw",
    ):
        value = candidate_profile.get(key)

        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    pieces.extend(
                        str(v)
                        for v in item.values()
                        if v is not None
                    )
                elif item is not None:
                    pieces.append(str(item))

        elif value is not None:
            pieces.append(str(value))

    return normalize_text(
        " ".join(pieces)
    )


def _candidate_skill_map(
    candidate_profile: Optional[Dict[str, Any]],
) -> Dict[int, Dict[str, Any]]:
    """
    Convert normalized taxonomy skills into a lookup map.

    Expected candidate_profile["skills"] items look like:

    {
        "skill_id": 12,
        "name": "Python",
        "slug": "python",
        "skill_type": "technical",
        "matched_aliases": ["python"],
        "confidence": 0.72,
        "evidence": {
            "source": "cv",
            "explicit_section": True
        }
    }
    """

    if not isinstance(candidate_profile, dict):
        return {}

    skills = candidate_profile.get("skills")

    if not isinstance(skills, list):
        return {}

    result: Dict[int, Dict[str, Any]] = {}

    for item in skills:
        if not isinstance(item, dict):
            continue

        skill_id = item.get("skill_id")

        if skill_id is None:
            continue

        try:
            skill_id = int(skill_id)
        except (TypeError, ValueError):
            continue

        result[skill_id] = item

    return result


def _build_candidate_profile(
    cv: Any,
) -> Dict[str, Any]:
    """
    Build the canonical candidate profile when the caller does not
    provide one.

    This keeps build_job_intelligence backward-compatible while allowing
    the main API flow to pass an already-built profile and avoid duplicate
    work.
    """

    if cv is None:
        return {}

    return build_canonical_candidate_profile(
        parsed_data=(
            cv.parsed_data
            if isinstance(cv.parsed_data, dict)
            else {}
        ),
        extracted_text=(
            cv.extracted_text or ""
        ),
    )


def extract_job_skills(
    job_description: str,
) -> List[Dict[str, Any]]:
    """
    Extract taxonomy skills explicitly mentioned in the job description.
    """

    text = normalize_text(
        job_description
    )

    if not text:
        return []

    matches: List[Dict[str, Any]] = []

    skills = (
        Skill.objects
        .filter(is_active=True)
        .only(
            "id",
            "name",
            "slug",
            "skill_type",
            "aliases",
        )
    )

    for skill in skills:
        terms = skill_terms(skill)

        found_terms = [
            term
            for term in terms
            if contains_term(
                text,
                term,
            )
        ]

        if not found_terms:
            continue

        matches.append(
            {
                "skill_id": skill.id,
                "name": skill.name,
                "slug": skill.slug,
                "skill_type": skill.skill_type,
                "matched_terms": found_terms,
            }
        )

    matches.sort(
        key=lambda item: item["name"].lower()
    )

    return matches


def _role_title_score(
    role: Role,
    job_text: str,
) -> float:
    titles = [role.name]

    if isinstance(
        role.typical_titles,
        list,
    ):
        titles.extend(
            str(item)
            for item in role.typical_titles
            if item
        )

    best = 0.0

    for title in titles:
        normalized = normalize_text(title)

        if not normalized:
            continue

        if contains_term(
            job_text,
            normalized,
        ):
            best = max(
                best,
                100.0,
            )

    return best


def rank_job_roles(
    job_description: str,
    limit: int = 5,
) -> List[Dict[str, Any]]:
    text = normalize_text(
        job_description
    )

    if not text:
        return []

    roles = (
        Role.objects
        .filter(is_active=True)
        .select_related(
            "track",
            "track__category",
        )
        .prefetch_related(
            "role_skills__skill"
        )
    )

    results: List[Dict[str, Any]] = []

    for role in roles:
        links = list(
            role.role_skills.all()
        )

        if not links:
            continue

        total_weight = (
            sum(
                float(link.weight or 0)
                for link in links
            )
            or 1.0
        )

        matched_weight = 0.0
        matched_skills = []

        for link in links:
            found = any(
                contains_term(
                    text,
                    term,
                )
                for term in skill_terms(
                    link.skill
                )
            )

            if found:
                matched_weight += float(
                    link.weight or 0
                )

                matched_skills.append(
                    link.skill.name
                )

        skill_score = (
            matched_weight
            / total_weight
        ) * 100.0

        title_score = _role_title_score(
            role,
            text,
        )

        score = min(
            100.0,
            skill_score * 0.8
            + title_score * 0.2,
        )

        results.append(
            {
                "role_id": role.id,
                "role": role.name,
                "track": role.track.name,
                "category": (
                    role.track.category.name
                ),
                "score": round(
                    score,
                    2,
                ),
                "matched_role_skills": matched_skills,
            }
        )

    results.sort(
        key=lambda item: (
            -item["score"],
            item["role"],
        )
    )

    return results[
        : max(
            1,
            int(limit),
        )
    ]


def match_candidate_to_role(
    cv: Any,
    role_id: int,
    candidate_profile: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Match a candidate against a taxonomy role.

    Preferred source:
        candidate_profile["skills"]

    Fallback:
        canonical/raw CV text

    This makes normalized taxonomy skills the primary source without
    breaking older CV records.
    """

    role = (
        Role.objects
        .filter(
            id=role_id,
            is_active=True,
        )
        .select_related(
            "track",
            "track__category",
        )
        .prefetch_related(
            "role_skills__skill"
        )
        .first()
    )

    if role is None:
        return {
            "score": 0.0,
            "matched": [],
            "partial": [],
            "missing": [],
            "required_skill_coverage": 0.0,
            "role": None,
        }

    if candidate_profile is None:
        candidate_profile = _build_candidate_profile(cv)

    normalized_skill_map = _candidate_skill_map(
        candidate_profile
    )

    profile_text = _candidate_profile_text(
        candidate_profile
    )

    if not profile_text:
        profile_text = candidate_text(cv)

    links = list(
        role.role_skills.all()
    )

    matched = []
    partial = []
    missing = []

    total_weight = (
        sum(
            float(link.weight or 0)
            for link in links
        )
        or 1.0
    )

    matched_weight = 0.0

    required_total = 0.0
    required_matched = 0.0

    for link in links:
        skill = link.skill

        normalized_skill = normalized_skill_map.get(
            skill.id
        )

        taxonomy_matched = (
            normalized_skill is not None
        )

        found_terms = []

        if normalized_skill:
            found_terms = (
                normalized_skill.get(
                    "matched_aliases",
                    [],
                )
                or []
            )

        # Raw/canonical text is only a fallback.
        if not taxonomy_matched:
            found_terms = [
                term
                for term in skill_terms(skill)
                if contains_term(
                    profile_text,
                    term,
                )
            ]

        found = bool(
            taxonomy_matched
            or found_terms
        )

        is_required = (
            link.importance
            == RoleSkill.Importance.REQUIRED
        )

        weight = float(
            link.weight or 0
        )

        if is_required:
            required_total += weight

        evidence = {}

        if normalized_skill:
            evidence = (
                normalized_skill.get(
                    "evidence",
                    {}
                )
                if isinstance(
                    normalized_skill.get(
                        "evidence"
                    ),
                    dict,
                )
                else {}
            )

        entry = {
            "skill_id": skill.id,
            "name": skill.name,
            "slug": skill.slug,
            "importance": link.importance,
            "weight": weight,
            "minimum_level": link.minimum_level,
            "matched_terms": list(
                dict.fromkeys(
                    found_terms
                )
            ),
            "confidence": (
                normalized_skill.get(
                    "confidence"
                )
                if normalized_skill
                else None
            ),
            "evidence": evidence,
            "match_source": (
                "taxonomy"
                if taxonomy_matched
                else (
                    "profile_text"
                    if found_terms
                    else None
                )
            ),
        }

        if found:
            matched.append(entry)

            matched_weight += weight

            if is_required:
                required_matched += weight

        elif is_required:
            missing.append(entry)

        else:
            partial.append(entry)

    role_score = (
        matched_weight
        / total_weight
    ) * 100.0

    required_coverage = (
        (
            required_matched
            / required_total
        ) * 100.0
        if required_total
        else role_score
    )

    score = round(
        role_score * 0.6
        + required_coverage * 0.4,
        2,
    )

    return {
        "role": {
            "id": role.id,
            "name": role.name,
            "track": role.track.name,
            "category": (
                role.track.category.name
            ),
        },
        "score": score,
        "matched": matched,
        "partial": partial,
        "missing": missing,
        "required_skill_coverage": round(
            min(
                required_coverage,
                100.0,
            ),
            2,
        ),
    }


def build_roadmap_for_missing_skills(
    role_id: int,
    missing_skill_ids: Iterable[int],
    max_steps: int = 12,
) -> List[Dict[str, Any]]:
    ids = {
        int(skill_id)
        for skill_id in missing_skill_ids
    }

    if not ids:
        return []

    role = (
        Role.objects
        .filter(
            id=role_id,
            is_active=True,
        )
        .prefetch_related(
            "roadmap_phases__steps__skill"
        )
        .first()
    )

    if role is None:
        return []

    wanted = []

    for phase in role.roadmap_phases.all():
        for step in phase.steps.all():

            if step.skill_id in ids:
                wanted.append(
                    {
                        "phase_number": (
                            phase.phase_number
                        ),
                        "phase": phase.title,
                        "title": step.title,
                        "description": (
                            step.description
                        ),
                        "skill": (
                            step.skill.name
                            if step.skill
                            else None
                        ),
                        "resource_type": (
                            step.resource_type
                        ),
                        "estimated_hours": (
                            step.estimated_hours
                        ),
                        "completion_criteria": (
                            step.completion_criteria
                        ),
                    }
                )

    return wanted[
        :max_steps
    ]


def _application_readiness(
    score: float,
    ats_score: float,
) -> Dict[str, Any]:
    combined = round(
        score * 0.7
        + float(
            ats_score or 0
        ) * 0.3,
        2,
    )

    if combined >= 85:
        label = "Strong Apply"
        verdict = "yes"

    elif combined >= 70:
        label = "Apply with Minor Gaps"
        verdict = "yes"

    elif combined >= 55:
        label = (
            "Consider Applying After Improvements"
        )
        verdict = "maybe"

    else:
        label = "Build Skills Before Applying"
        verdict = "not_yet"

    return {
        "score": combined,
        "verdict": verdict,
        "label": label,
    }


def _merge_job_skill(
    collection: Dict[int, Dict[str, Any]],
    skill: Skill,
    matched_terms: List[str],
) -> None:
    existing = collection.get(
        skill.id
    )

    if existing is None:
        collection[skill.id] = {
            "skill_id": skill.id,
            "name": skill.name,
            "slug": skill.slug,
            "skill_type": skill.skill_type,
            "matched_terms": list(
                dict.fromkeys(
                    matched_terms
                )
            ),
        }

        return

    existing["matched_terms"] = list(
        dict.fromkeys(
            [
                *existing.get(
                    "matched_terms",
                    [],
                ),
                *matched_terms,
            ]
        )
    )


def _enrich_job_skills_from_role(
    job_text: str,
    role_id: int,
    existing_matches: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    merged: Dict[int, Dict[str, Any]] = {}

    for item in existing_matches:
        merged[
            item["skill_id"]
        ] = dict(item)

    role = (
        Role.objects
        .filter(
            id=role_id,
            is_active=True,
        )
        .prefetch_related(
            "role_skills__skill"
        )
        .first()
    )

    if role is None:
        return list(
            sorted(
                merged.values(),
                key=lambda item: (
                    item["name"].lower()
                ),
            )
        )

    for link in role.role_skills.all():
        skill = link.skill

        found_terms = [
            term
            for term in skill_terms(skill)
            if contains_term(
                job_text,
                term,
            )
        ]

        if not found_terms:
            continue

        _merge_job_skill(
            merged,
            skill,
            found_terms,
        )

    return sorted(
        merged.values(),
        key=lambda item: (
            item["name"].lower()
        ),
    )


def build_job_intelligence(
    cv: Any,
    job_description: str,
    ats_score: float = 0.0,
    candidate_profile: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Main job intelligence pipeline.

    candidate_profile should ideally be passed from
    build_candidate_intelligence().

    If it is not passed, we build a canonical profile internally
    as a backward-compatible fallback.
    """

    job_text = normalize_text(
        job_description
    )

    if candidate_profile is None:
        candidate_profile = _build_candidate_profile(
            cv
        )

    job_skills = extract_job_skills(
        job_text
    )

    ranked_roles = rank_job_roles(
        job_text,
        limit=5,
    )

    if not ranked_roles:
        return {
            "job_skills": job_skills,
            "detected_roles": [],
            "job_match": {
                "score": 0.0,
                "role": None,
                "skill_match": {
                    "score": 0.0,
                    "required_skill_coverage": 0.0,
                    "matched": [],
                    "partial": [],
                    "missing": [],
                },
                "priority_missing_skills": [],
            },
            "application_readiness": (
                _application_readiness(
                    0,
                    ats_score,
                )
            ),
        }

    best_role = ranked_roles[0]

    job_skills = _enrich_job_skills_from_role(
        job_text=job_text,
        role_id=best_role["role_id"],
        existing_matches=job_skills,
    )

    matched = match_candidate_to_role(
        cv=cv,
        role_id=best_role["role_id"],
        candidate_profile=candidate_profile,
    )

    missing_ids = [
        item["skill_id"]
        for item in matched["missing"]
    ]

    roadmap = build_roadmap_for_missing_skills(
        best_role["role_id"],
        missing_ids,
    )

    job_score = matched["score"]

    readiness = _application_readiness(
        job_score,
        ats_score,
    )

    return {
        "job_skills": job_skills,
        "detected_roles": ranked_roles,
        "job_match": {
            "score": job_score,
            "role": matched["role"],
            "job_skills_count": len(
                job_skills
            ),
            "skill_match": {
                "score": job_score,
                "required_skill_coverage": (
                    matched[
                        "required_skill_coverage"
                    ]
                ),
                "matched": matched[
                    "matched"
                ],
                "partial": matched[
                    "partial"
                ],
                "missing": matched[
                    "missing"
                ],
            },
            "priority_missing_skills": [
                item
                for item in matched[
                    "missing"
                ]
                if item["importance"]
                == RoleSkill.Importance.REQUIRED
            ],
            "roadmap": roadmap,
        },
        "application_readiness": readiness,
    }