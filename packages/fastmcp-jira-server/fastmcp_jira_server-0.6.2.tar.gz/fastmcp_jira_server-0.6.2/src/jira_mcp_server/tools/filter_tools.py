"""MCP tools for filter management (T048-T053)"""

from typing import Any, Dict, Optional

from jira_mcp_server.jira_client import JiraClient

# Global client instance (initialized by server)
_client: Optional[JiraClient] = None


def initialize_filter_tools(client: JiraClient) -> None:
    """Initialize filter tools with JiraClient instance.

    Args:
        client: JiraClient instance
    """
    global _client
    _client = client


def jira_filter_create(
    name: str,
    jql: str,
    description: str | None = None,
    favourite: bool = False,
) -> Dict[str, Any]:
    """Create a new saved filter (T048).

    Args:
        name: Filter name
        jql: JQL query string
        description: Optional filter description
        favourite: Whether to mark as favorite (default: False)

    Returns:
        Created filter with ID and details

    Raises:
        ValueError: If filter creation fails

    Example:
        jira_filter_create(
            name="My Open Issues",
            jql="assignee = currentUser() AND status = Open",
            description="All my open issues"
        )
    """
    if not _client:
        raise RuntimeError("Filter tools not initialized")

    if not name or not name.strip():
        raise ValueError("Filter name cannot be empty")

    if not jql or not jql.strip():
        raise ValueError("JQL query cannot be empty")

    try:
        return _client.create_filter(name=name, jql=jql, description=description, favourite=favourite)
    except Exception as e:
        raise ValueError(f"Filter creation failed: {str(e)}")


def jira_filter_list() -> Dict[str, Any]:
    """List all accessible filters (T049).

    Returns:
        List of filter metadata (ID, name, JQL, owner)

    Raises:
        RuntimeError: If tools not initialized

    Example:
        jira_filter_list()
    """
    if not _client:
        raise RuntimeError("Filter tools not initialized")

    try:
        return _client.list_filters()
    except Exception as e:
        raise ValueError(f"Filter list failed: {str(e)}")


def jira_filter_get(filter_id: str) -> Dict[str, Any]:
    """Get filter details by ID (T050).

    Args:
        filter_id: Filter ID

    Returns:
        Complete filter information

    Raises:
        ValueError: If filter not found or access denied

    Example:
        jira_filter_get(filter_id="10000")
    """
    if not _client:
        raise RuntimeError("Filter tools not initialized")

    if not filter_id or not filter_id.strip():
        raise ValueError("Filter ID cannot be empty")

    try:
        return _client.get_filter(filter_id=filter_id)
    except Exception as e:
        raise ValueError(f"Get filter failed: {str(e)}")


def jira_filter_execute(
    filter_id: str,
    max_results: int = 50,
    start_at: int = 0,
) -> Dict[str, Any]:
    """Execute a saved filter (T051).

    Retrieves the filter's JQL and executes it.

    Args:
        filter_id: Filter ID
        max_results: Maximum results to return (default: 50)
        start_at: Starting offset for pagination (default: 0)

    Returns:
        Search results with total count, issues list, and pagination info

    Raises:
        ValueError: If filter not found or execution fails

    Example:
        jira_filter_execute(filter_id="10000", max_results=20)
    """
    if not _client:
        raise RuntimeError("Filter tools not initialized")

    if not filter_id or not filter_id.strip():
        raise ValueError("Filter ID cannot be empty")

    try:
        # Get filter to retrieve JQL
        filter_data = _client.get_filter(filter_id=filter_id)
        jql = filter_data.get("jql")

        if not jql:
            raise ValueError("Filter does not contain a valid JQL query")

        # Execute the filter's JQL
        return _client.search_issues(jql=jql, max_results=max_results, start_at=start_at)
    except Exception as e:
        raise ValueError(f"Filter execution failed: {str(e)}")


def jira_filter_update(
    filter_id: str,
    name: str | None = None,
    jql: str | None = None,
    description: str | None = None,
    favourite: bool | None = None,
) -> Dict[str, Any]:
    """Update an existing filter (T052).

    Only provided fields are updated.

    Args:
        filter_id: Filter ID
        name: New filter name
        jql: New JQL query
        description: New description
        favourite: Whether to mark as favorite

    Returns:
        Updated filter data

    Raises:
        ValueError: If no fields provided or update fails

    Example:
        jira_filter_update(
            filter_id="10000",
            jql="assignee = currentUser() AND status IN (Open, 'In Progress')"
        )
    """
    if not _client:
        raise RuntimeError("Filter tools not initialized")

    if not filter_id or not filter_id.strip():
        raise ValueError("Filter ID cannot be empty")

    if name is None and jql is None and description is None and favourite is None:
        raise ValueError("At least one field must be provided to update")

    try:
        return _client.update_filter(
            filter_id=filter_id, name=name, jql=jql, description=description, favourite=favourite
        )
    except Exception as e:
        raise ValueError(f"Filter update failed: {str(e)}")


def jira_filter_delete(filter_id: str) -> Dict[str, Any]:
    """Delete a filter (T053).

    Only the filter owner can delete it.

    Args:
        filter_id: Filter ID

    Returns:
        Success confirmation message

    Raises:
        ValueError: If filter deletion fails or permission denied

    Example:
        jira_filter_delete(filter_id="10000")
    """
    if not _client:
        raise RuntimeError("Filter tools not initialized")

    if not filter_id or not filter_id.strip():
        raise ValueError("Filter ID cannot be empty")

    try:
        _client.delete_filter(filter_id=filter_id)
        return {"success": True, "message": f"Filter {filter_id} deleted successfully"}
    except Exception as e:
        raise ValueError(f"Filter deletion failed: {str(e)}")
