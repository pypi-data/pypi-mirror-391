"""Contract tests for comment tools (T060-T063)"""

from unittest.mock import Mock

import pytest

from jira_mcp_server.jira_client import JiraClient
from jira_mcp_server.tools.comment_tools import (
    initialize_comment_tools,
    jira_comment_add,
    jira_comment_delete,
    jira_comment_list,
    jira_comment_update,
)


@pytest.fixture
def mock_client() -> JiraClient:
    """Create a mock JiraClient."""
    return Mock(spec=JiraClient)


class TestCommentToolsContract:
    """Contract tests for comment tools."""

    def test_initialize_comment_tools_sets_client(self, mock_client: JiraClient) -> None:
        """Test that initialize_comment_tools sets up global client."""
        initialize_comment_tools(mock_client)
        # Can't directly test global variable, but should not raise

    def test_jira_comment_add_signature(self, mock_client: JiraClient) -> None:
        """Test jira_comment_add function signature matches contract (T060)."""
        initialize_comment_tools(mock_client)
        mock_client.add_comment.return_value = {
            "id": "10001",
            "body": "Test comment",
            "author": {"displayName": "John Doe"},
            "created": "2025-01-15T10:00:00.000+0000",
        }

        result = jira_comment_add(issue_key="PROJ-123", body="Test comment")

        # Verify function accepts required parameters
        assert "id" in result
        assert "body" in result
        mock_client.add_comment.assert_called_once()

    def test_jira_comment_list_signature(self, mock_client: JiraClient) -> None:
        """Test jira_comment_list function signature matches contract (T061)."""
        initialize_comment_tools(mock_client)
        mock_client.list_comments.return_value = {
            "comments": [
                {
                    "id": "10001",
                    "body": "Comment 1",
                    "author": {"displayName": "John Doe"},
                    "created": "2025-01-15T10:00:00.000+0000",
                }
            ],
            "total": 1,
        }

        result = jira_comment_list(issue_key="PROJ-123")

        # Verify function accepts required parameters
        assert "comments" in result
        assert "total" in result
        mock_client.list_comments.assert_called_once()

    def test_jira_comment_add_returns_dict(self, mock_client: JiraClient) -> None:
        """Test jira_comment_add returns dictionary."""
        initialize_comment_tools(mock_client)
        mock_client.add_comment.return_value = {"id": "10001"}

        result = jira_comment_add(issue_key="PROJ-123", body="Test")

        assert isinstance(result, dict)

    def test_jira_comment_list_returns_dict(self, mock_client: JiraClient) -> None:
        """Test jira_comment_list returns dictionary."""
        initialize_comment_tools(mock_client)
        mock_client.list_comments.return_value = {"comments": [], "total": 0}

        result = jira_comment_list(issue_key="PROJ-123")

        assert isinstance(result, dict)

    def test_jira_comment_add_requires_issue_key(self, mock_client: JiraClient) -> None:
        """Test jira_comment_add requires issue_key parameter."""
        initialize_comment_tools(mock_client)

        with pytest.raises((ValueError, TypeError)):
            jira_comment_add(issue_key="", body="Test")  # type: ignore[arg-type]

    def test_jira_comment_add_requires_body(self, mock_client: JiraClient) -> None:
        """Test jira_comment_add requires body parameter."""
        initialize_comment_tools(mock_client)

        with pytest.raises((ValueError, TypeError)):
            jira_comment_add(issue_key="PROJ-123", body="")  # type: ignore[arg-type]

    def test_jira_comment_list_requires_issue_key(self, mock_client: JiraClient) -> None:
        """Test jira_comment_list requires issue_key parameter."""
        initialize_comment_tools(mock_client)

        with pytest.raises((ValueError, TypeError)):
            jira_comment_list(issue_key="")  # type: ignore[arg-type]

    def test_jira_comment_add_validates_empty_issue_key(self, mock_client: JiraClient) -> None:
        """Test that empty issue key raises ValueError."""
        initialize_comment_tools(mock_client)

        with pytest.raises(ValueError, match="Issue key cannot be empty"):
            jira_comment_add(issue_key="", body="Test")

    def test_jira_comment_add_validates_empty_body(self, mock_client: JiraClient) -> None:
        """Test that empty comment body raises ValueError."""
        initialize_comment_tools(mock_client)

        with pytest.raises(ValueError, match="Comment body cannot be empty"):
            jira_comment_add(issue_key="PROJ-123", body="")

    def test_jira_comment_list_validates_empty_issue_key(self, mock_client: JiraClient) -> None:
        """Test that empty issue key raises ValueError."""
        initialize_comment_tools(mock_client)

        with pytest.raises(ValueError, match="Issue key cannot be empty"):
            jira_comment_list(issue_key="")

    def test_jira_comment_add_handles_api_errors(self, mock_client: JiraClient) -> None:
        """Test jira_comment_add handles API errors gracefully."""
        initialize_comment_tools(mock_client)
        mock_client.add_comment.side_effect = Exception("API error")

        with pytest.raises(ValueError, match="Add comment failed"):
            jira_comment_add(issue_key="PROJ-123", body="Test")

    def test_jira_comment_list_handles_api_errors(self, mock_client: JiraClient) -> None:
        """Test jira_comment_list handles API errors gracefully."""
        initialize_comment_tools(mock_client)
        mock_client.list_comments.side_effect = Exception("API error")

        with pytest.raises(ValueError, match="List comments failed"):
            jira_comment_list(issue_key="PROJ-123")

    def test_jira_comment_update_signature(self, mock_client: JiraClient) -> None:
        """Test jira_comment_update function signature matches contract (T062)."""
        initialize_comment_tools(mock_client)
        mock_client.update_comment.return_value = {
            "id": "10001",
            "body": "Updated comment",
            "author": {"displayName": "John Doe"},
            "updated": "2025-01-15T12:00:00.000+0000",
        }

        result = jira_comment_update(issue_key="PROJ-123", comment_id="10001", body="Updated comment")

        # Verify function accepts required parameters
        assert "id" in result
        assert "body" in result
        mock_client.update_comment.assert_called_once()

    def test_jira_comment_update_returns_dict(self, mock_client: JiraClient) -> None:
        """Test jira_comment_update returns dictionary."""
        initialize_comment_tools(mock_client)
        mock_client.update_comment.return_value = {"id": "10001"}

        result = jira_comment_update(issue_key="PROJ-123", comment_id="10001", body="Updated")

        assert isinstance(result, dict)

    def test_jira_comment_update_requires_issue_key(self, mock_client: JiraClient) -> None:
        """Test jira_comment_update requires issue_key parameter."""
        initialize_comment_tools(mock_client)

        with pytest.raises((ValueError, TypeError)):
            jira_comment_update(issue_key="", comment_id="10001", body="Updated")  # type: ignore[arg-type]

    def test_jira_comment_update_requires_comment_id(self, mock_client: JiraClient) -> None:
        """Test jira_comment_update requires comment_id parameter."""
        initialize_comment_tools(mock_client)

        with pytest.raises((ValueError, TypeError)):
            jira_comment_update(issue_key="PROJ-123", comment_id="", body="Updated")  # type: ignore[arg-type]

    def test_jira_comment_update_requires_body(self, mock_client: JiraClient) -> None:
        """Test jira_comment_update requires body parameter."""
        initialize_comment_tools(mock_client)

        with pytest.raises((ValueError, TypeError)):
            jira_comment_update(issue_key="PROJ-123", comment_id="10001", body="")  # type: ignore[arg-type]

    def test_jira_comment_update_validates_empty_issue_key(self, mock_client: JiraClient) -> None:
        """Test that empty issue key raises ValueError."""
        initialize_comment_tools(mock_client)

        with pytest.raises(ValueError, match="Issue key cannot be empty"):
            jira_comment_update(issue_key="", comment_id="10001", body="Updated")

    def test_jira_comment_update_validates_empty_comment_id(self, mock_client: JiraClient) -> None:
        """Test that empty comment ID raises ValueError."""
        initialize_comment_tools(mock_client)

        with pytest.raises(ValueError, match="Comment ID cannot be empty"):
            jira_comment_update(issue_key="PROJ-123", comment_id="", body="Updated")

    def test_jira_comment_update_validates_empty_body(self, mock_client: JiraClient) -> None:
        """Test that empty body raises ValueError."""
        initialize_comment_tools(mock_client)

        with pytest.raises(ValueError, match="Comment body cannot be empty"):
            jira_comment_update(issue_key="PROJ-123", comment_id="10001", body="")

    def test_jira_comment_update_handles_api_errors(self, mock_client: JiraClient) -> None:
        """Test jira_comment_update handles API errors gracefully."""
        initialize_comment_tools(mock_client)
        mock_client.update_comment.side_effect = Exception("Permission denied")

        with pytest.raises(ValueError, match="Update comment failed"):
            jira_comment_update(issue_key="PROJ-123", comment_id="10001", body="Updated")

    def test_jira_comment_delete_signature(self, mock_client: JiraClient) -> None:
        """Test jira_comment_delete function signature matches contract (T063)."""
        initialize_comment_tools(mock_client)
        mock_client.delete_comment.return_value = None

        result = jira_comment_delete(issue_key="PROJ-123", comment_id="10001")

        # Verify function accepts required parameters
        assert "success" in result
        assert "message" in result
        assert result["success"] is True
        mock_client.delete_comment.assert_called_once()

    def test_jira_comment_delete_returns_dict(self, mock_client: JiraClient) -> None:
        """Test jira_comment_delete returns dictionary."""
        initialize_comment_tools(mock_client)
        mock_client.delete_comment.return_value = None

        result = jira_comment_delete(issue_key="PROJ-123", comment_id="10001")

        assert isinstance(result, dict)

    def test_jira_comment_delete_requires_issue_key(self, mock_client: JiraClient) -> None:
        """Test jira_comment_delete requires issue_key parameter."""
        initialize_comment_tools(mock_client)

        with pytest.raises((ValueError, TypeError)):
            jira_comment_delete(issue_key="", comment_id="10001")  # type: ignore[arg-type]

    def test_jira_comment_delete_requires_comment_id(self, mock_client: JiraClient) -> None:
        """Test jira_comment_delete requires comment_id parameter."""
        initialize_comment_tools(mock_client)

        with pytest.raises((ValueError, TypeError)):
            jira_comment_delete(issue_key="PROJ-123", comment_id="")  # type: ignore[arg-type]

    def test_jira_comment_delete_validates_empty_issue_key(self, mock_client: JiraClient) -> None:
        """Test that empty issue key raises ValueError."""
        initialize_comment_tools(mock_client)

        with pytest.raises(ValueError, match="Issue key cannot be empty"):
            jira_comment_delete(issue_key="", comment_id="10001")

    def test_jira_comment_delete_validates_empty_comment_id(self, mock_client: JiraClient) -> None:
        """Test that empty comment ID raises ValueError."""
        initialize_comment_tools(mock_client)

        with pytest.raises(ValueError, match="Comment ID cannot be empty"):
            jira_comment_delete(issue_key="PROJ-123", comment_id="")

    def test_jira_comment_delete_handles_api_errors(self, mock_client: JiraClient) -> None:
        """Test jira_comment_delete handles API errors gracefully."""
        initialize_comment_tools(mock_client)
        mock_client.delete_comment.side_effect = Exception("Permission denied")

        with pytest.raises(ValueError, match="Delete comment failed"):
            jira_comment_delete(issue_key="PROJ-123", comment_id="10001")
