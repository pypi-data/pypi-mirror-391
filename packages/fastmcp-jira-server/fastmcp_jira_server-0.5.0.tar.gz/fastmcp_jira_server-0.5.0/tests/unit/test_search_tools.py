"""Unit tests for search tools"""

from unittest.mock import Mock, patch

import pytest

from jira_mcp_server.jira_client import JiraClient
from jira_mcp_server.tools.search_tools import (
    build_jql_from_criteria,
    initialize_search_tools,
    jira_search_issues,
    jira_search_jql,
)


@pytest.fixture
def mock_client() -> JiraClient:
    """Create a mock JiraClient."""
    return Mock(spec=JiraClient)


class TestSearchToolsInitialization:
    """Test search tools initialization."""

    def test_initialize_search_tools(self, mock_client: JiraClient) -> None:
        """Test that initialize_search_tools sets up global client instance."""
        # Just test that it doesn't raise an error
        initialize_search_tools(mock_client)
        # The globals are set, but we can't easily test them directly
        # Integration will be tested through the function tests


class TestBuildJQLFromCriteria:
    """Test JQL query builder."""

    def test_single_criterion_project(self) -> None:
        """Test building JQL with single project criterion."""
        jql = build_jql_from_criteria(project="PROJ")
        assert jql == "project = PROJ"

    def test_single_criterion_assignee(self) -> None:
        """Test building JQL with assignee."""
        jql = build_jql_from_criteria(assignee="john.doe")
        assert jql == "assignee = john.doe"

    def test_current_user_assignee(self) -> None:
        """Test building JQL with currentUser() function."""
        jql = build_jql_from_criteria(assignee="currentUser()")
        assert jql == "assignee = currentUser()"

    def test_multiple_criteria(self) -> None:
        """Test building JQL with multiple criteria."""
        jql = build_jql_from_criteria(
            project="PROJ",
            status="Open",
            priority="High",
        )
        assert jql == 'project = PROJ AND status = "Open" AND priority = "High"'

    def test_with_labels(self) -> None:
        """Test building JQL with labels."""
        jql = build_jql_from_criteria(labels=["backend", "urgent"])
        assert jql == 'labels = "backend" AND labels = "urgent"'

    def test_with_date_ranges(self) -> None:
        """Test building JQL with date ranges."""
        jql = build_jql_from_criteria(
            created_after="2025-01-01",
            created_before="2025-12-31",
        )
        assert jql == 'created >= "2025-01-01" AND created <= "2025-12-31"'

    def test_with_updated_dates(self) -> None:
        """Test building JQL with updated date ranges."""
        jql = build_jql_from_criteria(
            updated_after="2025-01-01",
            updated_before="2025-01-15",
        )
        assert jql == 'updated >= "2025-01-01" AND updated <= "2025-01-15"'

    def test_complex_query(self) -> None:
        """Test building complex JQL with many criteria."""
        jql = build_jql_from_criteria(
            project="PROJ",
            assignee="john.doe",
            status="In Progress",
            priority="Critical",
            labels=["backend"],
            created_after="2025-01-01",
        )
        expected = (
            'project = PROJ AND assignee = john.doe AND status = "In Progress" '
            'AND priority = "Critical" AND labels = "backend" AND created >= "2025-01-01"'
        )
        assert jql == expected

    def test_empty_criteria(self) -> None:
        """Test building JQL with no criteria returns empty string."""
        jql = build_jql_from_criteria()
        assert jql == ""


class TestSearchIssues:
    """Test jira_search_issues function."""

    @patch("jira_mcp_server.tools.search_tools._client")
    def test_search_with_project(self, mock_client: Mock) -> None:
        """Test searching by project."""
        mock_client.search_issues.return_value = {
            "total": 5,
            "issues": [{"key": "PROJ-1"}, {"key": "PROJ-2"}],
            "maxResults": 50,
            "startAt": 0,
        }

        result = jira_search_issues(project="PROJ")

        assert result["total"] == 5
        assert len(result["issues"]) == 2
        mock_client.search_issues.assert_called_once_with(jql="project = PROJ", max_results=50, start_at=0)

    @patch("jira_mcp_server.tools.search_tools._client")
    def test_search_with_multiple_criteria(self, mock_client: Mock) -> None:
        """Test searching with multiple criteria."""
        mock_client.search_issues.return_value = {"total": 1, "issues": [], "maxResults": 50, "startAt": 0}

        result = jira_search_issues(project="PROJ", status="Open", assignee="john.doe")

        assert result["total"] == 1
        mock_client.search_issues.assert_called_once()
        call_args = mock_client.search_issues.call_args[1]
        assert "project = PROJ" in call_args["jql"]
        assert 'status = "Open"' in call_args["jql"]
        assert "assignee = john.doe" in call_args["jql"]

    @patch("jira_mcp_server.tools.search_tools._client")
    def test_search_with_pagination(self, mock_client: Mock) -> None:
        """Test searching with pagination parameters."""
        mock_client.search_issues.return_value = {"total": 100, "issues": [], "maxResults": 10, "startAt": 20}

        jira_search_issues(project="PROJ", max_results=10, start_at=20)

        mock_client.search_issues.assert_called_once_with(jql="project = PROJ", max_results=10, start_at=20)

    @patch("jira_mcp_server.tools.search_tools._client", None)
    def test_search_not_initialized(self) -> None:
        """Test that error is raised when tools not initialized."""
        with pytest.raises(RuntimeError, match="Search tools not initialized"):
            jira_search_issues(project="PROJ")

    @patch("jira_mcp_server.tools.search_tools._client")
    def test_search_no_criteria_error(self, mock_client: Mock) -> None:
        """Test that error is raised when no criteria provided."""
        with pytest.raises(ValueError, match="At least one search criterion must be provided"):
            jira_search_issues()

    @patch("jira_mcp_server.tools.search_tools._client")
    def test_search_api_error(self, mock_client: Mock) -> None:
        """Test that API errors are wrapped with helpful message."""
        mock_client.search_issues.side_effect = Exception("JQL syntax error")

        with pytest.raises(ValueError, match="Search failed: JQL syntax error"):
            jira_search_issues(project="PROJ")


class TestSearchJQL:
    """Test jira_search_jql function."""

    @patch("jira_mcp_server.tools.search_tools._client")
    def test_search_with_valid_jql(self, mock_client: Mock) -> None:
        """Test searching with valid JQL."""
        mock_client.search_issues.return_value = {
            "total": 3,
            "issues": [{"key": "PROJ-1"}],
            "maxResults": 50,
            "startAt": 0,
        }

        result = jira_search_jql(jql="project = PROJ AND status = Open")

        assert result["total"] == 3
        mock_client.search_issues.assert_called_once_with(
            jql="project = PROJ AND status = Open", max_results=50, start_at=0
        )

    @patch("jira_mcp_server.tools.search_tools._client")
    def test_search_with_complex_jql(self, mock_client: Mock) -> None:
        """Test searching with complex JQL query."""
        mock_client.search_issues.return_value = {"total": 0, "issues": [], "maxResults": 20, "startAt": 0}

        jql = "project = PROJ AND created >= -7d AND assignee = currentUser() ORDER BY created DESC"
        jira_search_jql(jql=jql, max_results=20)

        mock_client.search_issues.assert_called_once_with(jql=jql, max_results=20, start_at=0)

    @patch("jira_mcp_server.tools.search_tools._client", None)
    def test_jql_search_not_initialized(self) -> None:
        """Test that error is raised when tools not initialized."""
        with pytest.raises(RuntimeError, match="Search tools not initialized"):
            jira_search_jql(jql="project = PROJ")

    @patch("jira_mcp_server.tools.search_tools._client")
    def test_jql_search_empty_query_error(self, mock_client: Mock) -> None:
        """Test that error is raised for empty JQL."""
        with pytest.raises(ValueError, match="JQL query cannot be empty"):
            jira_search_jql(jql="")

    @patch("jira_mcp_server.tools.search_tools._client")
    def test_jql_search_whitespace_only_error(self, mock_client: Mock) -> None:
        """Test that error is raised for whitespace-only JQL."""
        with pytest.raises(ValueError, match="JQL query cannot be empty"):
            jira_search_jql(jql="   ")

    @patch("jira_mcp_server.tools.search_tools._client")
    def test_jql_search_api_error(self, mock_client: Mock) -> None:
        """Test that API errors are wrapped with helpful message."""
        mock_client.search_issues.side_effect = Exception("Invalid JQL syntax")

        with pytest.raises(ValueError, match="JQL search failed: Invalid JQL syntax"):
            jira_search_jql(jql="invalid jql query")
