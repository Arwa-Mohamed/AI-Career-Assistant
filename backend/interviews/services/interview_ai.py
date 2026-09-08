import os
import re

from ollama import Client


OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST",
    "http://127.0.0.1:11434",
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen3:1.7b",
)

client = Client(host=OLLAMA_HOST)


def _limit_text(value, max_chars):
    if value is None:
        return ""

    text = str(value).strip()

    if len(text) <= max_chars:
        return text

    return text[:max_chars] + "\n[content trimmed for local AI speed]"


def _generate_response(prompt, *, temperature=0.2, max_tokens=450):
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
    except Exception as exc:
        raise RuntimeError(
            "Local AI service is unavailable. "
            "Make sure Ollama is running and the model "
            f"'{OLLAMA_MODEL}' is installed."
        ) from exc

    message = getattr(response, "message", None)
    content = getattr(message, "content", None)

    if not content:
        raise RuntimeError(
            "The local AI model returned an empty response."
        )

    return content.strip()


def _is_unknown_answer(answer):
    normalized = re.sub(r"\s+", " ", str(answer).strip().lower())

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

    return normalized.strip(".!؟،, ") in exact_phrases


def _extract_rubric_score(evaluation_text):
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
            rf"^{re.escape(key)}\s*:\s*([0-5](?:\.\d+)?)\s*$",
            evaluation_text,
            re.IGNORECASE | re.MULTILINE,
        )
        if not match:
            return _legacy_score(evaluation_text)

        value = max(0.0, min(float(match.group(1)), 5.0))
        total += (value / 5.0) * weight

    return max(0, min(round(total), 100))


def _legacy_score(evaluation_text):
    match = re.search(
        r"SCORE\s*:\s*(\d+(?:\.\d+)?)",
        evaluation_text,
        re.IGNORECASE,
    )
    if not match:
        return 0

    return max(0, min(round(float(match.group(1))), 100))


def generate_interview_questions(
    cv_text,
    cv_data,
    job_description,
    role,
    missing_skills,
    number_of_questions=5,
):
    compact_cv = _limit_text(cv_text, 4500)
    compact_job = _limit_text(job_description, 2500)

    if isinstance(missing_skills, (list, tuple, set)):
        compact_missing = ", ".join(
            str(x) for x in list(missing_skills)[:12]
        )
    else:
        compact_missing = _limit_text(missing_skills, 800)

    prompt = f"""
You are a technical interviewer.

Create exactly {number_of_questions} interview questions for this candidate.

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

    return _generate_response(
        prompt,
        temperature=0.25,
        max_tokens=max(300, number_of_questions * 75),
    )


def evaluate_answer(
    question,
    answer,
    cv_text,
    cv_data,
    job_description,
    missing_skills,
):
    compact_cv = _limit_text(cv_text, 3000)
    compact_job = _limit_text(job_description, 1800)
    compact_question = _limit_text(question, 800)
    compact_answer = _limit_text(answer, 2500)

    if isinstance(missing_skills, (list, tuple, set)):
        compact_missing = ", ".join(
            str(x) for x in list(missing_skills)[:10]
        )
    else:
        compact_missing = _limit_text(missing_skills, 600)

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

        # Explicit "I don't know" / "معرفش" answers are scored 5/100.
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

        score = _extract_rubric_score(evaluation)

    evaluation_without_score = re.sub(
        r"^\s*SCORE\s*:\s*\d+(?:\.\d+)?\s*$",
        "",
        evaluation,
        flags=re.IGNORECASE | re.MULTILINE,
    ).strip()

    return f"SCORE: {score}\n\n{evaluation_without_score}"
