"""Unit tests for issue tools (T026-T033)"""

from typing import List
from unittest.mock import Mock, patch

import pytest

from jira_mcp_server.config import JiraConfig
from jira_mcp_server.models import FieldSchema, FieldType, FieldValidationError
from jira_mcp_server.tools.issue_tools import (
    _get_field_schema,
    initialize_issue_tools,
    jira_issue_create,
    jira_issue_get,
    jira_issue_update,
)


@pytest.fixture
def mock_config() -> JiraConfig:
    """Create a test configuration."""
    return JiraConfig(url="https://jira.test.com", token="test-token")


@pytest.fixture
def sample_schema() -> List[FieldSchema]:
    """Create a sample field schema."""
    return [
        FieldSchema(
            key="summary",
            name="Summary",
            type=FieldType.STRING,
            required=True,
            custom=False,
        ),
        FieldSchema(
            key="description",
            name="Description",
            type=FieldType.STRING,
            required=False,
            custom=False,
        ),
        FieldSchema(
            key="customfield_10001",
            name="Story Points",
            type=FieldType.NUMBER,
            required=False,
            custom=True,
        ),
    ]


class TestIssueToolsInitialization:
    """Test issue tools initialization."""

    def test_initialize_issue_tools(self, mock_config: JiraConfig) -> None:
        """Test that initialize_issue_tools sets up global instances."""
        # Just test that it doesn't raise an error
        initialize_issue_tools(mock_config)
        # The globals are set, but we can't easily test them directly
        # Integration will be tested through the function tests


class TestIssueCreate:
    """Test jira_issue_create function."""

    @patch("jira_mcp_server.tools.issue_tools._client", None)
    @patch("jira_mcp_server.tools.issue_tools._validator", None)
    def test_create_issue_not_initialized(self) -> None:
        """Test that RuntimeError is raised when tools not initialized."""
        with pytest.raises(RuntimeError, match="Issue tools not initialized"):
            jira_issue_create(project="PROJ", summary="Test", issue_type="Task")

    @patch("jira_mcp_server.tools.issue_tools._validator")
    @patch("jira_mcp_server.tools.issue_tools._client")
    @patch("jira_mcp_server.tools.issue_tools._cache")
    def test_create_issue_success(
        self, mock_cache: Mock, mock_client: Mock, mock_validator: Mock, sample_schema: List[FieldSchema]
    ) -> None:
        """Test successful issue creation."""
        # Mock cache to return None (cache miss)
        mock_cache.get.return_value = None

        # Mock client to return schema and created issue
        mock_client.get_project_schema.return_value = [
            {
                "key": "summary",
                "name": "Summary",
                "required": True,
                "schema": {"type": "string"},
            }
        ]
        mock_client.create_issue.return_value = {
            "key": "PROJ-123",
            "id": "10001",
        }

        result = jira_issue_create(project="PROJ", summary="Test issue", issue_type="Task")

        assert result["key"] == "PROJ-123"
        assert result["id"] == "10001"
        mock_client.create_issue.assert_called_once()

    @patch("jira_mcp_server.tools.issue_tools._validator")
    @patch("jira_mcp_server.tools.issue_tools._client")
    @patch("jira_mcp_server.tools.issue_tools._cache")
    def test_create_issue_with_all_optional_fields(
        self, mock_cache: Mock, mock_client: Mock, mock_validator: Mock
    ) -> None:
        """Test issue creation with all optional fields."""
        mock_cache.get.return_value = None
        mock_client.get_project_schema.return_value = [
            {"key": "summary", "name": "Summary", "required": True, "schema": {"type": "string"}}
        ]
        mock_client.create_issue.return_value = {"key": "PROJ-124", "id": "10002"}

        result = jira_issue_create(
            project="PROJ",
            summary="Test issue",
            issue_type="Task",
            description="Test description",
            priority="High",
            assignee="john.doe",
            labels=["backend", "urgent"],
            due_date="2025-12-31",
        )

        assert result["key"] == "PROJ-124"
        call_args = mock_client.create_issue.call_args[0][0]
        assert call_args["fields"]["description"] == "Test description"
        assert call_args["fields"]["priority"] == {"name": "High"}
        assert call_args["fields"]["assignee"] == {"name": "john.doe"}
        assert call_args["fields"]["labels"] == ["backend", "urgent"]
        assert call_args["fields"]["duedate"] == "2025-12-31"

    @patch("jira_mcp_server.tools.issue_tools._validator")
    @patch("jira_mcp_server.tools.issue_tools._get_field_schema")
    @patch("jira_mcp_server.tools.issue_tools._client")
    def test_create_issue_with_custom_fields(
        self, mock_client: Mock, mock_get_schema: Mock, mock_validator: Mock, sample_schema: List[FieldSchema]
    ) -> None:
        """Test issue creation with custom fields."""
        mock_get_schema.return_value = sample_schema
        mock_client.create_issue.return_value = {
            "key": "PROJ-124",
            "id": "10002",
        }

        result = jira_issue_create(project="PROJ", summary="Test issue", issue_type="Task", customfield_10001=5)

        assert result["key"] == "PROJ-124"
        call_args = mock_client.create_issue.call_args[0][0]
        assert call_args["fields"]["customfield_10001"] == 5

    @patch("jira_mcp_server.tools.issue_tools._validator")
    @patch("jira_mcp_server.tools.issue_tools._client")
    @patch("jira_mcp_server.tools.issue_tools._cache")
    def test_create_issue_validation_error(
        self, mock_cache: Mock, mock_client: Mock, mock_validator: Mock, sample_schema: List[FieldSchema]
    ) -> None:
        """Test that validation errors are raised."""
        # Mock cache to return None
        mock_cache.get.return_value = None

        # Mock client to return schema
        mock_client.get_project_schema.return_value = [
            {
                "key": "summary",
                "name": "Summary",
                "required": True,
                "schema": {"type": "string"},
            }
        ]

        # Mock validator to raise validation error
        mock_validator.validate_fields.side_effect = FieldValidationError("validation", "Summary is required")

        with pytest.raises(ValueError, match="Validation failed"):
            jira_issue_create(
                project="PROJ",
                summary="",  # Empty summary should fail
                issue_type="Task",
            )

    @patch("jira_mcp_server.tools.issue_tools._get_field_schema")
    def test_create_issue_schema_fetch_error(self, mock_get_schema: Mock) -> None:
        """Test error handling when schema fetch fails."""
        mock_get_schema.side_effect = Exception("Failed to fetch schema")

        with pytest.raises(ValueError, match="Failed to get project schema"):
            jira_issue_create(project="PROJ", summary="Test", issue_type="Task")

    @patch("jira_mcp_server.tools.issue_tools._validator")
    @patch("jira_mcp_server.tools.issue_tools._client")
    @patch("jira_mcp_server.tools.issue_tools._cache")
    def test_create_issue_api_error(self, mock_cache: Mock, mock_client: Mock, mock_validator: Mock) -> None:
        """Test error handling when API create fails."""
        mock_cache.get.return_value = None
        mock_client.get_project_schema.return_value = [
            {"key": "summary", "name": "Summary", "required": True, "schema": {"type": "string"}}
        ]
        mock_client.create_issue.side_effect = Exception("API error")

        with pytest.raises(ValueError, match="Failed to create issue"):
            jira_issue_create(project="PROJ", summary="Test", issue_type="Task")


class TestIssueUpdate:
    """Test jira_issue_update function."""

    def setup_method(self) -> None:
        """Setup for each test."""
        config = JiraConfig(url="https://jira.test.com", token="test-token")
        initialize_issue_tools(config)

    @patch("jira_mcp_server.tools.issue_tools._client", None)
    def test_update_issue_not_initialized(self) -> None:
        """Test that RuntimeError is raised when tools not initialized."""
        with pytest.raises(RuntimeError, match="Issue tools not initialized"):
            jira_issue_update(issue_key="PROJ-123", summary="Test")

    @patch("jira_mcp_server.tools.issue_tools._client")
    def test_update_issue_success(self, mock_client: Mock) -> None:
        """Test successful issue update."""
        mock_client.get_issue.return_value = {
            "key": "PROJ-123",
            "id": "10001",
            "fields": {"summary": "Updated summary"},
        }

        result = jira_issue_update(issue_key="PROJ-123", summary="Updated summary")

        assert result["key"] == "PROJ-123"
        mock_client.update_issue.assert_called_once()

    @patch("jira_mcp_server.tools.issue_tools._client")
    def test_update_issue_with_all_optional_fields(self, mock_client: Mock) -> None:
        """Test issue update with all optional fields."""
        mock_client.get_issue.return_value = {
            "key": "PROJ-123",
            "id": "10001",
            "fields": {"summary": "Updated"},
        }

        result = jira_issue_update(
            issue_key="PROJ-123",
            summary="Updated summary",
            description="Updated description",
            priority="Critical",
            assignee="jane.doe",
            labels=["frontend"],
            due_date="2025-11-30",
            customfield_10001=10,
        )

        assert result["key"] == "PROJ-123"
        call_args = mock_client.update_issue.call_args[0][1]
        assert call_args["fields"]["summary"] == "Updated summary"
        assert call_args["fields"]["description"] == "Updated description"
        assert call_args["fields"]["priority"] == {"name": "Critical"}
        assert call_args["fields"]["assignee"] == {"name": "jane.doe"}
        assert call_args["fields"]["labels"] == ["frontend"]
        assert call_args["fields"]["duedate"] == "2025-11-30"
        assert call_args["fields"]["customfield_10001"] == 10

    @patch("jira_mcp_server.tools.issue_tools._client")
    def test_update_issue_no_fields_error(self, mock_client: Mock) -> None:
        """Test that error is raised when no fields provided."""
        with pytest.raises(ValueError, match="No fields provided to update"):
            jira_issue_update(issue_key="PROJ-123")

    @patch("jira_mcp_server.tools.issue_tools._client")
    def test_update_issue_api_error(self, mock_client: Mock) -> None:
        """Test error handling for API errors."""
        mock_client.update_issue.side_effect = Exception("API error")

        with pytest.raises(ValueError, match="Failed to update issue"):
            jira_issue_update(issue_key="PROJ-123", summary="New summary")


class TestIssueGet:
    """Test jira_issue_get function."""

    def setup_method(self) -> None:
        """Setup for each test."""
        config = JiraConfig(url="https://jira.test.com", token="test-token")
        initialize_issue_tools(config)

    @patch("jira_mcp_server.tools.issue_tools._client", None)
    def test_get_issue_not_initialized(self) -> None:
        """Test that RuntimeError is raised when tools not initialized."""
        with pytest.raises(RuntimeError, match="Issue tools not initialized"):
            jira_issue_get(issue_key="PROJ-123")

    @patch("jira_mcp_server.tools.issue_tools._client")
    def test_get_issue_success(self, mock_client: Mock) -> None:
        """Test successful issue retrieval."""
        mock_client.get_issue.return_value = {
            "key": "PROJ-123",
            "id": "10001",
            "fields": {
                "summary": "Test issue",
                "status": {"name": "Open"},
            },
        }

        result = jira_issue_get(issue_key="PROJ-123")

        assert result["key"] == "PROJ-123"
        assert result["fields"]["summary"] == "Test issue"
        mock_client.get_issue.assert_called_once_with("PROJ-123")

    @patch("jira_mcp_server.tools.issue_tools._client")
    def test_get_issue_not_found(self, mock_client: Mock) -> None:
        """Test error when issue not found."""
        mock_client.get_issue.side_effect = Exception("Issue not found")

        with pytest.raises(ValueError, match="Failed to get issue"):
            jira_issue_get(issue_key="PROJ-999")


class TestGetFieldSchema:
    """Test _get_field_schema function."""

    def setup_method(self) -> None:
        """Setup for each test."""
        config = JiraConfig(url="https://jira.test.com", token="test-token")
        initialize_issue_tools(config)

    @patch("jira_mcp_server.tools.issue_tools._client", None)
    @patch("jira_mcp_server.tools.issue_tools._cache", None)
    def test_get_field_schema_not_initialized(self) -> None:
        """Test that RuntimeError is raised when tools not initialized."""
        with pytest.raises(RuntimeError, match="Issue tools not initialized"):
            _get_field_schema("PROJ", "Task")

    @patch("jira_mcp_server.tools.issue_tools._cache")
    @patch("jira_mcp_server.tools.issue_tools._client")
    def test_get_field_schema_cache_hit(
        self, mock_client: Mock, mock_cache: Mock, sample_schema: List[FieldSchema]
    ) -> None:
        """Test that cached schema is returned when available."""
        mock_cache.get.return_value = sample_schema

        result = _get_field_schema("PROJ", "Task")

        assert result == sample_schema
        mock_cache.get.assert_called_once_with("PROJ", "Task")
        mock_client.get_project_schema.assert_not_called()

    @patch("jira_mcp_server.tools.issue_tools._cache")
    @patch("jira_mcp_server.tools.issue_tools._client")
    def test_get_field_schema_cache_miss(self, mock_client: Mock, mock_cache: Mock) -> None:
        """Test that schema is fetched and cached when not in cache."""
        mock_cache.get.return_value = None
        mock_client.get_project_schema.return_value = [
            {
                "key": "summary",
                "name": "Summary",
                "required": True,
                "schema": {"type": "string"},
            }
        ]

        result = _get_field_schema("PROJ", "Task")

        assert len(result) == 1
        assert result[0].key == "summary"
        mock_cache.set.assert_called_once()

    @patch("jira_mcp_server.tools.issue_tools._cache")
    @patch("jira_mcp_server.tools.issue_tools._client")
    def test_get_field_schema_all_field_types(self, mock_client: Mock, mock_cache: Mock) -> None:
        """Test that all field types are correctly mapped."""
        mock_cache.get.return_value = None
        mock_client.get_project_schema.return_value = [
            {"key": "field1", "name": "Number Field", "required": False, "schema": {"type": "number"}},
            {"key": "field2", "name": "Date Field", "required": False, "schema": {"type": "date"}},
            {"key": "field3", "name": "DateTime Field", "required": False, "schema": {"type": "datetime"}},
            {"key": "field4", "name": "User Field", "required": False, "schema": {"type": "user"}},
            {"key": "field5", "name": "Option Field", "required": False, "schema": {"type": "option"}},
            {"key": "field6", "name": "Array Field", "required": False, "schema": {"type": "array"}},
        ]

        result = _get_field_schema("PROJ", "Task")

        assert len(result) == 6
        assert result[0].type == FieldType.NUMBER
        assert result[1].type == FieldType.DATE
        assert result[2].type == FieldType.DATETIME
        assert result[3].type == FieldType.USER
        assert result[4].type == FieldType.OPTION
        assert result[5].type == FieldType.ARRAY

    @patch("jira_mcp_server.tools.issue_tools._cache")
    @patch("jira_mcp_server.tools.issue_tools._client")
    def test_get_field_schema_with_allowed_values(self, mock_client: Mock, mock_cache: Mock) -> None:
        """Test that allowed values are extracted."""
        mock_cache.get.return_value = None
        mock_client.get_project_schema.return_value = [
            {
                "key": "priority",
                "name": "Priority",
                "required": False,
                "schema": {"type": "option"},
                "allowedValues": [
                    {"value": "High"},
                    {"name": "Medium"},
                    {"value": "Low"},
                ],
            }
        ]

        result = _get_field_schema("PROJ", "Task")

        assert len(result) == 1
        assert result[0].allowed_values == ["High", "Medium", "Low"]
