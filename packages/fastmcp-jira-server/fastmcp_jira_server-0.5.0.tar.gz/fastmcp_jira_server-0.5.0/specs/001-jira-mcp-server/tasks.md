# Implementation Tasks: Jira MCP Server with Token Authentication

**Feature**: 001-jira-mcp-server
**Branch**: `001-jira-mcp-server`
**Generated**: 2025-11-09

## Overview

This task list implements a pip-installable FastMCP server for self-hosted Jira instances with intelligent custom field handling. Tasks are organized by user story to enable independent development and testing.

**Total Tasks**: 73
**User Stories**: 6 (3 P1, 1 P2, 2 P3)
**Test-First**: Yes (per constitution requirement V)

---

## Implementation Strategy

### MVP Scope (Recommended First Delivery)
**User Story 1 only**: Create and Update Issues with Smart Custom Field Handling
- Provides immediate value (issue CRUD with field validation)
- Independently testable
- Establishes foundation (models, client, cache, validators)
- ~19 tasks (Setup + Foundational + US1)

### Incremental Delivery Order
1. **MVP**: US1 - Create/Update Issues + Custom Field Handling (P1)
2. **Release 2**: US2 - Robust Search (P1)
3. **Release 3**: US4 - Custom Filters (P2)
4. **Release 4**: US5 - Workflow Transitions (P3)
5. **Release 5**: US6 - Comments (P3)

Each release is independently testable and delivers user value.

---

## Dependencies & Execution Order

### Story Dependencies
```
Setup (Phase 1)
  ↓
Foundational (Phase 2) - BLOCKING for all user stories
  ↓
  ├→ US1: Create/Update Issues (P1) - No dependencies, can start immediately
  ├→ US2: Search (P1) - Depends on: US1 models
  ├→ US3: Custom Field Handling (P1) - Built into US1, no separate phase
  ├→ US4: Filters (P2) - Depends on: US2 search tools
  ├→ US5: Workflows (P3) - Depends on: US1 (uses Issue model)
  └→ US6: Comments (P3) - Depends on: US1 (uses Issue model)
  ↓
Polish & Documentation (Final Phase)
```

### Parallel Execution Opportunities

**Within Setup Phase**: All setup tasks can run in parallel after T001
**Within Foundational Phase**: Tests (T008-T010) parallel with models (T011-T016)
**Within US1**: Tests (T020-T021) parallel with tools (T022-T024)
**Within US2**: Tests (T027-T028) parallel with tools (T029-T030)
**Within US4**: Tests (T036-T039) parallel with tools (T040-T045)
**Within US5**: Tests (T049-T050) parallel with tools (T051-T052)
**Within US6**: Tests (T056-T057) parallel with tools (T058-T059)

---

## Phase 1: Setup & Project Initialization

**Goal**: Create project structure, configure packaging, and set up development environment

### Tasks

- [X] T001 Create Python package structure in src/jira_mcp_server/ with __init__.py
- [X] T002 [P] Create pyproject.toml with FastMCP, httpx, pydantic, pydantic-settings dependencies
- [X] T003 [P] Create .env.example with JIRA_MCP_URL, JIRA_MCP_TOKEN, JIRA_MCP_CACHE_TTL, JIRA_MCP_TIMEOUT
- [X] T004 [P] Create tests/ directory structure (unit/, integration/, contract/)
- [X] T005 [P] Create .gitignore for Python (*.pyc, __pycache__/, .env, .pytest_cache/, etc.)
- [X] T006 [P] Create README.md with installation instructions and quick start
- [X] T007 [P] Create LICENSE file (MIT or as specified)

**Completion Criteria**: Project structure matches plan.md, pip install works in development mode

---

## Phase 2: Foundational Components (BLOCKING)

**Goal**: Implement core infrastructure required by all user stories
**Must Complete Before**: Starting any user story implementation

### Independent Test Criteria
✅ Configuration loads from environment variables
✅ Jira client successfully authenticates and makes test API call
✅ Schema cache stores and retrieves data with TTL expiration
✅ All Pydantic models validate correctly with valid/invalid data

### Tests (TDD - Write First)

- [X] T008 [P] Write unit tests for JiraConfig in tests/unit/test_config.py
- [X] T009 [P] Write unit tests for SchemaCache in tests/unit/test_schema_cache.py
- [X] T010 [P] Write integration tests for JiraClient in tests/integration/test_jira_client.py

### Core Models (data-model.md)

- [X] T011 [P] Implement JiraConfig in src/jira_mcp_server/config.py using pydantic-settings
- [X] T012 [P] Implement FieldType enum and FieldSchema model in src/jira_mcp_server/models.py
- [X] T013 [P] Implement Issue model in src/jira_mcp_server/models.py
- [X] T014 [P] Implement Project model in src/jira_mcp_server/models.py
- [X] T015 [P] Implement SearchResult model in src/jira_mcp_server/models.py
- [X] T016 [P] Implement CachedSchema model in src/jira_mcp_server/models.py

### Core Services

- [X] T017 Implement SchemaCache class in src/jira_mcp_server/schema_cache.py with TTL logic
- [X] T018 Implement JiraClient class in src/jira_mcp_server/jira_client.py with httpx and auth
- [X] T019 Implement health_check method in JiraClient to verify connectivity

**Completion Criteria**: All foundation tests pass, can authenticate to Jira, cache works

---

## Phase 3: User Story 1 - Create and Update Issues (P1)

**Goal**: Enable creating and updating Jira issues with automatic custom field validation

**Story**: As a developer using an AI assistant, I want to create and update Jira issues through natural language commands so that I can track work without leaving my development environment.

**Priority**: P1 (Core MVP functionality)

### Independent Test Criteria
✅ Can create an issue in a project with required fields
✅ Can update specific fields on an existing issue
✅ System identifies and reports missing required fields
✅ System validates custom field values against schema before submission

### Tests (TDD - Write First)

- [ ] T020 [P] [US1] Write contract tests for jira_issue_create tool in tests/contract/test_issue_tools.py
- [ ] T021 [P] [US1] Write contract tests for jira_issue_update tool in tests/contract/test_issue_tools.py
- [ ] T022 [P] [US1] Write contract tests for jira_issue_get tool in tests/contract/test_issue_tools.py

### Field Validation

- [ ] T023 [US1] Implement FieldValidator class in src/jira_mcp_server/validators.py with type checking
- [ ] T024 [US1] Implement validate_required_fields method in validators.py
- [ ] T025 [US1] Implement validate_custom_field_values method in validators.py against schema

### MCP Tools (contracts/mcp-tools.yaml)

- [ ] T026 [US1] Implement jira_issue_create tool in src/jira_mcp_server/tools/issue_tools.py
- [ ] T027 [US1] Implement jira_issue_update tool in src/jira_mcp_server/tools/issue_tools.py
- [ ] T028 [US1] Implement jira_issue_get tool in src/jira_mcp_server/tools/issue_tools.py

### Integration with Schema Cache (US3 - Smart Custom Field Handling)

- [ ] T029 [US1] Add get_project_schema method to JiraClient in src/jira_mcp_server/jira_client.py
- [ ] T030 [US1] Integrate schema cache into issue_create to fetch and validate custom fields
- [ ] T031 [US1] Integrate schema cache into issue_update to validate custom fields

### Error Handling

- [ ] T032 [US1] Implement JiraAPIError and FieldValidationError in src/jira_mcp_server/models.py
- [ ] T033 [US1] Add error handling in issue tools with actionable messages per constitution

**Story Completion Criteria**:
- All US1 contract tests pass
- Can create issue with custom fields in test project
- Can update issue fields
- Missing required fields return clear error messages
- Invalid field values return validation errors with allowed values

---

## Phase 4: User Story 2 - Robust Issue Search (P1)

**Goal**: Enable searching issues by multiple criteria with pagination

**Story**: As a user, I want to search and retrieve Jira issues using a variety of parameters so that I can quickly find relevant work items.

**Priority**: P1 (Core functionality)

### Independent Test Criteria
✅ Can search by project, assignee, status, priority, labels
✅ Can search by date ranges (created, updated, due)
✅ Can combine multiple search criteria
✅ Can execute JQL queries directly
✅ Pagination works correctly

### Tests (TDD - Write First)

- [ ] T034 [P] [US2] Write contract tests for jira_search_issues tool in tests/contract/test_search_tools.py
- [ ] T035 [P] [US2] Write contract tests for jira_search_jql tool in tests/contract/test_search_tools.py

### Search Implementation

- [ ] T036 [US2] Implement build_jql_from_criteria helper in src/jira_mcp_server/tools/search_tools.py
- [ ] T037 [US2] Implement jira_search_issues tool in src/jira_mcp_server/tools/search_tools.py
- [ ] T038 [US2] Implement jira_search_jql tool in src/jira_mcp_server/tools/search_tools.py

### Jira Client Extensions

- [ ] T039 [US2] Add search_issues method to JiraClient with pagination support
- [ ] T040 [US2] Add error handling for invalid JQL queries with helpful messages

**Story Completion Criteria**:
- All US2 contract tests pass
- Can search by single criterion (e.g., project)
- Can search by multiple criteria (e.g., project + status + assignee)
- Can search by date ranges
- JQL search works and returns proper errors for invalid queries
- Pagination returns correct results

---

## Phase 5: User Story 4 - Custom Filter Management (P2)

**Goal**: Enable CRUD operations on saved filters

**Story**: As a user, I want to create, save, and use custom filters so that I can quickly access frequently-needed issue sets.

**Priority**: P2

**Dependencies**: Requires US2 (search tools)

### Independent Test Criteria
✅ Can create a filter with JQL and name
✅ Can list all accessible filters
✅ Can retrieve a single filter's details
✅ Can execute a saved filter
✅ Can update filter criteria
✅ Can delete a filter

### Tests (TDD - Write First)

- [ ] T041 [P] [US4] Write contract tests for jira_filter_create in tests/contract/test_filter_tools.py
- [ ] T042 [P] [US4] Write contract tests for jira_filter_list in tests/contract/test_filter_tools.py
- [ ] T043 [P] [US4] Write contract tests for jira_filter_get in tests/contract/test_filter_tools.py
- [ ] T044 [P] [US4] Write contract tests for jira_filter_execute in tests/contract/test_filter_tools.py
- [ ] T045 [P] [US4] Write contract tests for jira_filter_update in tests/contract/test_filter_tools.py
- [ ] T046 [P] [US4] Write contract tests for jira_filter_delete in tests/contract/test_filter_tools.py

### Data Model

- [ ] T047 [US4] Implement Filter model in src/jira_mcp_server/models.py

### MCP Tools

- [ ] T048 [US4] Implement jira_filter_create tool in src/jira_mcp_server/tools/filter_tools.py
- [ ] T049 [US4] Implement jira_filter_list tool in src/jira_mcp_server/tools/filter_tools.py
- [ ] T050 [US4] Implement jira_filter_get tool in src/jira_mcp_server/tools/filter_tools.py
- [ ] T051 [US4] Implement jira_filter_execute tool in src/jira_mcp_server/tools/filter_tools.py
- [ ] T052 [US4] Implement jira_filter_update tool in src/jira_mcp_server/tools/filter_tools.py
- [ ] T053 [US4] Implement jira_filter_delete tool in src/jira_mcp_server/tools/filter_tools.py

### Jira Client Extensions

- [ ] T054 [US4] Add filter CRUD methods to JiraClient in src/jira_mcp_server/jira_client.py

**Story Completion Criteria**:
- All US4 contract tests pass
- Can create filter and retrieve it by name
- Can execute filter and get results
- Can update filter JQL
- Can delete owned filter
- Cannot delete filter owned by someone else (error)

---

## Phase 6: User Story 5 - Workflow Transitions (P3)

**Goal**: Enable moving issues through workflow states

**Story**: As a user, I want to move issues through workflow states so that I can update issue status as work progresses.

**Priority**: P3

**Dependencies**: Requires US1 (Issue model)

### Independent Test Criteria
✅ Can retrieve available transitions for an issue
✅ Can execute a valid transition
✅ Cannot execute invalid transition (clear error)
✅ Transitions requiring fields prompt for them

### Tests (TDD - Write First)

- [ ] T055 [P] [US5] Write contract tests for jira_workflow_get_transitions in tests/contract/test_workflow_tools.py
- [ ] T056 [P] [US5] Write contract tests for jira_workflow_transition in tests/contract/test_workflow_tools.py

### Data Model

- [ ] T057 [US5] Implement WorkflowTransition model in src/jira_mcp_server/models.py

### MCP Tools

- [ ] T058 [US5] Implement jira_workflow_get_transitions tool in src/jira_mcp_server/tools/workflow_tools.py
- [ ] T059 [US5] Implement jira_workflow_transition tool in src/jira_mcp_server/tools/workflow_tools.py

### Jira Client Extensions

- [ ] T060 [US5] Add get_transitions method to JiraClient in src/jira_mcp_server/jira_client.py
- [ ] T061 [US5] Add transition_issue method to JiraClient in src/jira_mcp_server/jira_client.py

**Story Completion Criteria**:
- All US5 contract tests pass
- Can get available transitions for an issue
- Can transition issue to new state
- Invalid transitions return clear error with available options

---

## Phase 7: User Story 6 - Comments (P3)

**Goal**: Enable adding and retrieving comments on issues

**Story**: As a user, I want to add and retrieve comments on issues so that I can document discussion and decisions.

**Priority**: P3

**Dependencies**: Requires US1 (Issue model)

### Independent Test Criteria
✅ Can add a comment to an issue
✅ Can retrieve all comments from an issue
✅ Comments include author and timestamp

### Tests (TDD - Write First)

- [ ] T062 [P] [US6] Write contract tests for jira_comment_add in tests/contract/test_comment_tools.py
- [ ] T063 [P] [US6] Write contract tests for jira_comment_list in tests/contract/test_comment_tools.py

### Data Model

- [ ] T064 [US6] Implement Comment model in src/jira_mcp_server/models.py

### MCP Tools

- [ ] T065 [US6] Implement jira_comment_add tool in src/jira_mcp_server/tools/comment_tools.py
- [ ] T066 [US6] Implement jira_comment_list tool in src/jira_mcp_server/tools/comment_tools.py

### Jira Client Extensions

- [ ] T067 [US6] Add add_comment method to JiraClient in src/jira_mcp_server/jira_client.py
- [ ] T068 [US6] Add get_comments method to JiraClient in src/jira_mcp_server/jira_client.py

**Story Completion Criteria**:
- All US6 contract tests pass
- Can add comment to issue
- Can retrieve comments with author and timestamp
- Comments appear in Jira web interface

---

## Phase 8: Polish & Cross-Cutting Concerns

**Goal**: Complete MCP server setup, documentation, and quality improvements

### Server Setup

- [ ] T069 Implement FastMCP server initialization in src/jira_mcp_server/server.py
- [ ] T070 Register all MCP tools with FastMCP server in server.py
- [ ] T071 Implement jira_health_check tool in src/jira_mcp_server/tools/issue_tools.py
- [ ] T072 Add jira_project_get_schema tool in src/jira_mcp_server/tools/issue_tools.py for debugging

### Documentation & Quality

- [ ] T073 Run full test suite and achieve 80%+ coverage per constitution
- [ ] T074 Update README.md with complete usage examples from quickstart.md
- [ ] T075 Create CONTRIBUTING.md with development setup instructions
- [ ] T076 Add type hints verification with mypy configuration in pyproject.toml
- [ ] T077 Add code formatting with black configuration in pyproject.toml
- [ ] T078 Run mypy type checking and fix any errors
- [ ] T079 Run black formatting on all source files

**Completion Criteria**:
- MCP server starts and responds to tool calls
- Health check succeeds against test Jira instance
- README has clear install and usage instructions
- Test coverage ≥ 80%
- All type checks pass
- Code is formatted consistently

---

## Parallel Execution Examples

### Example 1: Setup Phase (After T001)
```bash
# All these can run in parallel:
git checkout 001-jira-mcp-server
# Terminal 1: T002 - Create pyproject.toml
# Terminal 2: T003 - Create .env.example
# Terminal 3: T004 - Create tests/ structure
# Terminal 4: T005 - Create .gitignore
# Terminal 5: T006 - Create README.md
# Terminal 6: T007 - Create LICENSE
```

### Example 2: Foundational Phase
```bash
# Tests (T008-T010) in parallel with models (T011-T016)
# Terminal 1: Write all test files (T008-T010)
# Terminal 2: Implement config (T011)
# Terminal 3: Implement models (T012-T016)
# Then: Sequential T017-T019 (depend on models)
```

### Example 3: US1 Implementation
```bash
# After US1 tests written (T020-T022):
# Terminal 1: T023-T025 - Validators
# Terminal 2: T026 - Create tool
# Terminal 3: T027 - Update tool
# Terminal 4: T028 - Get tool
# Then: Sequential integration tasks (T029-T033)
```

---

## Task Summary

### By Phase
- **Phase 1 (Setup)**: 7 tasks
- **Phase 2 (Foundational)**: 12 tasks (3 tests + 9 implementation)
- **Phase 3 (US1 - P1)**: 14 tasks (3 tests + 11 implementation)
- **Phase 4 (US2 - P1)**: 7 tasks (2 tests + 5 implementation)
- **Phase 5 (US4 - P2)**: 14 tasks (6 tests + 8 implementation)
- **Phase 6 (US5 - P3)**: 7 tasks (2 tests + 5 implementation)
- **Phase 7 (US6 - P3)**: 7 tasks (2 tests + 5 implementation)
- **Phase 8 (Polish)**: 11 tasks

**Total**: 79 tasks

### By Type
- **Setup**: 7 tasks
- **Tests (TDD)**: 19 tasks (contract + unit + integration)
- **Models**: 8 tasks
- **MCP Tools**: 18 tasks
- **Client/Services**: 16 tasks
- **Documentation/Quality**: 11 tasks

### Parallelization Opportunities
- **Setup Phase**: 6 tasks can run in parallel after T001
- **Foundational**: 9 tasks can run in parallel (models + tests)
- **Per User Story**: Average 3-6 parallel tasks (tests + tool implementations)

---

## Validation Checklist

✅ All tasks follow format: `- [ ] [TID] [P?] [Story?] Description with file path`
✅ Each user story has Independent Test Criteria
✅ Tasks organized by user story for independent development
✅ Dependencies clearly documented
✅ TDD approach (tests before implementation) per constitution
✅ File paths specified for all implementation tasks
✅ Parallel execution opportunities identified
✅ MVP scope clearly defined (US1 only)
✅ All 18 MCP tools from contracts/ covered
✅ All entities from data-model.md covered

---

## Next Steps

1. **Start MVP**: Complete Phase 1 → Phase 2 → Phase 3 (US1)
2. **Test MVP**: Verify US1 independent test criteria
3. **Iterate**: Add US2, US4, US5, US6 in priority order
4. **Each Story**: Complete tests → implementation → verify independent test criteria
5. **Final**: Complete Phase 8 (polish) before release

**Ready to implement!** 🚀
