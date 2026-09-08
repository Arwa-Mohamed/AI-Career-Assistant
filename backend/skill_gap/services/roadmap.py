SKILL_ROADMAPS = {
    "python": {
        "priority": "high",
        "steps": [
            "Python Fundamentals",
            "Object-Oriented Programming",
            "Advanced Python",
            "Build a Python Project",
        ],
    },

    "django": {
        "priority": "high",
        "steps": [
            "Django Fundamentals",
            "Models and ORM",
            "Django REST Framework",
            "Authentication and JWT",
            "Build a Django API",
        ],
    },

    "postgresql": {
        "priority": "high",
        "steps": [
            "SQL Fundamentals",
            "Database Design",
            "Joins and Aggregations",
            "Indexes",
            "PostgreSQL Projects",
        ],
    },

    "docker": {
        "priority": "medium",
        "steps": [
            "Docker Fundamentals",
            "Images and Containers",
            "Docker Compose",
            "Containerizing Django",
            "Deployment with Docker",
        ],
    },

    "aws": {
        "priority": "medium",
        "steps": [
            "AWS Fundamentals",
            "EC2",
            "S3",
            "RDS",
            "Basic Cloud Deployment",
        ],
    },

    "machine learning": {
        "priority": "high",
        "steps": [
            "Python for ML",
            "NumPy and Pandas",
            "Scikit-learn",
            "Model Evaluation",
            "Build an ML Project",
        ],
    },
}

def generate_learning_roadmap(missing_skills):
    roadmap = []

    for skill in missing_skills:
        key = skill.lower().strip()

        data = SKILL_ROADMAPS.get(
            key,
            {
                "priority": "medium",
                "steps": [
                    f"Learn {skill} fundamentals",
                    f"Practice {skill}",
                    f"Build a project using {skill}",
                ],
            },
        )

        roadmap.append({
            "skill": skill,
            "priority": data["priority"],
            "steps": data["steps"],
        })

    priority_order = {
        "high": 0,
        "medium": 1,
        "low": 2,
    }

    roadmap.sort(
        key=lambda item: priority_order.get(
            item["priority"],
            1,
        )
    )

    return roadmap