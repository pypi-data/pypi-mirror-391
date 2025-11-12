"""MCP tools for issue management (T026-T028)"""

from typing import Any, Dict, List, Optional

from jira_mcp_server.config import JiraConfig
from jira_mcp_server.jira_client import JiraClient
from jira_mcp_server.models import FieldSchema, FieldType, FieldValidationError
from jira_mcp_server.schema_cache import SchemaCache
from jira_mcp_server.validators import FieldValidator

# Global instances (initialized by server)
_client: Optional[JiraClient] = None
_cache: Optional[SchemaCache] = None
_validator: Optional[FieldValidator] = None


def initialize_issue_tools(config: JiraConfig) -> None:
    """Initialize issue tools with configuration.

    Args:
        config: JiraConfig instance
    """
    global _client, _cache, _validator
    _client = JiraClient(config)
    _cache = SchemaCache(ttl_seconds=config.cache_ttl)
    _validator = FieldValidator()


def _get_field_schema(project: str, issue_type: str) -> List[FieldSchema]:
    """Get field schema with caching (T029).

    Args:
        project: Project key
        issue_type: Issue type name

    Returns:
        List of FieldSchema

    Raises:
        ValueError: If schema cannot be retrieved
    """
    if not _cache or not _client:
        raise RuntimeError("Issue tools not initialized")

    # Try cache first
    cached_schema = _cache.get(project, issue_type)
    if cached_schema is not None:
        return cached_schema

    # Fetch from Jira
    raw_schema = _client.get_project_schema(project, issue_type)

    # Convert to FieldSchema models
    field_schemas: List[FieldSchema] = []
    for field_data in raw_schema:
        field_key = field_data.get("key", "")
        field_name = field_data.get("name", field_key)
        field_required = field_data.get("required", False)

        # Determine field type
        schema_info = field_data.get("schema", {})
        schema_type = schema_info.get("type", "string")
        is_custom = field_data.get("custom", field_key.startswith("customfield_"))

        # Map Jira type to our FieldType enum
        if schema_type == "number":
            field_type = FieldType.NUMBER
        elif schema_type == "date":
            field_type = FieldType.DATE
        elif schema_type == "datetime":
            field_type = FieldType.DATETIME
        elif schema_type == "user":
            field_type = FieldType.USER
        elif schema_type == "option":
            field_type = FieldType.OPTION
        elif schema_type == "array":
            field_type = FieldType.ARRAY
        else:
            field_type = FieldType.STRING

        # Get allowed values for select fields
        allowed_values = None
        if "allowedValues" in field_data:
            allowed_values = [v.get("value") or v.get("name") for v in field_data["allowedValues"]]

        field_schema = FieldSchema(
            key=field_key,
            name=field_name,
            type=field_type,
            required=field_required,
            allowed_values=allowed_values,
            custom=is_custom,
            schema_type=str(schema_info),
        )
        field_schemas.append(field_schema)

    # Cache the schema
    _cache.set(project, issue_type, field_schemas)

    return field_schemas


def jira_issue_create(
    project: str,
    summary: str,
    issue_type: str = "Task",
    description: str = "",
    priority: Optional[str] = None,
    assignee: Optional[str] = None,
    labels: Optional[List[str]] = None,
    due_date: Optional[str] = None,
    **custom_fields: Any,
) -> Dict[str, Any]:
    """Create a new Jira issue with automatic custom field validation (T026).

    Args:
        project: Project key (e.g., "PROJ")
        summary: Issue title/summary
        issue_type: Type of issue (default: "Task")
        description: Detailed description
        priority: Issue priority
        assignee: Username or ID to assign
        labels: List of labels
        due_date: Due date in ISO format (YYYY-MM-DD)
        **custom_fields: Additional custom fields as keyword arguments

    Returns:
        Created issue with key, ID, and field values

    Raises:
        ValueError: If validation fails or API error
        FieldValidationError: If field validation fails
    """
    if not _client or not _validator:
        raise RuntimeError("Issue tools not initialized")

    # Get field schema (T030)
    try:
        schema = _get_field_schema(project, issue_type)
    except Exception as e:
        raise ValueError(f"Failed to get project schema: {str(e)}")

    # Build fields dictionary
    fields: Dict[str, Any] = {
        "project": {"key": project},
        "summary": summary,
        "issuetype": {"name": issue_type},
    }

    if description:
        fields["description"] = description
    if priority:
        fields["priority"] = {"name": priority}
    if assignee:
        fields["assignee"] = {"name": assignee}
    if labels:
        fields["labels"] = labels
    if due_date:
        fields["duedate"] = due_date

    # Add custom fields
    for key, value in custom_fields.items():
        fields[key] = value

    # Validate fields (T031)
    try:
        _validator.validate_fields(fields, schema)
    except FieldValidationError as e:
        # Re-raise with clear message (T033)
        raise ValueError(f"Validation failed: {str(e)}")

    # Create issue
    issue_data = {"fields": fields}

    try:
        result = _client.create_issue(issue_data)
        return result
    except Exception as e:
        # Error handling (T033)
        raise ValueError(f"Failed to create issue: {str(e)}")


def jira_issue_update(
    issue_key: str,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    assignee: Optional[str] = None,
    labels: Optional[List[str]] = None,
    due_date: Optional[str] = None,
    **custom_fields: Any,
) -> Dict[str, Any]:
    """Update an existing Jira issue (T027).

    Args:
        issue_key: Issue key (e.g., "PROJ-123")
        summary: New summary
        description: New description
        priority: New priority
        assignee: New assignee
        labels: New labels (replaces existing)
        due_date: New due date
        **custom_fields: Custom fields to update

    Returns:
        Updated issue data

    Raises:
        ValueError: If issue not found or validation fails
    """
    if not _client:
        raise RuntimeError("Issue tools not initialized")

    # Build update dictionary
    fields: Dict[str, Any] = {}

    if summary is not None:
        fields["summary"] = summary
    if description is not None:
        fields["description"] = description
    if priority is not None:
        fields["priority"] = {"name": priority}
    if assignee is not None:
        fields["assignee"] = {"name": assignee}
    if labels is not None:
        fields["labels"] = labels
    if due_date is not None:
        fields["duedate"] = due_date

    # Add custom fields
    for key, value in custom_fields.items():
        fields[key] = value

    if not fields:
        raise ValueError("No fields provided to update")

    # Update issue
    update_data = {"fields": fields}

    try:
        _client.update_issue(issue_key, update_data)
        # Get updated issue
        return _client.get_issue(issue_key)
    except Exception as e:
        raise ValueError(f"Failed to update issue: {str(e)}")


def jira_issue_get(issue_key: str) -> Dict[str, Any]:
    """Get full details of a Jira issue (T028).

    Args:
        issue_key: Issue key (e.g., "PROJ-123")

    Returns:
        Complete issue details including all fields

    Raises:
        ValueError: If issue not found
    """
    if not _client:
        raise RuntimeError("Issue tools not initialized")

    try:
        return _client.get_issue(issue_key)
    except Exception as e:
        raise ValueError(f"Failed to get issue: {str(e)}")


# Tool metadata for FastMCP registration
ISSUE_TOOLS = {
    "jira_issue_create": {
        "function": jira_issue_create,
        "description": "Create a new Jira issue with automatic custom field validation",
    },
    "jira_issue_update": {
        "function": jira_issue_update,
        "description": "Update an existing Jira issue",
    },
    "jira_issue_get": {
        "function": jira_issue_get,
        "description": "Get full details of a Jira issue",
    },
}
