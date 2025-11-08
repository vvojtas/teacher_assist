"""
Tests for the lesson planner application
"""

from django.test import TestCase, Client
from django.urls import reverse


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


class GenerateMetadataViewTests(TestCase):
    """Tests for the generate metadata API endpoint"""

    def setUp(self):
        """Set up test client"""
        self.client = Client()
        self.url = reverse('lessonplanner:generate_metadata')

    def test_generate_metadata_requires_post(self):
        """Test that the endpoint only accepts POST requests"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)  # Method Not Allowed

    def test_generate_metadata_rejects_empty_activity(self):
        """Test that empty activity is rejected"""
        response = self.client.post(
            self.url,
            data='{"activity": "", "theme": "Test"}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['error_code'], 'VALIDATION_ERROR')

    def test_generate_metadata_rejects_long_activity(self):
        """Test that activity longer than 500 characters is rejected"""
        long_activity = 'a' * 501
        response = self.client.post(
            self.url,
            data=f'{{"activity": "{long_activity}", "theme": "Test"}}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['error_code'], 'VALIDATION_ERROR')

    def test_generate_metadata_rejects_long_theme(self):
        """Test that theme longer than 200 characters is rejected"""
        long_theme = 'a' * 201
        response = self.client.post(
            self.url,
            data=f'{{"activity": "Test", "theme": "{long_theme}"}}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['error_code'], 'VALIDATION_ERROR')

    def test_generate_metadata_rejects_invalid_json(self):
        """Test that invalid JSON is rejected"""
        response = self.client.post(
            self.url,
            data='not valid json',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['error_code'], 'INVALID_JSON')


class GenerateBulkViewTests(TestCase):
    """Tests for the bulk generate metadata API endpoint"""

    def setUp(self):
        """Set up test client"""
        self.client = Client()
        self.url = reverse('lessonplanner:generate_bulk')

    def test_generate_bulk_requires_post(self):
        """Test that the endpoint only accepts POST requests"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)  # Method Not Allowed

    def test_generate_bulk_rejects_empty_activities(self):
        """Test that empty activities list is rejected"""
        response = self.client.post(
            self.url,
            data='{"theme": "Test", "activities": []}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['error_code'], 'VALIDATION_ERROR')

    def test_generate_bulk_rejects_invalid_json(self):
        """Test that invalid JSON is rejected"""
        response = self.client.post(
            self.url,
            data='not valid json',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['error_code'], 'INVALID_JSON')


class CurriculumTooltipViewTests(TestCase):
    """Tests for the curriculum tooltip API endpoint"""

    def setUp(self):
        """Set up test client"""
        self.client = Client()

    def test_curriculum_tooltip_requires_get(self):
        """Test that the endpoint only accepts GET requests"""
        url = reverse('lessonplanner:curriculum_tooltip', args=['I.1.2'])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 405)  # Method Not Allowed

    def test_curriculum_tooltip_accepts_valid_code(self):
        """Test that a valid curriculum code is accepted"""
        url = reverse('lessonplanner:curriculum_tooltip', args=['I.1.2'])
        response = self.client.get(url)
        # Response should be either 200 (if found) or 404 (if not found in mock)
        self.assertIn(response.status_code, [200, 404])