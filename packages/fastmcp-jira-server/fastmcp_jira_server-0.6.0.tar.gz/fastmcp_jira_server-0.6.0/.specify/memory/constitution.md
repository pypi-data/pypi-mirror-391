# Jira MCP Server Constitution

## Core Principles

### I. MCP-First Architecture
All functionality is exposed through the Model Context Protocol (MCP) framework using FastMCP. The server acts as a bridge between AI assistants and Jira, enabling natural language interaction with Jira instances. All operations must be accessible as MCP tools with clear, descriptive interfaces.

### II. Self-Hosted Jira Focus
This server is designed exclusively for self-hosted (on-premise) Jira instances using token-based authentication. Cloud-specific features are out of scope. All API calls use Jira REST API v2 for maximum compatibility with Jira 7.0+.

### III. Schema-Aware Intelligence
The server must automatically discover and adapt to project-specific schemas. Custom field handling is a core competency, not an afterthought. Schema caching and validation are mandatory to prevent invalid API calls and provide helpful error messages.

### IV. Pip-Installable Package
The server must be installable via `pip install jira-mcp-server` and configurable through environment variables or config files. No complex setup processes. Users should be able to start using it within 30 seconds of installation.

### V. Test-First Development (NON-NEGOTIABLE)
All functionality requires tests before implementation:
- Unit tests for business logic and validation
- Integration tests for Jira API interactions (using mocked responses)
- Contract tests to ensure MCP tool interfaces remain stable
- Red-Green-Refactor cycle strictly enforced

### VI. Clear Error Messages
All errors must provide actionable guidance. Field validation errors must indicate which field failed and why. Authentication errors must explain how to fix the token. API errors must be translated from Jira's responses into user-friendly messages.

### VII. Minimal Dependencies
Keep dependencies to the essential minimum:
- FastMCP (required for MCP server)
- HTTP client for Jira API calls
- Standard library for everything else
- No heavy frameworks, no unnecessary abstractions

## Quality Standards

### Performance Targets
- Query results returned in <3 seconds for typical queries (up to 100 results)
- Multi-parameter searches complete in <5 seconds
- Schema caching reduces API calls by 80%+
- Filter execution completes in <3 seconds

### Reliability Requirements
- 99% success rate for operations with valid data
- Graceful degradation when Jira is slow or unavailable
- Clear timeout handling with configurable limits
- Automatic retry with exponential backoff for transient failures

### Type Safety
- All functions use type hints
- mypy strict mode compliance
- Pydantic models for all data structures
- No `Any` types except where truly necessary (external API responses)

## Development Workflow

### Package Structure
```
jira-mcp-server/
├── src/jira_mcp_server/
│   ├── server.py          # MCP server entry point
│   ├── jira_client.py     # Jira API client
│   ├── models.py          # Pydantic models
│   ├── schema_cache.py    # Schema caching logic
│   ├── tools/             # MCP tool definitions
│   └── validators.py      # Field validation
├── tests/
│   ├── unit/
│   ├── integration/
│   └── contract/
├── pyproject.toml
├── README.md
└── .env.example
```

### Testing Requirements
- Minimum 80% code coverage
- All MCP tools must have contract tests
- Jira API interactions must be integration tested with mocks
- CI/CD pipeline runs all tests before merge

### Configuration Management
Environment variables with sensible defaults:
- `JIRA_MCP_SERVER_URL` (required)
- `JIRA_MCP_SERVER_TOKEN` (required)
- `JIRA_MCP_SERVER_CACHE_TTL` (default: 3600 seconds)
- `JIRA_MCP_SERVER_TIMEOUT` (default: 30 seconds)

## Governance

This constitution guides all design and implementation decisions. Feature implementations must demonstrate compliance with these principles. Violations require documented justification in the implementation plan's Complexity Tracking table.

**Version**: 1.0.0 | **Ratified**: 2025-11-09 | **Last Amended**: 2025-11-09
