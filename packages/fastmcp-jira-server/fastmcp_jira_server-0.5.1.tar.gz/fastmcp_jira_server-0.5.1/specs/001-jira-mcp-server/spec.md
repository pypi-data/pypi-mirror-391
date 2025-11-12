# Feature Specification: Jira MCP Server with Token Authentication

**Feature Branch**: `001-jira-mcp-server`
**Created**: 2025-11-09
**Status**: Draft
**Input**: User description: "I want to create a jira MCP server that supports token authentication. We use this for our locally installed Jira (non-cloud). I want pip-installable fastmcp server that lets us manage issues. We have a ton of different projects with different custom fields and custom field requirements, so it needs to intelligently handle making sure that the right fields are always updated."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create and Update Issues (Priority: P1)

As a developer using an AI assistant, I want to create and update Jira issues through natural language commands so that I can track work without leaving my development environment.

**Why this priority**: This is the core value proposition of the MCP server - enabling AI assistants to interact with Jira on behalf of users. Without this, the server provides no meaningful functionality.

**Independent Test**: Can be fully tested by authenticating to a Jira instance and creating/updating a single issue with required fields, then verifying the issue appears correctly in Jira.

**Acceptance Scenarios**:

1. **Given** a valid token and Jira instance URL, **When** user requests to create an issue in a specific project, **Then** the system creates the issue with all required fields populated
2. **Given** an existing issue ID, **When** user requests to update specific fields, **Then** the system updates only those fields without affecting other data
3. **Given** a project with custom required fields, **When** user attempts to create an issue, **Then** the system identifies missing required fields and prompts for them
4. **Given** a project with custom field schemas, **When** user provides field values, **Then** the system validates values against field types and constraints before submission

---

### User Story 2 - Robust Issue Search and Query (Priority: P1)

As a user, I want to search and retrieve Jira issues using a variety of parameters and criteria so that I can quickly find relevant work items by project, assignee, status, labels, dates, and custom fields.

**Why this priority**: Users frequently need to get current issues based on various parameters - this is a core workflow that's essential for the MCP server to be useful. Without robust search, users cannot effectively work with their issues.

**Independent Test**: Can be tested by performing searches with different parameter combinations (single and multiple criteria) and verifying results match Jira's web interface and are returned in a usable format.

**Acceptance Scenarios**:

1. **Given** a project key, **When** user requests all issues in that project, **Then** the system returns a complete list of issues with their key details
2. **Given** search criteria combining multiple parameters (status, assignee, priority, labels), **When** user performs a search, **Then** the system returns only issues matching all criteria
3. **Given** an issue key, **When** user requests full issue details, **Then** the system returns all standard and custom fields for that issue
4. **Given** multiple projects with different schemas, **When** user searches across projects, **Then** the system returns results with appropriate fields for each project
5. **Given** date-based criteria (created date, updated date, due date), **When** user searches for issues, **Then** the system returns issues within the specified date ranges
6. **Given** custom field values as search criteria, **When** user searches by custom field, **Then** the system returns issues matching those custom field values
7. **Given** a user's name or ID, **When** user requests issues assigned to that user, **Then** the system returns all issues for that assignee
8. **Given** JQL (Jira Query Language) as input, **When** user executes the query, **Then** the system returns results matching the JQL query
9. **Given** search parameters, **When** user wants to limit results, **Then** the system supports pagination and result limiting

---

### User Story 3 - Smart Custom Field Handling (Priority: P1)

As a user working with multiple Jira projects, I want the system to automatically discover and validate custom field requirements so that I don't need to manually specify schemas for each project.

**Why this priority**: This addresses the user's specific pain point about "tons of different projects with different custom fields" and is critical for usability.

**Independent Test**: Can be tested by creating issues in two different projects with different custom field requirements and verifying the system prompts for the correct fields in each case.

**Acceptance Scenarios**:

1. **Given** a project key, **When** the system needs to create an issue, **Then** it automatically retrieves the project's field schema including custom fields
2. **Given** field schema for a project, **When** user provides field values, **Then** the system validates data types, required fields, and allowed values
3. **Given** a project with select-list custom fields, **When** user provides a value, **Then** the system verifies the value exists in the allowed options
4. **Given** cached field schemas, **When** schemas are older than one hour, **Then** the system automatically refreshes the schema from Jira

---

### User Story 4 - Custom Filter Management (Priority: P2)

As a user, I want to create, save, and use custom filters so that I can quickly access frequently-needed issue sets without reconstructing complex search queries each time.

**Why this priority**: Users often need to repeatedly access the same sets of issues (e.g., "my team's current sprint", "high priority bugs", "unassigned issues"). Custom filters dramatically improve efficiency for these common workflows.

**Independent Test**: Can be tested by creating a custom filter with specific criteria, saving it with a name, retrieving the filter by name, and executing it to verify it returns the expected results.

**Acceptance Scenarios**:

1. **Given** search criteria (any combination of parameters), **When** user requests to save it as a custom filter with a name, **Then** the system creates a reusable filter (CREATE)
2. **Given** saved custom filters, **When** user requests a list of available filters, **Then** the system returns all custom filters accessible to the user with their names, IDs, and basic metadata (READ - list)
3. **Given** a filter name or ID, **When** user retrieves the filter, **Then** the system returns the filter's complete details including JQL query, description, and metadata (READ - single)
4. **Given** a filter name or ID, **When** user executes the filter, **Then** the system returns issues matching the filter's criteria (EXECUTE)
5. **Given** an existing filter, **When** user requests to update its criteria or metadata, **Then** the system modifies the filter definition (UPDATE)
6. **Given** an existing filter, **When** user requests to delete it, **Then** the system removes the filter (DELETE)
7. **Given** Jira's built-in filters (favorites, system filters), **When** user requests them, **Then** the system provides access to pre-configured Jira filters

---

### User Story 5 - Transition Issues Through Workflows (Priority: P3)

As a user, I want to move issues through workflow states so that I can update issue status as work progresses.

**Why this priority**: Workflow transitions are important but less critical than basic CRUD operations and field handling.

**Independent Test**: Can be tested by retrieving available transitions for an issue and executing a valid transition.

**Acceptance Scenarios**:

1. **Given** an issue key, **When** user requests available transitions, **Then** the system returns all valid workflow transitions for the current state
2. **Given** a valid transition ID, **When** user requests to transition an issue, **Then** the system executes the transition and updates the issue status
3. **Given** a transition requiring additional fields, **When** user attempts the transition, **Then** the system prompts for required transition fields
4. **Given** an invalid transition for current state, **When** user attempts it, **Then** the system returns a clear error message with available transitions

---

### User Story 6 - Manage Issue Comments (Priority: P3)

As a user, I want to add and retrieve comments on issues so that I can document discussion and decisions.

**Why this priority**: Comments are useful but not essential for the MVP - users can still create and update issues without comment management.

**Independent Test**: Can be tested by adding a comment to an issue and verifying it appears in Jira, and by retrieving comments from an issue with existing comments.

**Acceptance Scenarios**:

1. **Given** an issue key, **When** user adds a comment, **Then** the comment appears in the issue's comment thread
2. **Given** an issue with comments, **When** user requests comments, **Then** the system returns all comments with author and timestamp
3. **Given** a comment, **When** user wants to format text, **Then** the system supports Jira's text formatting syntax

---

### Edge Cases

- What happens when token authentication fails or token expires?
- How does the system handle network connectivity issues to the Jira instance?
- What happens when a required custom field is added to a project after the schema was cached?
- How does the system handle Jira API rate limiting?
- What happens when a field value exceeds maximum length or doesn't match expected format?
- How does the system handle projects with hundreds of custom fields?
- What happens when attempting to update a field the user doesn't have permission to modify?
- How does the system handle concurrent updates to the same issue?
- What happens when the Jira instance version doesn't support certain API features?
- What happens when a search query returns thousands of results?
- How does the system handle searches with no matching results?
- What happens when a user attempts to create a filter with an invalid JQL query?
- How does the system handle attempting to access a filter that doesn't exist or was deleted?
- What happens when a user tries to update or delete a filter they don't own?
- How does the system handle filter name conflicts (duplicate names)?
- What happens when searching by a custom field that doesn't exist in some projects?
- How does the system handle date range searches with invalid date formats?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support token-based authentication for locally installed (self-hosted) Jira instances
- **FR-002**: System MUST be installable via pip package manager
- **FR-003**: System MUST be implemented using the FastMCP framework
- **FR-004**: System MUST support creating new issues in any project the authenticated user has access to
- **FR-005**: System MUST support updating existing issues by issue key or ID
- **FR-006**: System MUST automatically retrieve project metadata including custom field definitions
- **FR-007**: System MUST validate required fields before attempting to create or update issues
- **FR-008**: System MUST validate custom field values against their defined types and constraints
- **FR-009**: System MUST support searching and querying issues using JQL (Jira Query Language)
- **FR-010**: System MUST support searching issues by project key
- **FR-011**: System MUST support searching issues by assignee (user name or ID)
- **FR-012**: System MUST support searching issues by status
- **FR-013**: System MUST support searching issues by priority
- **FR-014**: System MUST support searching issues by labels
- **FR-015**: System MUST support searching issues by date ranges (created, updated, due dates)
- **FR-016**: System MUST support searching issues by custom field values
- **FR-017**: System MUST support combining multiple search criteria in a single query
- **FR-018**: System MUST support pagination and result limiting for search results
- **FR-019**: System MUST support retrieving full issue details including all custom fields
- **FR-020**: System MUST support creating custom filters with user-defined criteria
- **FR-021**: System MUST support saving custom filters with unique names
- **FR-022**: System MUST support retrieving a list of all accessible filters (owned and shared)
- **FR-023**: System MUST support retrieving a single filter's details and metadata by name or ID
- **FR-024**: System MUST support executing saved filters by name or ID to return matching issues
- **FR-025**: System MUST support updating existing custom filters
- **FR-026**: System MUST support deleting custom filters
- **FR-027**: System MUST support accessing Jira's built-in and favorite filters
- **FR-028**: System MUST cache project schemas to minimize API calls
- **FR-029**: System MUST handle authentication errors with clear error messages
- **FR-030**: System MUST handle API errors (network, permission, validation) gracefully
- **FR-031**: System MUST support issue workflow transitions
- **FR-032**: System MUST retrieve available workflow transitions for an issue
- **FR-033**: System MUST support adding comments to issues
- **FR-034**: System MUST support retrieving comments from issues
- **FR-035**: System MUST expose Jira instance URL as a configuration parameter
- **FR-036**: System MUST expose authentication token as a configuration parameter (environment variable or config file)
- **FR-037**: System MUST validate Jira instance connectivity on initialization

### Key Entities

- **Issue**: Represents a Jira work item with standard fields (key, summary, description, status, priority, assignee) and project-specific custom fields
- **Project**: Represents a Jira project with metadata including allowed issue types and field schemas
- **Field Schema**: Defines field metadata including name, type, required status, and allowed values for select-list fields
- **Filter**: Represents a saved search query with criteria, name, and metadata that can be reused to retrieve matching issues
- **Workflow Transition**: Represents a valid state change for an issue with optional required fields
- **Comment**: Represents user commentary on an issue with text content, author, and timestamp
- **Authentication Token**: API token for authenticating requests to the Jira instance

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can successfully authenticate to their self-hosted Jira instance within 30 seconds of installation
- **SC-002**: Users can create an issue in any project with 100% of required fields validated before submission
- **SC-003**: System correctly identifies and validates all custom fields for projects with 50+ custom fields
- **SC-004**: Users can query and retrieve issue data with results returned in under 3 seconds for typical queries (up to 100 results)
- **SC-005**: Users can search issues using multiple combined criteria (project, status, assignee, dates, custom fields) with results returned in under 5 seconds
- **SC-006**: 95% of field validation errors provide actionable error messages indicating which field failed and why
- **SC-007**: System successfully handles projects with different custom field schemas without manual configuration
- **SC-008**: Schema caching reduces API calls to Jira by at least 80% compared to fetching metadata on every operation
- **SC-009**: Users can create and execute a custom filter in under 60 seconds
- **SC-010**: Users can retrieve and execute saved filters with results returned in under 3 seconds
- **SC-011**: System supports searching across all standard issue parameters (project, assignee, status, priority, labels, dates) with 100% parameter coverage
- **SC-012**: Package installs successfully via pip on Python 3.8+ environments
- **SC-013**: All core operations (create, update, query, search, filter, transition) work reliably with 99% success rate when valid data provided

## Assumptions

- Jira instances are running version 7.0 or later with REST API v2 support
- Users have valid API tokens with appropriate permissions to create and update issues
- Network connectivity to Jira instance is reliable (standard HTTP timeout handling is sufficient)
- Users are familiar with basic Jira concepts (projects, issue types, issue keys)
- Python 3.8+ is available in the target environment
- MCP clients (Claude Desktop, etc.) are properly configured to use MCP servers
- Schema refresh frequency is set to hourly (cached schemas older than one hour are automatically refreshed)
- Standard Jira API rate limits are acceptable (no special high-volume requirements)
- Authentication tokens are stored securely by the user (not managed by this server)
- Field validation matches Jira's server-side validation rules

## Dependencies

- FastMCP framework for MCP server implementation
- Jira REST API v2 availability on target instances
- Python package manager (pip) in user's environment
- HTTP client library for API communication
- MCP client application (e.g., Claude Desktop) to consume the server

## Out of Scope

- OAuth authentication (token-based only)
- Jira Cloud instances (self-hosted only)
- Issue bulk operations (bulk create, bulk update)
- Attachment management (uploading, downloading files)
- Issue linking or relationship management
- Sprint and agile board management
- Time tracking or worklog management
- User and permission management
- Custom field creation or modification
- Webhook or notification handling
- Offline mode or local caching of issue data
- Multi-instance support (one Jira instance per server configuration)
