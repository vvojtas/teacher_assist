"""
Database models for the lesson planner application
"""

from django.db import models


class CurriculumReference(models.Model):
    """
    Stores Polish curriculum references (Podstawa Programowa)
    Used for AI generation and tooltip display
    """
    reference_code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Curriculum reference code (e.g., 'I.1.2', '4.15')"
    )
    full_text = models.TextField(
        help_text="Complete Polish text of curriculum requirement"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this reference was added"
    )

    class Meta:
        db_table = 'curriculum_references'
        ordering = ['reference_code']
        verbose_name = "Curriculum Reference"
        verbose_name_plural = "Curriculum References"

    def __str__(self):
        return f"{self.reference_code}: {self.full_text[:50]}..."


class EducationalModule(models.Model):
    """
    Stores educational modules (domains of learning)
    Can be predefined or AI-suggested
    """
    module_name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Name of educational module in Polish"
    )
    is_ai_suggested = models.BooleanField(
        default=True,
        help_text="Whether this module was suggested by AI (not predefined)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this module was added"
    )

    class Meta:
        db_table = 'educational_modules'
        ordering = ['module_name']
        verbose_name = "Educational Module"
        verbose_name_plural = "Educational Modules"

    def __str__(self):
        return self.module_name
