from django.core.management.base import BaseCommand
from types import SimpleNamespace
from django.db.models import Count

from career_taxonomy.models import Category, Track, Role, Skill, RoleSkill, RoadmapPhase, RoadmapStep


class Command(BaseCommand):
    help = "Run smoke tests for Career Taxonomy, Role Intelligence, and Roadmaps."

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Running Career Intelligence smoke test..."))

        counts = {
            "categories": Category.objects.filter(is_active=True).count(),
            "tracks": Track.objects.filter(is_active=True).count(),
            "roles": Role.objects.filter(is_active=True).count(),
            "skills": Skill.objects.filter(is_active=True).count(),
            "role_skills": RoleSkill.objects.count(),
            "roadmap_phases": RoadmapPhase.objects.count(),
            "roadmap_steps": RoadmapStep.objects.count(),
        }

        for key, value in counts.items():
            self.stdout.write(f"{key}: {value}")

        failures = []

        if counts["categories"] == 0:
            failures.append("No active categories found.")
        if counts["tracks"] == 0:
            failures.append("No active tracks found.")
        if counts["roles"] == 0:
            failures.append("No active roles found.")
        if counts["skills"] == 0:
            failures.append("No active skills found.")
        if counts["role_skills"] == 0:
            failures.append("No RoleSkill records found. Run seed_role_intelligence first.")
        if counts["roadmap_phases"] == 0 or counts["roadmap_steps"] == 0:
            failures.append("No roadmap data found. Run seed_role_roadmaps first.")

        roles_without_skills = list(
            Role.objects.filter(is_active=True, role_skills__isnull=True)
            .values("id", "name", "track__name")
            .distinct()
            .order_by("track__name", "name")[:15]
        )

        if roles_without_skills:
            self.stdout.write(self.style.WARNING("\nRoles without RoleSkill mappings (first 15):"))
            for role in roles_without_skills:
                self.stdout.write(
                    f"- {role['track__name']} / {role['name']}"
                )
        else:
            self.stdout.write(self.style.SUCCESS("\nAll active roles have at least one RoleSkill mapping."))

        top_roles = (
            Role.objects.filter(is_active=True)
            .annotate(skill_count=Count("role_skills", distinct=True))
            .order_by("-skill_count", "name")[:10]
        )

        self.stdout.write(self.style.SUCCESS("\nTop roles by mapped skills:"))
        for role in top_roles:
            self.stdout.write(
                f"- {role.name} | {role.track.name} | skills={role.skill_count}"
            )

        try:
            from career_taxonomy.services.career_detection import detect_career_roles

            sample_text = """
            Frontend Developer with JavaScript, React, HTML, CSS and Git experience.
            Built responsive dashboards, integrated REST APIs, worked with PostgreSQL,
            and created reusable components for web applications.
            """
            detected = detect_career_roles(extracted_text=sample_text, top_n=3)

            self.stdout.write(self.style.SUCCESS("\nCareer detection sample:"))
            if not detected:
                self.stdout.write(self.style.WARNING("No roles detected."))
            else:
                for item in detected:
                    self.stdout.write(
                        f"- {item.get('role')} | {item.get('track')} | score={item.get('score')}"
                    )
        except Exception as exc:
            failures.append(f"Career detection failed: {exc}")

        try:
            from career_taxonomy.services.job_intelligence import build_job_intelligence

            sample_cv = SimpleNamespace(
                extracted_text="""
                Frontend Developer with JavaScript, React, HTML, CSS and Git experience.
                Built responsive web applications and integrated REST APIs.
                """,
                parsed_data={},
            )
            sample_job = """
            We are looking for a Frontend Developer with strong JavaScript and React skills.
            Experience with HTML, CSS, Git, REST APIs and responsive web development is required.
            Familiarity with testing and modern frontend architecture is a plus.
            """
            intelligence = build_job_intelligence(
                cv=sample_cv,
                job_description=sample_job,
                ats_score=0,
            )
            job_match = intelligence.get("job_match") or {}
            self.stdout.write(self.style.SUCCESS("\nJob intelligence sample:"))
            self.stdout.write(f"- detected job skills: {len(intelligence.get('job_skills') or [])}")
            self.stdout.write(f"- ranked roles: {len(intelligence.get('detected_roles') or [])}")
            self.stdout.write(f"- best role: {(job_match.get('role') or {}).get('name', 'N/A')}")
            self.stdout.write(f"- match score: {job_match.get('score', 0)}")
            self.stdout.write(
                f"- required coverage: {(job_match.get('skill_match') or {}).get('required_skill_coverage', 0)}"
            )
        except Exception as exc:
            failures.append(f"Job intelligence failed: {exc}")

        if failures:
            self.stdout.write(self.style.ERROR("\nSmoke test FAILED:"))
            for failure in failures:
                self.stdout.write(self.style.ERROR(f"- {failure}"))
            raise SystemExit(1)

        self.stdout.write(self.style.SUCCESS("\nCareer Intelligence smoke test PASSED."))
