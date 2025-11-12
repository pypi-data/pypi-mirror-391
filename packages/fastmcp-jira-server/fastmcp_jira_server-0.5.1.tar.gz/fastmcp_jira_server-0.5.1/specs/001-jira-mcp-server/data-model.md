# Data Model: Jira MCP Server

**Feature**: 001-jira-mcp-server
**Date**: 2025-11-09

This document defines the core data models used throughout the Jira MCP server. All models use Pydantic for validation and type safety.

---

## Core Entities

### Issue

Represents a Jira work item with standard and custom fields.

**Fields**:
- `key`: str - Unique issue identifier (e.g., "PROJ-123")
- `id`: str - Internal Jira ID
- `self`: str - API URL for this issue
- `project`: str - Project key
- `issue_type`: str - Type of issue (Bug, Task, Story, etc.)
- `summary`: str - Issue title/summary
- `description`: Optional[str] - Detailed description
- `status`: str - Current workflow status
- `priority`: Optional[str] - Issue priority
- `assignee`: Optional[str] - Assigned user (username or ID)
- `reporter`: Optional[str] - Issue creator
- `created`: datetime - Creation timestamp
- `updated`: datetime - Last update timestamp
- `due_date`: Optional[date] - Due date if set
- `labels`: List[str] - Issue labels
- `custom_fields`: Dict[str, Any] - Project-specific custom fields

**Relationships**:
- Belongs to one Project
- Has zero or more Comments
- Has a current WorkflowStatus
- May have WorkflowTransitions available

**Validation Rules**:
- `key` must match pattern: `[A-Z]+-[0-9]+`
- `summary` is required (non-empty)
- `issue_type` must be valid for the project
- Custom fields validated against project schema

**State Transitions**:
- Status changes through workflow transitions only
- Not all transitions available from all statuses
- Some transitions require additional fields

**Pydantic Model**:
```python
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date
from typing import Optional, Dict, List, Any

class Issue(BaseModel):
    key: str = Field(..., pattern=r"^[A-Z]+-\d+$")
    id: str
    self: str
    project: str
    issue_type: str
    summary: str = Field(..., min_length=1)
    description: Optional[str] = None
    status: str
    priority: Optional[str] = None
    assignee: Optional[str] = None
    reporter: Optional[str] = None
    created: datetime
    updated: datetime
    due_date: Optional[date] = None
    labels: List[str] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("key")
    @classmethod
    def validate_key(cls, v: str) -> str:
        if not v or "-" not in v:
            raise ValueError("Issue key must be in format 'PROJECT-123'")
        return v.upper()
```

---

### Project

Represents a Jira project with metadata and schema information.

**Fields**:
- `key`: str - Project key (e.g., "PROJ")
- `id`: str - Internal project ID
- `name`: str - Human-readable project name
- `self`: str - API URL
- `issue_types`: List[str] - Allowed issue types for this project
- `lead`: Optional[str] - Project lead username

**Relationships**:
- Has many Issues
- Has one or more FieldSchemas (per issue type)

**Validation Rules**:
- `key` must be uppercase, alphanumeric
- `key` length typically 2-10 characters

**Pydantic Model**:
```python
class Project(BaseModel):
    key: str = Field(..., pattern=r"^[A-Z][A-Z0-9]{1,9}$")
    id: str
    name: str
    self: str
    issue_types: List[str]
    lead: Optional[str] = None
```

---

### FieldSchema

Defines metadata for a field (standard or custom) including validation rules.

**Fields**:
- `key`: str - Field identifier (e.g., "summary", "customfield_10001")
- `name`: str - Human-readable field name
- `type`: FieldType - Data type (string, number, date, user, option, array, etc.)
- `required`: bool - Whether field is mandatory
- `allowed_values`: Optional[List[str]] - For select-list fields
- `custom`: bool - Whether this is a custom field
- `schema_type`: Optional[str] - Jira schema type details

**Relationships**:
- Belongs to a Project + IssueType combination
- Used to validate Issue field values

**Validation Rules**:
- `key` format: standard fields or "customfield_[0-9]+"
- `allowed_values` only applicable for option/select types

**Pydantic Model**:
```python
from enum import Enum

class FieldType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    DATE = "date"
    DATETIME = "datetime"
    USER = "user"
    OPTION = "option"
    ARRAY = "array"
    MULTI_SELECT = "multiselect"

class FieldSchema(BaseModel):
    key: str
    name: str
    type: FieldType
    required: bool
    allowed_values: Optional[List[str]] = None
    custom: bool
    schema_type: Optional[str] = None

    @field_validator("key")
    @classmethod
    def validate_key(cls, v: str) -> str:
        # Standard fields or custom field pattern
        if not (v.isidentifier() or v.startswith("customfield_")):
            raise ValueError(f"Invalid field key: {v}")
        return v
```

---

### Filter

Represents a saved search query (JQL or structured criteria).

**Fields**:
- `id`: str - Filter ID
- `name`: str - User-defined filter name
- `description`: Optional[str] - Filter description
- `jql`: str - JQL query string
- `owner`: str - Filter creator username
- `favourite`: bool - Whether filter is favorited
- `share_permissions`: List[str] - Who can access this filter

**Relationships**:
- Owned by a user
- Can be shared with users/groups

**Validation Rules**:
- `name` must be unique per user
- `jql` syntax validated by Jira (not client-side)

**Pydantic Model**:
```python
class Filter(BaseModel):
    id: str
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    jql: str = Field(..., min_length=1)
    owner: str
    favourite: bool = False
    share_permissions: List[str] = Field(default_factory=list)
```

---

### WorkflowTransition

Represents a valid state change for an issue.

**Fields**:
- `id`: str - Transition ID
- `name`: str - Transition name (e.g., "Start Progress", "Resolve")
- `to_status`: str - Destination status
- `has_screen`: bool - Whether transition shows a screen (requires additional fields)
- `required_fields`: List[str] - Fields that must be provided for this transition

**Relationships**:
- Applies to specific Issue
- May require FieldSchema values

**Validation Rules**:
- `id` must match available transitions for current issue status

**Pydantic Model**:
```python
class WorkflowTransition(BaseModel):
    id: str
    name: str
    to_status: str
    has_screen: bool
    required_fields: List[str] = Field(default_factory=list)
```

---

### Comment

Represents user commentary on an issue.

**Fields**:
- `id`: str - Comment ID
- `author`: str - Comment author username
- `body`: str - Comment text (supports Jira markup)
- `created`: datetime - Creation timestamp
- `updated`: datetime - Last update timestamp
- `visibility`: Optional[str] - Visibility restriction (role/group)

**Relationships**:
- Belongs to one Issue

**Validation Rules**:
- `body` cannot be empty

**Pydantic Model**:
```python
class Comment(BaseModel):
    id: str
    author: str
    body: str = Field(..., min_length=1)
    created: datetime
    updated: datetime
    visibility: Optional[str] = None
```

---

## Supporting Models

### JiraConfig

Configuration settings for the Jira MCP server.

```python
from pydantic_settings import BaseSettings

class JiraConfig(BaseSettings):
    jira_url: str = Field(..., description="Jira instance URL")
    jira_token: str = Field(..., description="API authentication token")
    cache_ttl: int = Field(default=3600, description="Schema cache TTL in seconds")
    timeout: int = Field(default=30, description="HTTP request timeout")

    class Config:
        env_prefix = "JIRA_MCP_"
        env_file = ".env"
```

---

### SearchResult

Wrapper for search query results.

```python
class SearchResult(BaseModel):
    total: int = Field(..., description="Total matching issues")
    max_results: int = Field(..., description="Max results per page")
    start_at: int = Field(..., description="Offset for pagination")
    issues: List[Issue] = Field(..., description="List of matching issues")
```

---

### CachedSchema

Internal model for schema caching.

```python
from datetime import datetime

class CachedSchema(BaseModel):
    project_key: str
    issue_type: str
    fields: List[FieldSchema]
    cached_at: datetime
    expires_at: datetime
```

---

## Data Flow

### Issue Creation Flow
1. User provides: project, summary, issue_type, optional fields
2. System fetches FieldSchema for project+issue_type (from cache or Jira)
3. System validates required fields against schema
4. System validates field types and values
5. System sends request to Jira API
6. System returns created Issue model

### Search Flow
1. User provides search criteria or JQL
2. If criteria: System builds JQL query
3. System executes JQL via Jira API
4. System parses response into SearchResult with Issue models
5. System returns SearchResult

### Filter CRUD Flow
1. Create: User provides name, JQL → System creates Filter → Returns Filter model
2. Read: User provides filter ID → System fetches Filter → Returns Filter model
3. Update: User provides filter ID + changes → System updates → Returns updated Filter
4. Delete: User provides filter ID → System deletes → Returns confirmation
5. Execute: User provides filter ID → System fetches JQL → Executes search → Returns SearchResult

---

## Validation Strategy

All models use Pydantic validators to ensure data integrity:

1. **Type Validation**: Automatic via Pydantic type hints
2. **Field Validation**: Using `field_validator` for custom rules
3. **Schema Validation**: FieldSchema models validate against Jira metadata
4. **Business Logic Validation**: Custom validators in tool implementations

Example validation flow:
```python
def validate_custom_fields(fields: Dict[str, Any], schema: List[FieldSchema]) -> List[str]:
    """Returns list of validation errors."""
    errors = []

    # Check required fields
    required_keys = {f.key for f in schema if f.required}
    provided_keys = set(fields.keys())
    missing = required_keys - provided_keys

    if missing:
        missing_names = [f.name for f in schema if f.key in missing]
        errors.append(f"Missing required fields: {', '.join(missing_names)}")

    # Validate field types and values
    for field_schema in schema:
        if field_schema.key in fields:
            value = fields[field_schema.key]

            # Type-specific validation
            if field_schema.type == FieldType.OPTION:
                if field_schema.allowed_values and value not in field_schema.allowed_values:
                    errors.append(
                        f"Invalid value '{value}' for field '{field_schema.name}'. "
                        f"Allowed values: {', '.join(field_schema.allowed_values)}"
                    )

    return errors
```

---

## Summary

All core entities defined with:
✅ Pydantic models for type safety
✅ Validation rules matching requirements
✅ Relationships documented
✅ State transitions identified
✅ Clear data flow patterns

Models support all functional requirements (FR-001 through FR-037) and enable the MCP tools to provide type-safe, validated interactions with Jira.
