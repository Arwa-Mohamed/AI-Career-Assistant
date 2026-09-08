def calculate_skill_gap(
    current_skills,
    required_skills,
):
    current = {
        skill.strip().lower()
        for skill in current_skills
    }

    required = {
        skill.strip().lower()
        for skill in required_skills
    }

    matched = sorted(
        current.intersection(required)
    )

    missing = sorted(
        required.difference(current)
    )

    if required:
        gap_score = (
            len(missing) / len(required)
        ) * 100
    else:
        gap_score = 0

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "gap_score": round(gap_score, 2),
    }