"""FastMCP server entry point"""

import sys
from typing import Any, Dict

from fastmcp import FastMCP

from jira_mcp_server.config import JiraConfig
from jira_mcp_server.jira_client import JiraClient
from jira_mcp_server.tools.comment_tools import (
    initialize_comment_tools,
    jira_comment_add,
    jira_comment_delete,
    jira_comment_list,
    jira_comment_update,
)
from jira_mcp_server.tools.filter_tools import (
    initialize_filter_tools,
    jira_filter_create,
    jira_filter_delete,
    jira_filter_execute,
    jira_filter_get,
    jira_filter_list,
    jira_filter_update,
)
from jira_mcp_server.tools.issue_tools import (
    _get_field_schema,
    initialize_issue_tools,
    jira_issue_create,
    jira_issue_get,
    jira_issue_update,
)
from jira_mcp_server.tools.search_tools import (
    initialize_search_tools,
    jira_search_issues,
    jira_search_jql,
)
from jira_mcp_server.tools.workflow_tools import (
    initialize_workflow_tools,
    jira_workflow_get_transitions,
    jira_workflow_transition,
)

# Initialize FastMCP server
mcp = FastMCP("jira-mcp-server")


# Health check implementation
def _jira_health_check() -> Dict[str, Any]:
    """Verify connectivity to Jira instance and validate authentication.

    Returns:
        Connection status and server info including version and URL
    """
    try:
        config = JiraConfig()  # type: ignore[call-arg]  # pydantic-settings loads from env
        client = JiraClient(config)
        return client.health_check()
    except Exception as e:
        return {
            "connected": False,
            "error": str(e),
        }


# Health check tool
@mcp.tool()
def jira_health_check() -> Dict[str, Any]:  # pragma: no cover
    """Verify connectivity to Jira instance and validate authentication.

    Returns:
        Connection status and server info including version and URL
    """
    return _jira_health_check()  # pragma: no cover


# Register issue tools
@mcp.tool()
def jira_issue_create_tool(
    project: str,
    summary: str,
    issue_type: str = "Task",
    description: str = "",
    priority: str | None = None,
    assignee: str | None = None,
    labels: list[str] | None = None,
    due_date: str | None = None,
    custom_fields: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Create a new Jira issue with automatic custom field validation.

    The system automatically discovers and validates custom fields based on the project schema.

    Args:
        project: Project key (e.g., "PROJ", "DEV")
        summary: Issue title/summary (1-255 characters)
        issue_type: Type of issue (Task, Bug, Story, etc.) - default: Task
        description: Detailed issue description (supports Jira markup)
        priority: Issue priority (if not set, uses project default)
        assignee: Username or user ID to assign the issue to
        labels: List of labels to apply to the issue
        due_date: Due date in ISO format (YYYY-MM-DD)
        **custom_fields: Additional custom fields as key-value pairs

    Returns:
        Created issue with key, ID, and all field values

    Example:
        jira_issue_create_tool(
            project="PROJ",
            summary="Implement user authentication",
            issue_type="Task",
            priority="High",
            customfield_10001=5  # Story Points
        )
    """
    kwargs = {}  # pragma: no cover
    if custom_fields:  # pragma: no cover
        kwargs.update(custom_fields)  # pragma: no cover

    return jira_issue_create(  # pragma: no cover
        project=project,
        summary=summary,
        issue_type=issue_type,
        description=description,
        priority=priority,
        assignee=assignee,
        labels=labels or [],
        due_date=due_date,
        **kwargs,
    )


@mcp.tool()
def jira_issue_update_tool(
    issue_key: str,
    summary: str | None = None,
    description: str | None = None,
    priority: str | None = None,
    assignee: str | None = None,
    labels: list[str] | None = None,
    due_date: str | None = None,
    custom_fields: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Update an existing Jira issue.

    Only provided fields are updated. Custom fields are validated against the project schema.

    Args:
        issue_key: Issue key (e.g., "PROJ-123")
        summary: New issue summary
        description: New issue description
        priority: New priority
        assignee: New assignee (username or ID)
        labels: Replace existing labels
        due_date: New due date
        **custom_fields: Custom fields to update

    Returns:
        Updated issue with all current field values

    Example:
        jira_issue_update_tool(
            issue_key="PROJ-123",
            summary="Updated summary",
            priority="Critical"
        )
    """
    kwargs = {}  # pragma: no cover
    if custom_fields:  # pragma: no cover
        kwargs.update(custom_fields)  # pragma: no cover

    return jira_issue_update(  # pragma: no cover
        issue_key=issue_key,
        summary=summary,
        description=description,
        priority=priority,
        assignee=assignee,
        labels=labels,
        due_date=due_date,
        **kwargs,
    )


@mcp.tool()
def jira_issue_get_tool(issue_key: str) -> Dict[str, Any]:
    """Retrieve full details of a single issue including all custom fields.

    Args:
        issue_key: Issue key (e.g., "PROJ-123")

    Returns:
        Complete issue details including standard and custom fields

    Example:
        jira_issue_get_tool(issue_key="PROJ-123")
    """
    return jira_issue_get(issue_key=issue_key)  # pragma: no cover


@mcp.tool()
def jira_project_get_schema(project: str, issue_type: str = "Task") -> Dict[str, Any]:
    """Get field schema for a project and issue type for debugging.

    This tool helps you understand what fields are available for a project
    and issue type, including custom fields and their validation rules.

    Args:
        project: Project key (e.g., "PROJ")
        issue_type: Issue type name (default: "Task")

    Returns:
        Field schema showing all available fields with their types and requirements

    Example:
        jira_project_get_schema(project="PROJ", issue_type="Bug")
    """
    try:  # pragma: no cover
        schemas = _get_field_schema(project, issue_type)  # pragma: no cover
        return {  # pragma: no cover
            "project": project,
            "issue_type": issue_type,
            "fields": [
                {
                    "key": schema.key,
                    "name": schema.name,
                    "type": schema.type.value,
                    "required": schema.required,
                    "custom": schema.custom,
                    "allowed_values": schema.allowed_values,
                }
                for schema in schemas
            ],
        }
    except Exception as e:  # pragma: no cover
        return {"error": str(e)}  # pragma: no cover


# Register search tools
@mcp.tool()
def jira_search_issues_tool(
    project: str | None = None,
    assignee: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    labels: list[str] | None = None,
    created_after: str | None = None,
    created_before: str | None = None,
    updated_after: str | None = None,
    updated_before: str | None = None,
    max_results: int = 50,
    start_at: int = 0,
) -> Dict[str, Any]:
    """Search for Jira issues using multiple criteria.

    Build a JQL query from the provided criteria and execute it. At least one search criterion must be provided.

    Args:
        project: Project key (e.g., "PROJ")
        assignee: Assignee username or "currentUser()" for current user
        status: Status name (e.g., "Open", "In Progress", "Closed")
        priority: Priority name (e.g., "High", "Critical", "Low")
        labels: List of label names to filter by
        created_after: Created after date in YYYY-MM-DD format
        created_before: Created before date in YYYY-MM-DD format
        updated_after: Updated after date in YYYY-MM-DD format
        updated_before: Updated before date in YYYY-MM-DD format
        max_results: Maximum results to return (default: 50)
        start_at: Starting offset for pagination (default: 0)

    Returns:
        Search results with total count, issues list, and pagination info

    Example:
        jira_search_issues_tool(
            project="PROJ",
            status="Open",
            assignee="currentUser()",
            max_results=10
        )
    """
    return jira_search_issues(  # pragma: no cover
        project=project,
        assignee=assignee,
        status=status,
        priority=priority,
        labels=labels,
        created_after=created_after,
        created_before=created_before,
        updated_after=updated_after,
        updated_before=updated_before,
        max_results=max_results,
        start_at=start_at,
    )


@mcp.tool()
def jira_search_jql_tool(
    jql: str,
    max_results: int = 50,
    start_at: int = 0,
) -> Dict[str, Any]:
    """Execute a JQL (Jira Query Language) query directly.

    Use this for complex queries that can't be expressed through search_issues criteria.
    Supports all JQL operators and functions including ORDER BY clauses.

    Args:
        jql: JQL query string (e.g., 'project = PROJ AND created >= -7d ORDER BY created DESC')
        max_results: Maximum results to return (default: 50)
        start_at: Starting offset for pagination (default: 0)

    Returns:
        Search results with total count, issues list, and pagination info

    Example:
        jira_search_jql_tool(
            jql='project = PROJ AND created >= -7d AND assignee = currentUser() ORDER BY created DESC',
            max_results=20
        )
    """
    return jira_search_jql(  # pragma: no cover
        jql=jql,
        max_results=max_results,
        start_at=start_at,
    )


# Register filter tools
@mcp.tool()
def jira_filter_create_tool(
    name: str,
    jql: str,
    description: str | None = None,
    favourite: bool = False,
) -> Dict[str, Any]:
    """Create a new saved filter for reusing complex search queries.

    Filters allow you to save JQL queries for quick access to frequently-needed issue sets.

    Args:
        name: Filter name (required)
        jql: JQL query string (required)
        description: Optional filter description
        favourite: Whether to mark as favorite (default: False)

    Returns:
        Created filter with ID and details

    Example:
        jira_filter_create_tool(
            name="My Open Issues",
            jql="assignee = currentUser() AND status = Open",
            description="All my open issues"
        )
    """
    return jira_filter_create(  # pragma: no cover
        name=name,
        jql=jql,
        description=description,
        favourite=favourite,
    )


@mcp.tool()
def jira_filter_list_tool() -> Dict[str, Any]:
    """List all accessible filters.

    Returns all filters you have permission to view, including your own and shared filters.

    Returns:
        List of filter metadata (ID, name, JQL, owner)

    Example:
        jira_filter_list_tool()
    """
    return jira_filter_list()  # pragma: no cover


@mcp.tool()
def jira_filter_get_tool(filter_id: str) -> Dict[str, Any]:
    """Get complete filter details by ID.

    Args:
        filter_id: Filter ID

    Returns:
        Complete filter information including JQL, owner, and permissions

    Example:
        jira_filter_get_tool(filter_id="10000")
    """
    return jira_filter_get(filter_id=filter_id)  # pragma: no cover


@mcp.tool()
def jira_filter_execute_tool(
    filter_id: str,
    max_results: int = 50,
    start_at: int = 0,
) -> Dict[str, Any]:
    """Execute a saved filter and return matching issues.

    Retrieves the filter's JQL and executes it with pagination support.

    Args:
        filter_id: Filter ID
        max_results: Maximum results to return (default: 50)
        start_at: Starting offset for pagination (default: 0)

    Returns:
        Search results with total count, issues list, and pagination info

    Example:
        jira_filter_execute_tool(filter_id="10000", max_results=20)
    """
    return jira_filter_execute(  # pragma: no cover
        filter_id=filter_id,
        max_results=max_results,
        start_at=start_at,
    )


@mcp.tool()
def jira_filter_update_tool(
    filter_id: str,
    name: str | None = None,
    jql: str | None = None,
    description: str | None = None,
    favourite: bool | None = None,
) -> Dict[str, Any]:
    """Update an existing filter.

    Only provided fields are updated. At least one field must be provided.

    Args:
        filter_id: Filter ID
        name: New filter name
        jql: New JQL query
        description: New description
        favourite: Whether to mark as favorite

    Returns:
        Updated filter data

    Example:
        jira_filter_update_tool(
            filter_id="10000",
            jql="assignee = currentUser() AND status IN (Open, 'In Progress')"
        )
    """
    return jira_filter_update(  # pragma: no cover
        filter_id=filter_id,
        name=name,
        jql=jql,
        description=description,
        favourite=favourite,
    )


@mcp.tool()
def jira_filter_delete_tool(filter_id: str) -> Dict[str, Any]:
    """Delete a filter.

    Only the filter owner can delete it.

    Args:
        filter_id: Filter ID

    Returns:
        Success confirmation message

    Example:
        jira_filter_delete_tool(filter_id="10000")
    """
    return jira_filter_delete(filter_id=filter_id)  # pragma: no cover


# Register workflow tools
@mcp.tool()
def jira_workflow_get_transitions_tool(issue_key: str) -> Dict[str, Any]:
    """Get available workflow transitions for an issue.

    Returns all transitions available for the issue in its current state, including
    transition IDs, names, destination statuses, and required fields.

    Args:
        issue_key: Issue key (e.g., "PROJ-123")

    Returns:
        Available transitions with IDs, names, destination statuses, and required fields

    Example:
        jira_workflow_get_transitions_tool(issue_key="PROJ-123")
    """
    return jira_workflow_get_transitions(issue_key=issue_key)  # pragma: no cover


@mcp.tool()
def jira_workflow_transition_tool(
    issue_key: str, transition_id: str, fields: Dict[str, Any] | None = None
) -> Dict[str, Any]:
    """Transition an issue through workflow.

    Executes a workflow transition, moving the issue to a new status. Some transitions
    may require additional fields (e.g., resolution when closing an issue).

    Args:
        issue_key: Issue key (e.g., "PROJ-123")
        transition_id: Transition ID to execute (use get_transitions to find valid IDs)
        fields: Optional fields required by the transition (e.g., {"resolution": {"name": "Done"}})

    Returns:
        Success confirmation with issue key and transition details

    Example:
        # Simple transition
        jira_workflow_transition_tool(issue_key="PROJ-123", transition_id="21")

        # Transition with resolution
        jira_workflow_transition_tool(
            issue_key="PROJ-123",
            transition_id="31",
            fields={"resolution": {"name": "Done"}}
        )
    """
    return jira_workflow_transition(  # pragma: no cover
        issue_key=issue_key, transition_id=transition_id, fields=fields
    )


# Register comment tools
@mcp.tool()
def jira_comment_add_tool(issue_key: str, body: str) -> Dict[str, Any]:
    """Add a comment to an issue.

    Comments support Jira markup for formatting (bold, italic, lists, etc.).

    Args:
        issue_key: Issue key (e.g., "PROJ-123")
        body: Comment text (supports Jira markup)

    Returns:
        Created comment with ID, author, and timestamp

    Example:
        jira_comment_add_tool(
            issue_key="PROJ-123",
            body="This issue is ready for review"
        )
    """
    return jira_comment_add(issue_key=issue_key, body=body)  # pragma: no cover


@mcp.tool()
def jira_comment_list_tool(issue_key: str) -> Dict[str, Any]:
    """List all comments on an issue.

    Retrieves all comments with author information and timestamps.

    Args:
        issue_key: Issue key (e.g., "PROJ-123")

    Returns:
        Comments list with total count and comment details

    Example:
        jira_comment_list_tool(issue_key="PROJ-123")
    """
    return jira_comment_list(issue_key=issue_key)  # pragma: no cover


@mcp.tool()
def jira_comment_update_tool(issue_key: str, comment_id: str, body: str) -> Dict[str, Any]:
    """Update an existing comment.

    Only the comment author or users with appropriate permissions can update a comment.

    Args:
        issue_key: Issue key (e.g., "PROJ-123")
        comment_id: Comment ID to update
        body: New comment text (supports Jira markup)

    Returns:
        Updated comment with ID, author, and timestamp

    Example:
        jira_comment_update_tool(
            issue_key="PROJ-123",
            comment_id="10001",
            body="Updated comment text"
        )
    """
    return jira_comment_update(issue_key=issue_key, comment_id=comment_id, body=body)  # pragma: no cover


@mcp.tool()
def jira_comment_delete_tool(issue_key: str, comment_id: str) -> Dict[str, Any]:
    """Delete a comment.

    Only the comment author or users with appropriate permissions can delete a comment.

    Args:
        issue_key: Issue key (e.g., "PROJ-123")
        comment_id: Comment ID to delete

    Returns:
        Success confirmation with deleted comment ID

    Example:
        jira_comment_delete_tool(issue_key="PROJ-123", comment_id="10001")
    """
    return jira_comment_delete(issue_key=issue_key, comment_id=comment_id)  # pragma: no cover


def main() -> None:
    """Main entry point for the Jira MCP server."""
    try:
        # Load configuration
        config = JiraConfig()  # type: ignore[call-arg]  # pydantic-settings loads from env

        # Initialize client
        client = JiraClient(config)

        # Initialize issue tools
        initialize_issue_tools(config)

        # Initialize search tools
        initialize_search_tools(client)

        # Initialize filter tools
        initialize_filter_tools(client)

        # Initialize workflow tools
        initialize_workflow_tools(client)

        # Initialize comment tools
        initialize_comment_tools(client)

        print("Starting Jira MCP Server...")
        print(f"Jira URL: {config.url}")
        print(f"Cache TTL: {config.cache_ttl}s")
        print(f"Timeout: {config.timeout}s")
        print()
        print("Server ready! Use MCP client to interact with Jira.")

        # Run FastMCP server
        mcp.run()

    except Exception as e:
        print(f"Error starting server: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
