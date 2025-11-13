# Research: Jira MCP Server with Token Authentication

**Feature**: 001-jira-mcp-server
**Date**: 2025-11-09

## Research Questions

This document consolidates research findings for key technical decisions required to implement the Jira MCP server.

---

## 1. FastMCP Framework Usage

### Decision
Use FastMCP as the MCP server framework with its decorator-based tool definition pattern.

### Rationale
- FastMCP is the official Python framework for building MCP servers
- Provides decorator-based syntax (`@mcp.tool()`) for defining tools
- Handles MCP protocol details automatically
- Built-in support for typed parameters using Pydantic
- Simplifies server lifecycle management
- Active development and community support

### Implementation Approach
```python
from fastmcp import FastMCP

mcp = FastMCP("jira-mcp-server")

@mcp.tool()
def create_issue(project: str, summary: str, description: str, **custom_fields) -> dict:
    """Create a new Jira issue with required and custom fields."""
    # Implementation
    pass
```

### Alternatives Considered
- **Python MCP SDK**: Lower-level, requires manual protocol handling. Rejected because FastMCP abstracts this complexity.
- **Custom MCP implementation**: Would require significant protocol knowledge. Rejected due to maintenance burden.

---

## 2. HTTP Client for Jira API

### Decision
Use `httpx` as the HTTP client library for Jira REST API calls.

### Rationale
- Modern async/sync support (can add async later if needed)
- Better timeout handling than `requests`
- Built-in HTTP/2 support
- Clean API similar to `requests`
- Active maintenance
- Excellent error handling

### Implementation Approach
```python
import httpx

class JiraClient:
    def __init__(self, base_url: str, token: str, timeout: int = 30):
        self.client = httpx.Client(
            base_url=base_url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=timeout
        )

    def get_issue(self, issue_key: str) -> dict:
        response = self.client.get(f"/rest/api/2/issue/{issue_key}")
        response.raise_for_status()
        return response.json()
```

### Alternatives Considered
- **requests**: Widely used but lacks async support and modern timeout handling. Would work but httpx is more future-proof.
- **aiohttp**: Async-only, would complicate initial implementation. Can migrate later if performance demands it.

---

## 3. Schema Caching Strategy

### Decision
Implement in-memory TTL-based cache with 1-hour expiration, using Python's built-in `time` module and dictionaries.

### Rationale
- Simple implementation with no external dependencies
- 1-hour TTL matches requirement from spec (User Story 3, Scenario 4)
- In-memory storage is fast and appropriate for schema data
- Cache key: project_key + issue_type → schema
- Thread-safe with proper locking if needed for concurrent access

### Implementation Approach
```python
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Optional

@dataclass
class CachedSchema:
    schema: dict
    expires_at: datetime

class SchemaCache:
    def __init__(self, ttl_seconds: int = 3600):
        self._cache: Dict[str, CachedSchema] = {}
        self._ttl = timedelta(seconds=ttl_seconds)

    def get(self, project_key: str, issue_type: str) -> Optional[dict]:
        key = f"{project_key}:{issue_type}"
        entry = self._cache.get(key)

        if entry and datetime.now() < entry.expires_at:
            return entry.schema

        # Expired or not found
        if entry:
            del self._cache[key]
        return None

    def set(self, project_key: str, issue_type: str, schema: dict):
        key = f"{project_key}:{issue_type}"
        self._cache[key] = CachedSchema(
            schema=schema,
            expires_at=datetime.now() + self._ttl
        )
```

### Alternatives Considered
- **Redis/External cache**: Over-engineered for this use case. Adds deployment complexity.
- **File-based cache**: Slower, requires file I/O, cache invalidation complexity.
- **No caching**: Would violate SC-008 (80% API call reduction).

---

## 4. Field Validation Strategy

### Decision
Use Pydantic for data modeling and implement custom validators for Jira-specific field types.

### Rationale
- Pydantic provides runtime type validation
- Integrates seamlessly with FastMCP
- Can define custom validators for Jira field types
- Clear error messages out of the box
- JSON schema generation capability

### Implementation Approach
```python
from pydantic import BaseModel, field_validator
from typing import Optional, List, Any
from enum import Enum

class JiraFieldType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    DATE = "date"
    USER = "user"
    OPTION = "option"
    ARRAY = "array"

class FieldSchema(BaseModel):
    key: str
    name: str
    type: JiraFieldType
    required: bool
    allowed_values: Optional[List[str]] = None

class FieldValidator:
    def validate_field(self, value: Any, schema: FieldSchema) -> tuple[bool, Optional[str]]:
        """Returns (is_valid, error_message)"""
        if schema.required and value is None:
            return False, f"Field '{schema.name}' is required"

        if schema.type == JiraFieldType.OPTION:
            if schema.allowed_values and value not in schema.allowed_values:
                return False, f"Invalid value for '{schema.name}'. Allowed: {schema.allowed_values}"

        # Additional type checks...
        return True, None
```

### Alternatives Considered
- **Manual validation**: Error-prone, lots of boilerplate. Rejected for code quality.
- **cerberus**: Another validation library. Pydantic is more Pythonic and integrates with FastMCP.

---

## 5. JQL Query Handling

### Decision
Pass JQL queries directly to Jira API without validation or parsing. Rely on Jira's validation.

### Rationale
- JQL is complex and Jira already validates it
- Building a JQL parser/validator would be significant scope creep
- Error messages from Jira are already reasonably clear
- We can wrap errors with helpful context

### Implementation Approach
```python
def search_jql(jql: str, max_results: int = 100) -> List[dict]:
    """
    Execute a JQL query.

    Note: JQL syntax is validated by Jira. If query is invalid,
    you'll receive an error message explaining the problem.
    """
    try:
        response = client.get("/rest/api/2/search", params={
            "jql": jql,
            "maxResults": max_results
        })
        response.raise_for_status()
        return response.json()["issues"]
    except httpx.HTTPStatusError as e:
        # Wrap Jira error with context
        raise ValueError(f"Invalid JQL query: {e.response.json().get('errorMessages', [])}")
```

### Alternatives Considered
- **JQL parser library**: None mature enough in Python. Would add significant complexity.
- **Build our own parser**: Out of scope, massive undertaking.

---

## 6. MCP Tool Design Pattern

### Decision
Organize MCP tools by functional domain (issues, search, filters, workflows, comments) with clear, descriptive names.

### Rationale
- Follows FastMCP best practices
- Makes tool discovery intuitive for AI assistants
- Each tool has single responsibility
- Tool names match user mental model from spec

### Tool Naming Convention
- Prefix with domain: `jira_<domain>_<action>`
- Examples:
  - `jira_issue_create`
  - `jira_issue_update`
  - `jira_issue_get`
  - `jira_search_issues`
  - `jira_filter_create`
  - `jira_filter_list`
  - `jira_filter_execute`
  - `jira_workflow_transition`
  - `jira_comment_add`

### Parameter Design
- Use typed parameters with descriptions
- Required parameters first, optional after
- Use descriptive names matching Jira terminology
- Example:
```python
@mcp.tool()
def jira_issue_create(
    project: str,  # Project key (e.g., "PROJ")
    summary: str,  # Issue title/summary
    issue_type: str = "Task",  # Type of issue to create
    description: str = "",  # Detailed description
    **custom_fields  # Additional custom fields as keyword arguments
) -> dict:
    """Create a new Jira issue with automatic custom field validation."""
    pass
```

### Alternatives Considered
- **Flat namespace**: `create_issue`, `update_issue` - could conflict with other MCP servers.
- **Object-oriented**: Passing objects instead of primitives - violates MCP simplicity.

---

## 7. Error Handling Strategy

### Decision
Implement three-tier error handling: HTTP errors → Jira errors → Validation errors, with clear user-facing messages.

### Rationale
- SC-005 requires 95% of errors to be actionable
- Users need to understand what went wrong and how to fix it
- Different error types require different handling

### Implementation Approach
```python
class JiraAPIError(Exception):
    """Raised when Jira API returns an error."""
    def __init__(self, message: str, jira_errors: List[str]):
        self.jira_errors = jira_errors
        super().__init__(message)

class FieldValidationError(Exception):
    """Raised when field validation fails."""
    def __init__(self, field_name: str, reason: str):
        self.field_name = field_name
        super().__init__(f"Field '{field_name}' validation failed: {reason}")

# In tools:
try:
    # Validate fields
    if not validator.validate_required_fields(project, issue_type, fields):
        raise FieldValidationError("summary", "Field is required")

    # Call Jira API
    response = jira_client.create_issue(...)

except httpx.HTTPStatusError as e:
    # Network/auth errors
    if e.response.status_code == 401:
        raise ValueError("Authentication failed. Check your JIRA_TOKEN is valid.")
    elif e.response.status_code == 403:
        raise ValueError(f"Permission denied. You don't have access to project '{project}'.")
    else:
        jira_errors = e.response.json().get("errorMessages", [])
        raise JiraAPIError("Jira API error", jira_errors)
```

### Alternatives Considered
- **Let exceptions bubble**: Poor UX, violates clear error message principle.
- **Return error codes**: Not Pythonic, harder for AI assistants to understand.

---

## 8. Configuration Management

### Decision
Use environment variables with `pydantic-settings` for type-safe configuration.

### Rationale
- MCP servers are typically configured via environment variables
- pydantic-settings provides validation and type safety
- Can support .env files for local development
- Clear error messages for missing/invalid config

### Implementation Approach
```python
from pydantic_settings import BaseSettings

class JiraConfig(BaseSettings):
    jira_url: str  # Required: Jira instance URL
    jira_token: str  # Required: API token
    cache_ttl: int = 3600  # Optional: Cache TTL in seconds
    timeout: int = 30  # Optional: HTTP timeout

    class Config:
        env_prefix = "JIRA_MCP_"
        env_file = ".env"

# Usage
config = JiraConfig()
```

### Environment Variables
- `JIRA_MCP_URL` (required)
- `JIRA_MCP_TOKEN` (required)
- `JIRA_MCP_CACHE_TTL` (default: 3600)
- `JIRA_MCP_TIMEOUT` (default: 30)

### Alternatives Considered
- **Config file**: Could work but env vars are more MCP-standard.
- **CLI arguments**: Not applicable for MCP servers.

---

## 9. Testing Strategy

### Decision
Three-tier testing: Unit (business logic) → Integration (mocked Jira API) → Contract (MCP tool interfaces).

### Rationale
- Constitutional requirement for TDD
- 80% coverage target
- Need to test without actual Jira instance
- Contract tests ensure MCP tools remain stable

### Testing Approach

**Unit Tests** (pytest):
```python
def test_schema_cache_expiration():
    cache = SchemaCache(ttl_seconds=1)
    cache.set("PROJ", "Bug", {"fields": []})

    assert cache.get("PROJ", "Bug") is not None

    time.sleep(2)

    assert cache.get("PROJ", "Bug") is None  # Expired
```

**Integration Tests** (pytest + responses):
```python
import responses

@responses.activate
def test_create_issue_with_custom_fields():
    responses.add(
        responses.GET,
        "https://jira.example.com/rest/api/2/project/PROJ/...",
        json={"fields": [{"key": "customfield_123", "required": True}]},
        status=200
    )

    responses.add(
        responses.POST,
        "https://jira.example.com/rest/api/2/issue",
        json={"key": "PROJ-123"},
        status=201
    )

    result = jira_client.create_issue("PROJ", "Summary", custom_field_123="value")
    assert result["key"] == "PROJ-123"
```

**Contract Tests**:
```python
def test_mcp_tool_create_issue_signature():
    """Ensure create_issue tool has stable interface."""
    from fastmcp import get_tool

    tool = get_tool("jira_issue_create")

    assert "project" in tool.parameters
    assert "summary" in tool.parameters
    assert tool.parameters["project"]["required"] is True
```

### Alternatives Considered
- **VCR.py for recording**: Could work but responses is simpler for this use case.
- **Live Jira instance**: Flaky, slow, requires credentials in CI.

---

## 10. Package Distribution

### Decision
Use modern Python packaging with `pyproject.toml`, build with `hatchling`, publish to PyPI.

### Rationale
- pyproject.toml is the modern standard (PEP 621)
- hatchling is simple and well-maintained
- Enables `pip install jira-mcp-server`
- setuptools.cfg is legacy

### Configuration
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "jira-mcp-server"
version = "0.1.0"
description = "FastMCP server for self-hosted Jira instances"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "your@email.com"},
]
dependencies = [
    "fastmcp>=0.1.0",
    "httpx>=0.25.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-mock>=3.10.0",
    "responses>=0.22.0",
    "mypy>=1.0.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
]

[project.scripts]
jira-mcp-server = "jira_mcp_server.server:main"
```

### Alternatives Considered
- **setup.py**: Legacy, avoid unless absolutely necessary.
- **poetry**: Good but pyproject.toml + hatchling is simpler.

---

## Summary

All key technical decisions have been researched and documented. No "NEEDS CLARIFICATION" items remain from Technical Context:

✅ Language/Runtime: Python 3.8+ (3.10+ for development)
✅ Framework: FastMCP for MCP server
✅ HTTP Client: httpx
✅ Caching: In-memory TTL-based with 1-hour expiration
✅ Validation: Pydantic + custom Jira field validators
✅ Error Handling: Three-tier with actionable messages
✅ Configuration: Environment variables via pydantic-settings
✅ Testing: pytest with unit/integration/contract tests
✅ Packaging: pyproject.toml + hatchling → PyPI

Ready to proceed to Phase 1: Design & Contracts.
