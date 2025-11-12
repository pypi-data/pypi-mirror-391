# Implementation Plan: Jira MCP Server with Token Authentication

**Branch**: `001-jira-mcp-server` | **Date**: 2025-11-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-jira-mcp-server/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a pip-installable FastMCP server that enables AI assistants to interact with self-hosted Jira instances through token authentication. The server provides comprehensive issue management (CRUD operations), robust multi-parameter search, custom filter management, workflow transitions, and comment handling. Key differentiator is intelligent handling of project-specific custom field schemas with automatic discovery and validation.

## Technical Context

**Language/Version**: Python 3.8+ (requirement for pip installation, target 3.10+ for development)
**Primary Dependencies**: FastMCP (MCP server framework), httpx or requests (HTTP client for Jira API), Pydantic (data validation)
**Storage**: In-memory cache for project schemas (TTL-based, hourly refresh)
**Testing**: pytest (unit/integration), pytest-mock (mocking Jira API), pytest-cov (coverage tracking)
**Target Platform**: Cross-platform (Linux, macOS, Windows) - MCP server runs as a process
**Project Type**: Single Python package with MCP server entry point
**Performance Goals**:
- Query results <3s (100 results)
- Multi-parameter search <5s
- Filter execution <3s
- Schema cache 80% API call reduction
**Constraints**:
- Self-hosted Jira only (no Cloud)
- Token auth only (no OAuth)
- Jira REST API v2 compatibility (Jira 7.0+)
- 99% success rate with valid data
- Installation to first use <30 seconds
**Scale/Scope**:
- Support projects with 50+ custom fields
- Handle typical Jira installations (100s of projects)
- Concurrent usage by multiple MCP clients

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle Compliance

✅ **I. MCP-First Architecture**: All functionality exposed as MCP tools via FastMCP framework

✅ **II. Self-Hosted Jira Focus**: Exclusively targeting on-premise Jira with REST API v2, token auth only

✅ **III. Schema-Aware Intelligence**: Automatic schema discovery and caching with validation is core requirement (FR-006, FR-007, FR-008, FR-027)

✅ **IV. Pip-Installable Package**: Explicit requirement (FR-002, SC-008, SC-001)

✅ **V. Test-First Development**: Will follow TDD with unit, integration, and contract tests

✅ **VI. Clear Error Messages**: Requirement FR-028, FR-029, FR-030 and SC-005 (95% actionable error messages)

✅ **VII. Minimal Dependencies**: FastMCP + HTTP client + Pydantic + standard library

### Quality Standards Compliance

✅ **Performance Targets**: All targets explicitly defined in Success Criteria (SC-004 through SC-010)

✅ **Reliability Requirements**: 99% success rate required (SC-013), graceful error handling (FR-028, FR-029, FR-030)

✅ **Type Safety**: Will use Pydantic models for all data structures, mypy for type checking

### Gate Status: **PASS** ✅

All constitutional principles align with feature requirements. No violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/001-jira-mcp-server/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── mcp-tools.yaml   # MCP tool definitions
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
jira-mcp-server/
├── src/
│   └── jira_mcp_server/
│       ├── __init__.py
│       ├── server.py           # FastMCP server entry point
│       ├── jira_client.py      # Jira REST API client
│       ├── models.py            # Pydantic models (Issue, Project, Filter, etc.)
│       ├── schema_cache.py     # Schema caching with TTL
│       ├── validators.py       # Field validation logic
│       ├── config.py           # Configuration management
│       └── tools/              # MCP tool implementations
│           ├── __init__.py
│           ├── issue_tools.py      # Create, read, update issues
│           ├── search_tools.py     # Search and query tools
│           ├── filter_tools.py     # Filter CRUD operations
│           ├── workflow_tools.py   # Workflow transitions
│           └── comment_tools.py    # Comment operations
│
├── tests/
│   ├── unit/
│   │   ├── test_models.py
│   │   ├── test_validators.py
│   │   ├── test_schema_cache.py
│   │   └── test_tools/
│   ├── integration/
│   │   ├── test_jira_client.py
│   │   └── test_tool_integration.py
│   └── contract/
│       └── test_mcp_contracts.py
│
├── pyproject.toml          # Package metadata, dependencies, build config
├── README.md               # Installation, configuration, usage
├── .env.example            # Example environment variables
├── LICENSE
└── .gitignore
```

**Structure Decision**: Single Python package structure chosen. This is an MCP server (single-purpose tool), not a web application. All functionality is exposed through MCP tools, no frontend needed. Package follows standard Python packaging conventions with `src/` layout for pip installation.

## Complexity Tracking

*No constitutional violations - table not needed.*

---

## Post-Design Constitution Re-Check

*Evaluated after Phase 1 design artifacts (research.md, data-model.md, contracts/, quickstart.md)*

### Design Decisions Review

✅ **MCP Tools**: 18 tools defined in `contracts/mcp-tools.yaml`
- Issue management: 3 tools (create, update, get)
- Search: 2 tools (criteria-based, JQL)
- Filters: 6 tools (complete CRUD + execute)
- Workflow: 2 tools (get transitions, transition)
- Comments: 2 tools (add, list)
- Schema: 1 tool (get schema)
- Health: 1 tool (connection check)

✅ **Data Models**: All entities use Pydantic (data-model.md)
- Issue, Project, FieldSchema, Filter, WorkflowTransition, Comment
- Type-safe with validation
- No `Any` types except for Jira API responses

✅ **Dependencies Confirmed** (research.md):
- FastMCP (MCP framework)
- httpx (HTTP client)
- Pydantic + pydantic-settings (validation & config)
- pytest, pytest-cov, pytest-mock (testing)
- No additional dependencies

✅ **Architecture Decisions**:
- In-memory TTL cache (1-hour expiration)
- Three-tier error handling with actionable messages
- Environment variable configuration
- Standard Python package structure with src/ layout

✅ **Testing Strategy**:
- Unit tests for business logic
- Integration tests with mocked Jira API
- Contract tests for MCP tool stability
- Target: 80%+ coverage

### Final Gate Status: **PASS** ✅

All design decisions align with constitutional principles:
- MCP-first architecture maintained
- Self-hosted Jira focus preserved
- Schema-aware intelligence implemented via FieldSchema + validation
- Pip installable via pyproject.toml
- TDD approach with comprehensive test strategy
- Clear error messages designed into error handling strategy
- Minimal dependencies (4 production dependencies)

**No violations. Ready to proceed to `/speckit.tasks`.**
