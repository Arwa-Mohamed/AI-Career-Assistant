import os
import re
from typing import Any, Iterable, List, Optional

from ollama import Client


# ============================================================
# LOCAL AI CONFIGURATION
# ============================================================

OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST",
    "http://127.0.0.1:11434",
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen3:1.7b",
)

client = Client(host=OLLAMA_HOST)


# ============================================================
# ROLE QUESTION BANK
# ============================================================

ROLE_ALIASES = {
    "data_analyst": {
        "data analyst",
        "data analytics",
        "business analyst",
        "bi analyst",
        "business intelligence analyst",
    },
    "data_scientist": {
        "data scientist",
        "data science",
    },
    "machine_learning_engineer": {
        "machine learning engineer",
        "ml engineer",
        "machine learning",
        "ml developer",
    },
    "frontend_developer": {
        "frontend developer",
        "front end developer",
        "frontend engineer",
        "front end engineer",
        "react developer",
        "ui developer",
    },
    "backend_developer": {
        "backend developer",
        "back end developer",
        "backend engineer",
        "back end engineer",
        "api developer",
    },
    "full_stack_developer": {
        "full stack developer",
        "full-stack developer",
        "fullstack developer",
        "full stack engineer",
        "full-stack engineer",
    },
    "software_engineer": {
        "software engineer",
        "software developer",
        "application developer",
    },
    "devops_engineer": {
        "devops engineer",
        "devops",
        "site reliability engineer",
        "sre",
        "cloud engineer",
    },
    "cybersecurity": {
        "cybersecurity",
        "cyber security",
        "security engineer",
        "security analyst",
        "information security",
        "soc analyst",
    },
    "ui_ux_designer": {
        "ui ux designer",
        "ui/ux designer",
        "ux designer",
        "ui designer",
        "product designer",
        "user experience designer",
    },
}


ROLE_QUESTIONS = {
    "data_analyst": [
        "How would you clean and prepare a messy dataset before analyzing it?",
        "What is the difference between mean, median, and mode, and when would you use each?",
        "How would you use SQL to find duplicate records in a database?",
        "Explain how you would perform exploratory data analysis on a new dataset.",
        "How would you design a dashboard to help stakeholders understand important KPIs?",
        "Tell me about a data analysis project and the insights you would try to extract from it.",
    ],
    "data_scientist": [
        "How would you approach a new machine learning problem from data collection to evaluation?",
        "What is the difference between supervised and unsupervised learning?",
        "How would you detect and handle missing values in a dataset?",
        "What is overfitting and how can you reduce it?",
        "How would you choose an appropriate evaluation metric for a classification problem?",
        "Describe a machine learning project you have worked on or would like to build.",
    ],
    "machine_learning_engineer": [
        "What are the main steps involved in taking a machine learning model into production?",
        "How would you detect and reduce overfitting in a machine learning model?",
        "What is the difference between training, validation, and test datasets?",
        "How would you monitor a machine learning model after deployment?",
        "What factors would you consider when choosing between different ML models?",
        "How would you design an API that serves predictions from a trained model?",
    ],
    "frontend_developer": [
        "What is the difference between state and props in React?",
        "How would you improve the performance of a React application?",
        "What is the purpose of reusable components?",
        "How would you handle API loading, success, and error states in a frontend application?",
        "Explain how you would make a web interface responsive across different screen sizes.",
        "Describe a frontend project you built and the main technical challenges you faced.",
    ],
    "backend_developer": [
        "What is the difference between authentication and authorization?",
        "How would you design a REST API for a web application?",
        "What is the purpose of database indexing?",
        "How would you handle validation and errors in a backend API?",
        "What is the difference between SQL joins and when would you use them?",
        "Describe a backend project you built and how you structured its architecture.",
    ],
    "full_stack_developer": [
        "How would you design a full-stack application from frontend to database?",
        "How does a frontend application communicate with a backend API?",
        "What is the difference between authentication and authorization?",
        "How would you design and secure a REST API?",
        "How would you debug a problem where the frontend works locally but fails in production?",
        "Describe a full-stack project you built and explain the main technical decisions you made.",
    ],
    "software_engineer": [
        "What principles do you follow when designing maintainable software?",
        "What is the difference between unit testing and integration testing?",
        "How would you debug a difficult software problem?",
        "Explain the purpose of object-oriented programming.",
        "How would you design a system that needs to handle increasing numbers of users?",
        "Describe a software project you worked on and the challenges you solved.",
    ],
    "devops_engineer": [
        "What is the purpose of CI/CD?",
        "What is the difference between a container and a virtual machine?",
        "How would you deploy a web application using Docker?",
        "What problems does Kubernetes solve?",
        "How would you investigate a production deployment failure?",
        "How would you monitor the health of a production application?",
    ],
    "cybersecurity": [
        "What is the difference between authentication and authorization?",
        "What is SQL injection and how can it be prevented?",
        "How would you secure a REST API?",
        "What is the principle of least privilege?",
        "How would you investigate suspicious activity in a system?",
        "What are some common web application security vulnerabilities?",
    ],
    "ui_ux_designer": [
        "What is the difference between UX and UI design?",
        "How would you conduct user research before designing a product?",
        "How would you decide whether a design is easy to use?",
        "What is the purpose of wireframes and prototypes?",
        "How would you handle conflicting feedback from different users or stakeholders?",
        "Describe a design problem you solved and how you evaluated the result.",
    ],
}


GENERIC_QUESTIONS = [
    "Tell me about yourself and your technical background.",
    "Describe a project you are proud of and explain your contribution.",
    "What was the most difficult technical problem you faced in a project?",
    "How do you learn a new technology when you need it for a project?",
    "How would you debug a problem that you cannot immediately understand?",
    "Tell me about a time you had to solve a problem under a deadline.",
]


# ============================================================
# HELPERS
# ============================================================

def _limit_text(value: Any, max_chars: int) -> str:
    if value is None:
        return ""

    text = str(value).strip()

    if len(text) <= max_chars:
        return text

    return text[:max_chars] + "\n[content trimmed for local AI speed]"


def _normalize_role(role: Any) -> str:
    if role is None:
        return ""

    text = str(role).strip().lower()

    text = text.replace("-", " ")
    text = text.replace("_", " ")
    text = re.sub(r"\s+", " ", text)

    return text


def _find_role_key(role: Any) -> Optional[str]:
    normalized = _normalize_role(role)

    if not normalized:
        return None

    for role_key, aliases in ROLE_ALIASES.items():
        if normalized in aliases:
            return role_key

        for alias in aliases:
            if alias in normalized or normalized in alias:
                return role_key

    return None


def _skills_to_text(skills: Any) -> str:
    if skills is None:
        return ""

    if isinstance(skills, dict):
        values = []

        for key, value in skills.items():
            if isinstance(value, (list, tuple, set)):
                values.extend(str(item) for item in value)
            else:
                values.append(str(value))

        return ", ".join(values[:20])

    if isinstance(skills, (list, tuple, set)):
        return ", ".join(
            str(item)
            for item in list(skills)[:20]
        )

    return str(skills)


def _clean_question_line(line: str) -> str:
    line = str(line).strip()

    line = re.sub(
        r"^\s*(?:[-*•]|\d+[\.\):\-])\s*",
        "",
        line,
    )

    line = line.strip()

    return line


def _fallback_questions(
    role: str,
    missing_skills: Any = None,
    number_of_questions: int = 5,
) -> str:
    role_key = _find_role_key(role)

    if role_key:
        questions = list(
            ROLE_QUESTIONS.get(
                role_key,
                GENERIC_QUESTIONS,
            )
        )
    else:
        questions = list(GENERIC_QUESTIONS)

    missing_text = _skills_to_text(missing_skills)

    if missing_text:
        missing_items = [
            item.strip()
            for item in missing_text.split(",")
            if item.strip()
        ]

        for skill in missing_items[:2]:
            questions.append(
                f"How would you demonstrate your understanding of {skill}?"
            )

    selected = questions[:number_of_questions]

    return "\n".join(selected)


# ============================================================
# OLLAMA
# ============================================================

def _generate_response(
    prompt: str,
    *,
    temperature: float = 0.2,
    max_tokens: int = 450,
) -> Optional[str]:
    """
    Try local Ollama.

    On Vercel/cloud deployment Ollama is normally unavailable.
    In that case return None instead of raising an exception.
    The caller will use the deterministic fallback.
    """

    try:
        response = client.chat(
            model=OLLAMA_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            think=False,
            stream=False,
            options={
                "temperature": temperature,
                "num_predict": max_tokens,
                "num_ctx": 4096,
            },
        )

    except Exception:
        return None

    message = getattr(response, "message", None)

    content = getattr(
        message,
        "content",
        None,
    )

    if not content:
        return None

    content = str(content).strip()

    if not content:
        return None

    return content


# ============================================================
# UNKNOWN ANSWER
# ============================================================

def _is_unknown_answer(answer: Any) -> bool:
    normalized = re.sub(
        r"\s+",
        " ",
        str(answer).strip().lower(),
    )

    if not normalized:
        return True

    exact_phrases = {
        "i don't know",
        "i do not know",
        "idk",
        "no idea",
        "i have no idea",
        "i'm not sure",
        "i am not sure",
        "not sure",
        "i don't have an answer",
        "i do not have an answer",
        "معرفش",
        "مش عارف",
        "مش عارفة",
        "لا أعرف",
        "مش عارف الإجابة",
        "مش عارفة الإجابة",
    }

    return normalized.strip(
        ".!؟،, "
    ) in exact_phrases


# ============================================================
# SCORE PARSING
# ============================================================

def _extract_rubric_score(
    evaluation_text: str,
) -> int:
    weights = {
        "RELEVANCE": 15,
        "TECHNICAL_ACCURACY": 25,
        "CLARITY": 10,
        "COMPLETENESS": 15,
        "PROBLEM_SOLVING": 15,
        "COMMUNICATION": 5,
        "ROLE_ALIGNMENT": 10,
        "CV_CONSISTENCY": 5,
    }

    total = 0.0

    for key, weight in weights.items():
        match = re.search(
            rf"^{re.escape(key)}\s*:\s*"
            rf"([0-5](?:\.\d+)?)\s*$",
            evaluation_text,
            re.IGNORECASE | re.MULTILINE,
        )

        if not match:
            return _legacy_score(
                evaluation_text
            )

        value = max(
            0.0,
            min(
                float(match.group(1)),
                5.0,
            ),
        )

        total += (
            value / 5.0
        ) * weight

    return max(
        0,
        min(
            round(total),
            100,
        ),
    )


def _legacy_score(
    evaluation_text: str,
) -> int:
    match = re.search(
        r"SCORE\s*:\s*(\d+(?:\.\d+)?)",
        evaluation_text,
        re.IGNORECASE,
    )

    if not match:
        return 0

    return max(
        0,
        min(
            round(
                float(
                    match.group(1)
                )
            ),
            100,
        ),
    )


# ============================================================
# FALLBACK ANSWER EVALUATION
# ============================================================

def _fallback_evaluation(
    question: str,
    answer: str,
    role: str = "",
    missing_skills: Any = None,
) -> str:
    """
    Deterministic zero-cost evaluation used when Ollama
    is unavailable.

    This is intentionally conservative.
    """

    if _is_unknown_answer(answer):
        return """SCORE: 5

FEEDBACK:
The answer does not demonstrate the required knowledge for this question. Review the topic and try to explain the main concept in your own words.

STRENGTHS:
You were honest about not knowing the answer.

IMPROVEMENTS:
Review the underlying concept and practice explaining it with a simple example.

IMPROVED_ANSWER:
A strong answer should define the main concept clearly, explain how it works, and provide a short practical example.
"""

    normalized = re.sub(
        r"\s+",
        " ",
        str(answer).strip(),
    )

    words = normalized.split()
    word_count = len(words)

    score = 25

    if word_count < 8:
        score = 25
    elif word_count < 20:
        score = 45
    elif word_count < 45:
        score = 65
    else:
        score = 78

    lower_answer = normalized.lower()

    example_terms = {
        "example",
        "for example",
        "e.g",
        "مثال",
        "مثلاً",
        "مثلا",
        "مشروع",
        "project",
    }

    reasoning_terms = {
        "because",
        "therefore",
        "first",
        "then",
        "finally",
        "approach",
        "reason",
        "trade-off",
        "tradeoff",
        "because",
        "علشان",
        "لأن",
        "بالتالي",
        "أولاً",
        "ثم",
    }

    if any(
        term in lower_answer
        for term in example_terms
    ):
        score += 5

    if any(
        term in lower_answer
        for term in reasoning_terms
    ):
        score += 5

    score = min(score, 90)

    role_text = role or "the target role"

    missing_text = _skills_to_text(
        missing_skills
    )

    if score < 40:
        feedback = (
            "The answer is too short to demonstrate "
            "enough understanding. Try explaining the "
            "concept directly and include a practical example."
        )

        strengths = (
            "You attempted to address the question."
        )

        improvements = (
            "Add more technical detail, explain your reasoning, "
            "and connect the answer to a real project or example."
        )

    elif score < 70:
        feedback = (
            "The answer shows partial understanding, "
            "but it needs more technical detail and clearer reasoning."
        )

        strengths = (
            "You addressed the main idea of the question."
        )

        improvements = (
            "Explain the concept more systematically and "
            "support your answer with a concrete example."
        )

    else:
        feedback = (
            f"The answer demonstrates a reasonable level of "
            f"understanding for {role_text}. "
            "Adding more precise technical details would make it stronger."
        )

        strengths = (
            "The answer provides useful information and "
            "shows an attempt to explain the reasoning."
        )

        improvements = (
            "Add measurable details, technical terminology, "
            "or a concrete project example where appropriate."
        )

    if missing_text:
        improvements += (
            f" Pay particular attention to: {missing_text}."
        )

    improved_answer = (
        "A stronger answer would directly define the concept, "
        "explain the reasoning or steps involved, and finish "
        "with a short practical example relevant to the target role."
    )

    return f"""SCORE: {score}

FEEDBACK:
{feedback}

STRENGTHS:
{strengths}

IMPROVEMENTS:
{improvements}

IMPROVED_ANSWER:
{improved_answer}
"""


# ============================================================
# GENERATE INTERVIEW QUESTIONS
# ============================================================

def generate_interview_questions(
    cv_text,
    cv_data,
    job_description,
    role,
    missing_skills,
    number_of_questions=5,
):
    compact_cv = _limit_text(
        cv_text,
        4500,
    )

    compact_job = _limit_text(
        job_description,
        2500,
    )

    if isinstance(
        missing_skills,
        (list, tuple, set),
    ):
        compact_missing = ", ".join(
            str(x)
            for x in list(
                missing_skills
            )[:12]
        )
    else:
        compact_missing = _limit_text(
            missing_skills,
            800,
        )

    prompt = f"""
You are a technical interviewer.

Create exactly {number_of_questions} interview questions
for this candidate.

TARGET ROLE:
{_limit_text(role, 200)}

JOB:
{compact_job or "General interview"}

CV:
{compact_cv}

MISSING SKILLS:
{compact_missing or "None"}

Rules:
- Exactly {number_of_questions} questions.
- One question per line.
- No numbering.
- No explanations.
- Mix technical, behavioral, and CV/project questions.
- Do not invent experience.
- Keep each question concise.
"""

    ai_response = _generate_response(
        prompt,
        temperature=0.25,
        max_tokens=max(
            300,
            number_of_questions * 75,
        ),
    )

    if ai_response:
        lines = [
            _clean_question_line(line)
            for line in ai_response.splitlines()
        ]

        lines = [
            line
            for line in lines
            if line
        ]

        # Remove obvious headings accidentally returned by AI.
        lines = [
            line
            for line in lines
            if line.lower()
            not in {
                "questions:",
                "interview questions:",
                "questions",
            }
        ]

        if len(lines) >= number_of_questions:
            return "\n".join(
                lines[:number_of_questions]
            )

    # ========================================================
    # ZERO-COST FALLBACK
    # ========================================================

    return _fallback_questions(
        role=role,
        missing_skills=missing_skills,
        number_of_questions=number_of_questions,
    )


# ============================================================
# EVALUATE ANSWER
# ============================================================

def evaluate_answer(
    question,
    answer,
    cv_text,
    cv_data,
    job_description,
    missing_skills,
):
    compact_cv = _limit_text(
        cv_text,
        3000,
    )

    compact_job = _limit_text(
        job_description,
        1800,
    )

    compact_question = _limit_text(
        question,
        800,
    )

    compact_answer = _limit_text(
        answer,
        2500,
    )

    if isinstance(
        missing_skills,
        (list, tuple, set),
    ):
        compact_missing = ", ".join(
            str(x)
            for x in list(
                missing_skills
            )[:10]
        )
    else:
        compact_missing = _limit_text(
            missing_skills,
            600,
        )

    # ========================================================
    # UNKNOWN ANSWER
    # ========================================================

    if _is_unknown_answer(answer):
        prompt = f"""
The candidate does not know the answer to the interview question.

TARGET ROLE / JOB:
{compact_job or "General"}

QUESTION:
{compact_question}

CANDIDATE ANSWER:
{compact_answer}

Return exactly:

RELEVANCE: 0
TECHNICAL_ACCURACY: 0
CLARITY: 1
COMPLETENESS: 0
PROBLEM_SOLVING: 0
COMMUNICATION: 1
ROLE_ALIGNMENT: 0
CV_CONSISTENCY: 5

FEEDBACK:
<2 concise sentences explaining that the candidate did not demonstrate the required knowledge and should review the topic>

STRENGTHS:
<1 concise sentence>

IMPROVEMENTS:
<1-2 concise sentences>

IMPROVED_ANSWER:
<a concise example of what a strong answer could look like>
"""

        evaluation = _generate_response(
            prompt,
            temperature=0.1,
            max_tokens=450,
        )

        # If Ollama is unavailable, use local fallback.
        if not evaluation:
            return _fallback_evaluation(
                question=question,
                answer=answer,
                missing_skills=missing_skills,
            )

        # Explicit unknown answers are always scored 5.
        score = 5

    else:
        prompt = f"""
Evaluate this interview answer using a strict rubric.

TARGET JOB:
{compact_job or "General"}

CANDIDATE CV:
{compact_cv}

MISSING SKILLS:
{compact_missing or "None"}

QUESTION:
{compact_question}

ANSWER:
{compact_answer}

Score EACH dimension from 0 to 5:

RELEVANCE:
Does the answer directly address the question?

TECHNICAL_ACCURACY:
Is the technical content correct?

CLARITY:
Is the explanation clear and understandable?

COMPLETENESS:
Does it answer the question with enough useful detail?

PROBLEM_SOLVING:
Does it demonstrate reasoning, decision-making, or problem solving when relevant?

COMMUNICATION:
Is the answer well structured and professionally communicated?

ROLE_ALIGNMENT:
Does the answer demonstrate skills relevant to the target role?

CV_CONSISTENCY:
Is the answer consistent with the candidate's CV without inventing experience?

Scoring guidance:
0 = absent or seriously incorrect
1 = very weak
2 = weak / partial
3 = acceptable
4 = strong
5 = excellent

IMPORTANT:
- Do not give credit for information that is not actually present in the answer.
- For technically incorrect claims, reduce TECHNICAL_ACCURACY.
- For vague or very short answers, reduce COMPLETENESS.
- Do not assume that a confident tone means the answer is correct.
- Do not invent candidate experience.
- The application calculates the final score from these dimensions.

Return exactly:

RELEVANCE: <0-5>
TECHNICAL_ACCURACY: <0-5>
CLARITY: <0-5>
COMPLETENESS: <0-5>
PROBLEM_SOLVING: <0-5>
COMMUNICATION: <0-5>
ROLE_ALIGNMENT: <0-5>
CV_CONSISTENCY: <0-5>

FEEDBACK:
<2-4 concise sentences>

STRENGTHS:
<1-2 concise sentences>

IMPROVEMENTS:
<1-2 concise sentences>

IMPROVED_ANSWER:
<a concise stronger answer that is accurate and consistent with the CV>
"""

        evaluation = _generate_response(
            prompt,
            temperature=0.1,
            max_tokens=650,
        )

        # ====================================================
        # ZERO-COST FALLBACK
        # ====================================================

        if not evaluation:
            return _fallback_evaluation(
                question=question,
                answer=answer,
                missing_skills=missing_skills,
            )

        score = _extract_rubric_score(
            evaluation
        )

    # ========================================================
    # NORMALIZE AI RESPONSE
    # ========================================================

    evaluation_without_score = re.sub(
        r"^\s*SCORE\s*:\s*\d+(?:\.\d+)?\s*$",
        "",
        evaluation,
        flags=re.IGNORECASE | re.MULTILINE,
    ).strip()

    return (
        f"SCORE: {score}\n\n"
        f"{evaluation_without_score}"
    )