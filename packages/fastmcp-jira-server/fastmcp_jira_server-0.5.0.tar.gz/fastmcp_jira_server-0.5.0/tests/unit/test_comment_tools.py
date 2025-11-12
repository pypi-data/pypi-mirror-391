"""Unit tests for comment tools"""

from unittest.mock import Mock, patch

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


class TestCommentToolsInitialization:
    """Test comment tools initialization."""

    def test_initialize_comment_tools(self, mock_client: JiraClient) -> None:
        """Test that initialize_comment_tools sets up global client instance."""
        # Just test that it doesn't raise an error
        initialize_comment_tools(mock_client)
        # The globals are set, but we can't easily test them directly
        # Integration will be tested through the function tests


class TestAddComment:
    """Test jira_comment_add function."""

    @patch("jira_mcp_server.tools.comment_tools._client", None)
    def test_add_comment_not_initialized(self) -> None:
        """Test that error is raised when tools not initialized."""
        with pytest.raises(RuntimeError, match="Comment tools not initialized"):
            jira_comment_add(issue_key="PROJ-123", body="Test comment")

    @patch("jira_mcp_server.tools.comment_tools._client")
    def test_add_comment_success(self, mock_client: Mock) -> None:
        """Test successful comment addition."""
        mock_client.add_comment.return_value = {
            "id": "10001",
            "body": "Test comment",
            "author": {
                "displayName": "John Doe",
                "emailAddress": "john@example.com",
            },
            "created": "2025-01-15T10:00:00.000+0000",
            "updated": "2025-01-15T10:00:00.000+0000",
        }

        result = jira_comment_add(issue_key="PROJ-123", body="Test comment")

        assert result["id"] == "10001"
        assert result["body"] == "Test comment"
        assert result["author"]["displayName"] == "John Doe"
        mock_client.add_comment.assert_called_once_with(issue_key="PROJ-123", body="Test comment")

    @patch("jira_mcp_server.tools.comment_tools._client")
    def test_add_comment_empty_issue_key_error(self, mock_client: Mock) -> None:
        """Test that error is raised for empty issue key."""
        with pytest.raises(ValueError, match="Issue key cannot be empty"):
            jira_comment_add(issue_key="", body="Test comment")

    @patch("jira_mcp_server.tools.comment_tools._client")
    def test_add_comment_empty_body_error(self, mock_client: Mock) -> None:
        """Test that error is raised for empty comment body."""
        with pytest.raises(ValueError, match="Comment body cannot be empty"):
            jira_comment_add(issue_key="PROJ-123", body="")

    @patch("jira_mcp_server.tools.comment_tools._client")
    def test_add_comment_whitespace_issue_key_error(self, mock_client: Mock) -> None:
        """Test that error is raised for whitespace-only issue key."""
        with pytest.raises(ValueError, match="Issue key cannot be empty"):
            jira_comment_add(issue_key="   ", body="Test comment")

    @patch("jira_mcp_server.tools.comment_tools._client")
    def test_add_comment_whitespace_body_error(self, mock_client: Mock) -> None:
        """Test that error is raised for whitespace-only body."""
        with pytest.raises(ValueError, match="Comment body cannot be empty"):
            jira_comment_add(issue_key="PROJ-123", body="   ")

    @patch("jira_mcp_server.tools.comment_tools._client")
    def test_add_comment_api_error(self, mock_client: Mock) -> None:
        """Test that API errors are wrapped with helpful message."""
        mock_client.add_comment.side_effect = Exception("Issue not found")

        with pytest.raises(ValueError, match="Add comment failed: Issue not found"):
            jira_comment_add(issue_key="PROJ-999", body="Test comment")

    @patch("jira_mcp_server.tools.comment_tools._client")
    def test_add_comment_with_markdown(self, mock_client: Mock) -> None:
        """Test adding comment with Jira markup."""
        mock_client.add_comment.return_value = {
            "id": "10002",
            "body": "This is *bold* and _italic_",
            "author": {"displayName": "Jane Smith"},
            "created": "2025-01-15T11:00:00.000+0000",
        }

        result = jira_comment_add(issue_key="PROJ-123", body="This is *bold* and _italic_")

        assert result["id"] == "10002"
        assert "*bold*" in result["body"]
        mock_client.add_comment.assert_called_once()


class TestListComments:
    """Test jira_comment_list function."""

    @patch("jira_mcp_server.tools.comment_tools._client", None)
    def test_list_comments_not_initialized(self) -> None:
        """Test that error is raised when tools not initialized."""
        with pytest.raises(RuntimeError, match="Comment tools not initialized"):
            jira_comment_list(issue_key="PROJ-123")

    @patch("jira_mcp_server.tools.comment_tools._client")
    def test_list_comments_success(self, mock_client: Mock) -> None:
        """Test successful comments retrieval."""
        mock_client.list_comments.return_value = {
            "comments": [
                {
                    "id": "10001",
                    "body": "First comment",
                    "author": {"displayName": "John Doe"},
                    "created": "2025-01-15T10:00:00.000+0000",
                },
                {
                    "id": "10002",
                    "body": "Second comment",
                    "author": {"displayName": "Jane Smith"},
                    "created": "2025-01-15T11:00:00.000+0000",
                },
            ],
            "total": 2,
            "maxResults": 50,
            "startAt": 0,
        }

        result = jira_comment_list(issue_key="PROJ-123")

        assert result["total"] == 2
        assert len(result["comments"]) == 2
        assert result["comments"][0]["id"] == "10001"
        assert result["comments"][1]["id"] == "10002"
        mock_client.list_comments.assert_called_once_with(issue_key="PROJ-123")

    @patch("jira_mcp_server.tools.comment_tools._client")
    def test_list_comments_empty_issue_key_error(self, mock_client: Mock) -> None:
        """Test that error is raised for empty issue key."""
        with pytest.raises(ValueError, match="Issue key cannot be empty"):
            jira_comment_list(issue_key="")

    @patch("jira_mcp_server.tools.comment_tools._client")
    def test_list_comments_whitespace_issue_key_error(self, mock_client: Mock) -> None:
        """Test that error is raised for whitespace-only issue key."""
        with pytest.raises(ValueError, match="Issue key cannot be empty"):
            jira_comment_list(issue_key="   ")

    @patch("jira_mcp_server.tools.comment_tools._client")
    def test_list_comments_api_error(self, mock_client: Mock) -> None:
        """Test that API errors are wrapped with helpful message."""
        mock_client.list_comments.side_effect = Exception("Issue not found")

        with pytest.raises(ValueError, match="List comments failed: Issue not found"):
            jira_comment_list(issue_key="PROJ-999")

    @patch("jira_mcp_server.tools.comment_tools._client")
    def test_list_comments_no_comments(self, mock_client: Mock) -> None:
        """Test handling when issue has no comments."""
        mock_client.list_comments.return_value = {
            "comments": [],
            "total": 0,
            "maxResults": 50,
            "startAt": 0,
        }

        result = jira_comment_list(issue_key="PROJ-123")

        assert result["total"] == 0
        assert len(result["comments"]) == 0
        mock_client.list_comments.assert_called_once_with(issue_key="PROJ-123")


class TestUpdateComment:
    """Test jira_comment_update function."""

    @patch("jira_mcp_server.tools.comment_tools._client", None)
    def test_update_comment_not_initialized(self) -> None:
        """Test that error is raised when tools not initialized."""
        with pytest.raises(RuntimeError, match="Comment tools not initialized"):
            jira_comment_update(issue_key="PROJ-123", comment_id="10001", body="Updated")

    @patch("jira_mcp_server.tools.comment_tools._client")
    def test_update_comment_success(self, mock_client: Mock) -> None:
        """Test successful comment update."""
        mock_client.update_comment.return_value = {
            "id": "10001",
            "body": "Updated comment text",
            "author": {"displayName": "John Doe"},
            "updated": "2025-01-15T12:00:00.000+0000",
        }

        result = jira_comment_update(issue_key="PROJ-123", comment_id="10001", body="Updated comment text")

        assert result["id"] == "10001"
        assert result["body"] == "Updated comment text"
        mock_client.update_comment.assert_called_once_with(
            issue_key="PROJ-123", comment_id="10001", body="Updated comment text"
        )

    @patch("jira_mcp_server.tools.comment_tools._client")
    def test_update_comment_empty_issue_key_error(self, mock_client: Mock) -> None:
        """Test that error is raised for empty issue key."""
        with pytest.raises(ValueError, match="Issue key cannot be empty"):
            jira_comment_update(issue_key="", comment_id="10001", body="Updated")

    @patch("jira_mcp_server.tools.comment_tools._client")
    def test_update_comment_empty_comment_id_error(self, mock_client: Mock) -> None:
        """Test that error is raised for empty comment ID."""
        with pytest.raises(ValueError, match="Comment ID cannot be empty"):
            jira_comment_update(issue_key="PROJ-123", comment_id="", body="Updated")

    @patch("jira_mcp_server.tools.comment_tools._client")
    def test_update_comment_empty_body_error(self, mock_client: Mock) -> None:
        """Test that error is raised for empty body."""
        with pytest.raises(ValueError, match="Comment body cannot be empty"):
            jira_comment_update(issue_key="PROJ-123", comment_id="10001", body="")

    @patch("jira_mcp_server.tools.comment_tools._client")
    def test_update_comment_whitespace_issue_key_error(self, mock_client: Mock) -> None:
        """Test that error is raised for whitespace-only issue key."""
        with pytest.raises(ValueError, match="Issue key cannot be empty"):
            jira_comment_update(issue_key="   ", comment_id="10001", body="Updated")

    @patch("jira_mcp_server.tools.comment_tools._client")
    def test_update_comment_whitespace_comment_id_error(self, mock_client: Mock) -> None:
        """Test that error is raised for whitespace-only comment ID."""
        with pytest.raises(ValueError, match="Comment ID cannot be empty"):
            jira_comment_update(issue_key="PROJ-123", comment_id="   ", body="Updated")

    @patch("jira_mcp_server.tools.comment_tools._client")
    def test_update_comment_whitespace_body_error(self, mock_client: Mock) -> None:
        """Test that error is raised for whitespace-only body."""
        with pytest.raises(ValueError, match="Comment body cannot be empty"):
            jira_comment_update(issue_key="PROJ-123", comment_id="10001", body="   ")

    @patch("jira_mcp_server.tools.comment_tools._client")
    def test_update_comment_api_error(self, mock_client: Mock) -> None:
        """Test that API errors are wrapped with helpful message."""
        mock_client.update_comment.side_effect = Exception("Comment not found")

        with pytest.raises(ValueError, match="Update comment failed: Comment not found"):
            jira_comment_update(issue_key="PROJ-123", comment_id="99999", body="Updated")


class TestDeleteComment:
    """Test jira_comment_delete function."""

    @patch("jira_mcp_server.tools.comment_tools._client", None)
    def test_delete_comment_not_initialized(self) -> None:
        """Test that error is raised when tools not initialized."""
        with pytest.raises(RuntimeError, match="Comment tools not initialized"):
            jira_comment_delete(issue_key="PROJ-123", comment_id="10001")

    @patch("jira_mcp_server.tools.comment_tools._client")
    def test_delete_comment_success(self, mock_client: Mock) -> None:
        """Test successful comment deletion."""
        mock_client.delete_comment.return_value = None

        result = jira_comment_delete(issue_key="PROJ-123", comment_id="10001")

        assert result["success"] is True
        assert "10001" in result["message"]
        assert result["comment_id"] == "10001"
        assert result["issue_key"] == "PROJ-123"
        mock_client.delete_comment.assert_called_once_with(issue_key="PROJ-123", comment_id="10001")

    @patch("jira_mcp_server.tools.comment_tools._client")
    def test_delete_comment_empty_issue_key_error(self, mock_client: Mock) -> None:
        """Test that error is raised for empty issue key."""
        with pytest.raises(ValueError, match="Issue key cannot be empty"):
            jira_comment_delete(issue_key="", comment_id="10001")

    @patch("jira_mcp_server.tools.comment_tools._client")
    def test_delete_comment_empty_comment_id_error(self, mock_client: Mock) -> None:
        """Test that error is raised for empty comment ID."""
        with pytest.raises(ValueError, match="Comment ID cannot be empty"):
            jira_comment_delete(issue_key="PROJ-123", comment_id="")

    @patch("jira_mcp_server.tools.comment_tools._client")
    def test_delete_comment_whitespace_issue_key_error(self, mock_client: Mock) -> None:
        """Test that error is raised for whitespace-only issue key."""
        with pytest.raises(ValueError, match="Issue key cannot be empty"):
            jira_comment_delete(issue_key="   ", comment_id="10001")

    @patch("jira_mcp_server.tools.comment_tools._client")
    def test_delete_comment_whitespace_comment_id_error(self, mock_client: Mock) -> None:
        """Test that error is raised for whitespace-only comment ID."""
        with pytest.raises(ValueError, match="Comment ID cannot be empty"):
            jira_comment_delete(issue_key="PROJ-123", comment_id="   ")

    @patch("jira_mcp_server.tools.comment_tools._client")
    def test_delete_comment_api_error(self, mock_client: Mock) -> None:
        """Test that API errors are wrapped with helpful message."""
        mock_client.delete_comment.side_effect = Exception("Permission denied")

        with pytest.raises(ValueError, match="Delete comment failed: Permission denied"):
            jira_comment_delete(issue_key="PROJ-123", comment_id="10001")
