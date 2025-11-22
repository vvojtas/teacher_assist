"""
Tests for the lesson planner application

Tests verify compliance with django_api.md specification.
To run tests: python manage.py test lessonplanner
"""

import json
from unittest.mock import patch
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

    def test_index_page_has_react_root(self):
        """Test that the index page contains React app root element"""
        response = self.client.get(reverse('lessonplanner:index'))
        content = response.content.decode('utf-8')

        # Check for React root div
        self.assertIn('id="root"', content)

    def test_index_page_has_csrf_token_meta(self):
        """Test that the page includes CSRF token in meta tag"""
        response = self.client.get(reverse('lessonplanner:index'))
        content = response.content.decode('utf-8')

        # Check for CSRF meta tag
        self.assertIn('name="csrf-token"', content)
        self.assertIn('content="', content)

    def test_index_page_includes_vite_assets(self):
        """Test that Vite bundled assets are included"""
        response = self.client.get(reverse('lessonplanner:index'))
        content = response.content.decode('utf-8')

        # Check for Vite-bundled JavaScript (module script)
        self.assertIn('type="module"', content)
        self.assertIn('/static/lessonplanner/dist/assets/', content)

    def test_index_page_includes_bundled_css(self):
        """Test that Vite bundled CSS is included"""
        response = self.client.get(reverse('lessonplanner:index'))
        content = response.content.decode('utf-8')

        # Check for bundled CSS file
        self.assertIn('/static/lessonplanner/dist/assets/index-', content)
        self.assertIn('.css', content)

    def test_index_page_has_correct_title(self):
        """Test that the page has the correct title"""
        response = self.client.get(reverse('lessonplanner:index'))
        content = response.content.decode('utf-8')

        # Check for page title
        self.assertIn('Teacher Assist - Planowanie Lekcji', content)


class FillWorkPlanViewTests(TestCase):
    """Tests for POST /api/fill-work-plan endpoint"""

    def setUp(self):
        self.client = Client()
        self.url = reverse('lessonplanner:fill_work_plan')

    def test_fill_work_plan_requires_post(self):
        """Test that the endpoint only accepts POST requests"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)  # Method Not Allowed

    @patch('lessonplanner.services.ai_client.fill_work_plan')
    def test_fill_work_plan_success(self, mock_fill_work_plan):
        """Test successful metadata generation"""
        # Mock AI service response
        mock_fill_work_plan.return_value = {
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

    @patch('lessonplanner.services.ai_client.fill_work_plan')
    def test_fill_work_plan_ai_service_error(self, mock_fill_work_plan):
        """Test error handling: AI service failure"""
        mock_fill_work_plan.side_effect = Exception('AI service error')

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

    @patch('lessonplanner.services.ai_client.requests.post')
    def test_fill_work_plan_integration_flow(self, mock_requests_post):
        """
        Integration test: Verify complete Django -> AI Service -> Response flow.

        This test mocks the HTTP request to AI service and verifies:
        1. Request is sent to correct URL with correct payload
        2. Response is properly parsed and returned to client
        3. All data transformations are correct
        """
        # Mock AI service HTTP response
        mock_response = mock_requests_post.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'activity': 'Zabawa w sklep z owocami',
            'module': 'MATEMATYKA',
            'curriculum_refs': ['4.15', '4.18'],
            'objectives': [
                'Dziecko potrafi przeliczać w zakresie 5',
                'Rozpoznaje poznane wcześniej cyfry'
            ]
        }

        # Make request to Django endpoint
        response = self.client.post(
            self.url,
            data=json.dumps({
                'activity': 'Zabawa w sklep z owocami',
                'theme': 'Jesień - zbiory'
            }),
            content_type='application/json'
        )

        # Verify Django response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['module'], 'MATEMATYKA')
        self.assertIn('4.15', data['curriculum_refs'])
        self.assertEqual(len(data['objectives']), 2)

        # Verify HTTP request was made correctly
        mock_requests_post.assert_called_once()
        call_args = mock_requests_post.call_args

        # Check URL
        self.assertIn('/api/fill-work-plan', call_args[0][0])

        # Check payload
        sent_payload = call_args[1]['json']
        self.assertEqual(sent_payload['activity'], 'Zabawa w sklep z owocami')
        self.assertEqual(sent_payload['theme'], 'Jesień - zbiory')

        # Check headers and timeout
        self.assertEqual(call_args[1]['headers']['Content-Type'], 'application/json')
        self.assertEqual(call_args[1]['timeout'], 120)

    @patch('lessonplanner.services.ai_client.requests.post')
    def test_fill_work_plan_connection_error_handling(self, mock_requests_post):
        """Test that connection errors are properly handled in integration flow"""
        # Simulate connection error
        mock_requests_post.side_effect = __import__('requests').exceptions.ConnectionError(
            'Connection refused'
        )

        response = self.client.post(
            self.url,
            data=json.dumps({
                'activity': 'Test activity',
                'theme': 'Test theme'
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 503)
        data = response.json()
        self.assertEqual(data['error_code'], 'AI_SERVICE_UNAVAILABLE')

    @patch('lessonplanner.services.ai_client.requests.post')
    def test_fill_work_plan_timeout_error_handling(self, mock_requests_post):
        """Test that timeout errors are properly handled in integration flow"""
        # Simulate timeout
        mock_requests_post.side_effect = __import__('requests').exceptions.Timeout()

        response = self.client.post(
            self.url,
            data=json.dumps({
                'activity': 'Test activity',
                'theme': 'Test theme'
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 504)
        data = response.json()
        self.assertEqual(data['error_code'], 'AI_SERVICE_TIMEOUT')

    def test_fill_work_plan_csrf_required(self):
        """Test that CSRF token validation is enforced"""
        # Create client with CSRF checks enabled
        from django.test import Client as CSRFClient
        csrf_client = CSRFClient(enforce_csrf_checks=True)

        # Request without CSRF token should fail
        response = csrf_client.post(
            self.url,
            data=json.dumps({
                'activity': 'Test activity',
                'theme': 'Test theme'
            }),
            content_type='application/json'
        )

        # Should return 403 Forbidden due to missing CSRF token
        self.assertEqual(response.status_code, 403)

    def test_fill_work_plan_csrf_with_valid_token(self):
        """Test that request with valid CSRF token succeeds"""
        from django.test import Client as CSRFClient
        from django.middleware.csrf import get_token

        # Create client with CSRF checks enabled
        csrf_client = CSRFClient(enforce_csrf_checks=True)

        # Get CSRF token by visiting index page
        index_response = csrf_client.get(reverse('lessonplanner:index'))
        csrf_token = get_token(index_response.wsgi_request)

        # Make request with valid CSRF token in header
        with self.settings(CSRF_USE_SESSIONS=False, CSRF_COOKIE_HTTPONLY=False):
            response = csrf_client.post(
                self.url,
                data=json.dumps({
                    'activity': 'Test activity',
                    'theme': 'Test theme'
                }),
                content_type='application/json',
                HTTP_X_CSRFTOKEN=csrf_token
            )

        # Note: This will still fail with 500 because we're not mocking fill_work_plan,
        # but it proves CSRF validation passed (403 would indicate CSRF failure)
        self.assertNotEqual(response.status_code, 403)


class CurriculumRefsViewTests(TestCase):
    """Tests for GET /api/curriculum-refs endpoint"""

    def setUp(self):
        self.client = Client()
        self.url = reverse('lessonplanner:curriculum_refs_all')

    def test_get_all_curriculum_refs_success(self):
        """Test successful retrieval of all curriculum references (mock data)"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn('references', data)
        self.assertIn('count', data)
        # Database has 52 references from migration
        self.assertEqual(data['count'], 52)
        self.assertIn('1.1', data['references'])
        self.assertIn('2.5', data['references'])
        self.assertIn('3.8', data['references'])
        self.assertIn('4.15', data['references'])
        self.assertIn('4.18', data['references'])


class CurriculumRefByCodeViewTests(TestCase):
    """Tests for GET /api/curriculum-refs/<code> endpoint"""

    def setUp(self):
        self.client = Client()

    def test_get_curriculum_ref_by_code_success(self):
        """Test successful retrieval of curriculum reference by code (database)"""
        url = reverse('lessonplanner:curriculum_ref_by_code', args=['3.8'])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data['reference_code'], '3.8')
        self.assertEqual(data['full_text'], 'obdarza uwagą inne dzieci i osoby dorosłe')
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

    def test_get_modules_all(self):
        """Test retrieval of all modules (mock data)"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn('modules', data)
        self.assertIn('count', data)
        # Mock data has 12 modules
        self.assertEqual(data['count'], 12)

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

        # Database has 12 non-AI-suggested modules (all predefined)
        self.assertEqual(data['count'], 12)
        for module in data['modules']:
            self.assertFalse(module['is_ai_suggested'])

    def test_get_modules_filter_ai_suggested_true(self):
        """Test filtering by is_ai_suggested=true"""
        response = self.client.get(self.url, {'ai_suggested': 'true'})

        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Database has 0 AI-suggested modules initially (none created yet)
        self.assertEqual(data['count'], 0)
        for module in data['modules']:
            self.assertTrue(module['is_ai_suggested'])


# ============================================================================
# Model Tests
# ============================================================================

from lessonplanner.models import (
    MajorCurriculumReference,
    CurriculumReference,
    EducationalModule,
    WorkPlan,
    WorkPlanEntry,
    WorkPlanEntryCurriculumRef
)
from django.db import IntegrityError


class MajorCurriculumReferenceModelTest(TestCase):
    """Tests for MajorCurriculumReference model."""

    def test_create_major_reference(self):
        """Test creating a major curriculum reference."""
        major_ref = MajorCurriculumReference.objects.create(
            reference_code="99",
            full_text="Fizyczny obszar rozwoju dziecka"
        )
        self.assertEqual(major_ref.reference_code, "99")
        self.assertEqual(major_ref.full_text, "Fizyczny obszar rozwoju dziecka")
        self.assertIsNotNone(major_ref.created_at)

    def test_major_reference_str(self):
        """Test string representation."""
        major_ref = MajorCurriculumReference.objects.create(
            reference_code="99",
            full_text="Fizyczny obszar rozwoju dziecka"
        )
        self.assertIn("99:", str(major_ref))


class CurriculumReferenceModelTest(TestCase):
    """Tests for CurriculumReference model."""

    def setUp(self):
        """Set up test data."""
        self.major_ref = MajorCurriculumReference.objects.create(
            reference_code="99",
            full_text="Poznawczy obszar rozwoju dziecka"
        )

    def test_create_curriculum_reference(self):
        """Test creating a curriculum reference."""
        curr_ref = CurriculumReference.objects.create(
            reference_code="99.99",
            full_text="przelicza elementy zbiorów",
            major_reference=self.major_ref
        )
        self.assertEqual(curr_ref.reference_code, "99.99")
        self.assertEqual(curr_ref.major_reference, self.major_ref)

    def test_curriculum_reference_relationship(self):
        """Test relationship with major reference."""
        curr_ref1 = CurriculumReference.objects.create(
            reference_code="99.15",
            full_text="Test 1",
            major_reference=self.major_ref
        )
        curr_ref2 = CurriculumReference.objects.create(
            reference_code="99.18",
            full_text="Test 2",
            major_reference=self.major_ref
        )

        # Test reverse relationship
        self.assertEqual(self.major_ref.curriculum_references.count(), 2)
        self.assertIn(curr_ref1, self.major_ref.curriculum_references.all())
        self.assertIn(curr_ref2, self.major_ref.curriculum_references.all())


class EducationalModuleModelTest(TestCase):
    """Tests for EducationalModule model."""

    def test_create_educational_module(self):
        """Test creating an educational module."""
        module = EducationalModule.objects.create(
            module_name="TEST_MODULE",
            is_ai_suggested=False
        )
        self.assertEqual(module.module_name, "TEST_MODULE")
        self.assertFalse(module.is_ai_suggested)

    def test_module_ai_suggested_default(self):
        """Test that is_ai_suggested defaults to False."""
        module = EducationalModule.objects.create(
            module_name="TEST_MODULE2"
        )
        self.assertFalse(module.is_ai_suggested)


class WorkPlanModelTest(TestCase):
    """Tests for WorkPlan model."""

    def test_create_work_plan_with_theme(self):
        """Test creating a work plan with a theme."""
        plan = WorkPlan.objects.create(theme="Jesień - zbiory test")
        self.assertEqual(plan.theme, "Jesień - zbiory test")
        self.assertIsNotNone(plan.created_at)
        self.assertIsNotNone(plan.updated_at)

    def test_create_work_plan_without_theme(self):
        """Test creating a work plan without a theme."""
        plan = WorkPlan.objects.create()
        self.assertIsNone(plan.theme)

    def test_work_plan_str(self):
        """Test string representation."""
        plan = WorkPlan.objects.create(theme="Jesień - zbiory test")
        self.assertIn("Jesień - zbiory test", str(plan))


class WorkPlanEntryModelTest(TestCase):
    """Tests for WorkPlanEntry model."""

    def setUp(self):
        """Set up test data."""
        self.work_plan = WorkPlan.objects.create(theme="Test Theme")
        self.module, _ = EducationalModule.objects.get_or_create(
            module_name="MATEMATYKA",
            defaults={'is_ai_suggested': False}
        )
        self.major_ref = MajorCurriculumReference.objects.create(
            reference_code="99",
            full_text="Poznawczy obszar"
        )
        self.curr_ref1 = CurriculumReference.objects.create(
            reference_code="99.15",
            full_text="przelicza elementy zbiorów",
            major_reference=self.major_ref
        )
        self.curr_ref2 = CurriculumReference.objects.create(
            reference_code="99.18",
            full_text="rozpoznaje cyfry",
            major_reference=self.major_ref
        )

    def test_create_work_plan_entry(self):
        """Test creating a work plan entry."""
        entry = WorkPlanEntry.objects.create(
            work_plan=self.work_plan,
            activity="Zabawa w sklep z owocami test",
            objectives="Dziecko potrafi przeliczać",
            is_example=True
        )
        entry.modules.add(self.module)

        self.assertEqual(entry.activity, "Zabawa w sklep z owocami test")
        self.assertEqual(entry.modules.count(), 1)
        self.assertIn(self.module, entry.modules.all())
        self.assertTrue(entry.is_example)

    def test_work_plan_entry_cascade_delete(self):
        """Test that deleting work plan deletes entries."""
        entry = WorkPlanEntry.objects.create(
            work_plan=self.work_plan,
            activity="Test activity"
        )
        entry_id = entry.id

        # Delete work plan
        self.work_plan.delete()

        # Entry should be deleted
        self.assertEqual(WorkPlanEntry.objects.filter(id=entry_id).count(), 0)

    def test_work_plan_entry_curriculum_refs_relationship(self):
        """Test many-to-many relationship with curriculum references."""
        entry = WorkPlanEntry.objects.create(
            work_plan=self.work_plan,
            activity="Test activity"
        )
        entry.modules.add(self.module)

        # Add curriculum references
        entry.curriculum_references.add(self.curr_ref1, self.curr_ref2)

        # Test relationship
        self.assertEqual(entry.curriculum_references.count(), 2)
        self.assertIn(self.curr_ref1, entry.curriculum_references.all())
        self.assertIn(self.curr_ref2, entry.curriculum_references.all())

    def test_work_plan_entry_is_example_default(self):
        """Test that is_example defaults to False."""
        entry = WorkPlanEntry.objects.create(
            work_plan=self.work_plan,
            activity="Test activity"
        )
        self.assertFalse(entry.is_example)


class DatabaseMigrationDataTest(TestCase):
    """Tests to verify that migration data was populated correctly."""

    def test_major_curriculum_references_populated(self):
        """Test that major curriculum references were created."""
        count = MajorCurriculumReference.objects.count()
        self.assertGreaterEqual(count, 4, "Should have at least 4 major references")

    def test_curriculum_references_populated(self):
        """Test that curriculum references were created."""
        count = CurriculumReference.objects.count()
        self.assertGreaterEqual(count, 50, "Should have at least 50 curriculum references")

    def test_educational_modules_populated(self):
        """Test that educational modules were created."""
        count = EducationalModule.objects.count()
        self.assertGreaterEqual(count, 12, "Should have at least 12 modules")

        # Check specific modules from PRD
        self.assertTrue(
            EducationalModule.objects.filter(module_name="MATEMATYKA").exists()
        )
        self.assertTrue(
            EducationalModule.objects.filter(module_name="JĘZYK").exists()
        )

    def test_example_work_plans_populated(self):
        """Test that example work plans were created."""
        count = WorkPlan.objects.count()
        self.assertGreaterEqual(count, 2, "Should have at least 2 example work plans")

    def test_example_work_plan_entries_populated(self):
        """Test that example work plan entries were created."""
        count = WorkPlanEntry.objects.filter(is_example=True).count()
        self.assertGreaterEqual(count, 4, "Should have at least 4 example entries")

        # Check that example entries have curriculum references
        example_entry = WorkPlanEntry.objects.filter(is_example=True).first()
        self.assertIsNotNone(example_entry)
        self.assertGreater(
            example_entry.curriculum_references.count(),
            0,
            "Example entries should have curriculum references"
        )

