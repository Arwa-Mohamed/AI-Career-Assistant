import os
import time

from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
    OpenAIError,
    RateLimitError,
)


client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def _build_fallback_response(
    user_message,
    profile_data,
    cv_data,
    job_data,
    skill_gap_data,
):
    """
    Safe local fallback used when the OpenAI service is temporarily
    unavailable, rate-limited, or not configured correctly.

    The fallback intentionally avoids inventing user experience or skills.
    """

    profile = profile_data or {}
    cv = cv_data or {}
    job = job_data or {}
    gap = skill_gap_data or {}

    user_message = (user_message or "").strip()

    full_name = (
        profile.get("full_name")
        or profile.get("username")
        or "there"
    )

    career_goal = (
        profile.get("career_goal")
        or "your target career"
    )

    current_skills = []

    parsed_cv = cv.get("parsed_data") or {}

    if isinstance(parsed_cv, dict):
        skills = parsed_cv.get("skills", [])

        if isinstance(skills, list):
            current_skills.extend(
                str(skill).strip()
                for skill in skills
                if str(skill).strip()
            )

        technical_skills = parsed_cv.get(
            "technical_skills",
            [],
        )

        if isinstance(technical_skills, list):
            current_skills.extend(
                str(skill).strip()
                for skill in technical_skills
                if str(skill).strip()
            )

    current_skills = list(
        dict.fromkeys(current_skills)
    )

    missing_skills = gap.get(
        "missing_skills",
        [],
    )

    if not isinstance(missing_skills, list):
        missing_skills = []

    matched_skills = gap.get(
        "matched_skills",
        [],
    )

    if not isinstance(matched_skills, list):
        matched_skills = []

    job_score = job.get(
        "final_match_score"
    )

    try:
        job_score_text = (
            f"{float(job_score):.0f}%"
            if job_score is not None
            else "not available"
        )
    except (TypeError, ValueError):
        job_score_text = "not available"

    normalized_message = user_message.lower()

    # ---------------------------------------------------------
    # Greeting / generic career question
    # ---------------------------------------------------------

    if any(
        greeting in normalized_message
        for greeting in [
            "hello",
            "hi",
            "hey",
            "مرحبا",
            "اهلا",
            "أهلا",
            "السلام عليكم",
        ]
    ):
        return (
            f"Hi {full_name}! 👋\n\n"
            f"Your current career goal is "
            f"**{career_goal}**.\n\n"
            "I can help you review your CV, identify skill gaps, "
            "improve your job match, plan projects, and prepare "
            "for interviews.\n\n"
            "Start with your biggest concern and I’ll guide you step by step."
        )

    # ---------------------------------------------------------
    # CV / resume question
    # ---------------------------------------------------------

    if any(
        keyword in normalized_message
        for keyword in [
            "cv",
            "resume",
            "سيرة",
            "السيرة",
            "cv score",
            "resume score",
        ]
    ):
        cv_score = cv.get("score")

        if cv_score is not None:
            try:
                cv_score_text = (
                    f"{float(cv_score):.0f}/100"
                )
            except (TypeError, ValueError):
                cv_score_text = "available"
        else:
            cv_score_text = "not available yet"

        if missing_skills:
            missing_text = ", ".join(
                str(skill)
                for skill in missing_skills[:5]
            )
        else:
            missing_text = "No major skill gaps are currently available."

        return (
            f"Here’s what I can see from your current career data, {full_name}:\n\n"
            f"**Career goal:** {career_goal}\n"
            f"**CV score:** {cv_score_text}\n"
            f"**Current skills detected:** "
            f"{', '.join(current_skills[:10]) if current_skills else 'No skills detected yet.'}\n\n"
            f"**Main skill gaps:** {missing_text}\n\n"
            "For the strongest CV improvement, focus on clear section structure, "
            "quantified achievements, role-specific keywords, and strong evidence "
            "through projects or experience."
        )

    # ---------------------------------------------------------
    # Skill gap question
    # ---------------------------------------------------------

    if any(
        keyword in normalized_message
        for keyword in [
            "skill gap",
            "skills",
            "learn",
            "missing skill",
            "skills gap",
            "مهارات",
            "مهارة",
            "اتعلم",
            "تعلم",
            "ناقصنى",
            "ناقصني",
        ]
    ):
        if missing_skills:
            priority_text = "\n".join(
                f"{index + 1}. {skill}"
                for index, skill in enumerate(
                    missing_skills[:8]
                )
            )
        else:
            priority_text = (
                "No major missing skills are available yet. "
                "Analyze a target job to generate a more accurate skill gap."
            )

        return (
            f"Based on the career data currently available for {full_name}:\n\n"
            f"**Target:** {career_goal}\n\n"
            "**Priority skill gaps:**\n"
            f"{priority_text}\n\n"
            "**Recommended approach:**\n"
            "1. Learn the highest-priority missing skill.\n"
            "2. Apply it in a practical project.\n"
            "3. Add measurable evidence to your CV.\n"
            "4. Re-check your match against a real job description.\n"
        )

    # ---------------------------------------------------------
    # Job matching question
    # ---------------------------------------------------------

    if any(
        keyword in normalized_message
        for keyword in [
            "job",
            "job match",
            "match",
            "job description",
            "وظيفة",
            "وظيفه",
            "مباراة",
            "تطابق",
            "فرصة",
        ]
    ):
        if missing_skills:
            missing_text = ", ".join(
                str(skill)
                for skill in missing_skills[:6]
            )
        else:
            missing_text = (
                "No major missing skills are available from the latest analysis."
            )

        matched_text = (
            ", ".join(str(skill) for skill in matched_skills[:8])
            if matched_skills
            else "Not available yet."
        )

        return (
            f"Your latest available job match is **{job_score_text}**.\n\n"
            f"Matched skills: {matched_text}\n\n"
            f"Skills that need attention: {missing_text}\n\n"
            "For a stronger application, tailor your CV to the exact job "
            "description without adding skills or experience you do not actually have."
        )

    # ---------------------------------------------------------
    # Interview question
    # ---------------------------------------------------------

    if any(
        keyword in normalized_message
        for keyword in [
            "interview",
            "interviews",
            "mock interview",
            "مقابلة",
            "انترفيو",
            "الانترفيو",
        ]
    ):
        return (
            f"For your goal of **{career_goal}**, interview preparation should focus on:\n\n"
            "• Role-specific technical questions\n"
            "• Project explanation and problem-solving\n"
            "• Behavioral questions using real examples\n"
            "• Explaining decisions and trade-offs\n"
            "• Clear and concise communication\n\n"
            "A good next step is to practice with the Interview Simulator "
            "and review the feedback after each session."
        )

    # ---------------------------------------------------------
    # Roadmap / career planning
    # ---------------------------------------------------------

    if any(
        keyword in normalized_message
        for keyword in [
            "roadmap",
            "career plan",
            "path",
            "career path",
            "خطة",
            "رودماب",
            "خارطة",
            "مسار",
        ]
    ):
        return (
            f"Here is the practical career path I recommend for your current goal "
            f"of **{career_goal}**:\n\n"
            "**Phase 1 — Foundation**\n"
            "Strengthen the essential skills for your target role.\n\n"
            "**Phase 2 — Practical Skills**\n"
            "Build projects that prove you can actually use those skills.\n\n"
            "**Phase 3 — Career Evidence**\n"
            "Improve your CV, portfolio, GitHub, and measurable achievements.\n\n"
            "**Phase 4 — Job Readiness**\n"
            "Practice interviews and validate your profile against real jobs.\n\n"
            "The roadmap should become more personalized once your CV and a target "
            "job description are available."
        )

    # ---------------------------------------------------------
    # Generic fallback
    # ---------------------------------------------------------

    return (
        f"I’m currently unable to reach the AI reasoning service, "
        f"but I can still guide you using your saved career data.\n\n"
        f"**Current target:** {career_goal}\n"
        f"**Detected skills:** "
        f"{', '.join(current_skills[:8]) if current_skills else 'Not available yet.'}\n"
        f"**Latest job match:** {job_score_text}\n\n"
        "For the most accurate personalized answer, try again in a moment. "
        "Meanwhile, you can ask me about your CV, skills, roadmap, jobs, projects, or interviews."
    )


def generate_career_response(
    user_message,
    profile_data,
    cv_data,
    job_data,
    skill_gap_data,
    chat_history,
):
    system_prompt = f"""
You are an AI Career Assistant.

You help the user make practical career decisions.

Use the user's actual data when available.

USER PROFILE:
{profile_data}

CV DATA:
{cv_data}

LATEST JOB ANALYSIS:
{job_data}

SKILL GAP:
{skill_gap_data}

CONVERSATION HISTORY:
{chat_history}

Rules:
- Give practical and personalized career advice.
- Do not invent experience, skills, education, or achievements.
- Clearly separate known facts from recommendations.
- Prioritize actions that help the user's career goal.
- When recommending skills, explain why they matter.
- When recommending learning paths, order them by priority.
- Keep the answer clear and actionable.
- Do not claim that the user has a skill unless the provided data supports it.
"""

    # =========================================================
    # OpenAI request with limited retry handling
    # =========================================================

    last_error = None

    for attempt in range(3):
        try:
            response = client.responses.create(
                model="gpt-5.4-mini",
                instructions=system_prompt,
                input=user_message,
            )

            answer = (
                response.output_text
                if response.output_text
                else ""
            )

            if answer.strip():
                return answer.strip()

            return _build_fallback_response(
                user_message=user_message,
                profile_data=profile_data,
                cv_data=cv_data,
                job_data=job_data,
                skill_gap_data=skill_gap_data,
            )

        except RateLimitError as exc:
            last_error = exc

            # Retry only for the first two attempts.
            if attempt < 2:
                time.sleep(
                    1.0 * (attempt + 1)
                )
                continue

            return _build_fallback_response(
                user_message=user_message,
                profile_data=profile_data,
                cv_data=cv_data,
                job_data=job_data,
                skill_gap_data=skill_gap_data,
            )

        except (
            APIConnectionError,
            APITimeoutError,
        ) as exc:
            last_error = exc

            if attempt < 2:
                time.sleep(
                    0.8 * (attempt + 1)
                )
                continue

            return _build_fallback_response(
                user_message=user_message,
                profile_data=profile_data,
                cv_data=cv_data,
                job_data=job_data,
                skill_gap_data=skill_gap_data,
            )

        except AuthenticationError as exc:
            last_error = exc

            return _build_fallback_response(
                user_message=user_message,
                profile_data=profile_data,
                cv_data=cv_data,
                job_data=job_data,
                skill_gap_data=skill_gap_data,
            )

        except OpenAIError as exc:
            last_error = exc

            return _build_fallback_response(
                user_message=user_message,
                profile_data=profile_data,
                cv_data=cv_data,
                job_data=job_data,
                skill_gap_data=skill_gap_data,
            )

    # Extremely defensive fallback.
    return _build_fallback_response(
        user_message=user_message,
        profile_data=profile_data,
        cv_data=cv_data,
        job_data=job_data,
        skill_gap_data=skill_gap_data,
    )