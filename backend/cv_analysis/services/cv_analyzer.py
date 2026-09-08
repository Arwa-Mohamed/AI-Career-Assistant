def calculate_cv_score(parsed_data, extracted_text):
    """
    Calculate the CV quality score out of 100.

    Score breakdown:
        Contact Information -> 15
        Skills              -> 25
        Content             -> 30
        Sections            -> 30

        Total               -> 100
    """

    if not isinstance(parsed_data, dict):
        parsed_data = {}

    if not isinstance(extracted_text, str):
        extracted_text = ""

    score = 0
    breakdown = {}

    # ========================================================
    # 1. Contact Information - 15 Points
    # ========================================================

    contact_score = 0

    if parsed_data.get("name"):
        contact_score += 5

    if parsed_data.get("email"):
        contact_score += 5

    if parsed_data.get("phone"):
        contact_score += 5

    breakdown["contact_information"] = contact_score
    score += contact_score

    # ========================================================
    # 2. Skills - 25 Points
    # ========================================================

    skills = parsed_data.get("skills", [])

    if not isinstance(skills, list):
        skills = []

    skill_count = len(skills)

    if skill_count >= 15:
        skills_score = 25

    elif skill_count >= 10:
        skills_score = 22

    elif skill_count >= 7:
        skills_score = 18

    elif skill_count >= 4:
        skills_score = 13

    elif skill_count >= 1:
        skills_score = 7

    else:
        skills_score = 0

    breakdown["skills"] = skills_score
    score += skills_score

    # ========================================================
    # 3. Content - 30 Points
    # ========================================================

    text = extracted_text.strip()
    text_length = len(text)

    if text_length >= 4000:
        content_score = 30

    elif text_length >= 3000:
        content_score = 27

    elif text_length >= 2000:
        content_score = 23

    elif text_length >= 1000:
        content_score = 18

    elif text_length >= 500:
        content_score = 12

    elif text_length > 0:
        content_score = 6

    else:
        content_score = 0

    breakdown["content"] = content_score
    score += content_score

    # ========================================================
    # 4. Sections - 30 Points
    # ========================================================

    text_lower = text.lower()

    section_keywords = {
        "education": [
            "education",
            "academic",
            "academic background",
            "academic history",
            "university",
            "college",
            "degree",
            "bachelor",
            "master",
            "phd",
        ],

        "experience": [
            "experience",
            "work experience",
            "professional experience",
            "employment",
            "internship",
            "intern",
            "work history",
        ],

        "projects": [
            "projects",
            "project",
            "academic projects",
            "personal projects",
            "selected projects",
            "portfolio",
        ],

        "certifications": [
            "certification",
            "certifications",
            "certificate",
            "certificates",
            "licenses",
        ],

        "summary": [
            "summary",
            "professional summary",
            "profile",
            "objective",
            "career objective",
            "about me",
        ],

        "skills": [
            "skills",
            "technical skills",
            "core skills",
            "competencies",
            "technical competencies",
        ],
    }

    section_details = {}

    for section, keywords in section_keywords.items():

        found = any(
            keyword in text_lower
            for keyword in keywords
        )

        section_details[section] = found

    # --------------------------------------------------------
    # Section scoring
    # --------------------------------------------------------

    section_score = 0

    if section_details["education"]:
        section_score += 5

    if section_details["experience"]:
        section_score += 5

    if section_details["projects"]:
        section_score += 5

    if section_details["certifications"]:
        section_score += 5

    if section_details["summary"]:
        section_score += 5

    if section_details["skills"]:
        section_score += 5

    breakdown["sections"] = section_score
    score += section_score

    # ========================================================
    # Final Score
    # ========================================================

    score = min(score, 100)

    return {
        "score": score,
        "breakdown": breakdown,
        "sections": section_details,
    }