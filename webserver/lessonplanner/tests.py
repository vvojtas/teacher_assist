"""
Tests for the lesson planner application

Tests verify compliance with django_api.md specification.
To run tests: python manage.py test lessonplanner
"""

import json
from unittest.mock import patch
from django.test import TestCase, Client
from django.urls import reverse

from .models import CurriculumReference, EducationalModule


class LessonPlannerViewTests(TestCase):
    """Tests for the lesson planner view"""

    def setUp(self):
        """Set up test client"""
        self.client = Client()

    def test_index_view_renders(self):
        """Test that the index page renders successfully"""
        response = self.client.get(reverse('lessonplanner:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lessonplanner/index.html')

    def test_index_page_has_required_elements(self):
        """Test that the index page contains all required UI elements"""
        response = self.client.get(reverse('lessonplanner:index'))
        content = response.content.decode('utf-8')

        # Check for main buttons
        self.assertIn('id="bulkGenerateBtn"', content)
        self.assertIn('id="addRowBtn"', content)
        self.assertIn('id="clearAllBtn"', content)
        self.assertIn('id="copyTableBtn"', content)

        # Check for copy button with correct text
        self.assertIn('Skopiuj tabelę', content)

        # Check for table structure
        self.assertIn('id="planTable"', content)
        self.assertIn('id="planTableBody"', content)

        # Check for theme input
        self.assertIn('id="themeInput"', content)

    def test_index_page_has_row_checkboxes(self):
        """Test that the row template includes checkboxes for copy functionality"""
        response = self.client.get(reverse('lessonplanner:index'))
        content = response.content.decode('utf-8')

        # Check for checkbox in row template
        self.assertIn('class="form-check-input row-checkbox', content)
        self.assertIn('type="checkbox"', content)

    def test_index_page_has_table_headers(self):
        """Test that the table has correct column headers"""
        response = self.client.get(reverse('lessonplanner:index'))
        content = response.content.decode('utf-8')

        # Check for all column headers
        self.assertIn('Moduł', content)
        self.assertIn('Podstawa Programowa', content)
        self.assertIn('Cele', content)
        self.assertIn('Aktywność', content)

    def test_index_page_includes_javascript_files(self):
        """Test that all required JavaScript files are loaded"""
        response = self.client.get(reverse('lessonplanner:index'))
        content = response.content.decode('utf-8')

        # Check for JavaScript files
        self.assertIn('modalHelper.js', content)
        self.assertIn('tableManager.js', content)
        self.assertIn('aiService.js', content)
        self.assertIn('planner.js', content)

    def test_index_page_includes_css_file(self):
        """Test that the custom CSS file is loaded"""
        response = self.client.get(reverse('lessonplanner:index'))
        content = response.content.decode('utf-8')

        # Check for CSS file
        self.assertIn('planner.css', content)

    def test_index_page_has_modals(self):
        """Test that the page includes all required Bootstrap modals"""
        response = self.client.get(reverse('lessonplanner:index'))
        content = response.content.decode('utf-8')

        # Check for modals
        self.assertIn('id="errorModal"', content)
        self.assertIn('id="confirmModal"', content)
        self.assertIn('id="alertModal"', content)


class FillWorkPlanViewTests(TestCase):
    """Tests for POST /api/fill-work-plan endpoint"""

    def setUp(self):
        self.client = Client()
        self.url = reverse('lessonplanner:fill_work_plan')

    def test_fill_work_plan_requires_post(self):
        """Test that the endpoint only accepts POST requests"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)  # Method Not Allowed

    @patch('lessonplanner.services.ai_client.generate_metadata')
    def test_fill_work_plan_success(self, mock_generate):
        """Test successful metadata generation"""
        # Mock AI service response
        mock_generate.return_value = {
            'module': 'MATEMATYKA',
            'curriculum_refs': ['4.15', '4.18'],
            'objectives': [
                'Dziecko potrafi przeliczać w zakresie 5',
                'Rozpoznaje poznane wcześniej cyfry'
            ]
        }

        # Make request
        response = self.client.post(
            self.url,
            data=json.dumps({
                'activity': 'Zabawa w sklep z owocami',
                'theme': 'Jesień - zbiory'
            }),
            content_type='application/json'
        )

        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['module'], 'MATEMATYKA')
        self.assertIn('4.15', data['curriculum_refs'])
        self.assertEqual(len(data['objectives']), 2)

    def test_fill_work_plan_empty_activity(self):
        """Test validation: empty activity field"""
        response = self.client.post(
            self.url,
            data=json.dumps({
                'activity': '',
                'theme': 'Test theme'
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['error_code'], 'INVALID_INPUT')
        self.assertIn('error', data)

    def test_fill_work_plan_activity_too_long(self):
        """Test validation: activity exceeds 500 chars"""
        response = self.client.post(
            self.url,
            data=json.dumps({
                'activity': 'a' * 501,  # 501 characters
                'theme': 'Test'
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['error_code'], 'INVALID_INPUT')

    def test_fill_work_plan_theme_too_long(self):
        """Test validation: theme exceeds 200 chars"""
        response = self.client.post(
            self.url,
            data=json.dumps({
                'activity': 'Test activity',
                'theme': 'a' * 201  # 201 characters
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['error_code'], 'INVALID_INPUT')

    def test_fill_work_plan_invalid_json(self):
        """Test error handling: invalid JSON"""
        response = self.client.post(
            self.url,
            data='invalid json',
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['error_code'], 'INVALID_INPUT')

    def test_fill_work_plan_missing_activity(self):
        """Test validation: missing required activity field"""
        response = self.client.post(
            self.url,
            data=json.dumps({
                'theme': 'Test theme'
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['error_code'], 'INVALID_INPUT')

    @patch('lessonplanner.services.ai_client.generate_metadata')
    def test_fill_work_plan_ai_service_error(self, mock_generate):
        """Test error handling: AI service failure"""
        mock_generate.side_effect = Exception('AI service error')

        response = self.client.post(
            self.url,
            data=json.dumps({
                'activity': 'Test activity',
                'theme': 'Test theme'
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertEqual(data['error_code'], 'INTERNAL_ERROR')


class CurriculumRefsViewTests(TestCase):
    """Tests for GET /api/curriculum-refs endpoint"""

    def setUp(self):
        self.client = Client()
        self.url = reverse('lessonplanner:curriculum_refs_all')

        # Create test data
        CurriculumReference.objects.create(
            reference_code='1.1',
            full_text='zgłasza potrzeby fizjologiczne, samodzielnie wykonuje podstawowe czynności higieniczne;'
        )
        CurriculumReference.objects.create(
            reference_code='2.5',
            full_text='rozstaje się z rodzicami bez lęku, ma świadomość, że rozstanie takie bywa dłuższe lub krótsze;'
        )
        CurriculumReference.objects.create(
            reference_code='3.8',
            full_text='obdarza uwagą inne dzieci i osoby dorosłe;'
        )

    def test_get_all_curriculum_refs_success(self):
        """Test successful retrieval of all curriculum references"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn('references', data)
        self.assertIn('count', data)
        self.assertEqual(data['count'], 3)
        self.assertIn('1.1', data['references'])
        self.assertIn('2.5', data['references'])
        self.assertIn('3.8', data['references'])

    def test_get_all_curriculum_refs_empty_database(self):
        """Test response when database is empty"""
        CurriculumReference.objects.all().delete()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 0)
        self.assertEqual(data['references'], {})


class CurriculumRefByCodeViewTests(TestCase):
    """Tests for GET /api/curriculum-refs/<code> endpoint"""

    def setUp(self):
        self.client = Client()

        # Create test data
        self.ref = CurriculumReference.objects.create(
            reference_code='3.8',
            full_text='obdarza uwagą inne dzieci i osoby dorosłe;'
        )

    def test_get_curriculum_ref_by_code_success(self):
        """Test successful retrieval of curriculum reference by code"""
        url = reverse('lessonplanner:curriculum_ref_by_code', args=['3.8'])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data['reference_code'], '3.8')
        self.assertEqual(data['full_text'], 'obdarza uwagą inne dzieci i osoby dorosłe;')
        self.assertIn('created_at', data)

    def test_get_curriculum_ref_not_found(self):
        """Test 404 response for non-existent code"""
        url = reverse('lessonplanner:curriculum_ref_by_code', args=['99.99'])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data['error_code'], 'REFERENCE_NOT_FOUND')
        self.assertIn('error', data)

    def test_get_curriculum_ref_invalid_code_format(self):
        """Test 400 response for invalid code format"""
        # Code too long (>20 chars)
        url = reverse('lessonplanner:curriculum_ref_by_code', args=['a' * 21])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['error_code'], 'INVALID_CODE_FORMAT')


class ModulesViewTests(TestCase):
    """Tests for GET /api/modules endpoint"""

    def setUp(self):
        self.client = Client()
        self.url = reverse('lessonplanner:modules')

        # Create test data
        EducationalModule.objects.create(
            module_name='JĘZYK',
            is_ai_suggested=False
        )
        EducationalModule.objects.create(
            module_name='MATEMATYKA',
            is_ai_suggested=False
        )
        EducationalModule.objects.create(
            module_name='MOTORYKA DUŻA',
            is_ai_suggested=False
        )
        EducationalModule.objects.create(
            module_name='CUSTOM MODULE',
            is_ai_suggested=True
        )

    def test_get_modules_all(self):
        """Test retrieval of all modules"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn('modules', data)
        self.assertIn('count', data)
        self.assertEqual(data['count'], 4)

        # Verify structure
        module = data['modules'][0]
        self.assertIn('id', module)
        self.assertIn('name', module)
        self.assertIn('is_ai_suggested', module)
        self.assertIn('created_at', module)

    def test_get_modules_filter_ai_suggested_false(self):
        """Test filtering by is_ai_suggested=false"""
        response = self.client.get(self.url, {'ai_suggested': 'false'})

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data['count'], 3)
        for module in data['modules']:
            self.assertFalse(module['is_ai_suggested'])

    def test_get_modules_filter_ai_suggested_true(self):
        """Test filtering by is_ai_suggested=true"""
        response = self.client.get(self.url, {'ai_suggested': 'true'})

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data['count'], 1)
        self.assertTrue(data['modules'][0]['is_ai_suggested'])

    def test_get_modules_empty_database(self):
        """Test response when database is empty"""
        EducationalModule.objects.all().delete()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 0)
        self.assertEqual(data['modules'], [])


class ModelTests(TestCase):
    """Tests for database models"""

    def test_curriculum_reference_creation(self):
        """Test creating a curriculum reference"""
        ref = CurriculumReference.objects.create(
            reference_code='4.15',
            full_text='Test curriculum text'
        )

        self.assertEqual(ref.reference_code, '4.15')
        self.assertEqual(ref.full_text, 'Test curriculum text')
        self.assertIsNotNone(ref.created_at)

    def test_curriculum_reference_unique_code(self):
        """Test unique constraint on reference_code"""
        CurriculumReference.objects.create(
            reference_code='1.1',
            full_text='Test'
        )

        with self.assertRaises(Exception):
            CurriculumReference.objects.create(
                reference_code='1.1',  # Duplicate
                full_text='Different text'
            )

    def test_educational_module_creation(self):
        """Test creating an educational module"""
        module = EducationalModule.objects.create(
            module_name='JĘZYK',
            is_ai_suggested=False
        )

        self.assertEqual(module.module_name, 'JĘZYK')
        self.assertFalse(module.is_ai_suggested)
        self.assertIsNotNone(module.created_at)

    def test_educational_module_default_ai_suggested(self):
        """Test default value for is_ai_suggested"""
        module = EducationalModule.objects.create(
            module_name='TEST MODULE'
        )

        self.assertTrue(module.is_ai_suggested)

    def test_educational_module_unique_name(self):
        """Test unique constraint on module_name"""
        EducationalModule.objects.create(
            module_name='JĘZYK'
        )

        with self.assertRaises(Exception):
            EducationalModule.objects.create(
                module_name='JĘZYK'  # Duplicate
            )