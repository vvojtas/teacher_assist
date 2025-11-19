"""
Unit tests for lessonplanner.services.db_service module.

Tests cover all database query functions for curriculum references and modules.
"""

from django.test import TestCase
from lessonplanner.models import (
    CurriculumReference,
    MajorCurriculumReference,
    EducationalModule
)
from lessonplanner.services import db_service


class GetAllCurriculumRefsTests(TestCase):
    """Tests for get_all_curriculum_refs() function"""

    def setUp(self):
        """Create test data"""
        # Create major reference with unique code
        self.major_ref = MajorCurriculumReference.objects.create(
            reference_code='99',
            full_text='Major reference 99'
        )

        # Create curriculum references
        self.ref1 = CurriculumReference.objects.create(
            reference_code='99.1',
            full_text='Test reference 99.1 text',
            major_reference=self.major_ref
        )
        self.ref2 = CurriculumReference.objects.create(
            reference_code='99.2',
            full_text='Test reference 99.2 text',
            major_reference=self.major_ref
        )
        self.ref3 = CurriculumReference.objects.create(
            reference_code='99.5',
            full_text='Test reference 99.5 text',
            major_reference=self.major_ref
        )

    def test_returns_dict(self):
        """Test that function returns a dictionary"""
        result = db_service.get_all_curriculum_refs()
        self.assertIsInstance(result, dict)

    def test_returns_all_refs(self):
        """Test that all curriculum references are returned"""
        result = db_service.get_all_curriculum_refs()
        # Migration creates 52 refs, plus our 3 test refs = 55
        self.assertEqual(len(result), 55)

    def test_dict_keys_are_reference_codes(self):
        """Test that dictionary keys are reference codes"""
        result = db_service.get_all_curriculum_refs()
        self.assertIn('99.1', result)
        self.assertIn('99.2', result)
        self.assertIn('99.5', result)

    def test_dict_values_are_full_text(self):
        """Test that dictionary values are full text"""
        result = db_service.get_all_curriculum_refs()
        self.assertEqual(result['99.1'], 'Test reference 99.1 text')
        self.assertEqual(result['99.2'], 'Test reference 99.2 text')
        self.assertEqual(result['99.5'], 'Test reference 99.5 text')

    def test_returns_empty_dict_when_no_refs(self):
        """Test that empty dict is returned when no refs exist"""
        # Delete work plans first to avoid foreign key constraints
        from lessonplanner.models import WorkPlan
        WorkPlan.objects.all().delete()
        CurriculumReference.objects.all().delete()
        result = db_service.get_all_curriculum_refs()
        self.assertEqual(result, {})

    def test_refs_ordered_by_code(self):
        """Test that refs are ordered by reference_code"""
        result = db_service.get_all_curriculum_refs()
        keys = list(result.keys())
        # Verify our test refs are present and in order
        self.assertIn('99.1', keys)
        self.assertIn('99.2', keys)
        self.assertIn('99.5', keys)
        # Verify ordering: 99.1 should come before 99.2, 99.2 before 99.5
        idx_991 = keys.index('99.1')
        idx_992 = keys.index('99.2')
        idx_995 = keys.index('99.5')
        self.assertLess(idx_991, idx_992)
        self.assertLess(idx_992, idx_995)


class GetCurriculumRefByCodeTests(TestCase):
    """Tests for get_curriculum_ref_by_code() function"""

    def setUp(self):
        """Create test data"""
        self.major_ref = MajorCurriculumReference.objects.create(
            reference_code='98',
            full_text='Major reference 98'
        )

        self.ref = CurriculumReference.objects.create(
            reference_code='98.1',
            full_text='Test reference text',
            major_reference=self.major_ref
        )

    def test_returns_curriculum_reference_object(self):
        """Test that function returns CurriculumReference object"""
        result = db_service.get_curriculum_ref_by_code('98.1')
        self.assertIsInstance(result, CurriculumReference)

    def test_returns_correct_reference(self):
        """Test that correct reference is returned"""
        result = db_service.get_curriculum_ref_by_code('98.1')
        self.assertEqual(result.reference_code, '98.1')
        self.assertEqual(result.full_text, 'Test reference text')

    def test_returns_none_when_not_found(self):
        """Test that None is returned when reference doesn't exist"""
        result = db_service.get_curriculum_ref_by_code('97.97')
        self.assertIsNone(result)

    def test_returns_none_for_empty_code(self):
        """Test that None is returned for empty code"""
        result = db_service.get_curriculum_ref_by_code('')
        self.assertIsNone(result)

    def test_case_sensitive_lookup(self):
        """Test that code lookup is case-sensitive"""
        result = db_service.get_curriculum_ref_by_code('98.1')
        self.assertIsNotNone(result)
        # Assuming codes are lowercase in database


class GetAllModulesTests(TestCase):
    """Tests for get_all_modules() function"""

    def setUp(self):
        """Create test data"""
        self.module1 = EducationalModule.objects.create(
            module_name='TEST_MODULE_1',
            is_ai_suggested=False
        )
        self.module2 = EducationalModule.objects.create(
            module_name='TEST_MODULE_2',
            is_ai_suggested=False
        )
        self.module3 = EducationalModule.objects.create(
            module_name='TEST_AI_MODULE',
            is_ai_suggested=True
        )

    def test_returns_list(self):
        """Test that function returns a list"""
        result = db_service.get_all_modules()
        self.assertIsInstance(result, list)

    def test_returns_all_modules_when_no_filter(self):
        """Test that all modules are returned when no filter is applied"""
        result = db_service.get_all_modules()
        # Migration creates 12 modules, plus our 3 test modules = 15
        self.assertEqual(len(result), 15)

    def test_returns_dict_with_correct_structure(self):
        """Test that each module dict has correct structure"""
        result = db_service.get_all_modules()
        module = result[0]
        self.assertIn('id', module)
        self.assertIn('name', module)
        self.assertIn('is_ai_suggested', module)
        self.assertIn('created_at', module)

    def test_returns_correct_module_data(self):
        """Test that module data is correct"""
        result = db_service.get_all_modules()
        # Find TEST_AI_MODULE in results
        ai_module = next(m for m in result if m['name'] == 'TEST_AI_MODULE')
        self.assertEqual(ai_module['id'], self.module3.id)
        self.assertTrue(ai_module['is_ai_suggested'])

    def test_filter_by_ai_suggested_false(self):
        """Test filtering by is_ai_suggested=False"""
        result = db_service.get_all_modules(ai_suggested=False)
        # Migration creates 12 non-AI modules, plus our 2 test modules = 14
        self.assertEqual(len(result), 14)
        for module in result:
            self.assertFalse(module['is_ai_suggested'])

    def test_filter_by_ai_suggested_true(self):
        """Test filtering by is_ai_suggested=True"""
        result = db_service.get_all_modules(ai_suggested=True)
        # Only our TEST_AI_MODULE
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0]['is_ai_suggested'])
        self.assertEqual(result[0]['name'], 'TEST_AI_MODULE')

    def test_modules_ordered_by_name(self):
        """Test that modules are ordered by module_name"""
        result = db_service.get_all_modules()
        names = [m['name'] for m in result]
        # Should be in alphabetical order
        self.assertEqual(names, sorted(names))

    def test_returns_empty_list_when_no_modules(self):
        """Test that empty list is returned when no modules exist"""
        # Delete work plans first to avoid foreign key constraints
        from lessonplanner.models import WorkPlan
        WorkPlan.objects.all().delete()
        EducationalModule.objects.all().delete()
        result = db_service.get_all_modules()
        self.assertEqual(result, [])

    def test_created_at_is_iso_format(self):
        """Test that created_at is in ISO format string"""
        result = db_service.get_all_modules()
        created_at = result[0]['created_at']
        self.assertIsInstance(created_at, str)
        # Should contain ISO format indicators
        self.assertIn('T', created_at)
        self.assertIn(':', created_at)


class IntegrationTests(TestCase):
    """Integration tests for db_service functions"""

    def setUp(self):
        """Create comprehensive test data"""
        self.major_ref = MajorCurriculumReference.objects.create(
            reference_code='96',
            full_text='Major curriculum section 96'
        )

        self.ref1 = CurriculumReference.objects.create(
            reference_code='96.15',
            full_text='przelicza elementy zbiorów',
            major_reference=self.major_ref
        )
        self.ref2 = CurriculumReference.objects.create(
            reference_code='96.18',
            full_text='rozpoznaje cyfry',
            major_reference=self.major_ref
        )

        self.module1 = EducationalModule.objects.create(
            module_name='TEST_INT_MATEMATYKA',
            is_ai_suggested=False
        )
        self.module2 = EducationalModule.objects.create(
            module_name='TEST_INT_JĘZYK',
            is_ai_suggested=False
        )

    def test_get_all_refs_and_get_by_code_consistency(self):
        """Test that get_all_refs and get_by_code return consistent data"""
        all_refs = db_service.get_all_curriculum_refs()
        ref_by_code = db_service.get_curriculum_ref_by_code('96.15')

        self.assertEqual(all_refs['96.15'], ref_by_code.full_text)

    def test_get_all_modules_returns_consistent_data(self):
        """Test that get_all_modules returns consistent data"""
        all_modules = db_service.get_all_modules()

        # Verify at least our test modules are present
        module_names = [m['name'] for m in all_modules]
        self.assertIn('TEST_INT_MATEMATYKA', module_names)
        self.assertIn('TEST_INT_JĘZYK', module_names)

    def test_multiple_queries_return_same_data(self):
        """Test that multiple calls return consistent data"""
        result1 = db_service.get_all_modules()
        result2 = db_service.get_all_modules()

        # Both calls should return same number of modules
        self.assertEqual(len(result1), len(result2))

        # Module names should be the same
        names1 = [m['name'] for m in result1]
        names2 = [m['name'] for m in result2]
        self.assertEqual(names1, names2)

    def test_database_transaction_isolation(self):
        """Test that functions work correctly with database transactions"""
        # Get initial count
        initial_refs = db_service.get_all_curriculum_refs()
        initial_count = len(initial_refs)

        # Add new reference
        new_ref = CurriculumReference.objects.create(
            reference_code='96.99',
            full_text='New reference',
            major_reference=self.major_ref
        )

        # Verify new reference is returned
        updated_refs = db_service.get_all_curriculum_refs()
        self.assertEqual(len(updated_refs), initial_count + 1)
        self.assertIn('96.99', updated_refs)
