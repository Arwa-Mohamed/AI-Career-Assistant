import re


SECTION_ALIASES = {
    "summary": ["summary", "professional summary", "profile", "objective", "career objective"],
    "experience": ["experience", "work experience", "professional experience", "employment", "work history"],
    "education": ["education", "academic background", "academic history"],
    "skills": ["skills", "technical skills", "core skills", "competencies", "technical competencies"],
    "projects": ["projects", "academic projects", "personal projects", "selected projects"],
    "certifications": ["certifications", "certificates", "licenses"],
    "training": ["training", "courses", "professional training"],
}


EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE_RE = re.compile(r"(?:\+?\d[\d\s().-]{7,}\d)")
LINKEDIN_RE = re.compile(r"linkedin\.com(?:/in/[^\s]+)?", re.I)
GITHUB_RE = re.compile(r"github\.com(?:/[^\s]+)?", re.I)
SPECIAL_CHAR_RE = re.compile(r"[^\w\s.,:;()/%+#&@'\"\-]", re.UNICODE)
REPEATED_PUNCT_RE = re.compile(r"[!?.,]{4,}")


def _clean_text(text):
    if not text:
        return ""
    text = str(text).replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _contains_alias(text_lower, alias):
    return re.search(rf"(?<!\w){re.escape(alias.lower())}(?!\w)", text_lower) is not None


def _section_detection(text):
    lower = text.lower()
    result = {}
    for section, aliases in SECTION_ALIASES.items():
        matched = next((alias for alias in aliases if _contains_alias(lower, alias)), None)
        result[section] = {"present": matched is not None, "matched_heading": matched}
    return result


def _contact_score(text):
    detected = {
        "email": bool(EMAIL_RE.search(text)),
        "phone": bool(PHONE_RE.search(text)),
        "linkedin": bool(LINKEDIN_RE.search(text)),
        "github": bool(GITHUB_RE.search(text)),
    }
    score = (40 if detected["email"] else 0) + (30 if detected["phone"] else 0) + (20 if detected["linkedin"] else 0) + (10 if detected["github"] else 0)
    return {"score": score, "detected": detected}


def _section_score(sections):
    weights = {"summary": 10, "experience": 25, "education": 15, "skills": 20, "projects": 15, "certifications": 5, "training": 5}
    earned = sum(weight for name, weight in weights.items() if sections.get(name, {}).get("present"))
    return round((earned / sum(weights.values())) * 100)


def _skill_keyword_score(text, parsed_data):
    skills = parsed_data.get("skills", []) if isinstance(parsed_data, dict) else []
    names = []
    for item in skills if isinstance(skills, list) else []:
        if isinstance(item, str) and item.strip():
            names.append(item.strip())
        elif isinstance(item, dict):
            value = item.get("name") or item.get("skill")
            if value:
                names.append(str(value).strip())

    unique = []
    seen = set()
    for name in names:
        key = name.casefold()
        if key and key not in seen:
            seen.add(key)
            unique.append(name)

    matched = []
    for skill in unique:
        if re.search(rf"(?<!\w){re.escape(skill.lower())}(?!\w)", text.lower()):
            matched.append(skill)

    score = 50 if not unique else round(len(matched) / len(unique) * 100)
    return {
        "score": max(0, min(score, 100)),
        "skills_checked": len(unique),
        "matched_skills": matched,
        "unmatched_skills": [skill for skill in unique if skill not in matched],
    }


def _readability_score(text):
    words = re.findall(r"\b[\w+#./-]+\b", text, re.UNICODE)
    sentences = [s for s in re.split(r"[.!?]+", text) if s.strip()]
    count = len(words)
    sentence_count = len(sentences)
    avg = round(count / sentence_count, 1) if sentence_count else 0
    score = 100
    if count < 100:
        score -= 20
    if avg > 35:
        score -= 15
    if avg > 50:
        score -= 15
    return {"score": max(0, min(score, 100)), "word_count": count, "sentence_count": sentence_count, "avg_words_per_sentence": avg}


def _formatting_score(text):
    risks = []
    special_count = len(SPECIAL_CHAR_RE.findall(text))
    repeated_count = len(REPEATED_PUNCT_RE.findall(text))

    if special_count > 15:
        risks.append({"type": "special_characters", "count": special_count})
    if repeated_count:
        risks.append({"type": "repeated_punctuation", "count": repeated_count})

    score = 100 - min(25, max(0, special_count - 15)) - min(20, repeated_count * 5)
    return {"score": max(0, min(score, 100)), "risks": risks}


def _bullet_score(text):
    patterns = [r"(?m)^\s*[-•▪●◦*]\s+", r"(?m)^\s*\d+[.)]\s+"]
    count = sum(len(re.findall(pattern, text)) for pattern in patterns)
    score = 100 if count >= 8 else 90 if count >= 5 else 75 if count >= 3 else 60 if count else 40
    return {"score": score, "bullet_count": count}


def _extractability_score(text):
    if not text:
        return {"score": 0, "status": "poor", "issues": ["No extractable CV text was detected."]}

    issues = []
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(text) < 200:
        issues.append("Very little text was extracted from the CV.")
    if len(lines) < 8:
        issues.append("Very few readable lines were extracted.")

    score = 100 - min(40, len(issues) * 20)
    status = "excellent" if score >= 85 else "good" if score >= 70 else "needs_improvement" if score >= 50 else "poor"
    return {"score": score, "status": status, "issues": issues}


def _status(score):
    if score >= 85:
        return "ATS-Friendly"
    if score >= 70:
        return "Mostly ATS-Friendly"
    if score >= 50:
        return "Needs ATS Improvements"
    return "High ATS Risk"


def analyze_ats(parsed_data=None, extracted_text=""):
    parsed_data = parsed_data if isinstance(parsed_data, dict) else {}
    text = _clean_text(extracted_text)

    if not text:
        return {
            "score": 0,
            "status": "High ATS Risk",
            "breakdown": {},
            "sections": {},
            "contact_information": {"score": 0, "detected": {"email": False, "phone": False, "linkedin": False, "github": False}},
            "keyword_analysis": {"score": 0, "skills_checked": 0, "matched_skills": [], "unmatched_skills": []},
            "readability": {"score": 0, "word_count": 0, "sentence_count": 0, "avg_words_per_sentence": 0},
            "formatting": {"score": 0, "risks": []},
            "bullet_structure": {"score": 0, "bullet_count": 0},
            "text_extractability": {"score": 0, "status": "poor", "issues": ["No extractable CV text was detected."]},
            "issues": ["No extractable CV text was detected."],
            "recommendations": ["Upload a text-readable CV in PDF or DOCX format."],
        }

    sections = _section_detection(text)
    contact = _contact_score(text)
    keywords = _skill_keyword_score(text, parsed_data)
    readability = _readability_score(text)
    formatting = _formatting_score(text)
    bullets = _bullet_score(text)
    extractability = _extractability_score(text)
    section_score = _section_score(sections)

    score = round(
        contact["score"] * 0.15
        + section_score * 0.20
        + keywords["score"] * 0.20
        + readability["score"] * 0.10
        + formatting["score"] * 0.10
        + bullets["score"] * 0.05
        + extractability["score"] * 0.20
    )
    score = max(0, min(score, 100))

    issues = []
    recommendations = []

    for field, label in [("email", "email address"), ("phone", "phone number"), ("linkedin", "LinkedIn profile")]:
        if not contact["detected"][field]:
            issues.append(f"{label.capitalize()} was not detected.")
            recommendations.append(f"Add a professional {label}.")

    for section in ["skills", "education"]:
        if not sections[section]["present"]:
            issues.append(f"A standard {section.title()} section was not detected.")

    if not sections["experience"]["present"] and not sections["projects"]["present"]:
        issues.append("Neither Experience nor Projects was clearly detected.")
        recommendations.append("Add a clearly labeled Experience or Projects section.")

    if keywords["score"] < 70:
        recommendations.append("Make relevant skills explicit and consistent with the target role.")

    if readability["score"] < 70:
        recommendations.append("Use shorter, achievement-focused bullet points.")

    for item in extractability["issues"]:
        issues.append(item)
    if extractability["score"] < 70:
        recommendations.append("Use a simpler text-readable layout and avoid complex visual structures.")

    return {
        "score": score,
        "status": _status(score),
        "breakdown": {
            "contact_information": contact["score"],
            "standard_sections": section_score,
            "keyword_coverage": keywords["score"],
            "readability": readability["score"],
            "formatting_safety": formatting["score"],
            "bullet_structure": bullets["score"],
            "text_extractability": extractability["score"],
        },
        "sections": sections,
        "contact_information": contact,
        "keyword_analysis": keywords,
        "readability": readability,
        "formatting": formatting,
        "bullet_structure": bullets,
        "text_extractability": extractability,
        "issues": list(dict.fromkeys(issues)),
        "recommendations": list(dict.fromkeys(recommendations)),
    }
