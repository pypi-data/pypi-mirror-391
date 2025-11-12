"""Unit tests for models module."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from jira_mcp_server.models import (
    FieldSchema,
    FieldType,
    FieldValidationError,
    Issue,
    JiraAPIError,
)


class TestFieldSchema:
    """Test FieldSchema model."""

    def test_valid_field_schema(self) -> None:
        """Test creating a valid field schema."""
        schema = FieldSchema(
            key="summary",
            name="Summary",
            type=FieldType.STRING,
            required=True,
            custom=False,
        )
        assert schema.key == "summary"
        assert schema.name == "Summary"

    def test_custom_field_key_validation(self) -> None:
        """Test that customfield_ prefix is allowed."""
        schema = FieldSchema(
            key="customfield_10001",
            name="Story Points",
            type=FieldType.NUMBER,
            required=False,
            custom=True,
        )
        assert schema.key == "customfield_10001"

    def test_invalid_field_key(self) -> None:
        """Test that invalid field keys are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            FieldSchema(
                key="invalid key!",  # Contains space and special char
                name="Invalid",
                type=FieldType.STRING,
                required=False,
                custom=False,
            )

        assert "Invalid field key" in str(exc_info.value)


class TestIssue:
    """Test Issue model."""

    def test_valid_issue(self) -> None:
        """Test creating a valid issue."""
        issue = Issue(
            key="PROJ-123",
            id="10001",
            self="https://jira.example.com/rest/api/2/issue/10001",
            project="PROJ",
            issue_type="Task",
            summary="Test issue",
            status="Open",
            created=datetime.now(),
            updated=datetime.now(),
        )
        assert issue.key == "PROJ-123"
        assert issue.summary == "Test issue"

    def test_invalid_issue_key_no_hyphen(self) -> None:
        """Test that issue key without hyphen is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            Issue(
                key="INVALID",  # No hyphen and number
                id="10001",
                self="https://jira.example.com/rest/api/2/issue/10001",
                project="PROJ",
                issue_type="Task",
                summary="Test",
                status="Open",
                created=datetime.now(),
                updated=datetime.now(),
            )

        # Pydantic's pattern validator catches this first
        assert "pattern" in str(exc_info.value).lower()

    def test_invalid_issue_key_empty(self) -> None:
        """Test that empty issue key is rejected."""
        with pytest.raises(ValidationError):
            Issue(
                key="",  # Empty
                id="10001",
                self="https://jira.example.com/rest/api/2/issue/10001",
                project="PROJ",
                issue_type="Task",
                summary="Test",
                status="Open",
                created=datetime.now(),
                updated=datetime.now(),
            )


class TestJiraAPIError:
    """Test JiraAPIError exception."""

    def test_jira_api_error_with_errors(self) -> None:
        """Test creating JiraAPIError with Jira error list."""
        error = JiraAPIError("API request failed", jira_errors=["Field summary is required", "Invalid priority"])

        assert str(error) == "API request failed"
        assert error.jira_errors == ["Field summary is required", "Invalid priority"]

    def test_jira_api_error_without_errors(self) -> None:
        """Test creating JiraAPIError without error list."""
        error = JiraAPIError("Generic API error")

        assert str(error) == "Generic API error"
        assert error.jira_errors == []


class TestFieldValidationError:
    """Test FieldValidationError exception."""

    def test_field_validation_error(self) -> None:
        """Test creating FieldValidationError."""
        error = FieldValidationError("customfield_10001", "Must be a number")

        assert error.field_name == "customfield_10001"
        assert error.reason == "Must be a number"
        assert "Field 'customfield_10001' validation failed" in str(error)
        assert "Must be a number" in str(error)
