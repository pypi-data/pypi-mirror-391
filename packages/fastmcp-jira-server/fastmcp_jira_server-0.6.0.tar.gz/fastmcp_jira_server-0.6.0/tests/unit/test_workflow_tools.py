"""Unit tests for workflow tools"""

from unittest.mock import Mock, patch

import pytest

from jira_mcp_server.jira_client import JiraClient
from jira_mcp_server.tools.workflow_tools import (
    initialize_workflow_tools,
    jira_workflow_get_transitions,
    jira_workflow_transition,
)


@pytest.fixture
def mock_client() -> JiraClient:
    """Create a mock JiraClient."""
    return Mock(spec=JiraClient)


class TestWorkflowToolsInitialization:
    """Test workflow tools initialization."""

    def test_initialize_workflow_tools(self, mock_client: JiraClient) -> None:
        """Test that initialize_workflow_tools sets up global client instance."""
        # Just test that it doesn't raise an error
        initialize_workflow_tools(mock_client)
        # The globals are set, but we can't easily test them directly
        # Integration will be tested through the function tests


class TestGetTransitions:
    """Test jira_workflow_get_transitions function."""

    @patch("jira_mcp_server.tools.workflow_tools._client", None)
    def test_get_transitions_not_initialized(self) -> None:
        """Test that error is raised when tools not initialized."""
        with pytest.raises(RuntimeError, match="Workflow tools not initialized"):
            jira_workflow_get_transitions(issue_key="PROJ-123")

    @patch("jira_mcp_server.tools.workflow_tools._client")
    def test_get_transitions_success(self, mock_client: Mock) -> None:
        """Test successful transition retrieval."""
        mock_client.get_transitions.return_value = {
            "transitions": [
                {
                    "id": "21",
                    "name": "In Progress",
                    "to": {"name": "In Progress"},
                    "hasScreen": False,
                },
                {
                    "id": "31",
                    "name": "Done",
                    "to": {"name": "Done"},
                    "hasScreen": True,
                    "fields": {"resolution": {}},
                },
            ]
        }

        result = jira_workflow_get_transitions(issue_key="PROJ-123")

        assert result["issue_key"] == "PROJ-123"
        assert len(result["transitions"]) == 2
        assert result["transitions"][0]["id"] == "21"
        assert result["transitions"][0]["name"] == "In Progress"
        assert result["transitions"][0]["to_status"] == "In Progress"
        assert result["transitions"][0]["has_screen"] is False
        assert result["transitions"][1]["has_screen"] is True
        assert "resolution" in result["transitions"][1]["fields"]
        mock_client.get_transitions.assert_called_once_with(issue_key="PROJ-123")

    @patch("jira_mcp_server.tools.workflow_tools._client")
    def test_get_transitions_empty_issue_key_error(self, mock_client: Mock) -> None:
        """Test that error is raised for empty issue key."""
        with pytest.raises(ValueError, match="Issue key cannot be empty"):
            jira_workflow_get_transitions(issue_key="")

    @patch("jira_mcp_server.tools.workflow_tools._client")
    def test_get_transitions_api_error(self, mock_client: Mock) -> None:
        """Test that API errors are wrapped with helpful message."""
        mock_client.get_transitions.side_effect = Exception("Issue not found")

        with pytest.raises(ValueError, match="Get transitions failed: Issue not found"):
            jira_workflow_get_transitions(issue_key="PROJ-123")

    @patch("jira_mcp_server.tools.workflow_tools._client")
    def test_get_transitions_no_transitions(self, mock_client: Mock) -> None:
        """Test handling when no transitions are available."""
        mock_client.get_transitions.return_value = {"transitions": []}

        result = jira_workflow_get_transitions(issue_key="PROJ-123")

        assert result["issue_key"] == "PROJ-123"
        assert len(result["transitions"]) == 0


class TestTransitionIssue:
    """Test jira_workflow_transition function."""

    @patch("jira_mcp_server.tools.workflow_tools._client", None)
    def test_transition_issue_not_initialized(self) -> None:
        """Test that error is raised when tools not initialized."""
        with pytest.raises(RuntimeError, match="Workflow tools not initialized"):
            jira_workflow_transition(issue_key="PROJ-123", transition_id="21")

    @patch("jira_mcp_server.tools.workflow_tools._client")
    def test_transition_issue_success(self, mock_client: Mock) -> None:
        """Test successful issue transition."""
        mock_client.transition_issue.return_value = None

        result = jira_workflow_transition(issue_key="PROJ-123", transition_id="21")

        assert result["success"] is True
        assert "PROJ-123" in result["message"]
        assert result["issue_key"] == "PROJ-123"
        assert result["transition_id"] == "21"
        mock_client.transition_issue.assert_called_once_with(issue_key="PROJ-123", transition_id="21", fields=None)

    @patch("jira_mcp_server.tools.workflow_tools._client")
    def test_transition_issue_with_fields(self, mock_client: Mock) -> None:
        """Test transition with required fields."""
        mock_client.transition_issue.return_value = None
        fields = {"resolution": {"name": "Done"}}

        result = jira_workflow_transition(issue_key="PROJ-123", transition_id="31", fields=fields)

        assert result["success"] is True
        mock_client.transition_issue.assert_called_once_with(issue_key="PROJ-123", transition_id="31", fields=fields)

    @patch("jira_mcp_server.tools.workflow_tools._client")
    def test_transition_issue_empty_issue_key_error(self, mock_client: Mock) -> None:
        """Test that error is raised for empty issue key."""
        with pytest.raises(ValueError, match="Issue key cannot be empty"):
            jira_workflow_transition(issue_key="", transition_id="21")

    @patch("jira_mcp_server.tools.workflow_tools._client")
    def test_transition_issue_empty_transition_id_error(self, mock_client: Mock) -> None:
        """Test that error is raised for empty transition ID."""
        with pytest.raises(ValueError, match="Transition ID cannot be empty"):
            jira_workflow_transition(issue_key="PROJ-123", transition_id="")

    @patch("jira_mcp_server.tools.workflow_tools._client")
    def test_transition_issue_api_error(self, mock_client: Mock) -> None:
        """Test that API errors are wrapped with helpful message."""
        mock_client.transition_issue.side_effect = Exception("Invalid transition")

        with pytest.raises(ValueError, match="Transition failed: Invalid transition"):
            jira_workflow_transition(issue_key="PROJ-123", transition_id="99")
