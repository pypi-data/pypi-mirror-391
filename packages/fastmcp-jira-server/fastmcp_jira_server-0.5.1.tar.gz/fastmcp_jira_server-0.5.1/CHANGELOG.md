# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2025-01-15

### Added
- **Comment Management** - Full CRUD operations for issue comments
  - `jira_comment_add` - Add comments with Jira markup support
  - `jira_comment_list` - List all comments with author and timestamp info
  - `jira_comment_update` - Update existing comments (author/admin only)
  - `jira_comment_delete` - Delete comments (author/admin only)
- Permission controls for comment update/delete operations
- Comprehensive validation for comment operations
- 16 new contract tests for comment update/delete
- 338 total tests with 100% coverage

### Changed
- Updated README with complete comment CRUD examples
- Enhanced MCP tools documentation

## [0.4.0] - 2025-01-14

### Added
- **Workflow Transitions** - Move issues through workflow states
  - `jira_workflow_get_transitions` - Get available transitions for an issue
  - `jira_workflow_transition` - Execute workflow transitions
- Transition discovery with field requirements
- Support for transitions requiring resolution, comments, and other fields
- 32 tests for workflow operations (12 unit + 13 contract + 7 integration)

### Changed
- Updated README with workflow transition examples
- Added transition metadata (has_screen, required fields)

## [0.3.0] - 2025-01-13

### Added
- **Custom Filters** - Save and reuse complex search queries
  - `jira_filter_create` - Create custom filters with name and JQL
  - `jira_filter_list` - List all accessible filters
  - `jira_filter_get` - Get filter details by ID
  - `jira_filter_execute` - Run saved filters with pagination
  - `jira_filter_update` - Update filter criteria (name, JQL, description)
  - `jira_filter_delete` - Delete filters (owner only)
- Full CRUD operations for filter management
- Favorite filter support
- 74 tests for filter operations (30 unit + 26 contract + 18 integration)

### Changed
- Updated README with filter management examples
- Enhanced MCP tools documentation with filter operations

## [0.2.0] - 2025-01-12

### Added
- **Robust Search** - Multi-criteria issue search
  - `jira_search_issues` - Search by project, assignee, status, priority, labels, date ranges
  - `jira_search_jql` - Execute raw JQL queries directly
- Full JQL support with all Jira Query Language features
- Pagination support for search results
- Date range filtering (created_after, created_before, updated_after, updated_before)
- Label-based filtering
- 37 tests for search operations

### Changed
- Enhanced search capabilities with multiple filter criteria
- Updated README with search examples

## [0.1.0] - 2025-01-10

### Added
- **Issue Management** - Core CRUD operations for Jira issues
  - `jira_issue_create` - Create issues with automatic custom field validation
  - `jira_issue_update` - Update existing issues (only provided fields)
  - `jira_issue_get` - Get full issue details including custom fields
- **Smart Custom Field Handling** - Automatic discovery and validation
  - Project-specific custom field detection
  - Field type validation (string, number, option, array, etc.)
  - Allowed values validation for select fields
- **Schema Caching** - Intelligent caching reduces API calls by 80%+
  - In-memory TTL-based caching (1-hour default)
  - Configurable cache TTL via `JIRA_MCP_CACHE_TTL`
- **Health Check** - Verify connectivity and authentication
  - `jira_health_check` - Connection status and server info
- **Schema Introspection** - Debug tool for field exploration
  - `jira_project_get_schema` - Get all available fields for a project/issue type
- FastMCP server framework integration
- Support for self-hosted Jira instances (v7.0+)
- Token-based authentication
- Comprehensive error handling with actionable messages
- 100% test coverage requirement

### Configuration
- `JIRA_MCP_URL` - Your Jira instance URL (required)
- `JIRA_MCP_TOKEN` - API authentication token (required)
- `JIRA_MCP_CACHE_TTL` - Schema cache TTL in seconds (optional, default: 3600)
- `JIRA_MCP_TIMEOUT` - HTTP request timeout in seconds (optional, default: 30)

## [Unreleased]

### Planned
- Attachment management (upload, download, delete)
- Advanced JQL query builder
- Bulk operations support
- Webhook integration
- Custom field templates

---

## Version History

- **v0.5.0** - Comment Management (Full CRUD)
- **v0.4.0** - Workflow Transitions
- **v0.3.0** - Custom Filters
- **v0.2.0** - Search & JQL
- **v0.1.0** - Initial Release (MVP)

## Links

- [GitHub Repository](https://github.com/troylar/jira-mcp-server)
- [PyPI Package](https://pypi.org/project/fastmcp-jira-server/)
- [Documentation](https://github.com/troylar/jira-mcp-server#readme)
- [Issues](https://github.com/troylar/jira-mcp-server/issues)
