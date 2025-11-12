"""MCP tools for workflow transitions (T058-T059)"""

from typing import Any, Dict, Optional

from jira_mcp_server.jira_client import JiraClient

# Global client instance (initialized by server)
_client: Optional[JiraClient] = None


def initialize_workflow_tools(client: JiraClient) -> None:
    """Initialize workflow tools with JiraClient instance.

    Args:
        client: JiraClient instance
    """
    global _client
    _client = client


def jira_workflow_get_transitions(issue_key: str) -> Dict[str, Any]:
    """Get available transitions for an issue (T058).

    Returns all workflow transitions available for the issue in its current state.

    Args:
        issue_key: Issue key (e.g., "PROJ-123")

    Returns:
        Available transitions with IDs, names, destination statuses, and required fields

    Raises:
        ValueError: If issue not found or access denied

    Example:
        jira_workflow_get_transitions(issue_key="PROJ-123")
    """
    if not _client:
        raise RuntimeError("Workflow tools not initialized")

    if not issue_key or not issue_key.strip():
        raise ValueError("Issue key cannot be empty")

    try:
        result = _client.get_transitions(issue_key=issue_key)
        transitions = result.get("transitions", [])

        # Transform to simpler format
        return {
            "issue_key": issue_key,
            "transitions": [
                {
                    "id": t.get("id"),
                    "name": t.get("name"),
                    "to_status": t.get("to", {}).get("name"),
                    "has_screen": t.get("hasScreen", False),
                    "fields": list(t.get("fields", {}).keys()) if t.get("fields") else [],
                }
                for t in transitions
            ],
        }
    except Exception as e:
        raise ValueError(f"Get transitions failed: {str(e)}")


def jira_workflow_transition(
    issue_key: str, transition_id: str, fields: Dict[str, Any] | None = None
) -> Dict[str, Any]:
    """Transition an issue through workflow (T059).

    Executes a workflow transition, optionally providing required fields.

    Args:
        issue_key: Issue key (e.g., "PROJ-123")
        transition_id: Transition ID to execute
        fields: Optional fields required by the transition (e.g., resolution, comment)

    Returns:
        Success confirmation with issue key and transition details

    Raises:
        ValueError: If transition invalid or required fields missing

    Example:
        # Simple transition
        jira_workflow_transition(issue_key="PROJ-123", transition_id="21")

        # Transition with resolution
        jira_workflow_transition(
            issue_key="PROJ-123",
            transition_id="31",
            fields={"resolution": {"name": "Done"}}
        )
    """
    if not _client:
        raise RuntimeError("Workflow tools not initialized")

    if not issue_key or not issue_key.strip():
        raise ValueError("Issue key cannot be empty")

    if not transition_id or not transition_id.strip():
        raise ValueError("Transition ID cannot be empty")

    try:
        _client.transition_issue(issue_key=issue_key, transition_id=transition_id, fields=fields)
        return {
            "success": True,
            "message": f"Issue {issue_key} transitioned successfully",
            "issue_key": issue_key,
            "transition_id": transition_id,
        }
    except Exception as e:
        raise ValueError(f"Transition failed: {str(e)}")
