from __future__ import annotations

import re
from typing import Any


SECTION_ALIASES = {
    "skills": {
        "skills",
        "technical skills",
        "technical_skills",
        "core skills",
        "core_skills",
        "competencies",
        "technologies",
        "tools",
        "technical competencies",
        "technical_competencies",
    },
    "experience": {
        "experience",
        "work experience",
        "work_experience",
        "professional experience",
        "professional_experience",
        "employment",
        "employment history",
        "employment_history",
        "professional background",
    },
    "education": {
        "education",
        "academic background",
        "academic_background",
        "degrees",
        "qualifications",
        "academic experience",
        "academic_experience",
    },
    "projects": {
        "projects",
        "personal projects",
        "personal_projects",
        "academic projects",
        "academic_projects",
        "project experience",
        "project_experience",
    },
    "certifications": {
        "certifications",
        "certificates",
        "certificates and training",
        "licenses",
        "training",
        "courses",
        "professional certifications",
        "professional_certifications",
        "professional development",
    },
    "languages": {
        "languages",
        "spoken languages",
        "spoken_languages",
        "language skills",
        "language_skills",
    },
}


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(value: Any) -> str:
    """
    Convert arbitrary values into normalized single-line text.

    IMPORTANT:
    This function intentionally collapses whitespace.
    Do NOT use it on the full extracted CV before line-based
    section parsing. Use it on individual lines/records instead.
    """

    if value is None:
        return ""

    if isinstance(value, (list, tuple, set)):
        return " ".join(
            clean_text(item)
            for item in value
            if item is not None
        )

    if isinstance(value, dict):
        return " ".join(
            f"{clean_text(key)} {clean_text(item)}"
            for key, item in value.items()
            if key is not None and item is not None
        )

    text = str(value)

    text = text.replace("\u00a0", " ")
    text = text.replace("\u200b", "")
    text = text.replace("\u2060", "")
    text = text.replace("\ufeff", "")

    text = text.replace("●", "•")
    text = text.replace("▪", "•")
    text = text.replace("◦", "•")

    text = text.replace("—", "-")
    text = text.replace("–", "-")

    return " ".join(
        text.split()
    ).strip()


def normalize_key(value: Any) -> str:
    """
    Normalize field names and section headings.
    """

    text = clean_text(value).lower()

    replacements = {
        "&": " and ",
        "_": " ",
        "-": " ",
        ":": " ",
    }

    for old, new in replacements.items():
        text = text.replace(
            old,
            new,
        )

    return " ".join(
        text.split()
    ).strip()


def flatten_values(value: Any) -> list[str]:
    """
    Recursively extract useful values from structured parser data.
    """

    if value is None:
        return []

    if isinstance(value, str):
        text = clean_text(value)

        return [text] if text else []

    if isinstance(value, (list, tuple, set)):
        result = []

        for item in value:
            result.extend(
                flatten_values(item)
            )

        return result

    if isinstance(value, dict):
        result = []

        for key, item in value.items():
            key_text = clean_text(key)

            if key_text:
                result.append(
                    key_text
                )

            result.extend(
                flatten_values(item)
            )

        return result

    text = clean_text(value)

    return [text] if text else []


# ============================================================
# STRUCTURED PARSER HELPERS
# ============================================================

def collect_section_values(
    parsed_data: Any,
    section: str,
) -> list[str]:
    """
    Extract a section from structured parser output.
    """

    if not isinstance(
        parsed_data,
        dict,
    ):
        return []

    aliases = {
        normalize_key(value)
        for value in SECTION_ALIASES.get(
            section,
            set(),
        )
    }

    result = []

    for key, value in parsed_data.items():

        normalized_key = normalize_key(
            key
        )

        if normalized_key in aliases:

            result.extend(
                flatten_values(value)
            )

    return list(
        dict.fromkeys(
            value
            for value in result
            if value
        )
    )


def collect_named_fields(
    parsed_data: Any,
    field_names: set[str],
) -> list[str]:
    """
    Extract values from differently named fields.
    """

    if not isinstance(
        parsed_data,
        dict,
    ):
        return []

    targets = {
        normalize_key(name)
        for name in field_names
    }

    result = []

    for key, value in parsed_data.items():

        if normalize_key(key) in targets:

            result.extend(
                flatten_values(value)
            )

    return list(
        dict.fromkeys(
            value
            for value in result
            if value
        )
    )


# ============================================================
# SECTION HEADINGS
# ============================================================

def _normalize_heading(
    value: str,
) -> str:

    if not value:
        return ""

    return normalize_key(
        value.rstrip(":").strip()
    )


def _build_heading_lookup() -> dict[str, str]:

    lookup: dict[str, str] = {}

    for section, aliases in SECTION_ALIASES.items():

        for alias in aliases:

            lookup[
                _normalize_heading(alias)
            ] = section

    return lookup


SECTION_HEADING_LOOKUP = (
    _build_heading_lookup()
)


def _looks_like_heading(
    line: str,
) -> str | None:

    normalized = _normalize_heading(
        line
    )

    if not normalized:
        return None

    return SECTION_HEADING_LOOKUP.get(
        normalized
    )


# ============================================================
# RAW CV LINES
# ============================================================

def _get_raw_lines(
    extracted_text: str,
) -> list[str]:
    """
    Preserve the original CV line structure.

    This is critical because PDF extraction already gives us
    useful line boundaries. We should not collapse them before
    parsing sections.
    """

    if not extracted_text:
        return []

    lines = []

    for raw_line in str(
        extracted_text
    ).splitlines():

        line = raw_line.strip()

        if not line:
            continue

        line = line.replace(
            "\u200b",
            "",
        )

        line = line.replace(
            "\u2060",
            "",
        )

        line = line.replace(
            "\ufeff",
            "",
        )

        line = line.strip()

        if line:
            lines.append(
                line
            )

    return lines


def _extract_basic_sections(
    extracted_text: str,
) -> dict[str, list[str]]:
    """
    Split the original extracted CV text into logical sections.

    IMPORTANT:
    This function works from raw lines and therefore preserves
    project/experience/certification boundaries.
    """

    result = {
        "skills": [],
        "experience": [],
        "education": [],
        "projects": [],
        "certifications": [],
        "languages": [],
    }

    lines = _get_raw_lines(
        extracted_text
    )

    current_section: str | None = None

    for line in lines:

        section = _looks_like_heading(
            line
        )

        if section:
            current_section = section
            continue

        if current_section:

            result[
                current_section
            ].append(
                line
            )

    return result


# ============================================================
# BULLET HELPERS
# ============================================================

def _looks_like_bullet(
    line: str,
) -> bool:

    if not line:
        return False

    return bool(
        re.match(
            r"^\s*(?:[-*•●▪◦])\s*",
            line,
        )
    )


def _strip_bullet(
    line: str,
) -> str:

    if not line:
        return ""

    return re.sub(
        r"^\s*(?:[-*•●▪◦])\s*",
        "",
        line,
    ).strip()


# ============================================================
# DATE HELPERS
# ============================================================

def _contains_date(
    line: str,
) -> bool:

    if not line:
        return False

    return bool(
        re.search(
            r"\b(?:19|20)\d{2}\b",
            line,
        )
        or re.search(
            r"\b\d{1,2}/\d{4}\b",
            line,
        )
        or re.search(
            r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|"
            r"Sept|Oct|Nov|Dec)[a-z]*\b",
            line,
            flags=re.IGNORECASE,
        )
    )


def _is_date_range(
    line: str,
) -> bool:

    if not line:
        return False

    text = line.lower()

    has_date = (
        bool(
            re.search(
                r"\b(?:19|20)\d{2}\b",
                text,
            )
        )
        or bool(
            re.search(
                r"\b\d{1,2}/\d{4}\b",
                text,
            )
        )
        or bool(
            re.search(
                r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|"
                r"sep|sept|oct|nov|dec)[a-z]*\b",
                text,
            )
        )
    )

    return (
        has_date
        and bool(
            re.search(
                r"\s-\s",
                text,
            )
        )
    )


# ============================================================
# SENTENCE DETECTION
# ============================================================

ACTION_VERBS = {
    "built",
    "cleaned",
    "analyzed",
    "analysed",
    "generated",
    "designed",
    "modeled",
    "modelled",
    "used",
    "created",
    "developed",
    "implemented",
    "integrated",
    "applied",
    "worked",
    "collaborated",
    "performed",
    "managed",
    "maintained",
    "prepared",
    "presented",
    "conducted",
    "validated",
    "extracted",
    "transformed",
    "visualized",
    "visualised",
    "deployed",
    "tested",
    "configured",
    "supported",
    "handled",
    "organized",
    "organised",
    "improved",
    "enabled",
    "provided",
    "ensured",
    "leveraged",
    "utilized",
    "utilised",
    "monitored",
    "identified",
    "solved",
}


def _first_word(
    line: str,
) -> str:

    text = clean_text(
        _strip_bullet(line)
    )

    if not text:
        return ""

    return (
        text.split(
            " ",
            1,
        )[0]
        .lower()
        .strip(
            ".,:;()"
        )
    )


def _starts_with_action_verb(
    line: str,
) -> bool:

    return (
        _first_word(line)
        in ACTION_VERBS
    )


def _looks_like_sentence(
    line: str,
) -> bool:
    """
    Determine whether a non-bullet line looks like a description
    instead of a title.
    """

    text = clean_text(
        _strip_bullet(line)
    )

    if not text:
        return False

    lower = text.lower()

    if text.endswith("."):
        return True

    if _starts_with_action_verb(
        text
    ):
        return True

    if ";" in text:
        return True

    if "," in text and len(
        text.split()
    ) >= 9:
        return True

    long_sentence_starters = (
        "a ",
        "an ",
        "the ",
        "this ",
        "these ",
        "it ",
        "which ",
        "providing ",
        "using ",
        "with ",
        "to ",
    )

    if (
        lower.startswith(
            long_sentence_starters
        )
        and len(
            text.split()
        ) >= 8
    ):
        return True

    return False


# ============================================================
# PROJECT GROUPING
# ============================================================

def _looks_like_project_title(
    line: str,
) -> bool:

    text = clean_text(
        line
    )

    if not text:
        return False

    if _looks_like_bullet(
        line
    ):
        return False

    if _is_date_range(
        text
    ):
        return False

    if _looks_like_sentence(
        text
    ):
        return False

    word_count = len(
        text.split()
    )

    if word_count < 2:
        return False

    if word_count > 18:
        return False

    lower = text.lower()

    project_markers = (
        "project",
        "dashboard",
        "analysis",
        "analytics",
        "performance",
        "booking",
        "sales",
        "system",
        "application",
        "platform",
        "model",
        "classifier",
    )

    if any(
        marker in lower
        for marker in project_markers
    ):
        return True

    words = text.split()

    capitalized = sum(
        1
        for word in words
        if word
        and word[0].isupper()
    )

    return (
        capitalized
        >= max(
            2,
            int(
                len(words)
                * 0.45
            ),
        )
    )


def _group_project_records(
    lines: list[str],
) -> list[str]:
    """
    Convert project lines into logical project records.
    """

    records = []
    current = []

    for raw_line in lines:

        line = clean_text(
            raw_line
        )

        if not line:
            continue

        if _looks_like_bullet(
            raw_line
        ):
            content = _strip_bullet(
                line
            )

            if current:
                current.append(
                    content
                )
            else:
                current = [
                    content
                ]

            continue

        if _looks_like_project_title(
            line
        ):

            if current:

                joined = _join_record_lines(
                    current
                )

                if joined:
                    records.append(
                        joined
                    )

            current = [
                line
            ]

            continue

        if current:

            current.append(
                line
            )

        else:

            current = [
                line
            ]

    if current:

        joined = _join_record_lines(
            current
        )

        if joined:
            records.append(
                joined
            )

    return _deduplicate_records(
        records
    )


# ============================================================
# EXPERIENCE GROUPING
# ============================================================

EXPERIENCE_ROLE_MARKERS = (
    "intern",
    "developer",
    "engineer",
    "analyst",
    "designer",
    "specialist",
    "manager",
    "consultant",
    "assistant",
    "trainee",
    "coordinator",
    "administrator",
    "architect",
    "scientist",
)


def _looks_like_experience_title(
    line: str,
) -> bool:

    text = clean_text(
        _strip_bullet(line)
    )

    if not text:
        return False

    if _looks_like_bullet(
        line
    ):
        return False

    if _starts_with_action_verb(
        text
    ):
        return False

    if _looks_like_sentence(
        text
    ):
        return False

    word_count = len(
        text.split()
    )

    if word_count > 18:
        return False

    lower = text.lower()

    has_role_marker = any(
        marker in lower
        for marker in EXPERIENCE_ROLE_MARKERS
    )

    has_date = _contains_date(
        text
    )

    return (
        has_role_marker
        or has_date
    )


def _group_experience_records(
    lines: list[str],
) -> list[str]:

    records = []
    current = []

    for raw_line in lines:

        line = clean_text(
            raw_line
        )

        if not line:
            continue

        if _looks_like_bullet(
            raw_line
        ):

            content = _strip_bullet(
                line
            )

            if current:

                current.append(
                    content
                )

            else:

                current = [
                    content
                ]

            continue

        if _looks_like_experience_title(
            line
        ):

            if current:

                joined = _join_record_lines(
                    current
                )

                if joined:
                    records.append(
                        joined
                    )

            current = [
                line
            ]

            continue

        if current:

            current.append(
                line
            )

        else:

            current = [
                line
            ]

    if current:

        joined = _join_record_lines(
            current
        )

        if joined:
            records.append(
                joined
            )

    return _deduplicate_records(
        records
    )


# ============================================================
# CERTIFICATION DETECTION
# ============================================================

CERTIFICATION_EXCLUDED_MARKERS = (
    "intern",
    "internship",
    "employee",
    "professional experience",
    "work experience",
    "worked as",
    "work as",
    "job experience",
    "developer",
    "engineer",
    "analyst",
    "designer",
    "specialist",
    "manager",
    "consultant",
    "administrator",
    "architect",
    "scientist",
)


CERTIFICATION_STRONG_PHRASES = (
    "certificate",
    "certification",
    "course",
    "bootcamp",
    "workshop",
    "training program",
    "professional development",
    "data analysis course",
    "data analytics course",
    "python programming basics",
    "python programming course",
    "machine learning course",
    "deep learning course",
    "artificial intelligence course",
    "artificial intelligence training",
    "web development course",
    "sql course",
    "power bi course",
    "data science course",
    "programming course",
    "networking course",
)


CERTIFICATION_PROVIDER_MARKERS = (
    "route academy",
    "mahara",
    "maharatech",
    "itim ooca",
    "itimooca",
    "iti",
    "nti",
    "cisco",
    "coursera",
    "udemy",
    "linkedin learning",
    "edx",
    "google",
    "microsoft",
    "ibm",
)


def _is_obvious_experience_line(
    line: str,
) -> bool:
    """
    Reject lines that clearly describe a job/internship instead
    of a certification.
    """

    text = clean_text(
        line
    )

    if not text:
        return False

    normalized = text.lower()

    return any(
        marker in normalized
        for marker in CERTIFICATION_EXCLUDED_MARKERS
    )


def _looks_like_certification_title(
    line: str,
) -> bool:
    """
    Strict certification/course title detector.

    Important:
    - "Machine Learning Intern — NTI" => False
    - "Data Analysis Course – Route Academy" => True
    - "Python Programming Basics With MaharaTech - ITIMooca" => True

    Generic words such as "professional", "academy", "basics",
    or "training" are NOT sufficient alone.
    """

    text = clean_text(
        _strip_bullet(line)
    )

    if not text:
        return False

    if _looks_like_bullet(
        line
    ):
        return False

    if _starts_with_action_verb(
        text
    ):
        return False

    if _looks_like_sentence(
        text
    ):
        return False

    if _is_obvious_experience_line(
        text
    ):
        return False

    if _is_date_range(
        text
    ):
        return False

    word_count = len(
        text.split()
    )

    if word_count < 2:
        return False

    if word_count > 20:
        return False

    normalized = text.lower()

    # --------------------------------------------------------
    # Strong explicit course/certificate wording.
    # --------------------------------------------------------

    for phrase in CERTIFICATION_STRONG_PHRASES:

        if phrase in normalized:

            # "analyst course" is still fine,
            # because the decisive word is course.
            return True

    # --------------------------------------------------------
    # Provider + learning wording.
    # --------------------------------------------------------

    has_provider = any(
        provider in normalized
        for provider in CERTIFICATION_PROVIDER_MARKERS
    )

    has_learning_marker = any(
        marker in normalized
        for marker in (
            "course",
            "training",
            "bootcamp",
            "workshop",
            "program",
            "basics",
        )
    )

    if (
        has_provider
        and has_learning_marker
    ):
        return True

    # --------------------------------------------------------
    # Special case:
    #
    # "Python Programming Basics With MaharaTech - ITIMooca"
    #
    # It has "basics" and a known training provider, even though
    # the word "course" does not appear.
    # --------------------------------------------------------

    if (
        "programming basics" in normalized
        and has_provider
    ):
        return True

    return False


def _group_certification_records(
    lines: list[str],
) -> list[str]:
    """
    Group actual certifications/courses.

    Output remains a list of strings because the existing
    canonical profile and downstream Candidate Intelligence
    expect certifications in this form.
    """

    if not lines:
        return []

    records = []
    current = []

    for raw_line in lines:

        line = clean_text(
            raw_line
        )

        if not line:
            continue

        # ----------------------------------------------------
        # A job/internship inside the Certificates section
        # should never become a certification.
        # ----------------------------------------------------

        if _is_obvious_experience_line(
            line
        ):

            if current:

                joined = _join_record_lines(
                    current
                )

                if joined:
                    records.append(
                        joined
                    )

            current = []
            continue

        # ----------------------------------------------------
        # Bullet belongs to the active certification.
        # ----------------------------------------------------

        if _looks_like_bullet(
            raw_line
        ):

            content = _strip_bullet(
                line
            )

            if current and content:
                current.append(
                    content
                )

            continue

        # ----------------------------------------------------
        # Strong new certification title.
        # ----------------------------------------------------

        if _looks_like_certification_title(
            line
        ):

            if current:

                joined = _join_record_lines(
                    current
                )

                if joined:
                    records.append(
                        joined
                    )

            current = [
                line
            ]

            continue

        # ----------------------------------------------------
        # Wrapped line.
        # ----------------------------------------------------

        if current:
            current.append(
                line
            )

    # --------------------------------------------------------
    # Flush final certification.
    # --------------------------------------------------------

    if current:

        joined = _join_record_lines(
            current
        )

        if joined:
            records.append(
                joined
            )

    # --------------------------------------------------------
    # Final strict filtering.
    # --------------------------------------------------------

    filtered = []

    for record in records:

        normalized = clean_text(
            record
        ).lower()

        if not normalized:
            continue

        if _is_obvious_experience_line(
            normalized
        ):
            continue

        if normalize_key(
            record
        ) in {
            "certificates",
            "certifications",
            "training",
            "courses",
            "professional development",
            "certificates and training",
        }:
            continue

        filtered.append(
            clean_text(record)
        )

    return _deduplicate_records(
        filtered
    )


# ============================================================
# EDUCATION GROUPING
# ============================================================

EDUCATION_MARKERS = (
    "university",
    "college",
    "bachelor",
    "master",
    "phd",
    "faculty",
    "institute",
    "degree",
    "major",
)


def _looks_like_education_title(
    line: str,
) -> bool:

    text = clean_text(
        _strip_bullet(line)
    )

    if not text:
        return False

    if _looks_like_bullet(
        line
    ):
        return False

    if _looks_like_sentence(
        text
    ):
        return False

    word_count = len(
        text.split()
    )

    if word_count > 20:
        return False

    lower = text.lower()

    return (
        any(
            marker in lower
            for marker in EDUCATION_MARKERS
        )
        or _contains_date(
            text
        )
    )


def _group_education_records(
    lines: list[str],
) -> list[str]:
    """
    Group education entries.

    Date/location/major lines remain part of the same education
    record rather than becoming separate records.
    """

    records = []
    current = []

    for raw_line in lines:

        line = clean_text(
            raw_line
        )

        if not line:
            continue

        if _looks_like_bullet(
            raw_line
        ):

            content = _strip_bullet(
                line
            )

            if current:

                current.append(
                    content
                )

            else:

                current = [
                    content
                ]

            continue

        if not current:

            current = [
                line
            ]

            continue

        if (
            _looks_like_education_title(
                line
            )
            and not _is_date_range(
                line
            )
        ):

            lower = line.lower()

            if (
                "major" in lower
                or "degree" in lower
            ):

                current.append(
                    line
                )

                continue

            if (
                "university" in lower
                or "college" in lower
                or "bachelor" in lower
                or "master" in lower
            ):

                joined = _join_record_lines(
                    current
                )

                if joined:
                    records.append(
                        joined
                    )

                current = [
                    line
                ]

                continue

        current.append(
            line
        )

    if current:

        joined = _join_record_lines(
            current
        )

        if joined:
            records.append(
                joined
            )

    return _deduplicate_records(
        records
    )


# ============================================================
# GLOBAL EXPERIENCE RECOVERY
# ============================================================

def _extract_experience_from_all_text(
    extracted_text: str,
) -> list[str]:
    """
    Recover obvious job-role records from the full CV text.

    This is used only when the Professional Experience section
    fails to produce a record.
    """

    lines = _get_raw_lines(
        extracted_text
    )

    records = []

    for index, line in enumerate(lines):

        if _looks_like_heading(
            line
        ):
            continue

        text = clean_text(
            _strip_bullet(line)
        )

        if not text:
            continue

        if _looks_like_bullet(
            line
        ):
            continue

        if _starts_with_action_verb(
            text
        ):
            continue

        lower = text.lower()

        has_role = any(
            marker in lower
            for marker in EXPERIENCE_ROLE_MARKERS
        )

        if not has_role:
            continue

        if len(
            text.split()
        ) > 16:
            continue

        record = [
            text
        ]

        for next_line in lines[
            index + 1:
            index + 6
        ]:

            if _looks_like_heading(
                next_line
            ):
                break

            if (
                _looks_like_experience_title(
                    next_line
                )
                and not _looks_like_bullet(
                    next_line
                )
            ):
                break

            record.append(
                _strip_bullet(
                    clean_text(
                        next_line
                    )
                )
            )

        records.append(
            _join_record_lines(
                record
            )
        )

    return _deduplicate_records(
        records
    )


# ============================================================
# GLOBAL CERTIFICATION RECOVERY
# ============================================================

def _extract_certifications_from_all_text(
    extracted_text: str,
) -> list[str]:
    """
    Recover strong certification/course titles from the complete
    CV text.

    This is intentionally conservative so that global recovery
    does not turn jobs, projects, skills, or random text into
    certifications.

    Important supported examples:

        Data Analysis Course – Route Academy

        Python Programming Basics With MaharaTech - ITIMooca

    Important rejection:

        Machine Learning Intern — NTI
    """

    lines = _get_raw_lines(
        extracted_text
    )

    records = []

    for line in lines:

        # Never use section headers as records.
        if _looks_like_heading(
            line
        ):
            continue

        # Never use bullet descriptions as standalone certificates.
        if _looks_like_bullet(
            line
        ):
            continue

        text = clean_text(
            _strip_bullet(line)
        )

        if not text:
            continue

        if _looks_like_certification_title(
            text
        ):
            records.append(
                text
            )

    return _deduplicate_records(
        records
    )


# ============================================================
# SUMMARY
# ============================================================

def _extract_summary_from_text(
    extracted_text: str,
) -> str:

    lines = _get_raw_lines(
        extracted_text
    )

    if not lines:
        return ""

    summary_aliases = {
        "summary",
        "profile",
        "professional summary",
        "objective",
        "career objective",
        "about",
        "about me",
    }

    normalized_aliases = {
        _normalize_heading(alias)
        for alias in summary_aliases
    }

    result = []
    in_summary = False

    for line in lines:

        normalized = _normalize_heading(
            line
        )

        if normalized in normalized_aliases:

            in_summary = True
            continue

        if in_summary:

            if _looks_like_heading(
                line
            ):
                break

            result.append(
                line
            )

    return clean_text(
        " ".join(
            result
        )
    )


# ============================================================
# TARGET ROLE
# ============================================================

def _extract_target_role_from_text(
    extracted_text: str,
) -> str:

    lines = _get_raw_lines(
        extracted_text
    )

    labels = {
        "target role",
        "desired role",
        "career goal",
        "job title",
        "headline",
    }

    normalized_labels = {
        normalize_key(label)
        for label in labels
    }

    for line in lines[:40]:

        normalized_line = normalize_key(
            line
        )

        for label in normalized_labels:

            if normalized_line.startswith(
                f"{label}:"
            ):

                return clean_text(
                    line[
                        len(label) + 1:
                    ]
                )

    # Conservative fallback:
    # The second line of the provided CV is "Junior Data Analyst".
    if len(lines) >= 2:

        candidate = clean_text(
            lines[1]
        )

        lower = candidate.lower()

        if any(
            marker in lower
            for marker in (
                "analyst",
                "developer",
                "engineer",
                "designer",
                "scientist",
                "specialist",
                "manager",
            )
        ):

            return candidate

    return ""


# ============================================================
# RECORD HELPERS
# ============================================================

def _join_record_lines(
    lines: list[str],
) -> str:

    cleaned = []

    for line in lines:

        value = clean_text(
            _strip_bullet(line)
        )

        if value:
            cleaned.append(
                value
            )

    return clean_text(
        " ".join(
            cleaned
        )
    )


def _deduplicate_records(
    records: list[str],
) -> list[str]:

    result = []
    seen = set()

    for record in records:

        cleaned = clean_text(
            record
        )

        if not cleaned:
            continue

        key = cleaned.lower()

        if key in seen:
            continue

        seen.add(
            key
        )

        result.append(
            cleaned
        )

    return result


# ============================================================
# MAIN CANONICAL PROFILE
# ============================================================

def build_canonical_candidate_profile(
    parsed_data: Any,
    extracted_text: str = "",
) -> dict:
    """
    Build a stable canonical candidate profile.

    extracted_text is kept with its original line structure
    during section parsing.

    This prevents incorrect counts caused by collapsing the
    entire CV into a single line.

    Certification extraction uses:
        1. Dedicated certification section.
        2. Conservative global recovery.
        3. Structured parser fallback.
    """

    # --------------------------------------------------------
    # Preserve original raw text for parsing.
    # --------------------------------------------------------

    raw_extracted_text = str(
        extracted_text or ""
    )

    cleaned_raw_text = clean_text(
        raw_extracted_text
    )

    profile = {
        "summary": "",
        "target_role": "",
        "skills_raw": [],
        "experience": [],
        "education": [],
        "projects": [],
        "certifications": [],
        "languages": [],
        "raw_text": cleaned_raw_text,
    }

    # --------------------------------------------------------
    # Structured parser data.
    # --------------------------------------------------------

    structured_summary = []
    structured_target_role = []
    structured_sections = {}

    if isinstance(
        parsed_data,
        dict,
    ):

        structured_summary = (
            collect_named_fields(
                parsed_data,
                {
                    "summary",
                    "profile",
                    "professional summary",
                    "professional_summary",
                    "objective",
                    "career objective",
                    "career_objective",
                    "about",
                    "about me",
                },
            )
        )

        structured_target_role = (
            collect_named_fields(
                parsed_data,
                {
                    "target role",
                    "target_role",
                    "desired role",
                    "desired_role",
                    "career goal",
                    "career_goal",
                    "job title",
                    "job_title",
                    "headline",
                },
            )
        )

        for section in (
            "skills",
            "experience",
            "education",
            "projects",
            "certifications",
            "languages",
        ):

            structured_sections[
                section
            ] = collect_section_values(
                parsed_data,
                section,
            )

    # --------------------------------------------------------
    # Parse sections from ORIGINAL line-preserving text.
    # --------------------------------------------------------

    text_sections = _extract_basic_sections(
        raw_extracted_text
    )

    # --------------------------------------------------------
    # Summary.
    # --------------------------------------------------------

    profile["summary"] = clean_text(
        " ".join(
            structured_summary
        )
    )

    if not profile["summary"]:

        profile["summary"] = (
            _extract_summary_from_text(
                raw_extracted_text
            )
        )

    if not profile["summary"]:

        profile["summary"] = clean_text(
            cleaned_raw_text[:2000]
        )

    # --------------------------------------------------------
    # Target role.
    # --------------------------------------------------------

    if structured_target_role:

        profile["target_role"] = clean_text(
            structured_target_role[0]
        )

    else:

        profile["target_role"] = (
            _extract_target_role_from_text(
                raw_extracted_text
            )
        )

    # --------------------------------------------------------
    # Skills.
    # --------------------------------------------------------

    profile["skills_raw"] = (
        _deduplicate_records(
            [
                *structured_sections.get(
                    "skills",
                    [],
                ),
                *text_sections.get(
                    "skills",
                    [],
                ),
            ]
        )
    )

    # --------------------------------------------------------
    # Projects.
    #
    # Raw CV text has priority because parsed_data may contain
    # platform-generated projects unrelated to the uploaded CV.
    # --------------------------------------------------------

    project_lines = text_sections.get(
        "projects",
        [],
    )

    if project_lines:

        profile["projects"] = (
            _group_project_records(
                project_lines
            )
        )

    if not profile["projects"]:

        profile["projects"] = (
            _deduplicate_records(
                structured_sections.get(
                    "projects",
                    [],
                )
            )
        )

    # --------------------------------------------------------
    # Experience.
    # --------------------------------------------------------

    experience_lines = text_sections.get(
        "experience",
        [],
    )

    if experience_lines:

        profile["experience"] = (
            _group_experience_records(
                experience_lines
            )
        )

    if not profile["experience"]:

        profile["experience"] = (
            _extract_experience_from_all_text(
                raw_extracted_text
            )
        )

    if not profile["experience"]:

        profile["experience"] = (
            _deduplicate_records(
                structured_sections.get(
                    "experience",
                    [],
                )
            )
        )

    # --------------------------------------------------------
    # Education.
    # --------------------------------------------------------

    education_lines = text_sections.get(
        "education",
        [],
    )

    if education_lines:

        profile["education"] = (
            _group_education_records(
                education_lines
            )
        )

    if not profile["education"]:

        profile["education"] = (
            _deduplicate_records(
                structured_sections.get(
                    "education",
                    [],
                )
            )
        )

    # --------------------------------------------------------
    # Certifications.
    #
    # IMPORTANT:
    #
    # We intentionally COMBINE:
    #
    #   dedicated certification section
    #       +
    #   conservative global certification recovery
    #
    # because the user's actual PDF placed:
    #
    #   Data Analysis Course – Route Academy
    #
    # under CERTIFICATES, while:
    #
    #   Python Programming Basics With MaharaTech - ITIMooca
    #
    # appeared under PROFESSIONAL EXPERIENCE because of PDF
    # layout/extraction order.
    #
    # Global recovery is safe because its detector is strict.
    # --------------------------------------------------------

    certification_lines = (
        text_sections.get(
            "certifications",
            [],
        )
    )

    section_certifications = []

    if certification_lines:

        section_certifications = (
            _group_certification_records(
                certification_lines
            )
        )

    global_certifications = (
        _extract_certifications_from_all_text(
            raw_extracted_text
        )
    )

    profile["certifications"] = (
        _deduplicate_records(
            [
                *section_certifications,
                *global_certifications,
            ]
        )
    )

    # --------------------------------------------------------
    # Structured parser fallback.
    #
    # Only use it if raw extraction did not identify anything.
    # --------------------------------------------------------

    if not profile["certifications"]:

        profile["certifications"] = (
            _deduplicate_records(
                structured_sections.get(
                    "certifications",
                    [],
                )
            )
        )

    # --------------------------------------------------------
    # FINAL CERTIFICATION SAFETY FILTER
    # --------------------------------------------------------

    certification_filtered = []

    for certification in (
        profile["certifications"]
    ):

        normalized = clean_text(
            certification
        ).lower()

        if not normalized:
            continue

        # Reject obvious work experience.
        if any(
            marker in normalized
            for marker in CERTIFICATION_EXCLUDED_MARKERS
        ):
            continue

        # Reject section names.
        if normalize_key(
            certification
        ) in {
            "certificates",
            "certifications",
            "training",
            "courses",
            "professional development",
            "certificates and training",
        }:
            continue

        # Keep only records that still pass our strict detector.
        if not _looks_like_certification_title(
            certification
        ):
            continue

        certification_filtered.append(
            certification
        )

    profile["certifications"] = (
        _deduplicate_records(
            certification_filtered
        )
    )

    # --------------------------------------------------------
    # Languages.
    # --------------------------------------------------------

    language_lines = text_sections.get(
        "languages",
        [],
    )

    if language_lines:

        profile["languages"] = (
            _deduplicate_records(
                language_lines
            )
        )

    if not profile["languages"]:

        profile["languages"] = (
            _deduplicate_records(
                structured_sections.get(
                    "languages",
                    [],
                )
            )
        )

    # --------------------------------------------------------
    # Final normalization.
    #
    # All canonical professional sections remain lists of strings.
    # --------------------------------------------------------

    for key in (
        "skills_raw",
        "experience",
        "education",
        "projects",
        "certifications",
        "languages",
    ):

        profile[key] = (
            _deduplicate_records(
                profile.get(
                    key,
                    [],
                )
            )
        )

    return profile