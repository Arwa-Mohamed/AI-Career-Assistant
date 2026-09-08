import re

from .skill_normalizer import normalize_skills


# ============================================================
# Supported Skills
# ============================================================

COMMON_SKILLS = [
    # --------------------------------------------------------
    # Programming Languages
    # --------------------------------------------------------
    "python",
    "java",
    "javascript",
    "typescript",
    "c++",
    "c#",
    "php",
    "ruby",
    "go",
    "rust",
    "kotlin",
    "swift",
    "matlab",
    "r",

    # --------------------------------------------------------
    # Web Development
    # --------------------------------------------------------
    "html",
    "html5",
    "css",
    "css3",
    "bootstrap",
    "tailwind css",
    "tailwind",
    "react",
    "react.js",
    "reactjs",
    "angular",
    "vue",
    "vue.js",
    "next.js",
    "nextjs",
    "node.js",
    "nodejs",
    "express",
    "express.js",
    "django",
    "flask",
    "fastapi",
    "spring",
    "spring boot",
    "laravel",
    "asp.net",

    # --------------------------------------------------------
    # Backend / APIs
    # --------------------------------------------------------
    "rest api",
    "rest apis",
    "restful api",
    "graphql",
    "json",
    "xml",
    "microservices",

    # --------------------------------------------------------
    # Databases
    # --------------------------------------------------------
    "sql",
    "mysql",
    "postgresql",
    "postgres",
    "sqlite",
    "oracle",
    "sql server",
    "mongodb",
    "redis",
    "firebase",
    "elasticsearch",

    # --------------------------------------------------------
    # Data Analysis / Business Intelligence
    # --------------------------------------------------------
    "excel",
    "microsoft excel",
    "power bi",
    "powerbi",
    "tableau",
    "data analysis",
    "data analytics",
    "data cleaning",
    "data validation",
    "data visualization",
    "data manipulation",
    "data entry",
    "data modeling",
    "data mining",
    "business intelligence",
    "business analytics",
    "statistics",
    "statistical analysis",
    "dax",
    "power query",
    "pivot tables",
    "vlookup",
    "xlookup",
    "regular expressions",
    "web scraping",

    # --------------------------------------------------------
    # Python / Data Libraries
    # --------------------------------------------------------
    "pandas",
    "numpy",
    "scipy",
    "matplotlib",
    "seaborn",
    "plotly",
    "jupyter",
    "jupyter notebook",
    "openpyxl",

    # --------------------------------------------------------
    # AI / Machine Learning
    # --------------------------------------------------------
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "generative ai",
    "natural language processing",
    "nlp",
    "computer vision",
    "reinforcement learning",
    "supervised learning",
    "unsupervised learning",
    "neural networks",
    "predictive modeling",
    "feature engineering",
    "model evaluation",
    "scikit-learn",
    "sklearn",
    "tensorflow",
    "pytorch",
    "keras",
    "hugging face",
    "transformers",
    "llm",
    "large language models",
    "prompt engineering",
    "rag",
    "retrieval augmented generation",
    "langchain",
    "llamaindex",

    # --------------------------------------------------------
    # DevOps / Cloud
    # --------------------------------------------------------
    "git",
    "github",
    "gitlab",
    "bitbucket",
    "docker",
    "docker compose",
    "kubernetes",
    "jenkins",
    "ci/cd",
    "continuous integration",
    "continuous deployment",
    "aws",
    "amazon web services",
    "azure",
    "google cloud",
    "gcp",
    "terraform",
    "ansible",

    # --------------------------------------------------------
    # Testing
    # --------------------------------------------------------
    "software testing",
    "manual testing",
    "automation testing",
    "test automation",
    "unit testing",
    "integration testing",
    "selenium",
    "pytest",
    "jest",
    "cypress",
    "postman",

    # --------------------------------------------------------
    # Software Engineering
    # --------------------------------------------------------
    "object oriented programming",
    "oop",
    "data structures",
    "algorithms",
    "design patterns",
    "software architecture",
    "system design",
    "debugging",
    "version control",
    "agile",
    "scrum",
    "jira",

    # --------------------------------------------------------
    # Networking / Cybersecurity
    # --------------------------------------------------------
    "computer networks",
    "networking",
    "tcp/ip",
    "dns",
    "http",
    "https",
    "linux",
    "cybersecurity",
    "information security",
    "network security",
    "penetration testing",
    "ethical hacking",
    "cryptography",
    "firewalls",
    "wireshark",
    "cisco",
    "cisco packet tracer",

    # --------------------------------------------------------
    # Embedded / IoT
    # --------------------------------------------------------
    "embedded systems",
    "arduino",
    "raspberry pi",
    "microcontrollers",
    "iot",
    "internet of things",
    "simulink",

    # --------------------------------------------------------
    # Design
    # --------------------------------------------------------
    "figma",
    "photoshop",
    "adobe photoshop",
    "illustrator",
    "adobe illustrator",
    "ui design",
    "ux design",
    "user experience",
    "user interface",
    "graphic design",

    # --------------------------------------------------------
    # Business / Professional
    # --------------------------------------------------------
    "project management",
    "product management",
    "business analysis",
    "requirements analysis",
    "requirements gathering",
]


# ============================================================
# Text Normalization
# ============================================================

def normalize_text(text):
    """
    Normalize CV text while preserving important technical
    characters such as:

        C++
        C#
        Node.js
        CI/CD
        TCP/IP
    """

    if not text:
        return ""

    text = text.lower()

    # Normalize common dash characters
    text = text.replace("–", "-")
    text = text.replace("—", "-")

    # Replace bullet characters with spaces
    text = text.replace("•", " ")

    # Normalize multiple spaces
    text = re.sub(r"\s+", " ", text)

    return text


# ============================================================
# Skill Regex
# ============================================================

def skill_pattern(skill):
    """
    Build a safe regex pattern for matching a skill.

    This prevents substring false positives.

    Examples:

        Git      -> should NOT match Digital
        HTTP     -> should NOT match HTTPS
        R        -> should NOT match random words
        Express  -> should NOT match Expression

    At the same time it supports technical skills such as:

        C++
        C#
        Node.js
        CI/CD
        TCP/IP
    """

    skill = skill.lower().strip()

    escaped_skill = re.escape(skill)

    return (
        rf"(?<![a-z0-9])"
        rf"{escaped_skill}"
        rf"(?![a-z0-9])"
    )


def contains_skill(text, skill):
    """
    Check whether a skill exists as a standalone expression
    inside the CV text.
    """

    if not text or not skill:
        return False

    pattern = skill_pattern(skill)

    return bool(
        re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )
    )


# ============================================================
# Email Extraction
# ============================================================

def extract_email(text):
    """
    Extract the first valid email address from the CV.
    """

    if not text:
        return ""

    match = re.search(
        r"[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+"
        r"\.[A-Za-z]{2,}",
        text,
    )

    return match.group(0) if match else ""


# ============================================================
# Phone Extraction
# ============================================================

def extract_phone(text):
    """
    Extract an Egyptian phone number.

    Supports formats such as:

        01012345678
        +201012345678
        00201012345678
        010-1234-5678
    """

    if not text:
        return ""

    match = re.search(
        r"(?:\+20|0020)?"
        r"[\s\-()]?"
        r"01[0-9]"
        r"[\s\-0-9]{8,12}",
        text,
    )

    return match.group(0).strip() if match else ""


# ============================================================
# Name Extraction
# ============================================================

def extract_name(text):
    """
    Try to extract the candidate's name from the beginning
    of the CV.

    This is intentionally conservative because name extraction
    from arbitrary CV layouts is difficult without an NLP model.
    """

    if not text:
        return ""

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return ""

    email = extract_email(text)

    for line in lines[:10]:

        # Ignore line containing email
        if email and email.lower() in line.lower():
            continue

        # Ignore LinkedIn URLs
        if "linkedin.com" in line.lower():
            continue

        # Ignore GitHub URLs
        if "github.com" in line.lower():
            continue

        # Ignore obvious URLs
        if "http://" in line.lower():
            continue

        if "https://" in line.lower():
            continue

        # A name is usually between 1 and 5 words
        if 1 <= len(line.split()) <= 5:
            return line

    return lines[0]


# ============================================================
# Skill Extraction
# ============================================================

def extract_skills(text):
    """
    Extract technical and professional skills from CV text.

    The parser uses boundary-aware matching instead of simple
    substring matching.

    This is important because a CV may contain words like:

        digital
        expression
        https
        github.com

    without the candidate actually listing:

        git
        r
        http
        github

    as skills.
    """

    if not text:
        return []

    normalized_text = normalize_text(text)

    found = []

    for skill in COMMON_SKILLS:

        if contains_skill(
            normalized_text,
            skill,
        ):
            found.append(skill)

    # Normalize aliases and remove duplicates
    return normalize_skills(found)


# ============================================================
# Main CV Parser
# ============================================================

def parse_cv(text):
    """
    Parse extracted CV text into structured candidate data.

    Returned structure:

    {
        "name": "...",
        "email": "...",
        "phone": "...",
        "skills": [...]
    }
    """

    if not text:
        return {
            "name": "",
            "email": "",
            "phone": "",
            "skills": [],
        }

    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
    }
    
def calculate_cv_score(parsed_data, extracted_text):
    """
    Calculate a CV score out of 100.

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
    # 1. Contact Information - 15 points
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
    # 2. Skills - 25 points
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
    # 3. Content - 30 points
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
    # 4. Sections - 30 points
    # ========================================================

    text_lower = text.lower()

    section_keywords = {
        "education": [
            "education",
            "academic",
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
            "employment",
            "internship",
            "intern",
            "professional experience",
        ],

        "projects": [
            "projects",
            "project",
            "portfolio",
        ],

        "certifications": [
            "certification",
            "certifications",
            "certificate",
            "certificates",
        ],

        "summary": [
            "summary",
            "profile",
            "professional summary",
            "objective",
            "about me",
        ],

        "contact": [
            "email",
            "phone",
            "linkedin",
            "github",
        ],
    }

    section_details = {}

    for section, keywords in section_keywords.items():

        found = any(
            keyword in text_lower
            for keyword in keywords
        )

        section_details[section] = found

    # ========================================================
    # Section Score
    # ========================================================

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

    if section_details["contact"]:
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