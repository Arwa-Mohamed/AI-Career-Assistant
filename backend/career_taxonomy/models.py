from django.db import models


class Category(models.Model):
    """
    High-level career category.

    Examples:
    Technology & IT
    Data & AI
    Design & Creative
    Business & Management
    Healthcare
    Engineering
    etc.
    """

    name = models.CharField(
        max_length=120,
        unique=True,
    )

    slug = models.SlugField(
        max_length=140,
        unique=True,
    )

    description = models.TextField(
        blank=True,
    )

    icon = models.CharField(
        max_length=50,
        blank=True,
    )

    display_order = models.PositiveIntegerField(
        default=0,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "display_order",
            "name",
        ]

    def __str__(self):
        return self.name


class Track(models.Model):
    """
    A broad career track.

    Examples:
    Data & Analytics
    Artificial Intelligence
    Cybersecurity
    Software Development
    Cloud & DevOps
    """

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="tracks",
    )

    name = models.CharField(
        max_length=150,
    )

    slug = models.SlugField(
        max_length=170,
        unique=True,
    )

    description = models.TextField(
        blank=True,
    )

    short_description = models.CharField(
        max_length=255,
        blank=True,
    )

    icon = models.CharField(
        max_length=50,
        blank=True,
    )

    display_order = models.PositiveIntegerField(
        default=0,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = [
            "category__display_order",
            "display_order",
            "name",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "category",
                    "name",
                ],
                name="unique_track_per_category",
            ),
        ]

    def __str__(self):
        return self.name


class Skill(models.Model):
    """
    Normalized skill entity.

    A single skill can belong to multiple roles/tracks.
    """

    class SkillType(models.TextChoices):
        TECHNICAL = "technical", "Technical"
        SOFT = "soft", "Soft Skill"
        TOOL = "tool", "Tool"
        DOMAIN = "domain", "Domain"
        LANGUAGE = "language", "Language"
        CERTIFICATION = "certification", "Certification"

    name = models.CharField(
        max_length=150,
        unique=True,
    )

    slug = models.SlugField(
        max_length=170,
        unique=True,
    )

    skill_type = models.CharField(
        max_length=30,
        choices=SkillType.choices,
        default=SkillType.TECHNICAL,
    )

    category = models.CharField(
        max_length=120,
        blank=True,
    )

    description = models.TextField(
        blank=True,
    )

    aliases = models.JSONField(
        default=list,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Role(models.Model):
    """
    Concrete job/career role.

    Examples:
    Data Analyst
    Data Scientist
    Backend Developer
    Cybersecurity Analyst
    UI/UX Designer
    """

    class CareerLevel(models.TextChoices):
        ENTRY = "entry", "Entry Level"
        JUNIOR = "junior", "Junior"
        MID = "mid", "Mid Level"
        SENIOR = "senior", "Senior"
        LEAD = "lead", "Lead"
        MANAGER = "manager", "Manager"
        EXECUTIVE = "executive", "Executive"

    track = models.ForeignKey(
        Track,
        on_delete=models.CASCADE,
        related_name="roles",
    )

    name = models.CharField(
        max_length=180,
    )

    slug = models.SlugField(
        max_length=200,
        unique=True,
    )

    description = models.TextField(
        blank=True,
    )

    responsibilities = models.JSONField(
        default=list,
        blank=True,
    )

    typical_titles = models.JSONField(
        default=list,
        blank=True,
    )

    career_levels = models.JSONField(
        default=list,
        blank=True,
    )

    interview_topics = models.JSONField(
        default=list,
        blank=True,
    )

    project_types = models.JSONField(
        default=list,
        blank=True,
    )

    certifications = models.JSONField(
        default=list,
        blank=True,
    )

    average_experience_years_min = models.PositiveIntegerField(
        default=0,
    )

    average_experience_years_max = models.PositiveIntegerField(
        default=0,
    )

    is_active = models.BooleanField(
        default=True,
    )

    display_order = models.PositiveIntegerField(
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "track__category__display_order",
            "track__display_order",
            "display_order",
            "name",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "track",
                    "name",
                ],
                name="unique_role_per_track",
            ),
        ]

    def __str__(self):
        return self.name


class RoleSkill(models.Model):
    """
    Connects a Role to a Skill and stores how important
    that skill is for the role.

    This is the core of Track Intelligence.
    """

    class Importance(models.TextChoices):
        REQUIRED = "required", "Required"
        IMPORTANT = "important", "Important"
        OPTIONAL = "optional", "Optional"

    class EvidenceType(models.TextChoices):
        MENTION = "mention", "Mention"
        PROJECT = "project", "Project Evidence"
        EXPERIENCE = "experience", "Experience Evidence"
        CERTIFICATION = "certification", "Certification Evidence"

    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="role_skills",
    )

    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="role_skills",
    )

    importance = models.CharField(
        max_length=20,
        choices=Importance.choices,
        default=Importance.IMPORTANT,
    )

    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10,
    )

    minimum_level = models.PositiveIntegerField(
        default=1,
        help_text="Expected skill level from 1 to 5.",
    )

    evidence_types = models.JSONField(
        default=list,
        blank=True,
    )

    notes = models.TextField(
        blank=True,
    )

    class Meta:
        ordering = [
            "-weight",
            "skill__name",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "role",
                    "skill",
                ],
                name="unique_skill_per_role",
            ),
        ]

    def __str__(self):
        return f"{self.role.name} → {self.skill.name}"


class RoadmapPhase(models.Model):
    """
    Static role-level roadmap phase.

    The personalized roadmap engine will later decide
    which phases/steps the specific user actually needs.
    """

    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="roadmap_phases",
    )

    title = models.CharField(
        max_length=180,
    )

    description = models.TextField(
        blank=True,
    )

    phase_number = models.PositiveIntegerField(
        default=1,
    )

    estimated_weeks = models.PositiveIntegerField(
        default=2,
    )

    is_required = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = [
            "phase_number",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "role",
                    "phase_number",
                ],
                name="unique_roadmap_phase_per_role",
            ),
        ]

    def __str__(self):
        return f"{self.role.name} - {self.title}"


class RoadmapStep(models.Model):
    """
    Individual learning/action step inside a roadmap phase.
    """

    phase = models.ForeignKey(
        RoadmapPhase,
        on_delete=models.CASCADE,
        related_name="steps",
    )

    title = models.CharField(
        max_length=200,
    )

    description = models.TextField(
        blank=True,
    )

    step_number = models.PositiveIntegerField(
        default=1,
    )

    skill = models.ForeignKey(
        Skill,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="roadmap_steps",
    )

    resource_type = models.CharField(
        max_length=50,
        blank=True,
    )

    estimated_hours = models.PositiveIntegerField(
        default=5,
    )

    completion_criteria = models.TextField(
        blank=True,
    )

    is_required = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = [
            "phase__phase_number",
            "step_number",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "phase",
                    "step_number",
                ],
                name="unique_roadmap_step_per_phase",
            ),
        ]

    def __str__(self):
        return f"{self.phase.title} - {self.title}"