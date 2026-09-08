from __future__ import annotations

import re
from typing import Any


REQUIRED_PATTERNS = (
    "required",
    "must have",
    "must-have",
    "must be",
    "you must",
    "mandatory",
    "essential",
    "required skills",
    "required experience",
    "minimum requirement",
    "minimum requirements",
)

IMPORTANT_PATTERNS = (
    "strong knowledge",
    "strong understanding",
    "proficient",
    "proficiency",
    "solid experience",
    "hands-on experience",
    "experience with",
    "experience in",
    "advanced",
    "preferred experience",
)

PREFERRED_PATTERNS = (
    "preferred",
    "nice to have",
    "nice-to-have",
    "bonus",
    "plus",
    "desirable",
    "preferred qualifications",
)

ROLE_TITLE_PATTERNS = (
    "title",
    "job title",
    "role",
    "position",
    "position title",
)


def clean_text(value: Any) -> str:
    if value is None:
        return ""

    text = str(value)

    text = re.sub(
        r"\r\n?",
        "\n",
        text,
    )

    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    return text.strip()


def normalize_search_text(
    value: Any,
) -> str:
    text = clean_text(value).lower()

    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    return text.strip()


def extract_job_title(
    job_description: str,
) -> str:
    """
    Tries to identify the job title from common JD formats.

    Supported examples:
        Job Title: Data Analyst
        Position: Frontend Developer
        Role - Cybersecurity Analyst
    """

    text = clean_text(
        job_description
    )

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        normalized = line.lower()

        for pattern in ROLE_TITLE_PATTERNS:
            prefix = f"{pattern}:"

            if normalized.startswith(
                prefix
            ):
                title = line[
                    len(prefix):
                ].strip()

                if title:
                    return title

        for pattern in ROLE_TITLE_PATTERNS:
            prefix = f"{pattern} -"

            if normalized.startswith(
                prefix
            ):
                title = line[
                    len(prefix):
                ].strip()

                if title:
                    return title

    # Fallback:
    # use the first short meaningful line.
    for line in text.splitlines():
        candidate = line.strip()

        if (
            candidate
            and len(candidate) <= 100
            and not candidate.endswith(".")
        ):
            return candidate

    return ""


def classify_context(
    context: str,
) -> str:
    """
    Classify skill importance using nearby JD language.
    """

    normalized = normalize_search_text(
        context
    )

    if any(
        pattern in normalized
        for pattern in REQUIRED_PATTERNS
    ):
        return "required"

    if any(
        pattern in normalized
        for pattern in PREFERRED_PATTERNS
    ):
        return "preferred"

    if any(
        pattern in normalized
        for pattern in IMPORTANT_PATTERNS
    ):
        return "important"

    return "important"


def build_skill_context(
    text: str,
    start: int,
    end: int,
    window: int = 180,
) -> str:
    context_start = max(
        0,
        start - window,
    )

    context_end = min(
        len(text),
        end + window,
    )

    return text[
        context_start:context_end
    ]


def extract_job_sections(
    job_description: str,
) -> dict:
    """
    Splits a JD into broad semantic sections.

    This is intentionally lightweight and parser-independent.
    """

    sections = {
        "title": "",
        "summary": "",
        "responsibilities": [],
        "requirements": [],
        "preferred": [],
        "other": [],
    }

    text = clean_text(
        job_description
    )

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    current_section = "other"

    section_aliases = {
        "responsibilities": (
            "responsibilities",
            "what you'll do",
            "what you will do",
            "duties",
            "key responsibilities",
        ),
        "requirements": (
            "requirements",
            "qualifications",
            "required qualifications",
            "required skills",
            "what we're looking for",
            "what we are looking for",
        ),
        "preferred": (
            "preferred",
            "preferred qualifications",
            "nice to have",
            "bonus",
            "desirable",
        ),
    }

    for line in lines:
        normalized = line.lower().strip(
            ":"
        )

        matched_section = None

        for section, aliases in section_aliases.items():
            if normalized in aliases:
                matched_section = section
                break

        if matched_section:
            current_section = matched_section
            continue

        if not sections["title"]:
            possible_title = line

            if (
                len(possible_title) <= 100
                and not possible_title.endswith(".")
            ):
                sections["title"] = (
                    possible_title
                )
                continue

        if current_section == "responsibilities":
            sections[
                "responsibilities"
            ].append(line)

        elif current_section == "requirements":
            sections[
                "requirements"
            ].append(line)

        elif current_section == "preferred":
            sections[
                "preferred"
            ].append(line)

        else:
            sections["other"].append(
                line
            )

    extracted_title = extract_job_title(
        text
    )

    if extracted_title:
        sections["title"] = (
            extracted_title
        )

    sections["summary"] = " ".join(
        sections["other"]
    )[:1500]

    return sections


def infer_skill_importance(
    job_description: str,
    skill_alias: str,
) -> str:
    """
    Looks around a matched skill to infer importance.
    """

    text = normalize_search_text(
        job_description
    )

    alias = normalize_search_text(
        skill_alias
    )

    if not alias:
        return "important"

    index = text.find(alias)

    if index == -1:
        return "important"

    context = build_skill_context(
        text=text,
        start=index,
        end=index + len(alias),
    )

    return classify_context(
        context
    )