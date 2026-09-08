from django.core.management.base import BaseCommand
from django.db import transaction

from career_taxonomy.models import RoadmapPhase, RoadmapStep, Role


class Command(BaseCommand):
    help = "Create starter roadmaps for roles that do not already have a roadmap."

    @transaction.atomic
    def handle(self, *args, **options):
        created_phases = 0
        created_steps = 0

        roles = Role.objects.filter(is_active=True).prefetch_related(
            "role_skills__skill",
            "roadmap_phases__steps",
        )

        for role in roles:
            if role.roadmap_phases.exists():
                continue

            links = list(
                role.role_skills.select_related("skill")
                .order_by("-weight", "skill__name")[:9]
            )

            if not links:
                continue

            phase_definitions = [
                {
                    "number": 1,
                    "title": f"{role.name} Foundations",
                    "description": f"Build the core knowledge required for a {role.name} role.",
                    "links": links[:3],
                    "weeks": 3,
                },
                {
                    "number": 2,
                    "title": f"{role.name} Practical Skills",
                    "description": "Turn the core skills into practical, job-ready evidence.",
                    "links": links[3:6],
                    "weeks": 4,
                },
                {
                    "number": 3,
                    "title": "Portfolio & Interview Readiness",
                    "description": f"Build evidence and prepare for {role.name} applications and interviews.",
                    "links": links[6:9],
                    "weeks": 3,
                },
            ]

            step_counter = 0

            for phase_data in phase_definitions:
                phase_links = phase_data["links"]
                phase, created = RoadmapPhase.objects.get_or_create(
                    role=role,
                    phase_number=phase_data["number"],
                    defaults={
                        "title": phase_data["title"],
                        "description": phase_data["description"],
                        "estimated_weeks": phase_data["weeks"],
                        "is_required": phase_data["number"] < 3,
                    },
                )

                if created:
                    created_phases += 1

                for index, link in enumerate(phase_links, start=1):
                    skill_name = link.skill.name
                    if phase_data["number"] == 1:
                        title = f"Learn {skill_name} fundamentals"
                        resource_type = "course"
                        criteria = f"Explain and demonstrate the core concepts of {skill_name}."
                    elif phase_data["number"] == 2:
                        title = f"Practice {skill_name}"
                        resource_type = "project"
                        criteria = f"Complete a practical task that demonstrates {skill_name}."
                    else:
                        title = f"Show {skill_name} in your portfolio/interview"
                        resource_type = "portfolio"
                        criteria = f"Document evidence of {skill_name} in a project, work example, or interview answer."

                    _, step_created = RoadmapStep.objects.get_or_create(
                        phase=phase,
                        step_number=index,
                        defaults={
                            "title": title,
                            "description": f"Focus on {skill_name} for the {role.name} career path.",
                            "skill": link.skill,
                            "resource_type": resource_type,
                            "estimated_hours": 10 if link.importance == "required" else 6,
                            "completion_criteria": criteria,
                            "is_required": link.importance == "required",
                        },
                    )
                    if step_created:
                        created_steps += 1
                    step_counter += 1

        self.stdout.write(self.style.SUCCESS("Role roadmap seeding completed."))
        self.stdout.write(f"New roadmap phases: {created_phases}")
        self.stdout.write(f"New roadmap steps: {created_steps}")
