# Contributing to Jira MCP Server

Thank you for your interest in contributing to the Jira MCP Server! This document provides guidelines and instructions for contributing.

## Table of Contents

- [GitHub Issue Requirement](#github-issue-requirement)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Release Process](#release-process)
- [Getting Help](#getting-help)

## GitHub Issue Requirement

**CRITICAL: ALL work MUST be tied to a GitHub issue. No exceptions.**

Before starting ANY work:

1. **Check**: Does a GitHub issue exist for this work?
2. **Create if missing**: Use `gh issue create` to create one with:
   ```bash
   gh issue create \
     --title "Add attachment support" \
     --label "enhancement" \
     --body "Implement attachment upload/download functionality..."
   ```
3. **Reference in ALL commits**: Every commit MUST reference the issue number
   - Format: `type(scope): description (#issue)`
   - Example: `feat(comments): add comment edit functionality (#42)`
4. **Reference in PRs**: Every PR MUST link to issues
   - Use: `Closes #123`, `Fixes #456`, or `Addresses #789`

**Rationale**: Issue tracking provides traceability, enables project planning, facilitates collaboration, and creates searchable history.

## Development Setup

### Prerequisites

- Python 3.10 or higher (for development)
- Git
- A Jira instance for testing (can use a free Atlassian Cloud trial)

### Initial Setup

1. **Fork and clone the repository**:

   ```bash
   git clone https://github.com/YOUR-USERNAME/jira-mcp-server.git
   cd jira-mcp-server
   ```

   Replace `YOUR-USERNAME` with your GitHub username.

2. **Create a virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**:

   ```bash
   pip install -e ".[dev]"
   ```

4. **Configure environment variables** for testing:

   Create a `.env` file (see `.env.example`):

   ```env
   JIRA_MCP_URL=https://your-test-jira.com
   JIRA_MCP_TOKEN=your-test-token
   JIRA_MCP_CACHE_TTL=3600
   JIRA_MCP_TIMEOUT=30
   ```

## Development Workflow

### 1. Create an Issue

Create or identify a GitHub issue before starting work (see [GitHub Issue Requirement](#github-issue-requirement)).

### 2. Create a Branch

Branch names should include the issue number:

```bash
git checkout -b issue-42-add-attachment-support
# or
git checkout -b issue-123-fix-cache-bug
```

### 3. Make Your Changes

Follow the code style and testing guidelines below.

### 4. Run Tests

```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/unit/test_config.py

# Run with verbose output
pytest -v

# Run fast (without coverage)
pytest --no-cov
```

**All tests must pass and coverage must remain at 100%.**

### 5. Code Quality Checks

```bash
# Type checking
mypy src/

# Linting and formatting
ruff check src/ tests/ --fix
ruff format src/ tests/
```

All checks must pass before submitting a PR.

### 6. Commit Your Changes

Use conventional commit messages with issue numbers (required):

```
feat(comments): add support for attachments (#42)
fix(cache): resolve caching issue with custom fields (#123)
docs: update installation instructions (#89)
test(validation): add tests for schema validation (#101)
refactor(client): simplify error handling logic (#67)
```

**Commit format**: `type(scope): description (#issue)`

**Types**: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `perf`
**Scope**: Module name (e.g., `comments`, `search`, `filters`, `workflows`, `client`)

### 7. Push and Create Pull Request

```bash
git push origin your-branch-name
```

Then create a pull request on GitHub.

## Code Style Guidelines

### Python Style

- **Line length**: 120 characters maximum
- **Type hints**: Required for all functions and methods
- **Docstrings**: Required for all public functions, classes, and methods
- **Formatting**: Use ruff for formatting and linting

### Type Hints

All functions must have complete type hints:

```python
def create_issue(
    project: str,
    summary: str,
    issue_type: str = "Task",
) -> Dict[str, Any]:
    """Create a Jira issue.

    Args:
        project: Project key
        summary: Issue summary
        issue_type: Type of issue

    Returns:
        Created issue data
    """
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def validate_field(value: Any, schema: FieldSchema) -> bool:
    """Validate a field value against its schema.

    Args:
        value: The value to validate
        schema: Field schema with type and validation rules

    Returns:
        True if valid, False otherwise

    Raises:
        FieldValidationError: If validation fails with details
    """
    pass
```

## Testing Guidelines

### Test Organization

- `tests/unit/` - Unit tests for individual components
- `tests/integration/` - Integration tests with mocked HTTP calls
- `tests/contract/` - Contract tests for MCP tool interfaces

### Writing Tests

1. **Test-Driven Development (TDD)**: Write tests before implementation
2. **100% Coverage Required**: All code must be covered by tests
3. **Use descriptive test names**:

```python
def test_create_issue_validates_required_fields() -> None:
    """Test that create_issue rejects requests missing required fields."""
    pass
```

4. **Follow the AAA pattern** (Arrange, Act, Assert):

```python
def test_schema_cache_expiration() -> None:
    """Test that cached schemas expire after TTL."""
    # Arrange
    cache = SchemaCache(ttl_seconds=1)
    schema = [FieldSchema(...)]

    # Act
    cache.set("PROJ", "Task", schema)
    time.sleep(2)
    result = cache.get("PROJ", "Task")

    # Assert
    assert result is None
```

### Test Coverage

Use `pragma: no cover` sparingly and only for:
- FastMCP decorator wrappers that can't be tested directly
- Code that explicitly loads from environment (pydantic-settings)

All business logic must be testable and tested.

## Architecture Guidelines

### Project Structure

```
src/jira_mcp_server/
├── __init__.py          # Package initialization
├── config.py            # Configuration (pydantic-settings)
├── models.py            # Pydantic models
├── jira_client.py       # HTTP client for Jira API
├── schema_cache.py      # TTL-based caching
├── validators.py        # Field validation logic
├── server.py            # FastMCP server and tool registration
└── tools/
    ├── __init__.py
    └── issue_tools.py   # MCP tool implementations
```

### Design Principles

1. **Separation of Concerns**:
   - `jira_client.py` - HTTP communication only
   - `validators.py` - Validation logic only
   - `tools/` - MCP tool interfaces only

2. **Error Handling**:
   - Use descriptive error messages
   - Include actionable guidance in errors
   - Map HTTP errors to user-friendly messages

3. **Caching**:
   - Cache expensive operations (schema fetching)
   - Use TTL to prevent stale data
   - Make caching transparent to users

4. **Testing**:
   - Mock all external dependencies (HTTP calls)
   - Test error paths as thoroughly as success paths
   - Use fixtures for common test data

## Pull Request Guidelines

### Before Submitting

- [ ] All tests pass (`pytest`)
- [ ] 100% code coverage maintained
- [ ] Type checking passes (`mypy src/`)
- [ ] Code is formatted (`ruff format src/ tests/`)
- [ ] Linting passes (`ruff check src/ tests/`)
- [ ] Commit messages follow conventional commits
- [ ] Documentation updated if needed

### PR Description

Include:
1. **What** changed
2. **Why** the change was needed
3. **How** it was implemented
4. **Testing** performed

Example:
```markdown
## Description
Adds support for updating issue attachments.

## Motivation
Users need to attach files to issues programmatically.

## Implementation
- Added `add_attachment` method to JiraClient
- Added `jira_issue_add_attachment` MCP tool
- Implemented multipart form data handling

## Testing
- Added 5 unit tests for attachment validation
- Added 3 integration tests with mocked HTTP
- Manual testing with real Jira instance
```

## Feature Development Workflow

### Adding a New MCP Tool

1. **Define the contract** (in comments or separate spec):
   ```python
   # Tool: jira_issue_add_attachment
   # Parameters: issue_key (required), file_path (required), comment (optional)
   # Returns: attachment metadata
   ```

2. **Write contract tests** (`tests/contract/`):
   ```python
   def test_tool_has_required_parameters() -> None:
       """Verify tool signature matches contract."""
       pass
   ```

3. **Write unit tests** (`tests/unit/`):
   ```python
   def test_add_attachment_validates_file_exists() -> None:
       """Test that invalid file paths are rejected."""
       pass
   ```

4. **Implement the tool**:
   ```python
   def jira_issue_add_attachment(
       issue_key: str,
       file_path: str,
       comment: str = ""
   ) -> Dict[str, Any]:
       """Add an attachment to an issue."""
       pass
   ```

5. **Register with FastMCP** (`server.py`):
   ```python
   @mcp.tool()
   def jira_issue_add_attachment_tool(...) -> Dict[str, Any]:
       return jira_issue_add_attachment(...)
   ```

6. **Update documentation** (`README.md`).

## Versioning

We use Semantic Versioning (SemVer):

- **MAJOR**: Breaking API changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)

## Release Process

Releases are managed by project maintainers:

1. **Update Version**: Update `version` in `pyproject.toml`
2. **Update Changelog**: Add release notes to `CHANGELOG.md`
3. **Commit Changes**: `git commit -m "chore: release v0.6.0 (#N)"`
4. **Create Release**: Create GitHub release with tag (e.g., `v0.6.0`)
5. **Automated Publishing**: GitHub Actions automatically publishes to PyPI using trusted publishing
6. **Verify**: Check [PyPI package](https://pypi.org/project/jira-mcp-server/) and test installation

## Getting Help

- **Questions**: Open a [GitHub Discussion](https://github.com/troylar/jira-mcp-server/discussions)
- **Bugs**: Open a [GitHub Issue](https://github.com/troylar/jira-mcp-server/issues)
- **Documentation**: See [README.md](README.md) and [CHANGELOG.md](CHANGELOG.md)

## Code of Conduct

Be respectful, inclusive, and constructive. We're all here to make this project better.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🎉
