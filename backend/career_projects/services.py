from typing import Dict, List, Optional


# =========================================================
# AI CAREER ASSISTANT — CAREER-AWARE PROJECT RECOMMENDATIONS
# =========================================================
# The generator has two modes:
#   1) Job-specific: use missing skills from an analyzed job.
#   2) Career-based: use the detected/target role when no job exists.
#
# Important:
# - Existing skills should not automatically become project gaps.
# - Generic IT projects must never be used as a fallback for a
#   non-IT career such as Data Analyst.
# - Returned projects keep the API shape expected by the frontend.


CAREER_ALIASES = {
    "data analyst": "data_analyst",
    "data analytics": "data_analyst",
    "business intelligence analyst": "data_analyst",
    "bi analyst": "data_analyst",
    "data scientist": "data_scientist",
    "machine learning engineer": "machine_learning",
    "ml engineer": "machine_learning",
    "ai engineer": "ai_engineer",
    "artificial intelligence engineer": "ai_engineer",
    "ai developer": "ai_engineer",
    "backend developer": "backend",
    "backend engineer": "backend",
    "front end developer": "frontend",
    "frontend developer": "frontend",
    "frontend engineer": "frontend",
    "full stack developer": "full_stack",
    "full-stack developer": "full_stack",
    "full stack engineer": "full_stack",
    "software engineer": "software_engineer",
    "software developer": "software_engineer",
    "devops engineer": "devops",
    "cloud engineer": "cloud",
    "cybersecurity analyst": "cybersecurity",
    "cyber security analyst": "cybersecurity",
    "security analyst": "cybersecurity",
    "penetration tester": "cybersecurity",
    "ui ux designer": "ui_ux",
    "ui/ux designer": "ui_ux",
    "ux designer": "ui_ux",
    "ui designer": "ui_ux",
    "product designer": "ui_ux",
    "digital marketing specialist": "digital_marketing",
    "digital marketer": "digital_marketing",
    "marketing analyst": "marketing_analytics",
    "business analyst": "business_analyst",
    "project manager": "project_management",
}


CAREER_TEMPLATES: Dict[str, List[Dict]] = {
    "data_analyst": [
        {
            "title": "Sales Performance Analytics Dashboard",
            "description": (
                "Analyze a realistic sales dataset, build a KPI-driven dashboard, "
                "and turn business data into actionable recommendations."
            ),
            "difficulty": "intermediate",
            "estimated_days": 10,
            "skills": ["SQL", "Power BI", "DAX", "Data Visualization"],
            "required_skills": ["sql", "power bi", "dax", "data visualization"],
            "objectives": [
                "Clean and validate a realistic business dataset",
                "Write analytical SQL queries using joins and aggregations",
                "Build KPI measures and a business dashboard",
                "Create clear data visualizations",
                "Present actionable business insights",
            ],
        },
        {
            "title": "Customer Churn Analysis",
            "description": (
                "Investigate customer behavior, identify churn patterns, "
                "and communicate the factors most associated with customer loss."
            ),
            "difficulty": "intermediate",
            "estimated_days": 10,
            "skills": ["Python", "Pandas", "Statistics", "Data Visualization"],
            "required_skills": ["python", "pandas", "statistics", "data visualization"],
            "objectives": [
                "Clean and explore customer data",
                "Perform exploratory data analysis",
                "Apply descriptive statistics",
                "Visualize churn patterns",
                "Translate findings into business recommendations",
            ],
        },
        {
            "title": "E-commerce Business Intelligence Project",
            "description": (
                "Build an end-to-end analytics solution for an e-commerce dataset "
                "covering sales, customers, products, and business KPIs."
            ),
            "difficulty": "intermediate",
            "estimated_days": 12,
            "skills": ["SQL", "Power BI", "Excel", "Data Analysis"],
            "required_skills": ["sql", "power bi", "excel", "data analysis"],
            "objectives": [
                "Design an analysis-ready data model",
                "Prepare and validate business data",
                "Build reusable analytical queries",
                "Create an executive dashboard",
                "Explain trends and actionable insights",
            ],
        },
        {
            "title": "Marketing Campaign Performance Analysis",
            "description": (
                "Evaluate campaign performance across channels and identify the "
                "segments, campaigns, and channels that drive the best results."
            ),
            "difficulty": "beginner",
            "estimated_days": 7,
            "skills": ["Excel", "SQL", "Data Visualization", "Statistics"],
            "required_skills": ["excel", "sql", "data visualization", "statistics"],
            "objectives": [
                "Clean campaign performance data",
                "Calculate conversion and performance metrics",
                "Compare channels and segments",
                "Build a clear reporting dashboard",
                "Recommend data-driven campaign improvements",
            ],
        },
    ],
    "data_scientist": [
        {
            "title": "Customer Churn Prediction",
            "description": (
                "Build an end-to-end machine learning workflow to predict customer churn "
                "and explain the most important factors behind the predictions."
            ),
            "difficulty": "advanced",
            "estimated_days": 16,
            "skills": ["Python", "Pandas", "Scikit-learn", "Machine Learning"],
            "required_skills": ["python", "pandas", "scikit-learn", "machine learning"],
            "objectives": [
                "Prepare and explore a real dataset",
                "Engineer predictive features",
                "Train and compare multiple models",
                "Evaluate model performance",
                "Communicate model findings and limitations",
            ],
        },
        {
            "title": "Demand Forecasting Analytics",
            "description": (
                "Analyze historical demand and build a forecasting workflow that helps "
                "a business plan inventory and operations."
            ),
            "difficulty": "advanced",
            "estimated_days": 18,
            "skills": ["Python", "Statistics", "Time Series", "Data Visualization"],
            "required_skills": ["python", "statistics", "time series", "data visualization"],
            "objectives": [
                "Prepare time-series data",
                "Explore seasonality and trends",
                "Build forecasting baselines",
                "Evaluate forecasting accuracy",
                "Visualize forecasts for decision-makers",
            ],
        },
        {
            "title": "Recommendation System Prototype",
            "description": (
                "Build a recommendation prototype using real interaction data and "
                "evaluate the quality of the recommendations."
            ),
            "difficulty": "advanced",
            "estimated_days": 18,
            "skills": ["Python", "Machine Learning", "Pandas", "Recommendation Systems"],
            "required_skills": ["python", "machine learning", "pandas", "recommendation systems"],
            "objectives": [
                "Prepare user-item interaction data",
                "Build a recommendation baseline",
                "Train a recommendation approach",
                "Evaluate recommendation quality",
                "Document limitations and next steps",
            ],
        },
    ],
    "machine_learning": [
        {
            "title": "End-to-End Machine Learning Prediction System",
            "description": (
                "Build a production-style machine learning workflow from preprocessing "
                "and training to evaluation and inference."
            ),
            "difficulty": "advanced",
            "estimated_days": 16,
            "skills": ["Python", "Pandas", "Scikit-learn", "Machine Learning"],
            "required_skills": ["python", "pandas", "scikit-learn", "machine learning"],
            "objectives": [
                "Prepare a real-world dataset",
                "Engineer useful features",
                "Train and compare models",
                "Evaluate model performance",
                "Expose a prediction workflow for inference",
            ],
        },
    ],
    "ai_engineer": [
        {
            "title": "AI-Powered Document Intelligence Assistant",
            "description": (
                "Build an AI application that extracts, summarizes, and answers questions "
                "about structured or unstructured documents."
            ),
            "difficulty": "advanced",
            "estimated_days": 16,
            "skills": ["Python", "NLP", "LLM", "Generative AI"],
            "required_skills": ["python", "nlp", "llm", "generative ai"],
            "objectives": [
                "Process real documents",
                "Create an AI-powered retrieval workflow",
                "Design reliable prompts and structured outputs",
                "Evaluate answer quality",
                "Build a usable application interface",
            ],
        },
        {
            "title": "AI Recommendation & Insight Engine",
            "description": (
                "Create an AI service that combines structured user data with intelligent "
                "recommendations and explainable insights."
            ),
            "difficulty": "advanced",
            "estimated_days": 14,
            "skills": ["Python", "Machine Learning", "LLM", "APIs"],
            "required_skills": ["python", "machine learning", "llm", "apis"],
            "objectives": [
                "Prepare structured input data",
                "Combine predictive and generative components",
                "Design explainable recommendations",
                "Evaluate output quality",
                "Expose the solution through an application API",
            ],
        },
    ],
    "backend": [
        {
            "title": "Production-Ready REST API Platform",
            "description": (
                "Build a secure backend service with authentication, relational data, "
                "validation, permissions, testing, and API documentation."
            ),
            "difficulty": "intermediate",
            "estimated_days": 12,
            "skills": ["Python", "Django", "REST API", "PostgreSQL"],
            "required_skills": ["python", "django", "rest api", "postgresql"],
            "objectives": [
                "Design REST endpoints",
                "Implement authentication and permissions",
                "Model relational data",
                "Validate requests and handle errors",
                "Document and test the API",
            ],
        },
    ],
    "frontend": [
        {
            "title": "Data-Driven React Dashboard",
            "description": (
                "Build a polished responsive dashboard that consumes real APIs and "
                "presents useful data through reusable components."
            ),
            "difficulty": "intermediate",
            "estimated_days": 10,
            "skills": ["React", "JavaScript", "REST API", "Data Visualization"],
            "required_skills": ["react", "javascript", "rest api", "data visualization"],
            "objectives": [
                "Create reusable React components",
                "Connect the UI to real APIs",
                "Handle loading and error states",
                "Build responsive visualizations",
                "Deliver a polished user experience",
            ],
        },
    ],
    "full_stack": [
        {
            "title": "Production-Style Full-Stack SaaS Application",
            "description": (
                "Build a complete SaaS-style application with a modern frontend, secure "
                "backend API, relational database, authentication, and deployment."
            ),
            "difficulty": "advanced",
            "estimated_days": 18,
            "skills": ["React", "Django", "PostgreSQL", "REST API"],
            "required_skills": ["react", "django", "postgresql", "rest api"],
            "objectives": [
                "Design frontend and backend architecture",
                "Implement authentication and permissions",
                "Build a relational data model",
                "Integrate frontend and backend APIs",
                "Deploy and document the application",
            ],
        },
    ],
    "software_engineer": [
        {
            "title": "Production-Quality Software Engineering Project",
            "description": (
                "Build a complete software product with clean architecture, testing, "
                "documentation, version control, and deployment."
            ),
            "difficulty": "intermediate",
            "estimated_days": 14,
            "skills": ["Python", "Git", "Testing", "Software Engineering"],
            "required_skills": ["python", "git", "testing", "software engineering"],
            "objectives": [
                "Design maintainable application architecture",
                "Implement core functionality cleanly",
                "Write automated tests",
                "Use professional Git practices",
                "Document and deploy the project",
            ],
        },
    ],
    "devops": [
        {
            "title": "Containerized CI/CD Deployment Pipeline",
            "description": (
                "Containerize an application and automate testing, builds, and deployment "
                "through a repeatable CI/CD workflow."
            ),
            "difficulty": "advanced",
            "estimated_days": 12,
            "skills": ["Docker", "CI/CD", "Git", "Cloud"],
            "required_skills": ["docker", "ci/cd", "git", "cloud"],
            "objectives": [
                "Containerize the application",
                "Create a CI workflow",
                "Automate testing and builds",
                "Configure deployment stages",
                "Document operations and rollback steps",
            ],
        },
    ],
    "cloud": [
        {
            "title": "Cloud-Deployed Web Application",
            "description": (
                "Deploy a production-style web application with environment configuration, "
                "logging, monitoring, and basic cloud security practices."
            ),
            "difficulty": "intermediate",
            "estimated_days": 12,
            "skills": ["Cloud", "Docker", "Git", "Deployment"],
            "required_skills": ["cloud", "docker", "git", "deployment"],
            "objectives": [
                "Configure production environments",
                "Containerize application services",
                "Deploy the application to a cloud platform",
                "Configure basic monitoring and logging",
                "Document deployment and recovery steps",
            ],
        },
    ],
    "cybersecurity": [
        {
            "title": "Security Monitoring & Incident Analysis Lab",
            "description": (
                "Build a practical security monitoring lab that analyzes logs, identifies "
                "suspicious activity, and documents incident-response findings."
            ),
            "difficulty": "intermediate",
            "estimated_days": 12,
            "skills": ["Cybersecurity", "Linux", "Networking", "SIEM"],
            "required_skills": ["cybersecurity", "linux", "networking", "siem"],
            "objectives": [
                "Collect and normalize security logs",
                "Identify suspicious patterns",
                "Create useful security alerts",
                "Investigate a simulated incident",
                "Document findings and remediation steps",
            ],
        },
        {
            "title": "Web Application Security Assessment",
            "description": (
                "Perform a controlled security assessment on a deliberately vulnerable "
                "web application and document the findings and remediation."
            ),
            "difficulty": "advanced",
            "estimated_days": 14,
            "skills": ["Cybersecurity", "Web Security", "OWASP", "Networking"],
            "required_skills": ["cybersecurity", "web security", "owasp", "networking"],
            "objectives": [
                "Map the application attack surface",
                "Identify common web vulnerabilities in a safe lab",
                "Document evidence and severity",
                "Recommend remediation steps",
                "Create a professional security report",
            ],
        },
    ],
    "ui_ux": [
        {
            "title": "End-to-End Product Design Case Study",
            "description": (
                "Design a complete digital product from user research and flows to a "
                "high-fidelity responsive prototype and usability evaluation."
            ),
            "difficulty": "intermediate",
            "estimated_days": 12,
            "skills": ["UI/UX", "Figma", "User Research", "Prototyping"],
            "required_skills": ["ui/ux", "figma", "user research", "prototyping"],
            "objectives": [
                "Define user problems and personas",
                "Create user flows and wireframes",
                "Design a consistent visual system",
                "Build a high-fidelity prototype",
                "Evaluate the design with usability feedback",
            ],
        },
    ],
    "digital_marketing": [
        {
            "title": "Data-Driven Digital Marketing Campaign",
            "description": (
                "Plan, measure, and optimize a realistic digital marketing campaign using "
                "audience segmentation, content strategy, and performance analytics."
            ),
            "difficulty": "intermediate",
            "estimated_days": 10,
            "skills": ["Digital Marketing", "Analytics", "SEO", "Content Strategy"],
            "required_skills": ["digital marketing", "analytics", "seo", "content strategy"],
            "objectives": [
                "Define target audiences",
                "Build a campaign strategy",
                "Design measurable KPIs",
                "Analyze campaign performance",
                "Recommend optimization actions",
            ],
        },
    ],
    "marketing_analytics": [
        {
            "title": "Marketing Performance Analytics Dashboard",
            "description": (
                "Analyze marketing channels and campaigns to identify performance drivers, "
                "conversion patterns, and optimization opportunities."
            ),
            "difficulty": "intermediate",
            "estimated_days": 10,
            "skills": ["SQL", "Marketing Analytics", "Excel", "Data Visualization"],
            "required_skills": ["sql", "marketing analytics", "excel", "data visualization"],
            "objectives": [
                "Prepare campaign performance data",
                "Define marketing KPIs",
                "Analyze conversion funnels",
                "Visualize channel performance",
                "Recommend data-driven optimizations",
            ],
        },
    ],
    "business_analyst": [
        {
            "title": "Business Process Improvement Case Study",
            "description": (
                "Analyze a realistic business process, identify inefficiencies, and propose "
                "a data-backed improved workflow with clear requirements."
            ),
            "difficulty": "intermediate",
            "estimated_days": 10,
            "skills": ["Business Analysis", "Process Mapping", "SQL", "Requirements"],
            "required_skills": ["business analysis", "process mapping", "sql", "requirements"],
            "objectives": [
                "Map the current business process",
                "Identify bottlenecks and root causes",
                "Gather and document requirements",
                "Design the improved workflow",
                "Define measurable success criteria",
            ],
        },
    ],
    "project_management": [
        {
            "title": "Agile Product Delivery Case Study",
            "description": (
                "Create and manage a realistic product delivery plan including scope, "
                "backlog, milestones, risks, and stakeholder communication."
            ),
            "difficulty": "intermediate",
            "estimated_days": 8,
            "skills": ["Project Management", "Agile", "Scrum", "Risk Management"],
            "required_skills": ["project management", "agile", "scrum", "risk management"],
            "objectives": [
                "Define project scope and outcomes",
                "Create an actionable backlog",
                "Plan milestones and dependencies",
                "Track risks and blockers",
                "Document stakeholder communication",
            ],
        },
    ],
}


# Keep the legacy skill templates for backwards compatibility with callers that
# may still rely on skill-first recommendations.
SKILL_TEMPLATES: Dict[str, Dict] = {
    "python": {
        "title": "Python Automation & API Project",
        "description": "Build a practical Python application that solves a real problem and exposes reusable functionality.",
        "difficulty": "beginner",
        "estimated_days": 7,
        "objectives": [
            "Create a clean Python project structure",
            "Implement reusable functions and classes",
            "Handle errors and validate input",
            "Write a README and basic tests",
        ],
    },
    "django": {
        "title": "Production-Style Django REST API",
        "description": "Build a secure REST API with Django REST Framework, authentication, validation, and database integration.",
        "difficulty": "intermediate",
        "estimated_days": 10,
        "objectives": [
            "Design REST API endpoints",
            "Implement authentication and permissions",
            "Connect PostgreSQL",
            "Add validation",
            "Document the API",
        ],
    },
    "react": {
        "title": "Modern React Dashboard",
        "description": "Build a responsive React dashboard connected to a real backend API.",
        "difficulty": "intermediate",
        "estimated_days": 10,
        "objectives": [
            "Build reusable React components",
            "Manage application state",
            "Connect the frontend to REST APIs",
            "Handle loading and error states",
            "Create responsive UI",
        ],
    },
    "sql": {
        "title": "SQL Analytics Project",
        "description": "Analyze a realistic dataset using SQL and create useful insights.",
        "difficulty": "beginner",
        "estimated_days": 5,
        "objectives": [
            "Clean and prepare data",
            "Write analytical SQL queries",
            "Use joins and aggregations",
            "Create analytical reports",
            "Present actionable insights",
        ],
    },
    "power bi": {
        "title": "Power BI Business Dashboard",
        "description": "Build an interactive Power BI dashboard using a realistic business dataset.",
        "difficulty": "intermediate",
        "estimated_days": 7,
        "objectives": [
            "Prepare and transform source data",
            "Build a clean data model",
            "Create DAX measures",
            "Design an interactive dashboard",
            "Present actionable business insights",
        ],
    },
    "dax": {
        "title": "DAX KPI & Business Metrics Project",
        "description": "Create business metrics and advanced KPIs using DAX on a realistic analytical model.",
        "difficulty": "intermediate",
        "estimated_days": 6,
        "objectives": [
            "Build analytical measures",
            "Use filter and row context",
            "Create time intelligence metrics",
            "Validate KPI calculations",
            "Document business logic",
        ],
    },
    "excel": {
        "title": "Advanced Excel Business Analysis",
        "description": "Analyze a realistic business dataset using Excel and produce a decision-ready report.",
        "difficulty": "beginner",
        "estimated_days": 5,
        "objectives": [
            "Clean and structure data",
            "Use advanced formulas",
            "Create pivot tables",
            "Build a clear dashboard",
            "Present actionable insights",
        ],
    },
    "machine learning": {
        "title": "End-to-End Machine Learning Project",
        "description": "Build a complete machine learning pipeline from data preparation to evaluation and inference.",
        "difficulty": "intermediate",
        "estimated_days": 14,
        "objectives": [
            "Prepare a real dataset",
            "Engineer useful features",
            "Train and compare models",
            "Evaluate model performance",
            "Create an inference workflow",
        ],
    },
    "llm": {
        "title": "LLM-Powered Application",
        "description": "Build an application that uses an LLM to provide context-aware responses for a real user problem.",
        "difficulty": "advanced",
        "estimated_days": 14,
        "objectives": [
            "Design effective prompts",
            "Integrate an LLM",
            "Manage context",
            "Validate structured responses",
            "Evaluate AI output quality",
        ],
    },
}


def normalize_skill(skill: str) -> str:
    """Normalize a skill/role value for matching."""
    return " ".join(str(skill or "").strip().lower().split())


def normalize_role(role: str) -> str:
    """Map a role or career direction to a supported career family."""
    normalized = normalize_skill(role)

    if normalized in CAREER_ALIASES:
        return CAREER_ALIASES[normalized]

    # Soft matching for common role wording.
    for alias, family in CAREER_ALIASES.items():
        if alias in normalized or normalized in alias:
            return family

    if "data analyst" in normalized or "analytics" in normalized:
        return "data_analyst"
    if "data scientist" in normalized:
        return "data_scientist"
    if "machine learning" in normalized or normalized.startswith("ml "):
        return "machine_learning"
    if "artificial intelligence" in normalized or normalized.startswith("ai"):
        return "ai_engineer"
    if "full stack" in normalized or "full-stack" in normalized:
        return "full_stack"
    if "backend" in normalized or "back end" in normalized:
        return "backend"
    if "frontend" in normalized or "front end" in normalized:
        return "frontend"
    if "cyber" in normalized or "security" in normalized:
        return "cybersecurity"
    if "ui" in normalized or "ux" in normalized or "product design" in normalized:
        return "ui_ux"
    if "marketing" in normalized and "analytics" in normalized:
        return "marketing_analytics"
    if "marketing" in normalized:
        return "digital_marketing"
    if "business analyst" in normalized:
        return "business_analyst"
    if "project manager" in normalized:
        return "project_management"
    if "devops" in normalized:
        return "devops"
    if "cloud" in normalized:
        return "cloud"

    return ""


def find_template(skill: str) -> Optional[Dict]:
    """Legacy skill-first lookup, kept for compatibility."""
    normalized = normalize_skill(skill)

    if normalized in SKILL_TEMPLATES:
        return SKILL_TEMPLATES[normalized]

    for key, template in SKILL_TEMPLATES.items():
        if key in normalized or normalized in key:
            return template

    return None


def _skill_matches(skill: str, required_skills: List[str]) -> bool:
    normalized = normalize_skill(skill)
    for required in required_skills:
        required_normalized = normalize_skill(required)
        if (
            normalized == required_normalized
            or normalized in required_normalized
            or required_normalized in normalized
        ):
            return True
    return False


def _project_from_template(
    template: Dict,
    target_role: str,
    matched_gap: Optional[str] = None,
    relevance: int = 90,
) -> Dict:
    skills = list(template.get("skills", []))

    if matched_gap and not any(
        normalize_skill(matched_gap) == normalize_skill(skill)
        for skill in skills
    ):
        skills = [matched_gap, *skills]

    # Preserve the frontend/API response shape used by the existing Projects page.
    project = {
        "title": template["title"],
        "description": template["description"],
        "target_role": target_role,
        "skills": skills[:6],
        "objectives": template["objectives"],
        "difficulty": template["difficulty"],
        "estimated_days": template["estimated_days"],
        "matched_gap": matched_gap or "",
        "relevance": relevance,
    }

    return project


def _career_templates(target_role: str) -> List[Dict]:
    family = normalize_role(target_role)
    return CAREER_TEMPLATES.get(family, [])


def generate_project_recommendations(
    missing_skills: List[str],
    target_role: str = "",
) -> List[Dict]:
    """
    Generate up to 3 role-aware recommendations.

    Priority:
        1. Match projects to explicit job skill gaps.
        2. Fill remaining slots with projects from the target career.
        3. Only use the legacy skill template as a last compatibility fallback.

    This means a Data Analyst CV without a Job Analysis still gets Data Analyst
    projects instead of generic Django/React/AI projects.
    """
    target_role = str(target_role or "").strip()
    normalized_gaps = []
    for skill in missing_skills or []:
        normalized = normalize_skill(skill)
        if normalized and normalized not in normalized_gaps:
            normalized_gaps.append(normalized)

    recommendations: List[Dict] = []
    used_titles = set()

    career_templates = _career_templates(target_role)

    # ---------------------------------------------------------
    # MODE 1: Job-specific recommendations.
    # Prefer career templates that directly address missing skills.
    # ---------------------------------------------------------
    for template in career_templates:
        matched_gap = next(
            (
                gap
                for gap in normalized_gaps
                if _skill_matches(gap, template.get("required_skills", []))
            ),
            None,
        )

        if matched_gap is None:
            continue

        recommendations.append(
            _project_from_template(
                template,
                target_role,
                matched_gap=matched_gap,
                relevance=95,
            )
        )
        used_titles.add(template["title"])

        if len(recommendations) >= 3:
            return recommendations

    # ---------------------------------------------------------
    # MODE 2: Career-based fallback.
    # No job analysis OR not enough job-specific matches.
    # Use the role-specific project catalog.
    # ---------------------------------------------------------
    for index, template in enumerate(career_templates):
        if template["title"] in used_titles:
            continue

        relevance = max(82, 90 - (index * 3))
        recommendations.append(
            _project_from_template(
                template,
                target_role,
                relevance=relevance,
            )
        )
        used_titles.add(template["title"])

        if len(recommendations) >= 3:
            return recommendations

    # ---------------------------------------------------------
    # MODE 3: Explicit gap fallback for roles not yet represented
    # in CAREER_TEMPLATES. This keeps the service useful while the
    # taxonomy expands, without inventing a different career.
    # ---------------------------------------------------------
    for gap in normalized_gaps:
        template = find_template(gap)
        if template is None or template["title"] in used_titles:
            continue

        recommendations.append({
            "title": template["title"],
            "description": template["description"],
            "target_role": target_role,
            "skills": [gap],
            "objectives": template["objectives"],
            "difficulty": template["difficulty"],
            "estimated_days": template["estimated_days"],
            "matched_gap": gap,
            "relevance": 78,
        })
        used_titles.add(template["title"])

        if len(recommendations) >= 3:
            return recommendations

    return recommendations
