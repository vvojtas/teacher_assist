"""
Tests for validation nodes.

Tests input validation, output validation, and lenient mode filtering.
"""

import pytest
from ai_service.nodes.validators import validate_input, validate_output, parse_llm_response


class TestInputValidation:
    """Tests for input validator node."""

    def test_valid_input(self):
        """Test that valid input passes validation."""
        state = {
            "activity": "Zabawa w sklep z owocami",
            "theme": "Jesień - zbiory"
        }
        result = validate_input(state)

        assert result["validation_passed"] is True
        assert result["validation_errors"] == []
        assert result["activity"] == "Zabawa w sklep z owocami"
        assert result["theme"] == "Jesień - zbiory"

    def test_empty_activity(self):
        """Test that empty activity fails validation."""
        state = {
            "activity": "   ",
            "theme": "Jesień"
        }
        result = validate_input(state)

        assert result["validation_passed"] is False
        assert len(result["validation_errors"]) > 0
        assert any("activity" in err.lower() for err in result["validation_errors"])

    def test_activity_too_long(self):
        """Test that activity exceeding 500 chars fails."""
        state = {
            "activity": "A" * 501,
            "theme": ""
        }
        result = validate_input(state)

        assert result["validation_passed"] is False
        assert any("500" in err for err in result["validation_errors"])

    def test_theme_too_long(self):
        """Test that theme exceeding 200 chars fails."""
        state = {
            "activity": "Valid activity",
            "theme": "T" * 201
        }
        result = validate_input(state)

        assert result["validation_passed"] is False
        assert any("200" in err for err in result["validation_errors"])

    def test_whitespace_stripping(self):
        """Test that whitespace is stripped from inputs."""
        state = {
            "activity": "  Activity with spaces  ",
            "theme": "  Theme with spaces  "
        }
        result = validate_input(state)

        assert result["activity"] == "Activity with spaces"
        assert result["theme"] == "Theme with spaces"


class TestOutputValidation:
    """Tests for output validator node (with lenient mode)."""

    def test_valid_output(self):
        """Test that valid output passes validation."""
        state = {
            "llm_parsed_output": {
                "modules": ["MATEMATYKA"],
                "curriculum_refs": ["4.15", "4.18"],
                "objectives": [
                    "Dziecko potrafi przeliczać w zakresie 5",
                    "Rozpoznaje poznane wcześniej cyfry"
                ]
            },
            "available_modules": [
                {"module_name": "MATEMATYKA"},
                {"module_name": "JĘZYK"}
            ],
            "curriculum_refs": [
                {"reference_code": "4.15", "full_text": "...", "major_reference_id": 4},
                {"reference_code": "4.18", "full_text": "...", "major_reference_id": 4}
            ]
        }
        result = validate_output(state)

        assert result["validation_passed"] is True
        assert result["validation_errors"] == []

    def test_missing_required_fields(self):
        """Test that missing fields fail validation."""
        state = {
            "llm_parsed_output": {
                "modules": ["MATEMATYKA"]
                # Missing curriculum_refs and objectives
            },
            "available_modules": [{"module_name": "MATEMATYKA"}],
            "curriculum_refs": []
        }
        result = validate_output(state)

        assert result["validation_passed"] is False
        assert any("curriculum_refs" in err for err in result["validation_errors"])
        assert any("objectives" in err for err in result["validation_errors"])

    def test_invalid_module(self):
        """Test that invalid module fails validation."""
        state = {
            "llm_parsed_output": {
                "modules": ["INVALID_MODULE"],
                "curriculum_refs": ["4.15"],
                "objectives": ["Valid objective that is long enough"]
            },
            "available_modules": [{"module_name": "MATEMATYKA"}],
            "curriculum_refs": [{"reference_code": "4.15", "full_text": "...", "major_reference_id": 4}]
        }
        result = validate_output(state)

        assert result["validation_passed"] is False
        assert any("moduł" in err.lower() for err in result["validation_errors"])

    def test_lenient_mode_filters_invalid_codes(self):
        """Test that lenient mode filters invalid curriculum codes but keeps valid ones."""
        state = {
            "llm_parsed_output": {
                "modules": ["MATEMATYKA"],
                "curriculum_refs": ["4.15", "99.99", "4.18", "invalid"],  # 2 valid, 2 invalid
                "objectives": ["Valid objective that is long enough"]
            },
            "available_modules": [{"module_name": "MATEMATYKA"}],
            "curriculum_refs": [
                {"reference_code": "4.15", "full_text": "...", "major_reference_id": 4},
                {"reference_code": "4.18", "full_text": "...", "major_reference_id": 4}
            ]
        }
        result = validate_output(state)

        # Should pass because at least 1 valid code remains
        assert result["validation_passed"] is True
        # Invalid codes should be filtered out
        assert result["llm_parsed_output"]["curriculum_refs"] == ["4.15", "4.18"]

    def test_lenient_mode_fails_if_all_invalid(self):
        """Test that lenient mode fails if all curriculum codes are invalid."""
        state = {
            "llm_parsed_output": {
                "modules": ["MATEMATYKA"],
                "curriculum_refs": ["99.99", "invalid", "bad"],  # All invalid
                "objectives": ["Valid objective"]
            },
            "available_modules": [{"module_name": "MATEMATYKA"}],
            "curriculum_refs": [
                {"reference_code": "4.15", "full_text": "...", "major_reference_id": 4}
            ]
        }
        result = validate_output(state)

        assert result["validation_passed"] is False
        assert any("nieprawidłowe" in err.lower() for err in result["validation_errors"])

    def test_objectives_too_short(self):
        """Test that objectives shorter than 10 chars fail."""
        state = {
            "llm_parsed_output": {
                "modules": ["MATEMATYKA"],
                "curriculum_refs": ["4.15"],
                "objectives": ["Short"]  # Too short
            },
            "available_modules": [{"module_name": "MATEMATYKA"}],
            "curriculum_refs": [{"reference_code": "4.15", "full_text": "...", "major_reference_id": 4}]
        }
        result = validate_output(state)

        assert result["validation_passed"] is False
        assert any("krótki" in err.lower() for err in result["validation_errors"])

    def test_too_many_modules(self):
        """Test that more than 3 modules fails."""
        state = {
            "llm_parsed_output": {
                "modules": ["MOD1", "MOD2", "MOD3", "MOD4"],  # 4 modules
                "curriculum_refs": ["4.15"],
                "objectives": ["Valid objective"]
            },
            "available_modules": [
                {"module_name": "MOD1"},
                {"module_name": "MOD2"},
                {"module_name": "MOD3"},
                {"module_name": "MOD4"}
            ],
            "curriculum_refs": [{"reference_code": "4.15", "full_text": "...", "major_reference_id": 4}]
        }
        result = validate_output(state)

        assert result["validation_passed"] is False


class TestParseResponse:
    """Tests for LLM response parsing."""

    def test_parse_valid_json(self):
        """Test parsing valid JSON response."""
        state = {
            "llm_raw_response": '{"modules": ["MATEMATYKA"], "curriculum_refs": ["4.15"], "objectives": ["Objective 1"]}'
        }
        result = parse_llm_response(state)

        assert "llm_parsed_output" in result
        assert result["llm_parsed_output"]["modules"] == ["MATEMATYKA"]

    def test_parse_json_with_markdown(self):
        """Test parsing JSON wrapped in markdown code block."""
        state = {
            "llm_raw_response": '```json\n{"modules": ["MATEMATYKA"], "curriculum_refs": ["4.15"], "objectives": ["Obj"]}\n```'
        }
        result = parse_llm_response(state)

        assert "llm_parsed_output" in result
        assert result["llm_parsed_output"]["modules"] == ["MATEMATYKA"]

    def test_parse_invalid_json(self):
        """Test that invalid JSON fails gracefully."""
        state = {
            "llm_raw_response": "This is not JSON at all"
        }
        result = parse_llm_response(state)

        assert result["validation_passed"] is False
        assert len(result["validation_errors"]) > 0
