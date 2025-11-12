"""Unit tests for FieldValidator (T023-T025)"""

from typing import List

import pytest

from jira_mcp_server.models import FieldSchema, FieldType, FieldValidationError
from jira_mcp_server.validators import FieldValidator


class TestFieldValidator:
    """Test suite for FieldValidator."""

    @pytest.fixture
    def validator(self) -> FieldValidator:
        """Create a FieldValidator instance."""
        return FieldValidator()

    @pytest.fixture
    def sample_schema(self) -> List[FieldSchema]:
        """Create a sample field schema for testing."""
        return [
            FieldSchema(
                key="summary",
                name="Summary",
                type=FieldType.STRING,
                required=True,
                custom=False,
            ),
            FieldSchema(
                key="customfield_10001",
                name="Story Points",
                type=FieldType.NUMBER,
                required=False,
                custom=True,
            ),
            FieldSchema(
                key="priority",
                name="Priority",
                type=FieldType.OPTION,
                required=False,
                allowed_values=["High", "Medium", "Low"],
                custom=False,
            ),
        ]

    def test_validate_required_fields_success(
        self, validator: FieldValidator, sample_schema: List[FieldSchema]
    ) -> None:
        """Test that validation passes when all required fields are present."""
        fields = {"summary": "Test issue", "description": "Test description"}

        errors = validator.validate_required_fields(fields, sample_schema)

        assert len(errors) == 0

    def test_validate_required_fields_missing(
        self, validator: FieldValidator, sample_schema: List[FieldSchema]
    ) -> None:
        """Test that validation fails when required fields are missing."""
        fields = {"description": "Test description"}  # Missing 'summary'

        errors = validator.validate_required_fields(fields, sample_schema)

        assert len(errors) == 1
        assert "Summary" in errors[0]
        assert "Missing required fields" in errors[0]

    def test_validate_custom_field_values_success(
        self, validator: FieldValidator, sample_schema: List[FieldSchema]
    ) -> None:
        """Test that custom field validation passes for valid values."""
        fields = {
            "summary": "Test",
            "customfield_10001": 5,
            "priority": "High",
        }

        errors = validator.validate_custom_field_values(fields, sample_schema)

        assert len(errors) == 0

    def test_validate_custom_field_number_type(
        self, validator: FieldValidator, sample_schema: List[FieldSchema]
    ) -> None:
        """Test that number fields must be numeric."""
        fields = {"customfield_10001": "not a number"}

        errors = validator.validate_custom_field_values(fields, sample_schema)

        assert len(errors) == 1
        assert "Story Points" in errors[0]
        assert "must be a number" in errors[0]

    def test_validate_custom_field_string_type(
        self, validator: FieldValidator, sample_schema: List[FieldSchema]
    ) -> None:
        """Test that string fields must be strings."""
        fields = {"summary": 123}

        errors = validator.validate_custom_field_values(fields, sample_schema)

        assert len(errors) == 1
        assert "Summary" in errors[0]
        assert "must be a string" in errors[0]

    def test_validate_custom_field_option_allowed_values(
        self, validator: FieldValidator, sample_schema: List[FieldSchema]
    ) -> None:
        """Test that option fields validate against allowed values."""
        fields = {"priority": "Invalid"}

        errors = validator.validate_custom_field_values(fields, sample_schema)

        assert len(errors) == 1
        assert "Priority" in errors[0]
        assert "Invalid value" in errors[0]
        assert "High, Medium, Low" in errors[0]

    def test_validate_fields_raises_on_errors(
        self, validator: FieldValidator, sample_schema: List[FieldSchema]
    ) -> None:
        """Test that validate_fields raises FieldValidationError on validation failure."""
        fields = {}  # Missing required 'summary'

        with pytest.raises(FieldValidationError) as exc_info:
            validator.validate_fields(fields, sample_schema)

        assert "Summary" in str(exc_info.value)

    def test_validate_fields_success(self, validator: FieldValidator, sample_schema: List[FieldSchema]) -> None:
        """Test that validate_fields passes for valid input."""
        fields = {"summary": "Valid issue"}

        # Should not raise
        validator.validate_fields(fields, sample_schema)

    def test_validate_array_type(self, validator: FieldValidator) -> None:
        """Test validation of array fields."""
        schema = [
            FieldSchema(
                key="labels",
                name="Labels",
                type=FieldType.ARRAY,
                required=False,
                custom=False,
            )
        ]

        # Valid array
        fields = {"labels": ["bug", "urgent"]}
        errors = validator.validate_custom_field_values(fields, schema)
        assert len(errors) == 0

        # Invalid - not an array
        fields = {"labels": "not an array"}
        errors = validator.validate_custom_field_values(fields, schema)
        assert len(errors) == 1
        assert "must be an array" in errors[0]

    def test_validate_date_type(self, validator: FieldValidator) -> None:
        """Test validation of date fields."""
        schema = [
            FieldSchema(
                key="duedate",
                name="Due Date",
                type=FieldType.DATE,
                required=False,
                custom=False,
            )
        ]

        # Valid date string
        fields = {"duedate": "2024-12-31"}
        errors = validator.validate_custom_field_values(fields, schema)
        assert len(errors) == 0

        # Invalid - not a string
        fields = {"duedate": 20241231}
        errors = validator.validate_custom_field_values(fields, schema)
        assert len(errors) == 1
        assert "must be a date string" in errors[0]

    def test_validate_none_values(self, validator: FieldValidator) -> None:
        """Test that None values are handled correctly."""
        schema = [
            FieldSchema(
                key="optional",
                name="Optional",
                type=FieldType.STRING,
                required=False,
                custom=False,
            )
        ]

        # None for optional field is valid
        fields = {"optional": None}
        errors = validator.validate_custom_field_values(fields, schema)
        assert len(errors) == 0

    def test_validate_unknown_fields_ignored(self, validator: FieldValidator, sample_schema: List[FieldSchema]) -> None:
        """Test that unknown fields are ignored for forward compatibility."""
        fields = {"summary": "Test", "unknown_field": "value"}

        errors = validator.validate_custom_field_values(fields, sample_schema)

        # Should only validate known fields
        assert len(errors) == 0

    def test_validate_required_field_none_value(self, validator: FieldValidator) -> None:
        """Test that None value for required field is rejected."""
        schema = [
            FieldSchema(
                key="summary",
                name="Summary",
                type=FieldType.STRING,
                required=True,
                custom=False,
            )
        ]

        fields = {"summary": None}
        errors = validator.validate_custom_field_values(fields, schema)

        assert len(errors) == 1
        assert "Summary" in errors[0]
        assert "is required" in errors[0]

    def test_validate_multi_select_type(self, validator: FieldValidator) -> None:
        """Test validation of MULTI_SELECT fields."""
        schema = [
            FieldSchema(
                key="components",
                name="Components",
                type=FieldType.MULTI_SELECT,
                required=False,
                allowed_values=["Backend", "Frontend", "Database"],
                custom=False,
            )
        ]

        # Valid multi-select
        fields = {"components": ["Backend", "Frontend"]}
        errors = validator.validate_custom_field_values(fields, schema)
        assert len(errors) == 0

        # Invalid - not a list
        fields = {"components": "Backend"}
        errors = validator.validate_custom_field_values(fields, schema)
        assert len(errors) == 1
        assert "must be a list" in errors[0]

        # Invalid - contains disallowed value
        fields = {"components": ["Backend", "InvalidComponent"]}
        errors = validator.validate_custom_field_values(fields, schema)
        assert len(errors) == 1
        assert "InvalidComponent" in errors[0]
        assert "Backend, Frontend, Database" in errors[0]

    def test_validate_datetime_type(self, validator: FieldValidator) -> None:
        """Test validation of DATETIME fields."""
        schema = [
            FieldSchema(
                key="created",
                name="Created",
                type=FieldType.DATETIME,
                required=False,
                custom=False,
            )
        ]

        # Valid datetime string
        fields = {"created": "2024-12-31T23:59:59"}
        errors = validator.validate_custom_field_values(fields, schema)
        assert len(errors) == 0

        # Invalid - not a string
        fields = {"created": 1234567890}
        errors = validator.validate_custom_field_values(fields, schema)
        assert len(errors) == 1
        assert "must be a datetime string" in errors[0]
