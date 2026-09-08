from django.core.management.base import BaseCommand
from django.db.models import Count, Q

from career_taxonomy.models import Role
from career_taxonomy.services.career_detection import detect_career_roles


class Command(BaseCommand):
    help = "Smoke-test taxonomy-driven career detection and role coverage."

    def handle(self, *args, **options):
        samples = [
            (
                "Frontend sample",
                {
                    "skills": [
                        "JavaScript",
                        "React",
                        "HTML",
                        "CSS",
                        "Git",
                        "REST API",
                    ],
                    "job_title": "Frontend Developer",
                    "projects": [
                        "Built responsive React web applications and integrated REST APIs."
                    ],
                },
                "Frontend Developer with React and JavaScript experience.",
            ),
            (
                "Finance sample",
                {
                    "skills": ["Excel", "Financial Analysis", "Accounting"],
                    "job_title": "Financial Analyst",
                    "experience": [
                        "Prepared financial reports, forecasts, budgets and variance analysis."
                    ],
                },
                "Financial Analyst experienced in reporting and forecasting.",
            ),
            (
                "Healthcare sample",
                {
                    "skills": ["Patient Care", "Clinical Documentation"],
                    "job_title": "Registered Nurse",
                    "experience": [
                        "Provided patient care and maintained clinical documentation."
                    ],
                },
                "Registered Nurse with hospital and patient-care experience.",
            ),
            (
                "Marketing sample",
                {
                    "skills": ["SEO", "Google Analytics", "Content Marketing"],
                    "job_title": "Digital Marketing Specialist",
                    "experience": [
                        "Managed SEO campaigns, content strategy and website analytics."
                    ],
                },
                "Digital marketing specialist focused on SEO and analytics.",
            ),
        ]

        self.stdout.write(self.style.MIGRATE_HEADING("Career Detection Smoke Test"))

        for label, parsed_data, text in samples:
            results = detect_career_roles(
                parsed_data=parsed_data,
                extracted_text=text,
                top_n=5,
            )

            self.stdout.write(f"\n[{label}]")

            if not results:
                self.stdout.write(self.style.ERROR("No role detected."))
                continue

            for index, item in enumerate(results, start=1):
                self.stdout.write(
                    f"{index}. {item['role']} | "
                    f"{item['category']} / {item['track']} | "
                    f"score={item['score']} | "
                    f"confidence={item['confidence']} | "
                    f"required={item['required_skill_coverage']}%"
                )

                self.stdout.write(
                    "   evidence: "
                    + "; ".join(item["matched_evidence"])
                )

        active_roles = Role.objects.filter(is_active=True)
        roles_without_skills = active_roles.annotate(
            active_skill_count=Count(
                "role_skills",
                filter=Q(role_skills__skill__is_active=True),
            )
        ).filter(active_skill_count=0)

        role_count = active_roles.count()
        broken_count = roles_without_skills.count()

        self.stdout.write(
            f"\nActive roles: {role_count} | "
            f"Roles without active skills: {broken_count}"
        )

        if broken_count:
            self.stdout.write(
                self.style.ERROR(
                    "Some roles have no active RoleSkill mappings."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "All active roles have at least one active skill mapping."
                )
            )
