from django.db import models


class MajorCurriculumReference(models.Model):
    """
    Stores major sections of Polish kindergarten curriculum (Podstawa Programowa).
    Examples: "1", "2", "3", "4" representing top-level curriculum areas.
    """
    reference_code = models.CharField(
        max_length=10,
        unique=True,
        db_index=True,
        help_text="Major section code (e.g., '4', '3')"
    )
    full_text = models.TextField(
        help_text="Complete Polish text for major section"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'major_curriculum_references'
        verbose_name = 'Major Curriculum Reference'
        verbose_name_plural = 'Major Curriculum References'
        ordering = ['reference_code']

    def __str__(self):
        return f"{self.reference_code}: {self.full_text[:50]}..."


class CurriculumReference(models.Model):
    """
    Stores detailed Polish kindergarten curriculum paragraph references
    (Podstawa Programowa) and their complete text descriptions.
    Examples: "4.15", "3.8", "2.5"
    """
    reference_code = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text="Curriculum code (e.g., '4.15', '2.5')"
    )
    full_text = models.TextField(
        help_text="Complete Polish curriculum requirement text"
    )
    major_reference = models.ForeignKey(
        MajorCurriculumReference,
        on_delete=models.RESTRICT,
        related_name='curriculum_references',
        db_index=True,
        help_text="Parent major curriculum section"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'curriculum_references'
        verbose_name = 'Curriculum Reference'
        verbose_name_plural = 'Curriculum References'
        ordering = ['reference_code']

    def __str__(self):
        return f"{self.reference_code}: {self.full_text[:50]}..."


class EducationalModule(models.Model):
    """
    Stores educational module categories (e.g., MATEMATYKA, JĘZYK, MOTORYKA DUŻA).
    Tracks both predefined modules and AI-suggested modules.
    """
    module_name = models.CharField(
        max_length=200,
        unique=True,
        db_index=True,
        help_text="Module name in Polish (e.g., 'MATEMATYKA')"
    )
    is_ai_suggested = models.BooleanField(
        default=False,
        help_text="TRUE if AI-suggested, FALSE if predefined"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'educational_modules'
        verbose_name = 'Educational Module'
        verbose_name_plural = 'Educational Modules'
        ordering = ['module_name']

    def __str__(self):
        return self.module_name


class WorkPlan(models.Model):
    """
    Stores weekly lesson plans with their themes.
    Each work plan represents a complete weekly planning session.
    """
    theme = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text="Weekly theme (optional, e.g., 'Jesień - zbiory')"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'work_plans'
        verbose_name = 'Work Plan'
        verbose_name_plural = 'Work Plans'
        ordering = ['-created_at']

    def __str__(self):
        return f"Work Plan: {self.theme or 'No theme'} ({self.created_at.strftime('%Y-%m-%d')})"


class WorkPlanEntry(models.Model):
    """
    Stores individual activity rows within a work plan.
    Each entry corresponds to one row in the UI table.
    """
    work_plan = models.ForeignKey(
        WorkPlan,
        on_delete=models.CASCADE,
        related_name='entries',
        db_index=True,
        help_text="Parent work plan"
    )
    module = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text="Educational module name (e.g., 'MATEMATYKA')"
    )
    objectives = models.TextField(
        null=True,
        blank=True,
        help_text="Educational objectives (typically 2-3 items)"
    )
    activity = models.CharField(
        max_length=500,
        help_text="Activity description (required)"
    )
    curriculum_references = models.ManyToManyField(
        CurriculumReference,
        through='WorkPlanEntryCurriculumRef',
        related_name='work_plan_entries',
        help_text="Curriculum references for this activity"
    )
    is_example = models.BooleanField(
        default=False,
        db_index=True,
        help_text="TRUE if should be used as LLM training example"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'work_plan_entries'
        verbose_name = 'Work Plan Entry'
        verbose_name_plural = 'Work Plan Entries'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.activity[:50]}... ({self.module or 'No module'})"


class WorkPlanEntryCurriculumRef(models.Model):
    """
    Junction table implementing many-to-many relationship between
    work plan entries and curriculum references.
    """
    work_plan_entry = models.ForeignKey(
        WorkPlanEntry,
        on_delete=models.CASCADE,
        db_index=True
    )
    curriculum_reference = models.ForeignKey(
        CurriculumReference,
        on_delete=models.RESTRICT,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'work_plan_entry_curriculum_refs'
        verbose_name = 'Work Plan Entry Curriculum Reference'
        verbose_name_plural = 'Work Plan Entry Curriculum References'
        unique_together = [['work_plan_entry', 'curriculum_reference']]

    def __str__(self):
        return f"{self.work_plan_entry.activity[:30]}... -> {self.curriculum_reference.reference_code}"
