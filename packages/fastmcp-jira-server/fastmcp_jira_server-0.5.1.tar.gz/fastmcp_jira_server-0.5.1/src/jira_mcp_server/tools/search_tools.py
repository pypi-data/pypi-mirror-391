"""MCP tools for issue search (T036-T038)"""

from typing import Any, Dict, List, Optional

from jira_mcp_server.jira_client import JiraClient

# Global client instance (initialized by server)
_client: Optional[JiraClient] = None


def initialize_search_tools(client: JiraClient) -> None:
    """Initialize search tools with JiraClient instance.

    Args:
        client: JiraClient instance
    """
    global _client
    _client = client


def build_jql_from_criteria(
    project: Optional[str] = None,
    assignee: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    labels: Optional[List[str]] = None,
    created_after: Optional[str] = None,
    created_before: Optional[str] = None,
    updated_after: Optional[str] = None,
    updated_before: Optional[str] = None,
) -> str:
    """Build JQL query from search criteria (T036).

    Args:
        project: Project key
        assignee: Assignee username or "currentUser()"
        status: Status name
        priority: Priority name
        labels: List of label names
        created_after: Created after date (YYYY-MM-DD)
        created_before: Created before date (YYYY-MM-DD)
        updated_after: Updated after date (YYYY-MM-DD)
        updated_before: Updated before date (YYYY-MM-DD)

    Returns:
        JQL query string

    Example:
        >>> build_jql_from_criteria(project="PROJ", status="Open", assignee="john.doe")
        'project = PROJ AND status = "Open" AND assignee = john.doe'
    """
    clauses: List[str] = []

    if project:
        clauses.append(f"project = {project}")

    if assignee:
        if assignee == "currentUser()":
            clauses.append("assignee = currentUser()")
        else:
            clauses.append(f"assignee = {assignee}")

    if status:
        clauses.append(f'status = "{status}"')

    if priority:
        clauses.append(f'priority = "{priority}"')

    if labels:
        for label in labels:
            clauses.append(f'labels = "{label}"')

    if created_after:
        clauses.append(f'created >= "{created_after}"')

    if created_before:
        clauses.append(f'created <= "{created_before}"')

    if updated_after:
        clauses.append(f'updated >= "{updated_after}"')

    if updated_before:
        clauses.append(f'updated <= "{updated_before}"')

    return " AND ".join(clauses) if clauses else ""


def jira_search_issues(
    project: Optional[str] = None,
    assignee: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    labels: Optional[List[str]] = None,
    created_after: Optional[str] = None,
    created_before: Optional[str] = None,
    updated_after: Optional[str] = None,
    updated_before: Optional[str] = None,
    max_results: int = 50,
    start_at: int = 0,
) -> Dict[str, Any]:
    """Search issues using multiple criteria (T037).

    Builds a JQL query from the provided criteria and executes it.

    Args:
        project: Project key (e.g., "PROJ")
        assignee: Assignee username or "currentUser()"
        status: Status name (e.g., "Open", "In Progress")
        priority: Priority name (e.g., "High", "Critical")
        labels: List of label names
        created_after: Created after date in YYYY-MM-DD format
        created_before: Created before date in YYYY-MM-DD format
        updated_after: Updated after date in YYYY-MM-DD format
        updated_before: Updated before date in YYYY-MM-DD format
        max_results: Maximum results to return (default: 50)
        start_at: Starting offset for pagination (default: 0)

    Returns:
        Search results with total count, issues list, and pagination info

    Raises:
        ValueError: If no criteria provided or search fails

    Example:
        jira_search_issues(
            project="PROJ",
            status="Open",
            assignee="currentUser()",
            max_results=10
        )
    """
    if not _client:
        raise RuntimeError("Search tools not initialized")

    # Build JQL from criteria
    jql = build_jql_from_criteria(
        project=project,
        assignee=assignee,
        status=status,
        priority=priority,
        labels=labels,
        created_after=created_after,
        created_before=created_before,
        updated_after=updated_after,
        updated_before=updated_before,
    )

    if not jql:
        raise ValueError("At least one search criterion must be provided")

    try:
        return _client.search_issues(jql=jql, max_results=max_results, start_at=start_at)
    except Exception as e:
        raise ValueError(f"Search failed: {str(e)}")


def jira_search_jql(
    jql: str,
    max_results: int = 50,
    start_at: int = 0,
) -> Dict[str, Any]:
    """Execute a JQL query directly (T038).

    Use this for complex queries that can't be expressed through search_issues criteria.

    Args:
        jql: JQL query string
        max_results: Maximum results to return (default: 50)
        start_at: Starting offset for pagination (default: 0)

    Returns:
        Search results with total count, issues list, and pagination info

    Raises:
        ValueError: If JQL is invalid or search fails

    Example:
        jira_search_jql(
            jql='project = PROJ AND created >= -7d ORDER BY created DESC',
            max_results=20
        )
    """
    if not _client:
        raise RuntimeError("Search tools not initialized")

    if not jql or not jql.strip():
        raise ValueError("JQL query cannot be empty")

    try:
        return _client.search_issues(jql=jql, max_results=max_results, start_at=start_at)
    except Exception as e:
        raise ValueError(f"JQL search failed: {str(e)}")
