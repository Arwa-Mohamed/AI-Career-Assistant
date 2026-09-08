from cvs.utils.parser import COMMON_SKILLS
from cvs.utils.skill_normalizer import normalize_skills


def extract_job_skills(job_description):
    text_lower = job_description.lower()

    found_skills = []

    for skill in COMMON_SKILLS:
        if skill.lower() in text_lower:
            found_skills.append(skill)

    return normalize_skills(found_skills)


def compare_skills(cv_skills, job_skills):
    cv_skills_normalized = {
        skill.lower()
        for skill in normalize_skills(cv_skills)
    }

    job_skills_normalized = {
        skill.lower()
        for skill in normalize_skills(job_skills)
    }

    matched = sorted(
        cv_skills_normalized.intersection(job_skills_normalized)
    )

    missing = sorted(
        job_skills_normalized.difference(cv_skills_normalized)
    )

    if job_skills_normalized:
        skill_score = (
            len(matched) / len(job_skills_normalized)
        ) * 100
    else:
        skill_score = 0

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "skill_match_score": round(skill_score, 2),
    }