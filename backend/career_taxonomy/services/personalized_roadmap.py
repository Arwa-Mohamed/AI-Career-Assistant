from __future__ import annotations

from typing import Any


def build_personalized_roadmap(
    role: Any,
    skill_gap: dict,
) -> dict:
    """
    Converts the static role roadmap into a candidate-specific roadmap.

    Strong skills are skipped.
    Missing skills are high priority.
    Improvement skills are medium/high priority.
    Generic action steps remain available.
    """

    phases = list(
        role.roadmap_phases
        .all()
    )

    missing_ids = {
        item["skill_id"]
        for item in skill_gap.get(
            "missing_skills",
            [],
        )
    }

    improvement_ids = {
        item["skill_id"]
        for item in skill_gap.get(
            "improvement_skills",
            [],
        )
    }

    priority_ids = {
        item["skill_id"]
        for item in skill_gap.get(
            "priority_skills",
            [],
        )
    }

    personalized_phases = []

    for phase in phases:
        selected_steps = []

        steps = list(
            phase.steps.all()
        )

        for step in steps:
            if step.skill_id is None:
                selected_steps.append(
                    {
                        "id": step.id,
                        "title": step.title,
                        "description": step.description,
                        "skill": None,
                        "estimated_hours": step.estimated_hours,
                        "completion_criteria": (
                            step.completion_criteria
                        ),
                        "is_required": step.is_required,
                        "priority": "normal",
                        "reason": "general_action",
                    }
                )

                continue

            skill_id = step.skill_id

            if skill_id in priority_ids:
                priority = "high"
                reason = "priority_skill"

            elif skill_id in missing_ids:
                priority = "high"
                reason = "missing_skill"

            elif skill_id in improvement_ids:
                priority = "medium"
                reason = "skill_improvement"

            else:
                # Already strong enough.
                continue

            selected_steps.append(
                {
                    "id": step.id,
                    "title": step.title,
                    "description": step.description,
                    "skill": {
                        "id": step.skill.id,
                        "name": step.skill.name,
                        "slug": step.skill.slug,
                    },
                    "estimated_hours": step.estimated_hours,
                    "completion_criteria": (
                        step.completion_criteria
                    ),
                    "is_required": step.is_required,
                    "priority": priority,
                    "reason": reason,
                }
            )

        if not selected_steps:
            continue

        total_hours = sum(
            step["estimated_hours"]
            for step in selected_steps
        )

        personalized_phases.append(
            {
                "phase_id": phase.id,
                "phase_number": phase.phase_number,
                "title": phase.title,
                "description": phase.description,
                "estimated_weeks": phase.estimated_weeks,
                "estimated_hours": total_hours,
                "steps": selected_steps,
            }
        )

    total_hours = sum(
        phase["estimated_hours"]
        for phase in personalized_phases
    )

    return {
        "status": "success",
        "role": {
            "id": role.id,
            "name": role.name,
            "slug": role.slug,
            "track": role.track.name,
            "category": role.track.category.name,
        },
        "total_phases": len(
            personalized_phases
        ),
        "total_hours": total_hours,
        "phases": personalized_phases,
    }