# Generated manually on 2025-11-22
"""
Migration to convert work_plan_entries.module from ForeignKey to ManyToManyField.

This migration:
1. Creates the work_plan_entry_modules junction table
2. Migrates existing data from module_id to the junction table
3. Removes the module_id column from work_plan_entries
"""

import django.db.models.deletion
from django.db import migrations, models


def migrate_module_data_forward(apps, schema_editor):
    """
    Migrate existing module_id data to the new junction table.

    For each work_plan_entry with a module_id, create a corresponding
    entry in work_plan_entry_modules.
    """
    WorkPlanEntry = apps.get_model('lessonplanner', 'WorkPlanEntry')
    WorkPlanEntryModule = apps.get_model('lessonplanner', 'WorkPlanEntryModule')

    # Get all entries that have a module assigned
    entries_with_modules = WorkPlanEntry.objects.exclude(module_id=None)

    # Create junction table entries
    junction_entries = []
    for entry in entries_with_modules:
        junction_entries.append(
            WorkPlanEntryModule(
                work_plan_entry_id=entry.id,
                module_id=entry.module_id
            )
        )

    # Bulk create for efficiency
    if junction_entries:
        WorkPlanEntryModule.objects.bulk_create(junction_entries)
        print(f"Migrated {len(junction_entries)} module assignments to junction table")


def migrate_module_data_reverse(apps, schema_editor):
    """
    Reverse migration: Copy first module from junction table back to module_id.

    Note: If an entry has multiple modules, only the first one will be preserved.
    """
    WorkPlanEntry = apps.get_model('lessonplanner', 'WorkPlanEntry')
    WorkPlanEntryModule = apps.get_model('lessonplanner', 'WorkPlanEntryModule')

    # Get all junction entries
    junction_entries = WorkPlanEntryModule.objects.select_related('work_plan_entry').all()

    # Group by work_plan_entry_id and take the first module for each entry
    entry_module_map = {}
    for junction_entry in junction_entries:
        entry_id = junction_entry.work_plan_entry_id
        if entry_id not in entry_module_map:
            entry_module_map[entry_id] = junction_entry.module_id

    # Update work plan entries
    for entry_id, module_id in entry_module_map.items():
        WorkPlanEntry.objects.filter(id=entry_id).update(module_id=module_id)

    print(f"Restored module_id for {len(entry_module_map)} entries")


class Migration(migrations.Migration):

    dependencies = [
        ("lessonplanner", "0002_populate_curriculum_data"),
    ]

    operations = [
        # Step 1: Create the WorkPlanEntryModule junction table model
        migrations.CreateModel(
            name="WorkPlanEntryModule",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "module",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        to="lessonplanner.educationalmodule",
                        db_index=True,
                    ),
                ),
                (
                    "work_plan_entry",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="lessonplanner.workplanentry",
                        db_index=True,
                    ),
                ),
            ],
            options={
                "verbose_name": "Work Plan Entry Module",
                "verbose_name_plural": "Work Plan Entry Modules",
                "db_table": "work_plan_entry_modules",
                "unique_together": {("work_plan_entry", "module")},
            },
        ),

        # Step 2: Migrate existing data from module field to junction table
        migrations.RunPython(
            migrate_module_data_forward,
            migrate_module_data_reverse
        ),

        # Step 3: Remove the old module ForeignKey field
        migrations.RemoveField(
            model_name="workplanentry",
            name="module",
        ),

        # Step 4: Add the new ManyToManyField
        migrations.AddField(
            model_name="workplanentry",
            name="modules",
            field=models.ManyToManyField(
                help_text="Educational modules (AI can suggest new modules)",
                related_name="work_plan_entries",
                through="lessonplanner.WorkPlanEntryModule",
                to="lessonplanner.educationalmodule",
            ),
        ),
    ]
