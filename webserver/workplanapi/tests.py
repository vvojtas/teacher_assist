"""
Unit tests for workplanapi endpoints.

Tests all API endpoints with both success and error cases.
"""

import json
from django.test import TestCase, Client
from django.urls import reverse


class FillWorkPlanViewTests(TestCase):
    """
    Test suite for POST /api/fill-work-plan endpoint.
    """

    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.url = reverse('fill_work_plan')

    def test_valid_request_returns_200(self):
        """Valid POST with activity should return 200 and mock data."""
        data = {
            'activity': 'Zabawa w sklep z owocami'
        }
        response = self.client.post(
            self.url,
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn('module', response_data)
        self.assertIn('curriculum_refs', response_data)
        self.assertIn('objectives', response_data)
        self.assertEqual(response_data['module'], 'MATEMATYKA')
        self.assertIsInstance(response_data['curriculum_refs'], list)
        self.assertIsInstance(response_data['objectives'], list)

    def test_missing_activity_returns_400(self):
        """Empty or missing activity field should return 400."""
        data = {}
        response = self.client.post(
            self.url,
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn('error', response_data)
        self.assertIn('error_code', response_data)

    def test_activity_too_long_returns_400(self):
        """Activity longer than 500 characters should return 400."""
        data = {
            'activity': 'A' * 501  # 501 characters
        }
        response = self.client.post(
            self.url,
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn('error', response_data)
        self.assertIn('error_code', response_data)

    def test_optional_theme_works(self):
        """Request with theme parameter should succeed."""
        data = {
            'activity': 'Zabawa w sklep',
            'theme': 'Jesień - zbiory'
        }
        response = self.client.post(
            self.url,
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn('module', response_data)

    def test_invalid_json_returns_400(self):
        """Malformed JSON should return 400."""
        response = self.client.post(
            self.url,
            data='invalid json',
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn('error', response_data)

    def test_get_method_not_allowed(self):
        """GET request to POST endpoint should return 405."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)


class CurriculumRefsViewTests(TestCase):
    """
    Test suite for curriculum references endpoints.
    """

    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.list_url = reverse('get_curriculum_refs')

    def test_get_all_refs_returns_200(self):
        """GET /api/curriculum-refs should return 200."""
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)

    def test_response_has_correct_structure(self):
        """Response should have 'references' and 'count' fields."""
        response = self.client.get(self.list_url)
        response_data = response.json()

        self.assertIn('references', response_data)
        self.assertIn('count', response_data)
        self.assertIsInstance(response_data['references'], dict)
        self.assertIsInstance(response_data['count'], int)
        self.assertEqual(response_data['count'], len(response_data['references']))

    def test_get_ref_by_code_valid(self):
        """GET /api/curriculum-refs/3.8 should return 200."""
        url = reverse('get_curriculum_ref_by_code', kwargs={'code': '3.8'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data['reference_code'], '3.8')

    def test_get_ref_by_code_not_found(self):
        """Invalid code should return 404."""
        url = reverse('get_curriculum_ref_by_code', kwargs={'code': '99.99'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
        response_data = response.json()
        self.assertIn('error', response_data)
        self.assertIn('error_code', response_data)
        self.assertEqual(response_data['error_code'], 'REFERENCE_NOT_FOUND')

    def test_get_ref_by_code_structure(self):
        """Response should have reference_code, full_text, created_at."""
        url = reverse('get_curriculum_ref_by_code', kwargs={'code': '1.1'})
        response = self.client.get(url)
        response_data = response.json()

        self.assertIn('reference_code', response_data)
        self.assertIn('full_text', response_data)
        self.assertIn('created_at', response_data)
        self.assertIsInstance(response_data['full_text'], str)
        self.assertTrue(len(response_data['full_text']) > 0)


class ModulesViewTests(TestCase):
    """
    Test suite for GET /api/modules endpoint.
    """

    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.url = reverse('get_modules')

    def test_get_all_modules_returns_200(self):
        """GET /api/modules should return 200."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_modules_response_structure(self):
        """Response should have 'modules' array and 'count'."""
        response = self.client.get(self.url)
        response_data = response.json()

        self.assertIn('modules', response_data)
        self.assertIn('count', response_data)
        self.assertIsInstance(response_data['modules'], list)
        self.assertIsInstance(response_data['count'], int)
        self.assertEqual(response_data['count'], len(response_data['modules']))

        # Check first module structure
        if response_data['modules']:
            module = response_data['modules'][0]
            self.assertIn('id', module)
            self.assertIn('name', module)
            self.assertIn('is_ai_suggested', module)
            self.assertIn('created_at', module)

    def test_filter_by_ai_suggested_false(self):
        """Query param ai_suggested=false should filter correctly."""
        response = self.client.get(self.url, {'ai_suggested': 'false'})

        self.assertEqual(response.status_code, 200)
        response_data = response.json()

        # All mock modules have is_ai_suggested=False
        self.assertEqual(response_data['count'], 4)
        for module in response_data['modules']:
            self.assertFalse(module['is_ai_suggested'])

    def test_filter_by_ai_suggested_true(self):
        """Query param ai_suggested=true should filter correctly."""
        response = self.client.get(self.url, {'ai_suggested': 'true'})

        self.assertEqual(response.status_code, 200)
        response_data = response.json()

        # No mock modules have is_ai_suggested=True
        self.assertEqual(response_data['count'], 0)
        self.assertEqual(len(response_data['modules']), 0)

    def test_no_filter_returns_all_modules(self):
        """Without filter parameter, should return all modules."""
        response = self.client.get(self.url)
        response_data = response.json()

        self.assertEqual(response_data['count'], 4)
        self.assertEqual(len(response_data['modules']), 4)
