from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from career_taxonomy.models import Category, Track, Role


MASTER_TAXONOMY = {
    "Technology & IT": {
        "Software Development": [
            "Frontend Developer",
            "Backend Developer",
            "Full Stack Developer",
            "Software Engineer",
            "Web Developer",
            "Mobile Developer",
            "Android Developer",
            "iOS Developer",
            "Flutter Developer",
            "React Developer",
            ".NET Developer",
            "Java Developer",
            "PHP Developer",
            "WordPress Developer",
            "Game Developer",
        ],
        "Cloud & DevOps": [
            "DevOps Engineer",
            "Cloud Engineer",
            "AWS Engineer",
            "Azure Engineer",
            "GCP Engineer",
            "Site Reliability Engineer",
            "Platform Engineer",
            "Cloud Architect",
            "Infrastructure Engineer",
            "Kubernetes Engineer",
        ],
        "Cybersecurity": [
            "Cybersecurity Analyst",
            "SOC Analyst",
            "Security Engineer",
            "Penetration Tester",
            "Ethical Hacker",
            "Application Security Engineer",
            "Cloud Security Engineer",
            "Security Architect",
            "Digital Forensics",
            "Incident Response",
            "GRC",
            "Risk & Compliance",
        ],
        "IT": [
            "IT Support",
            "Help Desk",
            "System Administrator",
            "Network Administrator",
            "Network Engineer",
            "IT Engineer",
            "IT Manager",
            "Technical Support",
            "Infrastructure Specialist",
        ],
    },
    "Data & AI": {
        "Data & Analytics": [
            "Data Analyst",
            "BI Analyst",
            "Business Analyst",
            "Data Scientist",
            "Data Engineer",
            "Analytics Engineer",
            "BI Developer",
            "Data Architect",
            "Database Administrator",
            "Database Developer",
        ],
        "Artificial Intelligence": [
            "AI Engineer",
            "Machine Learning Engineer",
            "Deep Learning Engineer",
            "NLP Engineer",
            "Computer Vision Engineer",
            "Generative AI Engineer",
            "LLM Engineer",
            "AI Researcher",
            "MLOps Engineer",
            "Applied AI Engineer",
            "AI Solutions Architect",
        ],
        "Emerging AI": [
            "Prompt Engineer",
            "AI Product Manager",
            "AI Consultant",
            "AI Trainer",
            "AI Evaluator",
            "AI Safety",
            "Responsible AI",
            "AI Automation Specialist",
        ],
    },
    "Design & Creative": {
        "Design & Creative": [
            "UI Designer",
            "UX Designer",
            "UI/UX Designer",
            "Product Designer",
            "UX Researcher",
            "Interaction Designer",
            "Visual Designer",
            "Graphic Designer",
            "Brand Designer",
            "Motion Designer",
            "3D Designer",
            "3D Artist",
            "Animator",
            "Video Editor",
            "Art Director",
            "Creative Director",
            "Illustrator",
            "Game Artist",
            "Design Systems Designer",
        ],
    },
    "Product & Management": {
        "Product / Business / Management": [
            "Product Manager",
            "Product Owner",
            "Project Manager",
            "Program Manager",
            "Scrum Master",
            "Agile Coach",
            "Business Analyst",
            "Management Consultant",
            "Strategy Analyst",
            "Operations Manager",
            "Operations Analyst",
            "PMO Specialist",
            "Process Analyst",
            "Quality Analyst",
        ],
    },
    "Marketing": {
        "Marketing": [
            "Digital Marketing Specialist",
            "Marketing Specialist",
            "Marketing Manager",
            "SEO Specialist",
            "SEM Specialist",
            "Performance Marketer",
            "Social Media Specialist",
            "Social Media Manager",
            "Content Marketer",
            "Content Strategist",
            "Email Marketing Specialist",
            "Growth Marketer",
            "Growth Product Manager",
            "Brand Manager",
            "Marketing Analyst",
            "CRM Specialist",
            "Marketing Automation Specialist",
        ],
    },
    "Sales & Customer Success": {
        "Sales & Customer Success": [
            "Sales Representative",
            "Account Executive",
            "Business Development Representative",
            "Business Development Manager",
            "Sales Manager",
            "Account Manager",
            "Key Account Manager",
            "Sales Operations",
            "Revenue Operations",
            "Customer Success Manager",
            "Customer Success Specialist",
            "Customer Support Specialist",
            "Technical Account Manager",
        ],
    },
    "Finance & Accounting": {
        "Finance & Accounting": [
            "Accountant",
            "Financial Analyst",
            "Financial Advisor",
            "Investment Analyst",
            "Investment Banker",
            "Credit Analyst",
            "Risk Analyst",
            "Treasury Analyst",
            "FP&A Analyst",
            "Auditor",
            "Internal Auditor",
            "Tax Specialist",
            "Tax Accountant",
            "Bookkeeper",
            "Controller",
            "Finance Manager",
            "Actuary",
            "FinTech Specialist",
        ],
    },
    "Human Resources": {
        "Human Resources": [
            "HR Specialist",
            "HR Generalist",
            "Recruiter",
            "Technical Recruiter",
            "Talent Acquisition Specialist",
            "Talent Manager",
            "HR Business Partner",
            "Learning & Development Specialist",
            "Compensation & Benefits Specialist",
            "People Analyst",
            "HR Analyst",
            "People Operations Specialist",
        ],
    },
    "Engineering": {
        "Computer / Electrical": [
            "Embedded Engineer",
            "Embedded Software Engineer",
            "Firmware Engineer",
            "Hardware Engineer",
            "Electronics Engineer",
            "Robotics Engineer",
            "Control Engineer",
            "Automation Engineer",
            "IoT Engineer",
            "FPGA Engineer",
            "VLSI Engineer",
        ],
        "Mechanical": [
            "Mechanical Engineer",
            "Design Engineer",
            "Manufacturing Engineer",
            "Production Engineer",
            "Maintenance Engineer",
            "Automotive Engineer",
            "CAD Engineer",
            "HVAC Engineer",
            "Mechatronics Engineer",
            "Industrial Engineer",
        ],
        "Civil": [
            "Civil Engineer",
            "Structural Engineer",
            "Construction Engineer",
            "Site Engineer",
            "Geotechnical Engineer",
            "Transportation Engineer",
            "Environmental Engineer",
            "Quantity Surveyor",
        ],
        "Chemical": [
            "Chemical Engineer",
            "Process Engineer",
            "Petroleum Engineer",
            "Energy Engineer",
        ],
    },
    "Science & Research": {
        "Science & Research": [
            "Research Scientist",
            "Research Assistant",
            "Biostatistician",
            "Statistician",
            "Mathematician",
            "Physicist",
            "Chemist",
            "Biologist",
            "Bioinformatics Scientist",
            "Computational Scientist",
            "Research Data Analyst",
        ],
    },
    "Healthcare": {
        "Healthcare": [
            "Doctor",
            "Nurse",
            "Pharmacist",
            "Medical Laboratory Scientist",
            "Radiology Technologist",
            "Medical Imaging Specialist",
            "Physiotherapist",
            "Nutritionist",
            "Public Health Specialist",
            "Healthcare Administrator",
            "Clinical Research Associate",
            "Medical Researcher",
            "Health Data Analyst",
            "Health Informatics Specialist",
        ],
    },
    "Education": {
        "Education": [
            "Teacher",
            "University Lecturer",
            "Teaching Assistant",
            "Instructional Designer",
            "Curriculum Developer",
            "Educational Consultant",
            "E-Learning Specialist",
            "Academic Advisor",
            "Learning Experience Designer",
            "Education Program Manager",
        ],
    },
    "Legal": {
        "Legal": [
            "Lawyer",
            "Legal Counsel",
            "Legal Assistant",
            "Legal Researcher",
            "Compliance Specialist",
            "Contract Specialist",
            "Paralegal",
            "Corporate Lawyer",
            "Intellectual Property Specialist",
            "Legal Operations Specialist",
        ],
    },
    "Media & Communications": {
        "Media / Communication": [
            "Copywriter",
            "Content Writer",
            "Technical Writer",
            "Editor",
            "Journalist",
            "Blogger",
            "Script Writer",
            "PR Specialist",
            "Communications Specialist",
            "Public Relations Manager",
            "Media Planner",
            "Producer",
            "Creative Producer",
        ],
    },
    "Architecture & Construction": {
        "Architecture / Construction": [
            "Architect",
            "Interior Designer",
            "Urban Planner",
            "Landscape Architect",
            "BIM Engineer",
            "BIM Modeler",
            "Quantity Surveyor",
            "Construction Manager",
            "Project Engineer",
            "Site Supervisor",
        ],
    },
    "Supply Chain & Logistics": {
        "Supply Chain / Logistics": [
            "Supply Chain Analyst",
            "Supply Chain Manager",
            "Procurement Specialist",
            "Procurement Manager",
            "Logistics Coordinator",
            "Logistics Manager",
            "Inventory Analyst",
            "Demand Planner",
            "Warehouse Manager",
            "Operations Planner",
        ],
    },
    "Hospitality & Travel": {
        "Hospitality / Travel / Aviation": [
            "Hotel Manager",
            "Front Office Manager",
            "Event Planner",
            "Travel Consultant",
            "Tour Operator",
            "Flight Attendant",
            "Aviation Operations",
            "Airport Operations",
            "Revenue Manager",
            "Hospitality Manager",
        ],
    },
    "Agriculture & Environment": {
        "Agriculture / Environment": [
            "Agricultural Engineer",
            "Agronomist",
            "Environmental Specialist",
            "Environmental Engineer",
            "Sustainability Specialist",
            "Renewable Energy Specialist",
            "Food Scientist",
            "Agricultural Data Analyst",
        ],
    },
    "Government & Nonprofit": {
        "Government / Nonprofit / Social": [
            "Policy Analyst",
            "Public Administration Specialist",
            "Program Coordinator",
            "NGO Project Officer",
            "Monitoring & Evaluation Specialist",
            "Development Specialist",
            "Social Researcher",
            "Community Development Specialist",
        ],
    },
    "Skilled Trades": {
        "Skilled Trades": [
            "Electrician",
            "Plumber",
            "Welder",
            "HVAC Technician",
            "Automotive Technician",
            "Industrial Technician",
            "Machinist",
            "Carpenter",
            "Technician",
            "Maintenance Technician",
            "Solar Installation Technician",
            "Network Technician",
        ],
    },
}

CATEGORY_META = {
    "Technology & IT": ("Software, IT infrastructure, cloud, DevOps and cybersecurity careers.", "💻", 1),
    "Data & AI": ("Data, analytics, artificial intelligence and emerging AI careers.", "🧠", 2),
    "Design & Creative": ("UI, UX, product, visual and creative careers.", "🎨", 3),
    "Product & Management": ("Product, project, operations, strategy and management careers.", "📊", 4),
    "Marketing": ("Digital marketing, growth, SEO, content and marketing technology careers.", "📣", 5),
    "Sales & Customer Success": ("Sales, business development, account management and customer success careers.", "🤝", 6),
    "Finance & Accounting": ("Accounting, finance, investment, audit, tax, risk and fintech careers.", "💰", 7),
    "Human Resources": ("Recruitment, talent, HR operations, people analytics and learning careers.", "👥", 8),
    "Engineering": ("Engineering careers across electrical, mechanical, civil and chemical disciplines.", "⚙️", 9),
    "Science & Research": ("Scientific research, statistics, mathematics and computational science careers.", "🔬", 10),
    "Healthcare": ("Medical, clinical, healthcare administration and health technology careers.", "🏥", 11),
    "Education": ("Teaching, instructional design, academic and education management careers.", "📚", 12),
    "Legal": ("Law, compliance, contracts, legal research and legal operations careers.", "⚖️", 13),
    "Media & Communications": ("Writing, journalism, public relations and media careers.", "🎙️", 14),
    "Architecture & Construction": ("Architecture, BIM, construction, planning and site careers.", "🏗️", 15),
    "Supply Chain & Logistics": ("Supply chain, procurement, logistics, inventory and planning careers.", "🚚", 16),
    "Hospitality & Travel": ("Hospitality, tourism, travel, events and aviation careers.", "✈️", 17),
    "Agriculture & Environment": ("Agriculture, environment, sustainability and renewable energy careers.", "🌱", 18),
    "Government & Nonprofit": ("Public policy, administration, development and nonprofit careers.", "🏛️", 19),
    "Skilled Trades": ("Skilled technical trades, installation, maintenance and repair careers.", "🛠️", 20),
}

TRACK_META = {
    "Software Development": "Software engineering and application development careers.",
    "Cloud & DevOps": "Cloud infrastructure, DevOps, reliability and platform engineering careers.",
    "Cybersecurity": "Cybersecurity, security operations, offensive security and governance careers.",
    "IT": "IT support, systems, networking and infrastructure operations careers.",
    "Data & Analytics": "Data analytics, business intelligence, data engineering and database careers.",
    "Artificial Intelligence": "Artificial intelligence, machine learning and applied AI engineering careers.",
    "Emerging AI": "Prompting, AI evaluation, responsible AI, AI consulting and AI automation careers.",
    "Design & Creative": "UI, UX, product, visual, motion and creative design careers.",
    "Product / Business / Management": "Product, project, business, operations and management careers.",
    "Marketing": "Digital marketing, growth, SEO, content, CRM and marketing automation careers.",
    "Sales & Customer Success": "Sales, account management, business development and customer success careers.",
    "Finance & Accounting": "Accounting, financial analysis, investment, audit, tax, risk and fintech careers.",
    "Human Resources": "Recruitment, talent, HR operations, people analytics and L&D careers.",
    "Computer / Electrical": "Embedded, electronics, hardware, robotics, automation and electrical careers.",
    "Mechanical": "Mechanical, manufacturing, automotive, HVAC and industrial engineering careers.",
    "Civil": "Civil, structural, construction, geotechnical and transportation engineering careers.",
    "Chemical": "Chemical, process, petroleum and energy engineering careers.",
    "Science & Research": "Scientific research, statistics, mathematics and computational research careers.",
    "Healthcare": "Clinical, medical, health administration, health data and health technology careers.",
    "Education": "Teaching, instructional design, curriculum and education management careers.",
    "Legal": "Legal practice, research, contracts, compliance and legal operations careers.",
    "Media / Communication": "Writing, journalism, communications, public relations and media production careers.",
    "Architecture / Construction": "Architecture, interior design, BIM, construction and site careers.",
    "Supply Chain / Logistics": "Supply chain, procurement, inventory, logistics and planning careers.",
    "Hospitality / Travel / Aviation": "Hotels, events, travel, tourism and aviation operations careers.",
    "Agriculture / Environment": "Agriculture, environmental science, sustainability and renewable energy careers.",
    "Government / Nonprofit / Social": "Public policy, administration, nonprofit and community development careers.",
    "Skilled Trades": "Skilled technical trades, installation, maintenance and repair careers.",
}


class Command(BaseCommand):
    help = "Add the complete master career roles and tracks without deleting existing taxonomy data."

    def _get_category(self, name):
        description, icon, order = CATEGORY_META[name]
        slug = slugify(name)

        category = Category.objects.filter(slug=slug).first()

        if category is None:
            category = Category.objects.create(
                name=name,
                slug=slug,
                description=description,
                icon=icon,
                display_order=order,
                is_active=True,
            )
        else:
            changed = False
            if not category.description:
                category.description = description
                changed = True
            if not category.icon:
                category.icon = icon
                changed = True
            if not category.is_active:
                category.is_active = True
                changed = True
            if changed:
                category.save(update_fields=["description", "icon", "is_active"])

        return category

    def _get_track(self, category, name, order):
        description = TRACK_META.get(
            name,
            f"Career opportunities in {name.lower()}.",
        )
        slug = slugify(name)

        track = Track.objects.filter(slug=slug).first()

        if track is None:
            track = Track.objects.create(
                category=category,
                name=name,
                slug=slug,
                description=description,
                short_description=description[:255],
                display_order=order,
                is_active=True,
            )
            return track

        changed = False

        if track.category_id != category.id:
            # Keep a globally unique track slug and move only when the
            # existing record is clearly incomplete/unassigned.
            if not track.is_active:
                track.category = category
                changed = True

        if not track.description:
            track.description = description
            changed = True
        if not track.short_description:
            track.short_description = description[:255]
            changed = True
        if not track.is_active:
            track.is_active = True
            changed = True

        if changed:
            track.save(
                update_fields=[
                    "category",
                    "description",
                    "short_description",
                    "is_active",
                ]
            )

        return track

    def _unique_role_slug(self, track, role_name):
        base = slugify(role_name)
        if not base:
            base = "role"

        existing = Role.objects.filter(slug=base).first()

        if existing is None or existing.track_id == track.id:
            return base

        prefix = slugify(track.name) or slugify(track.category.name) or "track"
        candidate = f"{prefix}-{base}"

        counter = 2
        while Role.objects.filter(slug=candidate).exclude(track=track).exists():
            candidate = f"{prefix}-{base}-{counter}"
            counter += 1

        return candidate

    def _get_role(self, track, name, order):
        # Prefer the role already attached to this exact track.
        role = Role.objects.filter(
            track=track,
            name=name,
        ).first()

        if role is not None:
            changed = False

            if not role.is_active:
                role.is_active = True
                changed = True

            if not role.description:
                role.description = f"{name} career role."
                changed = True

            if not role.typical_titles:
                role.typical_titles = [name]
                changed = True

            if not role.career_levels:
                role.career_levels = [
                    "entry",
                    "junior",
                    "mid",
                    "senior",
                ]
                changed = True

            if changed:
                role.save(
                    update_fields=[
                        "is_active",
                        "description",
                        "typical_titles",
                        "career_levels",
                    ]
                )

            return role, False

        role = Role.objects.create(
            track=track,
            name=name,
            slug=self._unique_role_slug(track, name),
            description=f"{name} career role.",
            responsibilities=[],
            typical_titles=[name],
            career_levels=[
                "entry",
                "junior",
                "mid",
                "senior",
            ],
            interview_topics=[],
            project_types=[],
            certifications=[],
            average_experience_years_min=0,
            average_experience_years_max=0,
            display_order=order,
            is_active=True,
        )

        return role, True

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.WARNING(
                "Adding Master Career Taxonomy..."
            )
        )

        new_categories = 0
        new_tracks = 0
        new_roles = 0

        for category_name, tracks in MASTER_TAXONOMY.items():
            category = self._get_category(category_name)

            if not Category.objects.filter(pk=category.pk).exists():
                new_categories += 1

            for track_order, (track_name, roles) in enumerate(
                tracks.items(),
                start=1,
            ):
                before_track_count = Track.objects.filter(
                    slug=slugify(track_name)
                ).count()

                track = self._get_track(
                    category,
                    track_name,
                    track_order,
                )

                if before_track_count == 0:
                    new_tracks += 1

                for role_order, role_name in enumerate(
                    roles,
                    start=1,
                ):
                    _, created = self._get_role(
                        track,
                        role_name,
                        role_order,
                    )

                    if created:
                        new_roles += 1

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Master Career Taxonomy completed successfully."
            )
        )
        self.stdout.write(
            f"Categories in DB: {Category.objects.filter(is_active=True).count()}"
        )
        self.stdout.write(
            f"Tracks in DB: {Track.objects.filter(is_active=True).count()}"
        )
        self.stdout.write(
            f"Roles in DB: {Role.objects.filter(is_active=True).count()}"
        )
        self.stdout.write("")
        self.stdout.write(
            f"New tracks added by this command: {new_tracks}"
        )
        self.stdout.write(
            f"New roles added by this command: {new_roles}"
        )
