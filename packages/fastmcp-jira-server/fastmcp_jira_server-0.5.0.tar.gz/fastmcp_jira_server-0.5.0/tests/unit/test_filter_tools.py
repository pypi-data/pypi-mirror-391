"""Unit tests for filter tools"""

from unittest.mock import Mock, patch

import pytest

from jira_mcp_server.jira_client import JiraClient
from jira_mcp_server.tools.filter_tools import (
    initialize_filter_tools,
    jira_filter_create,
    jira_filter_delete,
    jira_filter_execute,
    jira_filter_get,
    jira_filter_list,
    jira_filter_update,
)


@pytest.fixture
def mock_client() -> JiraClient:
    """Create a mock JiraClient."""
    return Mock(spec=JiraClient)


class TestFilterToolsInitialization:
    """Test filter tools initialization."""

    def test_initialize_filter_tools(self, mock_client: JiraClient) -> None:
        """Test that initialize_filter_tools sets up global client instance."""
        # Just test that it doesn't raise an error
        initialize_filter_tools(mock_client)
        # The globals are set, but we can't easily test them directly
        # Integration will be tested through the function tests


class TestFilterCreate:
    """Test jira_filter_create function."""

    @patch("jira_mcp_server.tools.filter_tools._client", None)
    def test_create_filter_not_initialized(self) -> None:
        """Test that error is raised when tools not initialized."""
        with pytest.raises(RuntimeError, match="Filter tools not initialized"):
            jira_filter_create(name="Test", jql="project = PROJ")

    @patch("jira_mcp_server.tools.filter_tools._client")
    def test_create_filter_success(self, mock_client: Mock) -> None:
        """Test successful filter creation."""
        mock_client.create_filter.return_value = {
            "id": "10000",
            "name": "My Filter",
            "jql": "project = PROJ",
            "owner": "testuser",
        }

        result = jira_filter_create(name="My Filter", jql="project = PROJ")

        assert result["id"] == "10000"
        assert result["name"] == "My Filter"
        mock_client.create_filter.assert_called_once_with(
            name="My Filter", jql="project = PROJ", description=None, favourite=False
        )

    @patch("jira_mcp_server.tools.filter_tools._client")
    def test_create_filter_with_description(self, mock_client: Mock) -> None:
        """Test filter creation with description."""
        mock_client.create_filter.return_value = {"id": "10000"}

        jira_filter_create(name="My Filter", jql="project = PROJ", description="Test filter")

        mock_client.create_filter.assert_called_once_with(
            name="My Filter", jql="project = PROJ", description="Test filter", favourite=False
        )

    @patch("jira_mcp_server.tools.filter_tools._client")
    def test_create_filter_empty_name_error(self, mock_client: Mock) -> None:
        """Test that error is raised for empty name."""
        with pytest.raises(ValueError, match="Filter name cannot be empty"):
            jira_filter_create(name="", jql="project = PROJ")

    @patch("jira_mcp_server.tools.filter_tools._client")
    def test_create_filter_empty_jql_error(self, mock_client: Mock) -> None:
        """Test that error is raised for empty JQL."""
        with pytest.raises(ValueError, match="JQL query cannot be empty"):
            jira_filter_create(name="Test", jql="")

    @patch("jira_mcp_server.tools.filter_tools._client")
    def test_create_filter_api_error(self, mock_client: Mock) -> None:
        """Test that API errors are wrapped with helpful message."""
        mock_client.create_filter.side_effect = Exception("Permission denied")

        with pytest.raises(ValueError, match="Filter creation failed: Permission denied"):
            jira_filter_create(name="Test", jql="project = PROJ")


class TestFilterList:
    """Test jira_filter_list function."""

    @patch("jira_mcp_server.tools.filter_tools._client", None)
    def test_list_filters_not_initialized(self) -> None:
        """Test that error is raised when tools not initialized."""
        with pytest.raises(RuntimeError, match="Filter tools not initialized"):
            jira_filter_list()

    @patch("jira_mcp_server.tools.filter_tools._client")
    def test_list_filters_success(self, mock_client: Mock) -> None:
        """Test successful filter listing."""
        mock_client.list_filters.return_value = [
            {"id": "10000", "name": "Filter 1"},
            {"id": "10001", "name": "Filter 2"},
        ]

        result = jira_filter_list()

        assert len(result) == 2
        assert result[0]["id"] == "10000"
        mock_client.list_filters.assert_called_once()

    @patch("jira_mcp_server.tools.filter_tools._client")
    def test_list_filters_api_error(self, mock_client: Mock) -> None:
        """Test that API errors are wrapped with helpful message."""
        mock_client.list_filters.side_effect = Exception("Network error")

        with pytest.raises(ValueError, match="Filter list failed: Network error"):
            jira_filter_list()


class TestFilterGet:
    """Test jira_filter_get function."""

    @patch("jira_mcp_server.tools.filter_tools._client", None)
    def test_get_filter_not_initialized(self) -> None:
        """Test that error is raised when tools not initialized."""
        with pytest.raises(RuntimeError, match="Filter tools not initialized"):
            jira_filter_get(filter_id="10000")

    @patch("jira_mcp_server.tools.filter_tools._client")
    def test_get_filter_success(self, mock_client: Mock) -> None:
        """Test successful filter retrieval."""
        mock_client.get_filter.return_value = {
            "id": "10000",
            "name": "My Filter",
            "jql": "project = PROJ",
            "owner": "testuser",
        }

        result = jira_filter_get(filter_id="10000")

        assert result["id"] == "10000"
        assert result["name"] == "My Filter"
        mock_client.get_filter.assert_called_once_with(filter_id="10000")

    @patch("jira_mcp_server.tools.filter_tools._client")
    def test_get_filter_empty_id_error(self, mock_client: Mock) -> None:
        """Test that error is raised for empty filter ID."""
        with pytest.raises(ValueError, match="Filter ID cannot be empty"):
            jira_filter_get(filter_id="")

    @patch("jira_mcp_server.tools.filter_tools._client")
    def test_get_filter_api_error(self, mock_client: Mock) -> None:
        """Test that API errors are wrapped with helpful message."""
        mock_client.get_filter.side_effect = Exception("Filter not found")

        with pytest.raises(ValueError, match="Get filter failed: Filter not found"):
            jira_filter_get(filter_id="10000")


class TestFilterExecute:
    """Test jira_filter_execute function."""

    @patch("jira_mcp_server.tools.filter_tools._client", None)
    def test_execute_filter_not_initialized(self) -> None:
        """Test that error is raised when tools not initialized."""
        with pytest.raises(RuntimeError, match="Filter tools not initialized"):
            jira_filter_execute(filter_id="10000")

    @patch("jira_mcp_server.tools.filter_tools._client")
    def test_execute_filter_success(self, mock_client: Mock) -> None:
        """Test successful filter execution."""
        mock_client.get_filter.return_value = {"id": "10000", "jql": "project = PROJ"}
        mock_client.search_issues.return_value = {"total": 5, "issues": []}

        result = jira_filter_execute(filter_id="10000")

        assert result["total"] == 5
        mock_client.get_filter.assert_called_once_with(filter_id="10000")
        mock_client.search_issues.assert_called_once_with(jql="project = PROJ", max_results=50, start_at=0)

    @patch("jira_mcp_server.tools.filter_tools._client")
    def test_execute_filter_with_pagination(self, mock_client: Mock) -> None:
        """Test filter execution with pagination."""
        mock_client.get_filter.return_value = {"jql": "project = PROJ"}
        mock_client.search_issues.return_value = {"total": 100, "issues": []}

        jira_filter_execute(filter_id="10000", max_results=10, start_at=20)

        mock_client.search_issues.assert_called_once_with(jql="project = PROJ", max_results=10, start_at=20)

    @patch("jira_mcp_server.tools.filter_tools._client")
    def test_execute_filter_empty_id_error(self, mock_client: Mock) -> None:
        """Test that error is raised for empty filter ID."""
        with pytest.raises(ValueError, match="Filter ID cannot be empty"):
            jira_filter_execute(filter_id="")

    @patch("jira_mcp_server.tools.filter_tools._client")
    def test_execute_filter_no_jql_error(self, mock_client: Mock) -> None:
        """Test that error is raised when filter has no JQL."""
        mock_client.get_filter.return_value = {"id": "10000"}

        with pytest.raises(ValueError, match="Filter does not contain a valid JQL query"):
            jira_filter_execute(filter_id="10000")

    @patch("jira_mcp_server.tools.filter_tools._client")
    def test_execute_filter_api_error(self, mock_client: Mock) -> None:
        """Test that API errors are wrapped with helpful message."""
        mock_client.get_filter.side_effect = Exception("Permission denied")

        with pytest.raises(ValueError, match="Filter execution failed: Permission denied"):
            jira_filter_execute(filter_id="10000")


class TestFilterUpdate:
    """Test jira_filter_update function."""

    @patch("jira_mcp_server.tools.filter_tools._client", None)
    def test_update_filter_not_initialized(self) -> None:
        """Test that error is raised when tools not initialized."""
        with pytest.raises(RuntimeError, match="Filter tools not initialized"):
            jira_filter_update(filter_id="10000", name="Updated")

    @patch("jira_mcp_server.tools.filter_tools._client")
    def test_update_filter_success(self, mock_client: Mock) -> None:
        """Test successful filter update."""
        mock_client.update_filter.return_value = {"id": "10000", "name": "Updated"}

        result = jira_filter_update(filter_id="10000", name="Updated")

        assert result["name"] == "Updated"
        mock_client.update_filter.assert_called_once_with(
            filter_id="10000", name="Updated", jql=None, description=None, favourite=None
        )

    @patch("jira_mcp_server.tools.filter_tools._client")
    def test_update_filter_jql_only(self, mock_client: Mock) -> None:
        """Test updating only JQL."""
        mock_client.update_filter.return_value = {"id": "10000"}

        jira_filter_update(filter_id="10000", jql="project = NEW")

        mock_client.update_filter.assert_called_once_with(
            filter_id="10000", name=None, jql="project = NEW", description=None, favourite=None
        )

    @patch("jira_mcp_server.tools.filter_tools._client")
    def test_update_filter_empty_id_error(self, mock_client: Mock) -> None:
        """Test that error is raised for empty filter ID."""
        with pytest.raises(ValueError, match="Filter ID cannot be empty"):
            jira_filter_update(filter_id="", name="Updated")

    @patch("jira_mcp_server.tools.filter_tools._client")
    def test_update_filter_no_fields_error(self, mock_client: Mock) -> None:
        """Test that error is raised when no fields provided."""
        with pytest.raises(ValueError, match="At least one field must be provided to update"):
            jira_filter_update(filter_id="10000")

    @patch("jira_mcp_server.tools.filter_tools._client")
    def test_update_filter_api_error(self, mock_client: Mock) -> None:
        """Test that API errors are wrapped with helpful message."""
        mock_client.update_filter.side_effect = Exception("Permission denied")

        with pytest.raises(ValueError, match="Filter update failed: Permission denied"):
            jira_filter_update(filter_id="10000", name="Updated")


class TestFilterDelete:
    """Test jira_filter_delete function."""

    @patch("jira_mcp_server.tools.filter_tools._client", None)
    def test_delete_filter_not_initialized(self) -> None:
        """Test that error is raised when tools not initialized."""
        with pytest.raises(RuntimeError, match="Filter tools not initialized"):
            jira_filter_delete(filter_id="10000")

    @patch("jira_mcp_server.tools.filter_tools._client")
    def test_delete_filter_success(self, mock_client: Mock) -> None:
        """Test successful filter deletion."""
        mock_client.delete_filter.return_value = None

        result = jira_filter_delete(filter_id="10000")

        assert result["success"] is True
        assert "10000" in result["message"]
        mock_client.delete_filter.assert_called_once_with(filter_id="10000")

    @patch("jira_mcp_server.tools.filter_tools._client")
    def test_delete_filter_empty_id_error(self, mock_client: Mock) -> None:
        """Test that error is raised for empty filter ID."""
        with pytest.raises(ValueError, match="Filter ID cannot be empty"):
            jira_filter_delete(filter_id="")

    @patch("jira_mcp_server.tools.filter_tools._client")
    def test_delete_filter_api_error(self, mock_client: Mock) -> None:
        """Test that API errors are wrapped with helpful message."""
        mock_client.delete_filter.side_effect = Exception("Permission denied")

        with pytest.raises(ValueError, match="Filter deletion failed: Permission denied"):
            jira_filter_delete(filter_id="10000")
