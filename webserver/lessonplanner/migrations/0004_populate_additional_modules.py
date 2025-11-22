# Generated manually on 2025-11-22
"""
Add additional modules to example work plan entries.

This migration adds the 2nd, 3rd, etc. modules to work plan entries that
have multiple modules in the example data. Migration 0002 only added the
first module (due to ForeignKey limitation), and migration 0003 converted
it to many-to-many.
"""

from django.db import migrations


def add_additional_modules(apps, schema_editor):
    """
    Add additional modules to example entries that have multiple modules.

    This completes the data population started in migration 0002.
    """
    WorkPlanEntry = apps.get_model('lessonplanner', 'WorkPlanEntry')
    EducationalModule = apps.get_model('lessonplanner', 'EducationalModule')
    WorkPlan = apps.get_model('lessonplanner', 'WorkPlan')

    # Same example data structure as in 0002, but we only care about entries with multiple modules
    examples = [
        {
            'theme': """JA W PRZEDSZKOLU
W pierwszym tygodniu odbywają się zajęcia wprowadzające w tematykę projektu. Mają one na celu pobudzenie zainteresowania tematem oraz pokazanie nauczycielowi stanu wiedzy i doświadczeń oraz zasobu słownictwa dzieci.""",
            'entries': [
                {
                    'activity': 'Wprowadzenie do tematu projektu z użyciem wiersza "mam trzy latka", oraz książki "Tosia i Julek idą do przedszkola"',
                    'modules': ['JĘZYK'],  # Single module, skip
                },
                {
                    'activity': 'Praca plastyczna - wspólne tworzenie logo grupy "Promyczki" z użyciem kolorowego papieru, kleju i farby',
                    'modules': ['WSPÓŁPRACA', 'FORMY PLASTYCZNE', 'MOTORYKA MAŁA'],  # Multiple modules!
                },
            ]
        },
        {
            'theme': """JA W PRZEDSZKOLU
W drugim tygodniu dzieci poznają zasady bezpiecznego zachowania się w przedszkolu. Odbywa się to przy użyciu materiałów edukacyjnych, gier i zabaw.""",
            'entries': [
                {
                    'activity': 'Historyjki obrazkowe - wspólne układanie historyjek obrazkowych. Dzieci określają kto znajduje się na poszczególnych obrazkach oraz co robi, a następnie wybierają kolejność zdarzeń. Na końcu opowiadają całą historię.',
                    'modules': ['POZNAWCZE', 'JĘZYKOWE'],  # Multiple modules! Note: JĘZYKOWE might not exist, should be JĘZYK
                },
                {
                    'activity': 'Gasimy pożar - tor przeszkód, dzieci pokonują tor zakończony trafianiem do celu tj. "ugaszenia pożaru".',
                    'modules': ['MOTORYKA DUŻA'],  # Single module, skip
                },
            ]
        }
    ]

    # Build modules map
    modules_map = {mod.module_name: mod for mod in EducationalModule.objects.all()}

    # For each example, find the work plan and add additional modules
    added_count = 0
    for example in examples:
        # Find the work plan by theme
        try:
            work_plan = WorkPlan.objects.get(theme=example['theme'])
        except WorkPlan.DoesNotExist:
            print(f"Warning: Work plan with theme not found: {example['theme'][:50]}...")
            continue

        for entry_data in example['entries']:
            # Skip entries with only one module (already handled by migration 0002)
            if len(entry_data['modules']) <= 1:
                continue

            # Find the entry by activity
            try:
                entry = WorkPlanEntry.objects.get(
                    work_plan=work_plan,
                    activity=entry_data['activity']
                )
            except WorkPlanEntry.DoesNotExist:
                print(f"Warning: Entry not found: {entry_data['activity'][:50]}...")
                continue

            # Add modules beyond the first one (first was added in migration 0002)
            for module_name in entry_data['modules'][1:]:
                # Handle case where 'JĘZYKOWE' should be 'JĘZYK'
                if module_name == 'JĘZYKOWE':
                    module_name = 'JĘZYK'

                if module_name in modules_map:
                    entry.modules.add(modules_map[module_name])
                    added_count += 1
                else:
                    print(f"Warning: Module '{module_name}' not found")

    print(f"Added {added_count} additional module associations to example entries")


def remove_additional_modules(apps, schema_editor):
    """
    Reverse migration: Remove additional modules, leaving only the first one.
    """
    WorkPlanEntry = apps.get_model('lessonplanner', 'WorkPlanEntry')
    WorkPlanEntryModule = apps.get_model('lessonplanner', 'WorkPlanEntryModule')

    # For each example entry, keep only the first module association
    example_entries = WorkPlanEntry.objects.filter(is_example=True)

    removed_count = 0
    for entry in example_entries:
        # Get all module associations for this entry
        module_associations = WorkPlanEntryModule.objects.filter(
            work_plan_entry=entry
        ).order_by('id')

        # Delete all but the first
        if module_associations.count() > 1:
            associations_to_delete = module_associations[1:]
            count = len(associations_to_delete)
            for assoc in associations_to_delete:
                assoc.delete()
            removed_count += count

    print(f"Removed {removed_count} additional module associations")


class Migration(migrations.Migration):

    dependencies = [
        ("lessonplanner", "0003_convert_module_to_many_to_many"),
    ]

    operations = [
        migrations.RunPython(
            add_additional_modules,
            remove_additional_modules
        ),
    ]
