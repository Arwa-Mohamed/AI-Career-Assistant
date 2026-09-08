SKILL_ALIASES = {
    "react.js": "React",
    "react js": "React",
    "reactjs": "React",

    "node": "Node.js",
    "nodejs": "Node.js",

    "ml": "Machine Learning",
    "machine learning": "Machine Learning",

    "ai": "Artificial Intelligence",
    "artificial intelligence": "Artificial Intelligence",

    "postgres": "PostgreSQL",

    "sklearn": "scikit-learn",
    "scikit learn": "scikit-learn",

    "js": "JavaScript",
    "javascript": "JavaScript",
}

def normalize_skills(skills):
    normalized = []

    for skill in skills:
        key = skill.strip().lower()

        normalized_skill = SKILL_ALIASES.get(
            key,
            skill,
        )

        normalized.append(normalized_skill)

    return sorted(set(normalized))