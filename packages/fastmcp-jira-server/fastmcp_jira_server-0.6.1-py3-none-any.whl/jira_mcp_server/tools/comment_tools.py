"""MCP tools for issue comments (T060-T063)"""

from typing import Any, Dict, Optional

from jira_mcp_server.jira_client import JiraClient

# Global client instance (initialized by server)
_client: Optional[JiraClient] = None


def initialize_comment_tools(client: JiraClient) -> None:
    """Initialize comment tools with JiraClient instance.

    Args:
        client: JiraClient instance
    """
    global _client
    _client = client


def jira_comment_add(issue_key: str, body: str) -> Dict[str, Any]:
    """Add a comment to an issue (T060).

    Args:
        issue_key: Issue key (e.g., "PROJ-123")
        body: Comment text (supports Jira markup)

    Returns:
        Created comment with ID, author, and timestamp

    Raises:
        ValueError: If issue not found or validation fails

    Example:
        jira_comment_add(
            issue_key="PROJ-123",
            body="This issue is ready for review"
        )
    """
    if not _client:
        raise RuntimeError("Comment tools not initialized")

    if not issue_key or not issue_key.strip():
        raise ValueError("Issue key cannot be empty")

    if not body or not body.strip():
        raise ValueError("Comment body cannot be empty")

    try:
        return _client.add_comment(issue_key=issue_key, body=body)
    except Exception as e:
        raise ValueError(f"Add comment failed: {str(e)}")


def jira_comment_list(issue_key: str) -> Dict[str, Any]:
    """List all comments on an issue (T061).

    Retrieves all comments with author, timestamp, and comment text.

    Args:
        issue_key: Issue key (e.g., "PROJ-123")

    Returns:
        Comments list with total count and comment details

    Raises:
        ValueError: If issue not found or access denied

    Example:
        jira_comment_list(issue_key="PROJ-123")
    """
    if not _client:
        raise RuntimeError("Comment tools not initialized")

    if not issue_key or not issue_key.strip():
        raise ValueError("Issue key cannot be empty")

    try:
        return _client.list_comments(issue_key=issue_key)
    except Exception as e:
        raise ValueError(f"List comments failed: {str(e)}")


def jira_comment_update(issue_key: str, comment_id: str, body: str) -> Dict[str, Any]:
    """Update an existing comment (T062).

    Only the comment author or users with appropriate permissions can update a comment.

    Args:
        issue_key: Issue key (e.g., "PROJ-123")
        comment_id: Comment ID to update
        body: New comment text (supports Jira markup)

    Returns:
        Updated comment with ID, author, and timestamp

    Raises:
        ValueError: If comment not found or permission denied

    Example:
        jira_comment_update(
            issue_key="PROJ-123",
            comment_id="10001",
            body="Updated comment text"
        )
    """
    if not _client:
        raise RuntimeError("Comment tools not initialized")

    if not issue_key or not issue_key.strip():
        raise ValueError("Issue key cannot be empty")

    if not comment_id or not comment_id.strip():
        raise ValueError("Comment ID cannot be empty")

    if not body or not body.strip():
        raise ValueError("Comment body cannot be empty")

    try:
        return _client.update_comment(issue_key=issue_key, comment_id=comment_id, body=body)
    except Exception as e:
        raise ValueError(f"Update comment failed: {str(e)}")


def jira_comment_delete(issue_key: str, comment_id: str) -> Dict[str, Any]:
    """Delete a comment (T063).

    Only the comment author or users with appropriate permissions can delete a comment.

    Args:
        issue_key: Issue key (e.g., "PROJ-123")
        comment_id: Comment ID to delete

    Returns:
        Success confirmation with deleted comment ID

    Raises:
        ValueError: If comment not found or permission denied

    Example:
        jira_comment_delete(issue_key="PROJ-123", comment_id="10001")
    """
    if not _client:
        raise RuntimeError("Comment tools not initialized")

    if not issue_key or not issue_key.strip():
        raise ValueError("Issue key cannot be empty")

    if not comment_id or not comment_id.strip():
        raise ValueError("Comment ID cannot be empty")

    try:
        _client.delete_comment(issue_key=issue_key, comment_id=comment_id)
        return {
            "success": True,
            "message": f"Comment {comment_id} deleted successfully",
            "issue_key": issue_key,
            "comment_id": comment_id,
        }
    except Exception as e:
        raise ValueError(f"Delete comment failed: {str(e)}")
