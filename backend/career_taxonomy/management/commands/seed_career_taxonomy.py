from django.core.management.base import BaseCommand
from django.utils.text import slugify

from career_taxonomy.models import (
    Category,
    Track,
    Role,
    Skill,
    RoleSkill,
    RoadmapPhase,
    RoadmapStep,
)


class Command(BaseCommand):
    help = "Seed the Career Taxonomy with categories, tracks, roles, skills and starter roadmaps."

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.WARNING(
                "Starting Career Taxonomy seed..."
            )
        )

        categories = self.create_categories()

        self.create_data_ai(
            categories["Data & AI"]
        )

        self.create_software(
            categories["Technology & IT"]
        )

        self.create_cybersecurity(
            categories["Cybersecurity"]
        )

        self.create_cloud_devops(
            categories["Cloud & DevOps"]
        )

        self.create_design(
            categories["Design & Creative"]
        )

        self.create_business(
            categories["Business & Consulting"]
        )

        self.create_product(
            categories["Product & Management"]
        )

        self.create_marketing(
            categories["Marketing"]
        )

        self.create_sales(
            categories["Sales & Customer Success"]
        )

        self.create_finance(
            categories["Finance & Accounting"]
        )

        self.create_hr(
            categories["Human Resources"]
        )

        self.create_engineering(
            categories["Engineering"]
        )

        self.create_healthcare(
            categories["Healthcare"]
        )

        self.create_science(
            categories["Science & Research"]
        )

        self.create_education(
            categories["Education"]
        )

        self.create_legal(
            categories["Legal"]
        )

        self.create_media(
            categories["Media & Communications"]
        )

        self.create_architecture(
            categories["Architecture & Construction"]
        )

        self.create_supply_chain(
            categories["Supply Chain & Logistics"]
        )

        self.create_hospitality(
            categories["Hospitality & Travel"]
        )

        self.create_agriculture(
            categories["Agriculture & Environment"]
        )

        self.create_government(
            categories["Government & Nonprofit"]
        )

        self.create_trades(
            categories["Skilled Trades"]
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Career Taxonomy seed completed successfully."
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Categories: {Category.objects.count()}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Tracks: {Track.objects.count()}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Roles: {Role.objects.count()}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Skills: {Skill.objects.count()}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Role Skills: {RoleSkill.objects.count()}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Roadmap Phases: {RoadmapPhase.objects.count()}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Roadmap Steps: {RoadmapStep.objects.count()}"
            )
        )

    # =========================================================
    # HELPERS
    # =========================================================

    def get_or_create_category(
        self,
        name,
        description="",
        icon="",
        display_order=0,
    ):
        category, _ = Category.objects.get_or_create(
            slug=slugify(name),
            defaults={
                "name": name,
                "description": description,
                "icon": icon,
                "display_order": display_order,
                "is_active": True,
            },
        )

        return category

    def create_categories(self):
        category_data = [
            (
                "Technology & IT",
                "Software development, IT infrastructure and technical careers.",
                "💻",
                1,
            ),
            (
                "Data & AI",
                "Data analytics, artificial intelligence, machine learning and intelligent systems.",
                "🧠",
                2,
            ),
            (
                "Cybersecurity",
                "Security engineering, offensive security, SOC, GRC and cyber defense.",
                "🔐",
                3,
            ),
            (
                "Cloud & DevOps",
                "Cloud platforms, infrastructure, DevOps, SRE and platform engineering.",
                "☁️",
                4,
            ),
            (
                "Design & Creative",
                "UX, UI, product design, visual design and creative careers.",
                "🎨",
                5,
            ),
            (
                "Product & Management",
                "Product management, project management and agile careers.",
                "📊",
                6,
            ),
            (
                "Business & Consulting",
                "Business analysis, strategy, operations and consulting.",
                "💼",
                7,
            ),
            (
                "Marketing",
                "Digital marketing, growth, SEO, content and performance marketing.",
                "📣",
                8,
            ),
            (
                "Sales & Customer Success",
                "Sales, business development, account management and customer success.",
                "🤝",
                9,
            ),
            (
                "Finance & Accounting",
                "Accounting, finance, investment, auditing, risk and fintech careers.",
                "💰",
                10,
            ),
            (
                "Human Resources",
                "Recruiting, talent management, HR operations and people analytics.",
                "👥",
                11,
            ),
            (
                "Engineering",
                "Mechanical, electrical, embedded, civil, industrial and other engineering careers.",
                "⚙️",
                12,
            ),
            (
                "Healthcare",
                "Medical, clinical, healthcare technology and health administration careers.",
                "🏥",
                13,
            ),
            (
                "Science & Research",
                "Scientific, research, statistics, computational science and laboratory careers.",
                "🔬",
                14,
            ),
            (
                "Education",
                "Teaching, instructional design, educational technology and academic careers.",
                "📚",
                15,
            ),
            (
                "Legal",
                "Law, legal operations, compliance, contracts and legal research.",
                "⚖️",
                16,
            ),
            (
                "Media & Communications",
                "Writing, journalism, PR, content, media production and communications.",
                "🎙️",
                17,
            ),
            (
                "Architecture & Construction",
                "Architecture, BIM, construction, surveying and site careers.",
                "🏗️",
                18,
            ),
            (
                "Supply Chain & Logistics",
                "Procurement, logistics, planning, inventory and supply chain careers.",
                "🚚",
                19,
            ),
            (
                "Hospitality & Travel",
                "Hospitality, tourism, travel, aviation and events.",
                "✈️",
                20,
            ),
            (
                "Agriculture & Environment",
                "Agriculture, environment, sustainability, food and renewable energy.",
                "🌱",
                21,
            ),
            (
                "Government & Nonprofit",
                "Public administration, policy, development and nonprofit careers.",
                "🏛️",
                22,
            ),
            (
                "Skilled Trades",
                "Technical trades, maintenance, electrical, HVAC, automotive and craft careers.",
                "🛠️",
                23,
            ),
        ]

        categories = {}

        for (
            name,
            description,
            icon,
            display_order,
        ) in category_data:
            categories[name] = (
                self.get_or_create_category(
                    name=name,
                    description=description,
                    icon=icon,
                    display_order=display_order,
                )
            )

        return categories

    def get_or_create_track(
        self,
        category,
        name,
        description="",
        short_description="",
        icon="",
        display_order=0,
    ):
        track, _ = Track.objects.get_or_create(
            slug=slugify(name),
            defaults={
                "category": category,
                "name": name,
                "description": description,
                "short_description": short_description,
                "icon": icon,
                "display_order": display_order,
                "is_active": True,
            },
        )

        return track

    def get_or_create_skill(
        self,
        name,
        skill_type=Skill.SkillType.TECHNICAL,
        category="",
        description="",
        aliases=None,
    ):
        aliases = aliases or []

        skill, _ = Skill.objects.get_or_create(
            slug=slugify(name),
            defaults={
                "name": name,
                "skill_type": skill_type,
                "category": category,
                "description": description,
                "aliases": aliases,
                "is_active": True,
            },
        )

        return skill

    def get_or_create_role(
        self,
        track,
        name,
        description="",
        responsibilities=None,
        typical_titles=None,
        career_levels=None,
        interview_topics=None,
        project_types=None,
        certifications=None,
        experience_min=0,
        experience_max=0,
        display_order=0,
    ):
        role, _ = Role.objects.get_or_create(
            slug=slugify(name),
            defaults={
                "track": track,
                "name": name,
                "description": description,
                "responsibilities": responsibilities or [],
                "typical_titles": typical_titles or [],
                "career_levels": career_levels or [],
                "interview_topics": interview_topics or [],
                "project_types": project_types or [],
                "certifications": certifications or [],
                "average_experience_years_min": experience_min,
                "average_experience_years_max": experience_max,
                "display_order": display_order,
                "is_active": True,
            },
        )

        return role

    def add_role_skill(
        self,
        role,
        skill,
        weight,
        importance=RoleSkill.Importance.IMPORTANT,
        minimum_level=2,
        evidence_types=None,
        notes="",
    ):
        RoleSkill.objects.update_or_create(
            role=role,
            skill=skill,
            defaults={
                "weight": weight,
                "importance": importance,
                "minimum_level": minimum_level,
                "evidence_types": (
                    evidence_types
                    or [
                        RoleSkill.EvidenceType.MENTION,
                        RoleSkill.EvidenceType.PROJECT,
                    ]
                ),
                "notes": notes,
            },
        )

    def add_roadmap(
        self,
        role,
        phases,
    ):
        for phase_data in phases:
            phase, _ = RoadmapPhase.objects.update_or_create(
                role=role,
                phase_number=phase_data["phase_number"],
                defaults={
                    "title": phase_data["title"],
                    "description": phase_data.get(
                        "description",
                        "",
                    ),
                    "estimated_weeks": phase_data.get(
                        "estimated_weeks",
                        2,
                    ),
                    "is_required": phase_data.get(
                        "is_required",
                        True,
                    ),
                },
            )

            for step_data in phase_data.get(
                "steps",
                [],
            ):
                skill = None

                if step_data.get(
                    "skill"
                ):
                    skill = Skill.objects.filter(
                        slug=slugify(
                            step_data["skill"]
                        )
                    ).first()

                RoadmapStep.objects.update_or_create(
                    phase=phase,
                    step_number=step_data["step_number"],
                    defaults={
                        "title": step_data["title"],
                        "description": step_data.get(
                            "description",
                            "",
                        ),
                        "skill": skill,
                        "resource_type": step_data.get(
                            "resource_type",
                            "",
                        ),
                        "estimated_hours": step_data.get(
                            "estimated_hours",
                            5,
                        ),
                        "completion_criteria": step_data.get(
                            "completion_criteria",
                            "",
                        ),
                        "is_required": step_data.get(
                            "is_required",
                            True,
                        ),
                    },
                )

    # =========================================================
    # DATA CREATION
    # =========================================================

    def create_data_ai(self, category):
        track = self.get_or_create_track(
            category,
            "Data & Analytics",
            "Careers focused on extracting insights from data and supporting data-driven decisions.",
            "Analyze, visualize and communicate insights from data.",
            "📈",
            1,
        )

        sql = self.get_or_create_skill(
            "SQL",
            category="Data",
            aliases=[
                "Structured Query Language",
            ],
        )

        excel = self.get_or_create_skill(
            "Microsoft Excel",
            skill_type=Skill.SkillType.TOOL,
            category="Data",
            aliases=[
                "Excel",
            ],
        )

        statistics = self.get_or_create_skill(
            "Statistics",
            category="Data",
        )

        python = self.get_or_create_skill(
            "Python",
            category="Programming",
        )

        pandas = self.get_or_create_skill(
            "Pandas",
            category="Data",
        )

        power_bi = self.get_or_create_skill(
            "Power BI",
            skill_type=Skill.SkillType.TOOL,
            category="Business Intelligence",
        )

        data_visualization = self.get_or_create_skill(
            "Data Visualization",
            category="Data",
        )

        communication = self.get_or_create_skill(
            "Communication",
            skill_type=Skill.SkillType.SOFT,
            category="Soft Skills",
        )

        role = self.get_or_create_role(
            track,
            "Data Analyst",
            "Analyzes data to identify trends, patterns and actionable business insights.",
            [
                "Collect and clean data.",
                "Analyze datasets using SQL and analytical tools.",
                "Build reports and dashboards.",
                "Communicate insights to stakeholders.",
            ],
            [
                "Data Analyst",
                "Junior Data Analyst",
                "Reporting Analyst",
                "Business Intelligence Analyst",
            ],
            [
                "entry",
                "junior",
                "mid",
                "senior",
            ],
            [
                "SQL",
                "Data cleaning",
                "Statistics",
                "Dashboarding",
                "Business cases",
            ],
            [
                "Sales dashboard",
                "Customer churn analysis",
                "Marketing analytics",
                "Business performance dashboard",
            ],
            [
                "Microsoft Power BI Data Analyst",
                "Google Data Analytics",
            ],
            0,
            5,
            1,
        )

        self.add_role_skill(
            role,
            sql,
            25,
            RoleSkill.Importance.REQUIRED,
            2,
            [
                "mention",
                "project",
                "experience",
            ],
        )

        self.add_role_skill(
            role,
            excel,
            15,
            RoleSkill.Importance.IMPORTANT,
            2,
        )

        self.add_role_skill(
            role,
            statistics,
            15,
            RoleSkill.Importance.REQUIRED,
            2,
        )

        self.add_role_skill(
            role,
            power_bi,
            15,
            RoleSkill.Importance.IMPORTANT,
            2,
            [
                "mention",
                "project",
            ],
        )

        self.add_role_skill(
            role,
            python,
            10,
            RoleSkill.Importance.IMPORTANT,
            2,
        )

        self.add_role_skill(
            role,
            pandas,
            8,
            RoleSkill.Importance.IMPORTANT,
            2,
        )

        self.add_role_skill(
            role,
            data_visualization,
            7,
            RoleSkill.Importance.REQUIRED,
            2,
            [
                "mention",
                "project",
            ],
        )

        self.add_role_skill(
            role,
            communication,
            5,
            RoleSkill.Importance.IMPORTANT,
            2,
            [
                "experience",
                "project",
            ],
        )

        self.add_roadmap(
            role,
            [
                {
                    "phase_number": 1,
                    "title": "Data Foundations",
                    "description": "Build the essential analytical foundation.",
                    "estimated_weeks": 2,
                    "steps": [
                        {
                            "step_number": 1,
                            "title": "Learn descriptive statistics",
                            "skill": "Statistics",
                            "resource_type": "course",
                            "estimated_hours": 8,
                            "completion_criteria": "Explain mean, median, variance, distributions and basic correlation.",
                        },
                        {
                            "step_number": 2,
                            "title": "Master Excel fundamentals",
                            "skill": "Microsoft Excel",
                            "resource_type": "practice",
                            "estimated_hours": 10,
                            "completion_criteria": "Create formulas, pivot tables and basic charts.",
                        },
                    ],
                },
                {
                    "phase_number": 2,
                    "title": "SQL & Data Manipulation",
                    "description": "Become comfortable querying and transforming data.",
                    "estimated_weeks": 3,
                    "steps": [
                        {
                            "step_number": 1,
                            "title": "Learn SQL querying",
                            "skill": "SQL",
                            "resource_type": "course",
                            "estimated_hours": 12,
                            "completion_criteria": "Write SELECT, JOIN, GROUP BY, subqueries and window functions.",
                        },
                        {
                            "step_number": 2,
                            "title": "Practice analytical SQL",
                            "skill": "SQL",
                            "resource_type": "practice",
                            "estimated_hours": 8,
                            "completion_criteria": "Solve at least 20 realistic analytical SQL problems.",
                        },
                    ],
                },
                {
                    "phase_number": 3,
                    "title": "Visualization & BI",
                    "description": "Turn analysis into decision-ready dashboards.",
                    "estimated_weeks": 3,
                    "steps": [
                        {
                            "step_number": 1,
                            "title": "Learn Power BI",
                            "skill": "Power BI",
                            "resource_type": "project",
                            "estimated_hours": 15,
                            "completion_criteria": "Build an interactive dashboard using a realistic dataset.",
                        },
                        {
                            "step_number": 2,
                            "title": "Practice data storytelling",
                            "skill": "Data Visualization",
                            "resource_type": "project",
                            "estimated_hours": 8,
                            "completion_criteria": "Explain key findings and recommendations from a dashboard.",
                        },
                    ],
                },
                {
                    "phase_number": 4,
                    "title": "Portfolio & Job Readiness",
                    "description": "Convert skills into evidence employers can evaluate.",
                    "estimated_weeks": 3,
                    "steps": [
                        {
                            "step_number": 1,
                            "title": "Build two portfolio projects",
                            "resource_type": "project",
                            "estimated_hours": 20,
                            "completion_criteria": "Complete two end-to-end analytics projects with clear business insights.",
                        },
                        {
                            "step_number": 2,
                            "title": "Prepare for Data Analyst interviews",
                            "resource_type": "interview",
                            "estimated_hours": 8,
                            "completion_criteria": "Complete SQL, analytics and behavioral mock interviews.",
                        },
                    ],
                },
            ],
        )

    def create_software(self, category):
        track = self.get_or_create_track(
            category,
            "Software Development",
            "Careers focused on designing, building, testing and maintaining software applications.",
            "Build modern web, mobile and software systems.",
            "💻",
            1,
        )

        python = self.get_or_create_skill(
            "Python",
            category="Programming",
        )

        javascript = self.get_or_create_skill(
            "JavaScript",
            category="Programming",
        )

        git = self.get_or_create_skill(
            "Git",
            skill_type=Skill.SkillType.TOOL,
            category="Development Tools",
        )

        html = self.get_or_create_skill(
            "HTML",
            category="Web Development",
        )

        css = self.get_or_create_skill(
            "CSS",
            category="Web Development",
        )

        react = self.get_or_create_skill(
            "React",
            skill_type=Skill.SkillType.TOOL,
            category="Web Development",
        )

        databases = self.get_or_create_skill(
            "Database Management",
            category="Backend",
        )

        problem_solving = self.get_or_create_skill(
            "Problem Solving",
            skill_type=Skill.SkillType.SOFT,
        )

        frontend = self.get_or_create_role(
            track,
            "Frontend Developer",
            "Builds user interfaces and browser-based applications.",
            [
                "Build responsive interfaces.",
                "Implement reusable components.",
                "Integrate APIs.",
                "Optimize user experience and performance.",
            ],
            [
                "Frontend Developer",
                "Front-End Engineer",
                "Web Developer",
                "UI Developer",
            ],
            [
                "entry",
                "junior",
                "mid",
                "senior",
            ],
            [
                "JavaScript",
                "React",
                "CSS",
                "Web performance",
                "Frontend architecture",
            ],
            [
                "Portfolio website",
                "Dashboard application",
                "E-commerce frontend",
            ],
            [],
            0,
            5,
            1,
        )

        for skill, weight, importance in [
            (javascript, 25, RoleSkill.Importance.REQUIRED),
            (react, 20, RoleSkill.Importance.IMPORTANT),
            (html, 10, RoleSkill.Importance.REQUIRED),
            (css, 10, RoleSkill.Importance.REQUIRED),
            (git, 10, RoleSkill.Importance.IMPORTANT),
            (databases, 10, RoleSkill.Importance.IMPORTANT),
            (problem_solving, 15, RoleSkill.Importance.REQUIRED),
        ]:
            self.add_role_skill(
                frontend,
                skill,
                weight,
                importance,
                2,
            )

        self.add_roadmap(
            frontend,
            [
                {
                    "phase_number": 1,
                    "title": "Web Foundations",
                    "description": "Learn the core technologies behind the web.",
                    "estimated_weeks": 3,
                    "steps": [
                        {
                            "step_number": 1,
                            "title": "Master HTML",
                            "skill": "HTML",
                            "resource_type": "course",
                            "estimated_hours": 8,
                            "completion_criteria": "Build semantic multi-page websites.",
                        },
                        {
                            "step_number": 2,
                            "title": "Master CSS",
                            "skill": "CSS",
                            "resource_type": "practice",
                            "estimated_hours": 12,
                            "completion_criteria": "Build responsive layouts using modern CSS.",
                        },
                    ],
                },
                {
                    "phase_number": 2,
                    "title": "JavaScript & React",
                    "description": "Build interactive modern interfaces.",
                    "estimated_weeks": 4,
                    "steps": [
                        {
                            "step_number": 1,
                            "title": "Master modern JavaScript",
                            "skill": "JavaScript",
                            "resource_type": "course",
                            "estimated_hours": 20,
                            "completion_criteria": "Build applications using ES6+, async programming and modules.",
                        },
                        {
                            "step_number": 2,
                            "title": "Build React applications",
                            "skill": "React",
                            "resource_type": "project",
                            "estimated_hours": 20,
                            "completion_criteria": "Build a complete React application using components, hooks and API integration.",
                        },
                    ],
                },
                {
                    "phase_number": 3,
                    "title": "Portfolio & Job Readiness",
                    "description": "Create employer-ready evidence.",
                    "estimated_weeks": 3,
                    "steps": [
                        {
                            "step_number": 1,
                            "title": "Build portfolio projects",
                            "resource_type": "project",
                            "estimated_hours": 25,
                            "completion_criteria": "Publish at least two strong frontend projects.",
                        },
                        {
                            "step_number": 2,
                            "title": "Practice frontend interviews",
                            "resource_type": "interview",
                            "estimated_hours": 8,
                            "completion_criteria": "Complete frontend technical and behavioral interviews.",
                        },
                    ],
                },
            ],
        )

    def create_cybersecurity(self, category):
        track = self.get_or_create_track(
            category,
            "Cybersecurity",
            "Protect systems, applications, networks and organizations from cyber threats.",
            "Build careers in cyber defense, security engineering and offensive security.",
            "🔐",
            1,
        )

        networking = self.get_or_create_skill(
            "Computer Networking",
            category="Cybersecurity",
        )

        linux = self.get_or_create_skill(
            "Linux",
            category="Systems",
        )

        python = self.get_or_create_skill(
            "Python",
            category="Programming",
        )

        security = self.get_or_create_skill(
            "Security Fundamentals",
            category="Cybersecurity",
        )

        siem = self.get_or_create_skill(
            "SIEM",
            skill_type=Skill.SkillType.TOOL,
            category="Cybersecurity",
        )

        incident_response = self.get_or_create_skill(
            "Incident Response",
            category="Cybersecurity",
        )

        role = self.get_or_create_role(
            track,
            "Cybersecurity Analyst",
            "Monitors, investigates and responds to cybersecurity threats.",
            [
                "Monitor security alerts.",
                "Investigate suspicious activity.",
                "Analyze logs and incidents.",
                "Document and communicate security findings.",
            ],
            [
                "Cybersecurity Analyst",
                "SOC Analyst",
                "Security Analyst",
            ],
            [
                "entry",
                "junior",
                "mid",
                "senior",
            ],
            [
                "Networking",
                "Linux",
                "Incident response",
                "Security monitoring",
                "SIEM",
            ],
            [
                "SOC lab",
                "Incident response investigation",
                "Security monitoring project",
            ],
            [
                "CompTIA Security+",
                "CompTIA CySA+",
            ],
            0,
            5,
            1,
        )

        for skill, weight, importance in [
            (security, 25, RoleSkill.Importance.REQUIRED),
            (networking, 20, RoleSkill.Importance.REQUIRED),
            (linux, 15, RoleSkill.Importance.IMPORTANT),
            (siem, 15, RoleSkill.Importance.IMPORTANT),
            (incident_response, 15, RoleSkill.Importance.REQUIRED),
            (python, 10, RoleSkill.Importance.IMPORTANT),
        ]:
            self.add_role_skill(
                role,
                skill,
                weight,
                importance,
                2,
            )

        self.add_roadmap(
            role,
            [
                {
                    "phase_number": 1,
                    "title": "Security Foundations",
                    "description": "Understand networking, operating systems and core security concepts.",
                    "estimated_weeks": 4,
                    "steps": [
                        {
                            "step_number": 1,
                            "title": "Learn networking fundamentals",
                            "skill": "Computer Networking",
                            "resource_type": "course",
                            "estimated_hours": 15,
                            "completion_criteria": "Understand TCP/IP, DNS, HTTP, routing and common network attacks.",
                        },
                        {
                            "step_number": 2,
                            "title": "Learn Linux fundamentals",
                            "skill": "Linux",
                            "resource_type": "practice",
                            "estimated_hours": 10,
                            "completion_criteria": "Comfortably manage files, processes, permissions and logs.",
                        },
                    ],
                },
                {
                    "phase_number": 2,
                    "title": "Security Operations",
                    "description": "Practice monitoring and incident investigation.",
                    "estimated_weeks": 4,
                    "steps": [
                        {
                            "step_number": 1,
                            "title": "Learn SIEM workflows",
                            "skill": "SIEM",
                            "resource_type": "lab",
                            "estimated_hours": 15,
                            "completion_criteria": "Investigate alerts and correlate security events.",
                        },
                        {
                            "step_number": 2,
                            "title": "Practice incident response",
                            "skill": "Incident Response",
                            "resource_type": "lab",
                            "estimated_hours": 15,
                            "completion_criteria": "Analyze and document a complete simulated incident.",
                        },
                    ],
                },
                {
                    "phase_number": 3,
                    "title": "Job Readiness",
                    "description": "Build a portfolio and prepare for SOC interviews.",
                    "estimated_weeks": 3,
                    "steps": [
                        {
                            "step_number": 1,
                            "title": "Build a SOC portfolio lab",
                            "resource_type": "project",
                            "estimated_hours": 20,
                            "completion_criteria": "Publish a documented security monitoring lab.",
                        },
                        {
                            "step_number": 2,
                            "title": "Practice security interviews",
                            "resource_type": "interview",
                            "estimated_hours": 8,
                            "completion_criteria": "Complete security and behavioral mock interviews.",
                        },
                    ],
                },
            ],
        )

    def create_cloud_devops(self, category):
        track = self.get_or_create_track(
            category,
            "Cloud & DevOps",
            "Cloud infrastructure, automation, deployment and reliability engineering.",
            "Build and operate scalable cloud infrastructure.",
            "☁️",
            1,
        )

        linux = self.get_or_create_skill(
            "Linux",
            category="Systems",
        )

        git = self.get_or_create_skill(
            "Git",
            skill_type=Skill.SkillType.TOOL,
        )

        docker = self.get_or_create_skill(
            "Docker",
            skill_type=Skill.SkillType.TOOL,
        )

        kubernetes = self.get_or_create_skill(
            "Kubernetes",
            skill_type=Skill.SkillType.TOOL,
        )

        aws = self.get_or_create_skill(
            "AWS",
            skill_type=Skill.SkillType.TOOL,
            category="Cloud",
        )

        cicd = self.get_or_create_skill(
            "CI/CD",
            category="DevOps",
        )

        python = self.get_or_create_skill(
            "Python",
            category="Programming",
        )

        role = self.get_or_create_role(
            track,
            "DevOps Engineer",
            "Automates software delivery and manages reliable cloud infrastructure.",
            [
                "Build CI/CD pipelines.",
                "Automate infrastructure and deployments.",
                "Manage cloud environments.",
                "Monitor reliability and performance.",
            ],
            [
                "DevOps Engineer",
                "Cloud DevOps Engineer",
                "Platform Engineer",
            ],
            [
                "entry",
                "junior",
                "mid",
                "senior",
            ],
            [
                "Linux",
                "Docker",
                "Kubernetes",
                "Cloud",
                "CI/CD",
            ],
            [
                "CI/CD pipeline",
                "Containerized application deployment",
                "Cloud infrastructure project",
            ],
            [
                "AWS Certified Cloud Practitioner",
                "AWS Certified Solutions Architect",
            ],
            0,
            6,
            1,
        )

        for skill, weight, importance in [
            (linux, 15, RoleSkill.Importance.REQUIRED),
            (git, 10, RoleSkill.Importance.REQUIRED),
            (docker, 20, RoleSkill.Importance.REQUIRED),
            (kubernetes, 15, RoleSkill.Importance.IMPORTANT),
            (aws, 15, RoleSkill.Importance.REQUIRED),
            (cicd, 15, RoleSkill.Importance.REQUIRED),
            (python, 10, RoleSkill.Importance.IMPORTANT),
        ]:
            self.add_role_skill(
                role,
                skill,
                weight,
                importance,
                2,
            )

        self.add_roadmap(
            role,
            [
                {
                    "phase_number": 1,
                    "title": "Infrastructure Foundations",
                    "description": "Learn Linux, Git and networking fundamentals.",
                    "estimated_weeks": 3,
                    "steps": [
                        {
                            "step_number": 1,
                            "title": "Master Linux",
                            "skill": "Linux",
                            "resource_type": "lab",
                            "estimated_hours": 15,
                            "completion_criteria": "Manage services, permissions, processes and system logs.",
                        },
                        {
                            "step_number": 2,
                            "title": "Master Git workflows",
                            "skill": "Git",
                            "resource_type": "practice",
                            "estimated_hours": 6,
                            "completion_criteria": "Use branching, merging, pull requests and release workflows.",
                        },
                    ],
                },
                {
                    "phase_number": 2,
                    "title": "Containers & CI/CD",
                    "description": "Automate application delivery.",
                    "estimated_weeks": 4,
                    "steps": [
                        {
                            "step_number": 1,
                            "title": "Containerize applications",
                            "skill": "Docker",
                            "resource_type": "project",
                            "estimated_hours": 12,
                            "completion_criteria": "Create reproducible container images and multi-container deployments.",
                        },
                        {
                            "step_number": 2,
                            "title": "Build CI/CD pipelines",
                            "skill": "CI/CD",
                            "resource_type": "project",
                            "estimated_hours": 12,
                            "completion_criteria": "Automate testing and deployment using a CI/CD platform.",
                        },
                    ],
                },
                {
                    "phase_number": 3,
                    "title": "Cloud Engineering",
                    "description": "Deploy and operate production-like infrastructure.",
                    "estimated_weeks": 4,
                    "steps": [
                        {
                            "step_number": 1,
                            "title": "Learn AWS fundamentals",
                            "skill": "AWS",
                            "resource_type": "course",
                            "estimated_hours": 15,
                            "completion_criteria": "Deploy a basic application using core AWS services.",
                        },
                        {
                            "step_number": 2,
                            "title": "Learn Kubernetes",
                            "skill": "Kubernetes",
                            "resource_type": "lab",
                            "estimated_hours": 15,
                            "completion_criteria": "Deploy and manage a containerized application on Kubernetes.",
                        },
                    ],
                },
            ],
        )

    def create_design(self, category):
        track = self.get_or_create_track(
            category,
            "Design",
            "Digital and visual design careers focused on user experience and product interfaces.",
            "Create useful, accessible and compelling digital experiences.",
            "🎨",
            1,
        )

        figma = self.get_or_create_skill(
            "Figma",
            skill_type=Skill.SkillType.TOOL,
            category="Design",
        )

        ux = self.get_or_create_skill(
            "UX Design",
            category="Design",
        )

        ui = self.get_or_create_skill(
            "UI Design",
            category="Design",
        )

        prototyping = self.get_or_create_skill(
            "Prototyping",
            category="Design",
        )

        user_research = self.get_or_create_skill(
            "User Research",
            category="Design",
        )

        role = self.get_or_create_role(
            track,
            "UI/UX Designer",
            "Designs user experiences, interfaces and interaction systems.",
            [
                "Conduct user research.",
                "Design user flows and interfaces.",
                "Create prototypes.",
                "Collaborate with product and engineering teams.",
            ],
            [
                "UI/UX Designer",
                "Product Designer",
                "UX Designer",
                "UI Designer",
            ],
            [
                "entry",
                "junior",
                "mid",
                "senior",
            ],
            [
                "Design process",
                "User research",
                "Figma",
                "Prototyping",
                "Design systems",
            ],
            [
                "Mobile app redesign",
                "E-commerce UX case study",
                "SaaS dashboard design",
            ],
            [
                "Google UX Design Certificate",
            ],
            0,
            6,
            1,
        )

        for skill, weight, importance in [
            (ux, 25, RoleSkill.Importance.REQUIRED),
            (ui, 20, RoleSkill.Importance.REQUIRED),
            (figma, 20, RoleSkill.Importance.REQUIRED),
            (prototyping, 15, RoleSkill.Importance.REQUIRED),
            (user_research, 20, RoleSkill.Importance.IMPORTANT),
        ]:
            self.add_role_skill(
                role,
                skill,
                weight,
                importance,
                2,
            )

        self.add_roadmap(
            role,
            [
                {
                    "phase_number": 1,
                    "title": "Design Foundations",
                    "description": "Understand visual and interaction fundamentals.",
                    "estimated_weeks": 3,
                    "steps": [
                        {
                            "step_number": 1,
                            "title": "Learn UX fundamentals",
                            "skill": "UX Design",
                            "resource_type": "course",
                            "estimated_hours": 10,
                            "completion_criteria": "Understand user-centered design and problem framing.",
                        },
                        {
                            "step_number": 2,
                            "title": "Learn UI principles",
                            "skill": "UI Design",
                            "resource_type": "practice",
                            "estimated_hours": 10,
                            "completion_criteria": "Create consistent visual interfaces using typography, spacing and hierarchy.",
                        },
                    ],
                },
                {
                    "phase_number": 2,
                    "title": "Figma & Prototyping",
                    "description": "Create realistic digital product designs.",
                    "estimated_weeks": 3,
                    "steps": [
                        {
                            "step_number": 1,
                            "title": "Master Figma",
                            "skill": "Figma",
                            "resource_type": "practice",
                            "estimated_hours": 12,
                            "completion_criteria": "Build reusable components and organized design files.",
                        },
                        {
                            "step_number": 2,
                            "title": "Create interactive prototypes",
                            "skill": "Prototyping",
                            "resource_type": "project",
                            "estimated_hours": 10,
                            "completion_criteria": "Create an interactive prototype for a real product flow.",
                        },
                    ],
                },
                {
                    "phase_number": 3,
                    "title": "Portfolio",
                    "description": "Turn design skills into convincing case studies.",
                    "estimated_weeks": 3,
                    "steps": [
                        {
                            "step_number": 1,
                            "title": "Build two case studies",
                            "resource_type": "project",
                            "estimated_hours": 20,
                            "completion_criteria": "Publish two complete UX/UI case studies showing decisions and outcomes.",
                        },
                    ],
                },
            ],
        )

    # =========================================================
    # REMAINING CATEGORY SEEDS
    # =========================================================

    def create_business(self, category):
        self.get_or_create_track(
            category,
            "Business Analysis",
            "Analyze business processes, requirements and opportunities.",
            "Understand business problems and translate them into actionable solutions.",
            "📊",
            1,
        )

        self.get_or_create_track(
            category,
            "Strategy & Consulting",
            "Solve organizational and strategic business problems.",
            "Build careers in strategy, consulting and business transformation.",
            "🧩",
            2,
        )

    def create_product(self, category):
        self.get_or_create_track(
            category,
            "Product Management",
            "Plan, build and improve products around user and business needs.",
            "Lead product discovery, strategy and delivery.",
            "🚀",
            1,
        )

        self.get_or_create_track(
            category,
            "Project Management",
            "Plan and deliver projects across teams and organizations.",
            "Lead projects, resources, timelines and delivery.",
            "📋",
            2,
        )

    def create_marketing(self, category):
        for index, name, description in [
            (
                1,
                "Digital Marketing",
                "Digital channels, campaigns and online customer acquisition.",
            ),
            (
                2,
                "SEO",
                "Search engine optimization and organic growth.",
            ),
            (
                3,
                "Performance Marketing",
                "Paid acquisition, measurement and conversion optimization.",
            ),
            (
                4,
                "Content Marketing",
                "Content strategy, creation and audience growth.",
            ),
        ]:
            self.get_or_create_track(
                category,
                name,
                description,
                description,
                "📣",
                index,
            )

    def create_sales(self, category):
        for index, name in enumerate(
            [
                "Sales",
                "Business Development",
                "Account Management",
                "Customer Success",
            ],
            start=1,
        ):
            self.get_or_create_track(
                category,
                name,
                f"Career opportunities in {name.lower()}.",
                f"Build a career in {name.lower()}.",
                "🤝",
                index,
            )

    def create_finance(self, category):
        for index, name in enumerate(
            [
                "Accounting",
                "Financial Analysis",
                "Investment",
                "Risk Management",
                "Auditing",
                "FinTech",
            ],
            start=1,
        ):
            self.get_or_create_track(
                category,
                name,
                f"Career opportunities in {name.lower()}.",
                f"Build a career in {name.lower()}.",
                "💰",
                index,
            )

    def create_hr(self, category):
        for index, name in enumerate(
            [
                "Human Resources",
                "Recruitment & Talent Acquisition",
                "People Analytics",
                "Learning & Development",
            ],
            start=1,
        ):
            self.get_or_create_track(
                category,
                name,
                f"Career opportunities in {name.lower()}.",
                f"Build a career in {name.lower()}.",
                "👥",
                index,
            )

    def create_engineering(self, category):
        for index, name in enumerate(
            [
                "Electrical Engineering",
                "Mechanical Engineering",
                "Civil Engineering",
                "Industrial Engineering",
                "Embedded Systems",
                "Robotics & Automation",
                "Mechatronics",
                "Chemical Engineering",
            ],
            start=1,
        ):
            self.get_or_create_track(
                category,
                name,
                f"Career opportunities in {name.lower()}.",
                f"Build a career in {name.lower()}.",
                "⚙️",
                index,
            )

    def create_healthcare(self, category):
        for index, name in enumerate(
            [
                "Healthcare Administration",
                "Health Informatics",
                "Medical Research",
                "Clinical Research",
                "Public Health",
                "Medical Imaging",
            ],
            start=1,
        ):
            self.get_or_create_track(
                category,
                name,
                f"Career opportunities in {name.lower()}.",
                f"Build a career in {name.lower()}.",
                "🏥",
                index,
            )

    def create_science(self, category):
        for index, name in enumerate(
            [
                "Scientific Research",
                "Statistics",
                "Bioinformatics",
                "Computational Science",
                "Data Science Research",
            ],
            start=1,
        ):
            self.get_or_create_track(
                category,
                name,
                f"Career opportunities in {name.lower()}.",
                f"Build a career in {name.lower()}.",
                "🔬",
                index,
            )

    def create_education(self, category):
        for index, name in enumerate(
            [
                "Teaching",
                "Instructional Design",
                "Educational Technology",
                "Academic Research",
                "Learning & Development",
            ],
            start=1,
        ):
            self.get_or_create_track(
                category,
                name,
                f"Career opportunities in {name.lower()}.",
                f"Build a career in {name.lower()}.",
                "📚",
                index,
            )

    def create_legal(self, category):
        for index, name in enumerate(
            [
                "Legal Practice",
                "Legal Operations",
                "Compliance",
                "Contracts",
                "Legal Research",
            ],
            start=1,
        ):
            self.get_or_create_track(
                category,
                name,
                f"Career opportunities in {name.lower()}.",
                f"Build a career in {name.lower()}.",
                "⚖️",
                index,
            )

    def create_media(self, category):
        for index, name in enumerate(
            [
                "Content Writing",
                "Technical Writing",
                "Journalism",
                "Public Relations",
                "Media Production",
                "Communications",
            ],
            start=1,
        ):
            self.get_or_create_track(
                category,
                name,
                f"Career opportunities in {name.lower()}.",
                f"Build a career in {name.lower()}.",
                "🎙️",
                index,
            )

    def create_architecture(self, category):
        for index, name in enumerate(
            [
                "Architecture",
                "Interior Design",
                "BIM",
                "Construction Management",
                "Quantity Surveying",
            ],
            start=1,
        ):
            self.get_or_create_track(
                category,
                name,
                f"Career opportunities in {name.lower()}.",
                f"Build a career in {name.lower()}.",
                "🏗️",
                index,
            )

    def create_supply_chain(self, category):
        for index, name in enumerate(
            [
                "Supply Chain",
                "Procurement",
                "Logistics",
                "Inventory Management",
                "Demand Planning",
            ],
            start=1,
        ):
            self.get_or_create_track(
                category,
                name,
                f"Career opportunities in {name.lower()}.",
                f"Build a career in {name.lower()}.",
                "🚚",
                index,
            )

    def create_hospitality(self, category):
        for index, name in enumerate(
            [
                "Hospitality Management",
                "Travel & Tourism",
                "Events",
                "Aviation Operations",
            ],
            start=1,
        ):
            self.get_or_create_track(
                category,
                name,
                f"Career opportunities in {name.lower()}.",
                f"Build a career in {name.lower()}.",
                "✈️",
                index,
            )

    def create_agriculture(self, category):
        for index, name in enumerate(
            [
                "Agriculture",
                "Environmental Management",
                "Sustainability",
                "Renewable Energy",
                "Food Science",
            ],
            start=1,
        ):
            self.get_or_create_track(
                category,
                name,
                f"Career opportunities in {name.lower()}.",
                f"Build a career in {name.lower()}.",
                "🌱",
                index,
            )

    def create_government(self, category):
        for index, name in enumerate(
            [
                "Public Administration",
                "Public Policy",
                "Development",
                "Nonprofit Management",
                "Monitoring & Evaluation",
            ],
            start=1,
        ):
            self.get_or_create_track(
                category,
                name,
                f"Career opportunities in {name.lower()}.",
                f"Build a career in {name.lower()}.",
                "🏛️",
                index,
            )

    def create_trades(self, category):
        for index, name in enumerate(
            [
                "Electrical Trades",
                "HVAC",
                "Automotive",
                "Industrial Maintenance",
                "Welding",
                "Plumbing",
                "Machining",
            ],
            start=1,
        ):
            self.get_or_create_track(
                category,
                name,
                f"Career opportunities in {name.lower()}.",
                f"Build a career in {name.lower()}.",
                "🛠️",
                index,
            )