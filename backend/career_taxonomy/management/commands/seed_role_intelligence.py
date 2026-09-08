from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from career_taxonomy.models import Role, Skill, RoleSkill


TRACK_SKILLS = {
    "Software Development": [
        ("Git", "tool", ["GitHub", "GitLab", "version control"]),
        ("Data Structures & Algorithms", "technical", ["DSA", "data structures", "algorithms"]),
        ("Object-Oriented Programming", "technical", ["OOP", "object oriented programming"]),
        ("Software Testing", "technical", ["testing", "unit testing", "integration testing"]),
        ("REST APIs", "technical", ["REST", "RESTful APIs", "API development"]),
        ("SQL", "technical", ["Structured Query Language"]),
    ],
    "Cloud & DevOps": [
        ("Linux", "technical", ["Linux administration"]),
        ("Git", "tool", ["GitHub", "GitLab", "version control"]),
        ("Docker", "tool", ["containers", "containerization"]),
        ("Kubernetes", "tool", ["K8s"]),
        ("CI/CD", "technical", ["continuous integration", "continuous delivery"]),
        ("Infrastructure as Code", "technical", ["IaC", "Terraform"]),
        ("Cloud Computing", "technical", ["cloud"]),
    ],
    "Cybersecurity": [
        ("Computer Networking", "technical", ["TCP/IP", "networking", "network security"]),
        ("Linux", "technical", ["Linux administration"]),
        ("Security Fundamentals", "domain", ["cybersecurity", "information security"]),
        ("SIEM", "tool", ["security information and event management"]),
        ("Incident Response", "technical", ["incident handling", "IR"]),
        ("Vulnerability Assessment", "technical", ["vulnerability management", "vulnerability scanning"]),
    ],
    "IT": [
        ("Computer Networking", "technical", ["TCP/IP", "networking"]),
        ("Windows Administration", "technical", ["Windows Server", "Active Directory"]),
        ("Linux", "technical", ["Linux administration"]),
        ("Troubleshooting", "technical", ["technical troubleshooting", "problem diagnosis"]),
        ("IT Service Management", "domain", ["ITSM", "service management"]),
    ],
    "Data & Analytics": [
        ("SQL", "technical", ["Structured Query Language"]),
        ("Statistics", "technical", ["statistical analysis"]),
        ("Data Cleaning", "technical", ["data preparation", "data preprocessing"]),
        ("Data Visualization", "technical", ["data storytelling"]),
        ("Microsoft Excel", "tool", ["Excel", "spreadsheets"]),
        ("Power BI", "tool", ["Microsoft Power BI", "BI"]),
        ("Python", "technical", ["Python programming"]),
        ("Pandas", "tool", ["pandas Python"]),
    ],
    "AI / ML": [
        ("Python", "technical", ["Python programming"]),
        ("Machine Learning", "technical", ["ML", "machine learning"]),
        ("Deep Learning", "technical", ["DL", "deep neural networks"]),
        ("Statistics", "technical", ["statistical analysis"]),
        ("Model Evaluation", "technical", ["model validation", "evaluation metrics"]),
        ("TensorFlow", "tool", ["Keras"]),
        ("PyTorch", "tool", ["torch"]),
    ],
    "Emerging AI": [
        ("Generative AI", "domain", ["GenAI", "generative artificial intelligence"]),
        ("Prompt Engineering", "technical", ["prompt engineer", "prompt design"]),
        ("Large Language Models", "technical", ["LLM", "LLMs", "language models"]),
        ("AI Evaluation", "technical", ["model evaluation", "LLM evaluation"]),
        ("Responsible AI", "domain", ["AI ethics", "ethical AI"]),
        ("AI Automation", "technical", ["AI workflows", "automation"]),
    ],
    "Design": [
        ("Figma", "tool", ["Figma design"]),
        ("UI Design", "technical", ["user interface design", "visual interface design"]),
        ("UX Design", "technical", ["user experience design"]),
        ("User Research", "technical", ["UX research", "usability research"]),
        ("Prototyping", "technical", ["interactive prototypes"]),
        ("Design Systems", "technical", ["design system"]),
    ],
    "Product & Management": [
        ("Product Strategy", "domain", ["product planning", "product management"]),
        ("Requirements Analysis", "technical", ["requirements gathering", "business requirements"]),
        ("Stakeholder Management", "soft", ["stakeholder communication"]),
        ("Agile", "domain", ["Agile methodology"]),
        ("Scrum", "domain", ["Scrum framework"]),
        ("Jira", "tool", ["Atlassian Jira"]),
    ],
    "Project Management": [
        ("Project Management", "domain", ["project planning", "project delivery"]),
        ("Agile", "domain", ["Agile methodology"]),
        ("Risk Management", "domain", ["project risk"]),
        ("Stakeholder Management", "soft", ["stakeholder communication"]),
        ("Jira", "tool", ["Atlassian Jira"]),
        ("Microsoft Project", "tool", ["MS Project"]),
    ],
    "Marketing": [
        ("Digital Marketing", "domain", ["online marketing"]),
        ("SEO", "technical", ["search engine optimization"]),
        ("Content Marketing", "domain", ["content strategy"]),
        ("Google Analytics", "tool", ["GA4", "Google Analytics 4"]),
        ("Marketing Analytics", "technical", ["marketing data analysis"]),
    ],
    "SEO": [
        ("SEO", "technical", ["search engine optimization"]),
        ("Keyword Research", "technical", ["keyword analysis"]),
        ("Google Search Console", "tool", ["Search Console"]),
        ("Google Analytics", "tool", ["GA4"]),
        ("Content Optimization", "technical", ["on-page SEO"]),
    ],
    "Performance Marketing": [
        ("Paid Advertising", "technical", ["PPC", "paid media"]),
        ("Google Ads", "tool", ["Google Adwords"]),
        ("Meta Ads", "tool", ["Facebook Ads", "Instagram Ads"]),
        ("Conversion Rate Optimization", "technical", ["CRO"]),
        ("Marketing Analytics", "technical", ["campaign analytics"]),
    ],
    "Content Marketing": [
        ("Content Strategy", "domain", ["content planning"]),
        ("Copywriting", "technical", ["content writing"]),
        ("SEO", "technical", ["search engine optimization"]),
        ("Social Media", "technical", ["social media marketing"]),
        ("Content Analytics", "technical", ["content performance"]),
    ],
    "Finance": [
        ("Financial Analysis", "domain", ["financial modeling", "financial analytics"]),
        ("Financial Reporting", "domain", ["financial statements"]),
        ("Microsoft Excel", "tool", ["Excel"]),
        ("Accounting", "domain", ["accounting principles"]),
    ],
    "Accounting": [
        ("Accounting", "domain", ["accounting principles"]),
        ("Financial Reporting", "domain", ["financial statements"]),
        ("Microsoft Excel", "tool", ["Excel"]),
        ("Bookkeeping", "domain", ["general ledger"]),
    ],
    "Financial Analysis": [
        ("Financial Analysis", "domain", ["financial modeling"]),
        ("Financial Modeling", "technical", ["valuation models"]),
        ("Microsoft Excel", "tool", ["Excel"]),
        ("Financial Reporting", "domain", ["financial statements"]),
    ],
    "Human Resources": [
        ("Recruitment", "domain", ["hiring"]),
        ("Talent Management", "domain", ["talent development"]),
        ("HR Operations", "domain", ["human resources operations"]),
        ("Employee Relations", "domain", ["employee engagement"]),
        ("Microsoft Excel", "tool", ["Excel"]),
    ],
    "Recruitment & Talent Acquisition": [
        ("Recruitment", "domain", ["hiring", "talent acquisition"]),
        ("Sourcing", "technical", ["candidate sourcing"]),
        ("Applicant Tracking Systems", "tool", ["ATS"]),
        ("Interviewing", "technical", ["candidate interviewing"]),
        ("LinkedIn Recruiting", "tool", ["LinkedIn Recruiter"]),
    ],
    "People Analytics": [
        ("People Analytics", "domain", ["HR analytics"]),
        ("Microsoft Excel", "tool", ["Excel"]),
        ("Data Visualization", "technical", ["data storytelling"]),
        ("Statistics", "technical", ["statistical analysis"]),
        ("SQL", "technical", ["Structured Query Language"]),
    ],
    "Engineering": [
        ("Technical Drawing", "technical", ["engineering drawing"]),
        ("Engineering Mathematics", "technical", ["engineering math"]),
        ("Problem Solving", "soft", ["analytical problem solving"]),
        ("Project Management", "domain", ["project planning"]),
    ],
    "Electrical Engineering": [
        ("Circuit Analysis", "technical", ["electrical circuits"]),
        ("MATLAB", "tool", ["Matlab"]),
        ("Control Systems", "technical", ["control engineering"]),
        ("Electronics", "technical", ["electronic systems"]),
    ],
    "Mechanical Engineering": [
        ("Computer-Aided Design", "tool", ["CAD", "computer aided design"]),
        ("SolidWorks", "tool", ["SOLIDWORKS"]),
        ("Mechanical Design", "technical", ["product design"]),
        ("Manufacturing", "domain", ["manufacturing processes"]),
    ],
    "Civil Engineering": [
        ("AutoCAD", "tool", ["AutoCAD"]),
        ("Structural Analysis", "technical", ["structural engineering"]),
        ("Construction Management", "domain", ["construction"]),
        ("Quantity Surveying", "domain", ["quantity surveying"]),
    ],
    "Embedded Systems": [
        ("C", "technical", ["C programming"]),
        ("C++", "technical", ["CPP"]),
        ("Microcontrollers", "technical", ["MCU", "microcontroller"]),
        ("Embedded C", "technical", ["C for embedded systems"]),
        ("Git", "tool", ["version control"]),
    ],
    "Robotics & Automation": [
        ("Robotics", "domain", ["robotic systems"]),
        ("Control Systems", "technical", ["control engineering"]),
        ("Python", "technical", ["Python programming"]),
        ("C++", "technical", ["CPP"]),
        ("ROS", "tool", ["Robot Operating System"]),
    ],
    "Healthcare": [
        ("Patient Care", "domain", ["clinical care"]),
        ("Medical Terminology", "domain", ["medical terminology"]),
        ("Healthcare Documentation", "domain", ["clinical documentation"]),
        ("Communication", "soft", ["communication skills"]),
    ],
    "Health Informatics": [
        ("Health Informatics", "domain", ["health information systems"]),
        ("Electronic Health Records", "tool", ["EHR", "EMR"]),
        ("SQL", "technical", ["Structured Query Language"]),
        ("Data Analysis", "technical", ["data analytics"]),
    ],
    "Medical Research": [
        ("Research Methods", "domain", ["scientific research methods"]),
        ("Clinical Research", "domain", ["clinical studies"]),
        ("Statistics", "technical", ["statistical analysis"]),
        ("Scientific Writing", "technical", ["research writing"]),
    ],
    "Education": [
        ("Teaching", "domain", ["instruction"]),
        ("Curriculum Development", "domain", ["curriculum design"]),
        ("Learning Design", "domain", ["instructional design"]),
        ("Communication", "soft", ["communication skills"]),
    ],
    "Instructional Design": [
        ("Instructional Design", "domain", ["learning design"]),
        ("Curriculum Development", "domain", ["curriculum design"]),
        ("Learning Management Systems", "tool", ["LMS"]),
        ("Content Development", "technical", ["learning content"]),
    ],
    "Legal": [
        ("Legal Research", "domain", ["legal research"]),
        ("Contract Law", "domain", ["contracts"]),
        ("Legal Writing", "technical", ["legal drafting"]),
        ("Compliance", "domain", ["regulatory compliance"]),
    ],
    "Media & Communications": [
        ("Writing", "technical", ["professional writing"]),
        ("Editing", "technical", ["content editing"]),
        ("Communication", "soft", ["communication skills"]),
        ("Content Strategy", "domain", ["content planning"]),
    ],
    "Architecture & Construction": [
        ("AutoCAD", "tool", ["AutoCAD"]),
        ("Building Information Modeling", "technical", ["BIM"]),
        ("Construction Management", "domain", ["construction"]),
        ("Technical Drawing", "technical", ["engineering drawing"]),
    ],
    "Supply Chain & Logistics": [
        ("Supply Chain Management", "domain", ["supply chain"]),
        ("Procurement", "domain", ["purchasing"]),
        ("Inventory Management", "domain", ["inventory control"]),
        ("Demand Planning", "domain", ["demand forecasting"]),
        ("Microsoft Excel", "tool", ["Excel"]),
    ],
    "Hospitality & Travel": [
        ("Customer Service", "soft", ["guest service"]),
        ("Hospitality Operations", "domain", ["hotel operations"]),
        ("Reservations Management", "domain", ["booking systems"]),
        ("Communication", "soft", ["communication skills"]),
    ],
    "Agriculture & Environment": [
        ("Environmental Science", "domain", ["environmental studies"]),
        ("Sustainability", "domain", ["sustainable development"]),
        ("Data Analysis", "technical", ["data analytics"]),
        ("GIS", "tool", ["geographic information systems"]),
    ],
    "Government & Nonprofit": [
        ("Policy Analysis", "domain", ["public policy"]),
        ("Program Management", "domain", ["program coordination"]),
        ("Monitoring & Evaluation", "domain", ["M&E"]),
        ("Research", "domain", ["research methods"]),
        ("Report Writing", "technical", ["reporting"]),
    ],
    "Skilled Trades": [
        ("Safety Procedures", "domain", ["workplace safety", "occupational safety"]),
        ("Equipment Maintenance", "technical", ["maintenance"]),
        ("Troubleshooting", "technical", ["fault diagnosis"]),
        ("Technical Documentation", "technical", ["technical reports"]),
    ],
}

ROLE_SKILL_OVERRIDES = {
    "Frontend Developer": ["JavaScript", "React", "HTML", "CSS"],
    "Backend Developer": ["Python", "Django", "REST APIs", "SQL", "Docker"],
    "Full Stack Developer": ["JavaScript", "React", "Python", "Django", "REST APIs", "SQL", "Git"],
    "Software Engineer": ["Python", "Java", "C++", "Data Structures & Algorithms", "Object-Oriented Programming", "Git"],
    "Web Developer": ["HTML", "CSS", "JavaScript", "REST APIs", "Git"],
    "Mobile Developer": ["Mobile Development", "REST APIs", "Git"],
    "Android Developer": ["Android", "Kotlin", "Java", "Android Studio"],
    "iOS Developer": ["iOS", "Swift", "Xcode"],
    "Flutter Developer": ["Flutter", "Dart", "REST APIs", "Git"],
    "React Developer": ["React", "JavaScript", "HTML", "CSS", "Git"],
    ".NET Developer": ["C#", ".NET", "ASP.NET Core", "SQL", "REST APIs"],
    "Java Developer": ["Java", "Spring Boot", "SQL", "REST APIs", "Git"],
    "PHP Developer": ["PHP", "Laravel", "SQL", "REST APIs", "Git"],
    "WordPress Developer": ["WordPress", "PHP", "HTML", "CSS", "JavaScript"],
    "Game Developer": ["Game Development", "C++", "Unity", "Unreal Engine"],
    "Data Analyst": ["SQL", "Statistics", "Microsoft Excel", "Power BI", "Python", "Data Visualization"],
    "BI Analyst": ["SQL", "Power BI", "Microsoft Excel", "Data Visualization", "Statistics"],
    "Business Analyst": ["Requirements Analysis", "Business Analysis", "SQL", "Microsoft Excel", "Stakeholder Management"],
    "Data Scientist": ["Python", "Statistics", "Machine Learning", "Pandas", "SQL", "Model Evaluation"],
    "Data Engineer": ["Python", "SQL", "ETL", "Data Warehousing", "Apache Spark", "Docker"],
    "Analytics Engineer": ["SQL", "dbt", "Data Modeling", "Git", "Data Warehousing"],
    "BI Developer": ["SQL", "Power BI", "Data Warehousing", "ETL", "Data Visualization"],
    "Data Architect": ["Data Architecture", "SQL", "Data Modeling", "Data Warehousing", "Cloud Computing"],
    "Database Administrator": ["SQL", "Database Administration", "Database Security", "Backup & Recovery"],
    "Database Developer": ["SQL", "Database Development", "Stored Procedures", "Database Design"],
    "AI Engineer": ["Python", "Machine Learning", "Deep Learning", "APIs", "Model Deployment"],
    "Machine Learning Engineer": ["Python", "Machine Learning", "Deep Learning", "Model Deployment", "Docker"],
    "Deep Learning Engineer": ["Python", "Deep Learning", "PyTorch", "TensorFlow", "Computer Vision"],
    "NLP Engineer": ["Python", "Natural Language Processing", "Machine Learning", "Transformers", "LLMs"],
    "Computer Vision Engineer": ["Python", "Computer Vision", "Deep Learning", "OpenCV", "PyTorch"],
    "Generative AI Engineer": ["Python", "Generative AI", "Large Language Models", "Prompt Engineering", "RAG"],
    "LLM Engineer": ["Python", "Large Language Models", "Transformers", "RAG", "Prompt Engineering"],
    "AI Researcher": ["Python", "Machine Learning", "Deep Learning", "Statistics", "Research Methods"],
    "MLOps Engineer": ["Python", "Machine Learning", "Docker", "Kubernetes", "CI/CD", "Model Deployment"],
    "Applied AI Engineer": ["Python", "Machine Learning", "Generative AI", "APIs", "Model Deployment"],
    "AI Solutions Architect": ["AI Architecture", "Cloud Computing", "Machine Learning", "Generative AI", "System Design"],
    "Prompt Engineer": ["Prompt Engineering", "Generative AI", "Large Language Models", "AI Evaluation"],
    "AI Product Manager": ["Product Strategy", "Generative AI", "Requirements Analysis", "Stakeholder Management", "Responsible AI"],
    "AI Consultant": ["Generative AI", "AI Strategy", "Stakeholder Management", "AI Evaluation"],
    "AI Trainer": ["Generative AI", "Prompt Engineering", "AI Evaluation", "Communication"],
    "AI Evaluator": ["AI Evaluation", "Large Language Models", "Prompt Engineering", "Quality Assurance"],
    "AI Safety": ["Responsible AI", "AI Safety", "AI Evaluation", "Risk Management"],
    "Responsible AI": ["Responsible AI", "AI Ethics", "AI Governance", "AI Evaluation"],
    "AI Automation Specialist": ["AI Automation", "Generative AI", "APIs", "Workflow Automation", "Prompt Engineering"],
    "UI/UX Designer": ["Figma", "UI Design", "UX Design", "User Research", "Prototyping", "Design Systems"],
    "UI Designer": ["Figma", "UI Design", "Design Systems", "Typography", "Visual Design"],
    "UX Designer": ["Figma", "UX Design", "User Research", "Prototyping", "Usability Testing"],
    "Product Designer": ["Figma", "UX Design", "UI Design", "User Research", "Design Systems", "Product Strategy"],
    "UX Researcher": ["User Research", "Usability Testing", "Qualitative Research", "Quantitative Research"],
    "Graphic Designer": ["Adobe Photoshop", "Adobe Illustrator", "Typography", "Visual Design", "Branding"],
    "Motion Designer": ["Adobe After Effects", "Motion Graphics", "Adobe Premiere Pro", "Visual Design"],
    "Video Editor": ["Adobe Premiere Pro", "Video Editing", "After Effects", "Storytelling"],
    "Product Manager": ["Product Strategy", "Product Analytics", "Requirements Analysis", "Stakeholder Management", "Agile"],
    "Product Owner": ["Product Strategy", "Requirements Analysis", "Agile", "Scrum", "Jira"],
    "Project Manager": ["Project Management", "Risk Management", "Stakeholder Management", "Agile", "Microsoft Project"],
    "Program Manager": ["Program Management", "Project Management", "Risk Management", "Stakeholder Management"],
    "Scrum Master": ["Scrum", "Agile", "Jira", "Facilitation", "Stakeholder Management"],
    "Agile Coach": ["Agile", "Scrum", "Coaching", "Facilitation", "Change Management"],
    "Marketing Manager": ["Digital Marketing", "Marketing Strategy", "Marketing Analytics", "SEO", "Content Marketing"],
    "SEO Specialist": ["SEO", "Keyword Research", "Google Search Console", "Google Analytics", "Content Optimization"],
    "Performance Marketer": ["Paid Advertising", "Google Ads", "Meta Ads", "Conversion Rate Optimization", "Marketing Analytics"],
    "Content Marketer": ["Content Strategy", "Copywriting", "SEO", "Social Media", "Content Analytics"],
    "Accountant": ["Accounting", "Financial Reporting", "Microsoft Excel", "Bookkeeping"],
    "Financial Analyst": ["Financial Analysis", "Financial Modeling", "Microsoft Excel", "Financial Reporting", "Statistics"],
    "Auditor": ["Auditing", "Accounting", "Risk Management", "Financial Reporting", "Microsoft Excel"],
    "HR Specialist": ["Human Resources", "HR Operations", "Employee Relations", "Recruitment", "Microsoft Excel"],
    "Recruiter": ["Recruitment", "Sourcing", "Interviewing", "Applicant Tracking Systems", "LinkedIn Recruiting"],
    "Technical Recruiter": ["Technical Recruiting", "Recruitment", "Sourcing", "Applicant Tracking Systems", "Technical Skills"],
    "Mechanical Engineer": ["Computer-Aided Design", "Mechanical Design", "Manufacturing", "Engineering Mathematics"],
    "Embedded Engineer": ["C", "C++", "Microcontrollers", "Embedded C", "Git"],
    "Robotics Engineer": ["Robotics", "Control Systems", "Python", "C++", "ROS"],
    "Civil Engineer": ["AutoCAD", "Structural Analysis", "Construction Management", "Quantity Surveying"],
    "Architect": ["AutoCAD", "Building Information Modeling", "Architectural Design", "Technical Drawing"],
    "BIM Engineer": ["Building Information Modeling", "Revit", "AutoCAD", "Technical Drawing"],
    "Supply Chain Analyst": ["Supply Chain Management", "Microsoft Excel", "Data Analysis", "Inventory Management", "Demand Planning"],
    "Procurement Specialist": ["Procurement", "Supplier Management", "Negotiation", "Microsoft Excel"],
    "Electrician": ["Electrical Systems", "Electrical Safety", "Troubleshooting", "Equipment Maintenance"],
    "HVAC Technician": ["HVAC", "Equipment Maintenance", "Troubleshooting", "Safety Procedures"],
    "Automotive Technician": ["Automotive Systems", "Vehicle Diagnostics", "Equipment Maintenance", "Troubleshooting"],
}


def normalize_name(value):
    return " ".join(str(value).strip().lower().split())


class Command(BaseCommand):
    help = "Create normalized skills and weighted RoleSkill intelligence for all active career roles."

    def skill(self, name, category="Career", aliases=None, skill_type="technical"):
        aliases = aliases or []
        type_value = getattr(Skill.SkillType, skill_type.upper(), Skill.SkillType.TECHNICAL)
        skill, _ = Skill.objects.get_or_create(
            slug=slugify(name),
            defaults={
                "name": name,
                "skill_type": type_value,
                "category": category,
                "description": f"{name} competency.",
                "aliases": aliases,
                "is_active": True,
            },
        )

        changed = False
        if not skill.aliases and aliases:
            skill.aliases = aliases
            changed = True
        if not skill.category:
            skill.category = category
            changed = True
        if not skill.is_active:
            skill.is_active = True
            changed = True
        if changed:
            skill.save(update_fields=["aliases", "category", "is_active"])
        return skill

    def resolve_skill(self, name):
        skill = Skill.objects.filter(slug=slugify(name)).first()
        if skill:
            return skill

        # A few existing seeds use slightly different names.
        aliases = {
            "HTML": "HTML",
            "CSS": "CSS",
            "JavaScript": "JavaScript",
            "React": "React",
            "Python": "Python",
            "Git": "Git",
            "SQL": "SQL",
            "Django": "Django",
            "Docker": "Docker",
            "Kubernetes": "Kubernetes",
            "Power BI": "Power BI",
            "Microsoft Excel": "Microsoft Excel",
            "Figma": "Figma",
        }
        canonical = aliases.get(name, name)
        return self.skill(canonical)

    def get_track_family(self, track_name):
        normalized = normalize_name(track_name)
        for family in TRACK_SKILLS:
            if normalize_name(family) == normalized:
                return family
        return None

    def build_required_names(self, role):
        names = []
        track_family = self.get_track_family(role.track.name)
        if track_family:
            names.extend(item[0] for item in TRACK_SKILLS[track_family])

        for role_name, role_skills in ROLE_SKILL_OVERRIDES.items():
            if normalize_name(role_name) == normalize_name(role.name):
                names = role_skills + [x for x in names if x not in role_skills]
                break

        if not names:
            # Cross-track fallback based on role title.
            title = normalize_name(role.name)
            if any(word in title for word in ["analyst", "analytics"]):
                names.extend(["Data Analysis", "Microsoft Excel", "Communication"])
            elif any(word in title for word in ["manager", "director", "lead"]):
                names.extend(["Leadership", "Stakeholder Management", "Project Management"])
            elif any(word in title for word in ["engineer", "developer", "architect", "technician"]):
                names.extend(["Problem Solving", "Technical Documentation", "Project Management"])
            elif any(word in title for word in ["designer", "artist", "illustrator"]):
                names.extend(["Visual Design", "Communication", "Portfolio Development"])
            elif any(word in title for word in ["writer", "editor", "journalist"]):
                names.extend(["Writing", "Editing", "Communication"])
            else:
                names.extend(["Communication", "Problem Solving"])
        return list(dict.fromkeys(names))

    def importance_for(self, index, total):
        if index <= max(2, total // 3):
            return RoleSkill.Importance.REQUIRED
        if index <= max(4, (2 * total) // 3):
            return RoleSkill.Importance.IMPORTANT
        return RoleSkill.Importance.OPTIONAL

    def weight_for(self, index, total):
        if total <= 1:
            return 100
        high = 30
        low = 5
        return round(high - ((index - 1) * (high - low) / (total - 1)), 2)

    @transaction.atomic
    def handle(self, *args, **options):
        roles = Role.objects.filter(is_active=True).select_related("track", "track__category")
        created_skills = 0
        created_links = 0

        for role in roles:
            skill_names = self.build_required_names(role)
            total = len(skill_names)

            # Keep a modest minimum skill set for every role.
            if total == 0:
                continue

            for index, skill_name in enumerate(skill_names, start=1):
                existing = Skill.objects.filter(slug=slugify(skill_name)).first()
                skill = self.resolve_skill(skill_name)
                if existing is None:
                    created_skills += 1

                importance = self.importance_for(index, total)
                evidence = [
                    RoleSkill.EvidenceType.MENTION,
                    RoleSkill.EvidenceType.PROJECT,
                    RoleSkill.EvidenceType.EXPERIENCE,
                ]

                if importance == RoleSkill.Importance.OPTIONAL:
                    evidence = [RoleSkill.EvidenceType.MENTION]

                _, created = RoleSkill.objects.update_or_create(
                    role=role,
                    skill=skill,
                    defaults={
                        "weight": self.weight_for(index, total),
                        "importance": importance,
                        "minimum_level": 2 if importance == RoleSkill.Importance.REQUIRED else 1,
                        "evidence_types": evidence,
                        "notes": f"Normalized career intelligence skill for {role.name}.",
                    },
                )
                if created:
                    created_links += 1

        self.stdout.write(self.style.SUCCESS("Role Intelligence seeding completed."))
        self.stdout.write(f"Active roles: {roles.count()}")
        self.stdout.write(f"New skills: {created_skills}")
        self.stdout.write(f"New RoleSkill links: {created_links}")
        self.stdout.write(f"Total skills: {Skill.objects.filter(is_active=True).count()}")
        self.stdout.write(f"Total RoleSkill links: {RoleSkill.objects.count()}")
