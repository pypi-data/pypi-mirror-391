"""Pydantic models for Jira MCP Server (T012-T016)"""

from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

# Enums


class FieldType(str, Enum):
    """Jira field types (T012)."""

    STRING = "string"
    NUMBER = "number"
    DATE = "date"
    DATETIME = "datetime"
    USER = "user"
    OPTION = "option"
    ARRAY = "array"
    MULTI_SELECT = "multiselect"


# Core Models


class FieldSchema(BaseModel):
    """Schema definition for a Jira field (T012)."""

    key: str = Field(..., description="Field identifier (e.g., 'summary', 'customfield_10001')")
    name: str = Field(..., description="Human-readable field name")
    type: FieldType = Field(..., description="Field data type")
    required: bool = Field(..., description="Whether field is mandatory")
    allowed_values: Optional[List[str]] = Field(default=None, description="Allowed values for select-list fields")
    custom: bool = Field(..., description="Whether this is a custom field")
    schema_type: Optional[str] = Field(default=None, description="Jira schema type details")

    @field_validator("key")
    @classmethod
    def validate_key(cls, v: str) -> str:
        """Validate field key format."""
        if not (v.isidentifier() or v.startswith("customfield_")):
            raise ValueError(f"Invalid field key: {v}")
        return v


class Issue(BaseModel):
    """Jira issue model (T013)."""

    key: str = Field(..., pattern=r"^[A-Z]+-\d+$", description="Issue key (e.g., 'PROJ-123')")
    id: str = Field(..., description="Internal Jira ID")
    self: str = Field(..., description="API URL for this issue")
    project: str = Field(..., description="Project key")
    issue_type: str = Field(..., description="Issue type (Bug, Task, Story, etc.)")
    summary: str = Field(..., min_length=1, description="Issue title/summary")
    description: Optional[str] = Field(default=None, description="Detailed description")
    status: str = Field(..., description="Current workflow status")
    priority: Optional[str] = Field(default=None, description="Issue priority")
    assignee: Optional[str] = Field(default=None, description="Assigned user")
    reporter: Optional[str] = Field(default=None, description="Issue creator")
    created: datetime = Field(..., description="Creation timestamp")
    updated: datetime = Field(..., description="Last update timestamp")
    due_date: Optional[date] = Field(default=None, description="Due date if set")
    labels: List[str] = Field(default_factory=list, description="Issue labels")
    custom_fields: Dict[str, Any] = Field(default_factory=dict, description="Project-specific custom fields")

    # Note: Pattern validator above already ensures correct format (PROJECT-123)


class Project(BaseModel):
    """Jira project model (T014)."""

    key: str = Field(..., pattern=r"^[A-Z][A-Z0-9]{1,9}$", description="Project key")
    id: str = Field(..., description="Internal project ID")
    name: str = Field(..., description="Human-readable project name")
    self: str = Field(..., description="API URL")
    issue_types: List[str] = Field(..., description="Allowed issue types for this project")
    lead: Optional[str] = Field(default=None, description="Project lead username")


class SearchResult(BaseModel):
    """Wrapper for search query results (T015)."""

    total: int = Field(..., description="Total matching issues")
    max_results: int = Field(..., description="Max results per page")
    start_at: int = Field(..., description="Offset for pagination")
    issues: List[Issue] = Field(..., description="List of matching issues")


class CachedSchema(BaseModel):
    """Internal model for schema caching (T016)."""

    project_key: str = Field(..., description="Project key")
    issue_type: str = Field(..., description="Issue type")
    fields: List[FieldSchema] = Field(..., description="Field schemas")
    cached_at: datetime = Field(..., description="When schema was cached")
    expires_at: datetime = Field(..., description="When schema expires")


class Filter(BaseModel):
    """Saved search filter model."""

    id: str = Field(..., description="Filter ID")
    name: str = Field(..., min_length=1, description="User-defined filter name")
    description: Optional[str] = Field(default=None, description="Filter description")
    jql: str = Field(..., min_length=1, description="JQL query string")
    owner: str = Field(..., description="Filter creator username")
    favourite: bool = Field(default=False, description="Whether filter is favorited")
    share_permissions: List[str] = Field(default_factory=list, description="Who can access this filter")


class WorkflowTransition(BaseModel):
    """Workflow transition model."""

    id: str = Field(..., description="Transition ID")
    name: str = Field(..., description="Transition name")
    to_status: str = Field(..., description="Destination status")
    has_screen: bool = Field(..., description="Whether transition shows a screen")
    required_fields: List[str] = Field(default_factory=list, description="Fields that must be provided")


class Comment(BaseModel):
    """Issue comment model."""

    id: str = Field(..., description="Comment ID")
    author: str = Field(..., description="Comment author username")
    body: str = Field(..., min_length=1, description="Comment text")
    created: datetime = Field(..., description="Creation timestamp")
    updated: datetime = Field(..., description="Last update timestamp")
    visibility: Optional[str] = Field(default=None, description="Visibility restriction (role/group)")


# Exception Classes


class JiraAPIError(Exception):
    """Raised when Jira API returns an error."""

    def __init__(self, message: str, jira_errors: Optional[List[str]] = None):
        self.jira_errors = jira_errors or []
        super().__init__(message)


class FieldValidationError(Exception):
    """Raised when field validation fails."""

    def __init__(self, field_name: str, reason: str):
        self.field_name = field_name
        self.reason = reason
        super().__init__(f"Field '{field_name}' validation failed: {reason}")
