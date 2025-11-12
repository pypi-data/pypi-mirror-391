# Quickstart Guide: Jira MCP Server

**Feature**: 001-jira-mcp-server
**Target**: Get from zero to working MCP server in under 30 seconds (SC-001)

---

## Prerequisites

- Python 3.8 or higher
- Self-hosted Jira instance (version 7.0+)
- Jira API token with appropriate permissions

---

## Installation

Install via pip:

```bash
pip install jira-mcp-server
```

---

## Configuration

### Step 1: Get Your Jira API Token

1. Log into your Jira instance
2. Go to Profile → Personal Access Tokens (or Account Settings → Security → API Tokens)
3. Create a new token
4. Copy the token value (you won't be able to see it again)

### Step 2: Set Environment Variables

Create a `.env` file or set environment variables:

```bash
# Required
export JIRA_MCP_URL="https://jira.yourcompany.com"
export JIRA_MCP_TOKEN="your-api-token-here"

# Optional (with defaults)
export JIRA_MCP_CACHE_TTL=3600    # Schema cache TTL in seconds
export JIRA_MCP_TIMEOUT=30         # HTTP request timeout in seconds
```

**Example `.env` file**:
```env
JIRA_MCP_URL=https://jira.yourcompany.com
JIRA_MCP_TOKEN=ATBBx...your-token-here...xyz
JIRA_MCP_CACHE_TTL=3600
JIRA_MCP_TIMEOUT=30
```

---

## Running the Server

### Option 1: Command Line

```bash
jira-mcp-server
```

The server will start and listen for MCP connections.

### Option 2: As a Module

```bash
python -m jira_mcp_server
```

### Option 3: With Custom Configuration

```bash
JIRA_MCP_URL=https://jira.example.com \
JIRA_MCP_TOKEN=your-token \
jira-mcp-server
```

---

## Verifying Connection

### Test Authentication

Once the server is running, you can verify the connection using the MCP client (e.g., Claude Desktop).

**Example verification with Claude**:
```
Use the jira_health_check tool to verify the connection to Jira.
```

Expected response:
```json
{
  "connected": true,
  "server_version": "8.20.0",
  "base_url": "https://jira.yourcompany.com"
}
```

---

## First Steps

### 1. Get Issues from a Project

```
Show me all open issues in project PROJ
```

This uses `jira_search_issues` with project="PROJ" and status="Open".

### 2. Create an Issue

```
Create a new task in project PROJ with summary "Test issue from MCP"
```

This uses `jira_issue_create` with automatic custom field handling.

### 3. Search with Multiple Criteria

```
Find all high priority bugs assigned to john.doe in project PROJ
```

This uses `jira_search_issues` with multiple parameters combined.

### 4. Create and Use a Filter

```
Create a filter named "My Open Tasks" that shows all tasks assigned to me that are open
```

Then execute it:
```
Run the "My Open Tasks" filter
```

---

## Common Use Cases

### Issue Management

**Create an issue**:
```
Create a bug in PROJ: "Login page shows 404 error", assign to alice
```

**Update an issue**:
```
Update PROJ-123: set priority to High and add label "urgent"
```

**Get issue details**:
```
Show me all details of PROJ-123
```

### Search & Discovery

**By project and status**:
```
Show me all in-progress issues in DEV project
```

**By assignee**:
```
What issues are assigned to bob.smith?
```

**By date range**:
```
Show issues created this week in PROJ
```

**By custom fields** (if your project has custom fields):
```
Find all issues in PROJ where Sprint = "Sprint 23"
```

### Filter Management

**Create filter**:
```
Create a filter "Urgent Bugs" for: priority = High AND type = Bug AND status != Done
```

**List filters**:
```
Show me all my saved filters
```

**Execute filter**:
```
Run the "Urgent Bugs" filter
```

**Update filter**:
```
Update "Urgent Bugs" filter to also include Critical priority
```

### Workflow Transitions

**Get available transitions**:
```
What can I do with issue PROJ-456?
```

**Transition an issue**:
```
Move PROJ-456 to "In Progress"
```

**Transition with comment**:
```
Move PROJ-456 to "Done" and add comment "Fixed in version 2.3"
```

### Comments

**Add comment**:
```
Add comment to PROJ-789: "This is related to the database migration issue"
```

**Read comments**:
```
Show me all comments on PROJ-789
```

---

## Troubleshooting

### "Authentication failed" Error

**Problem**: Server returns 401 Unauthorized

**Solutions**:
1. Verify `JIRA_MCP_TOKEN` is correct
2. Check token hasn't expired
3. Ensure token has necessary permissions
4. For Jira Data Center, verify bearer token authentication is enabled

### "Connection timeout" Error

**Problem**: Server can't reach Jira instance

**Solutions**:
1. Verify `JIRA_MCP_URL` is correct and accessible
2. Check network connectivity to Jira
3. Increase `JIRA_MCP_TIMEOUT` if Jira is slow
4. Verify VPN connection if required

### "Missing required field" Error

**Problem**: Creating/updating issue fails with validation error

**Solutions**:
1. The error message tells you which field is missing
2. Use `jira_project_get_schema` to see all required fields for your project
3. Each project may have different custom field requirements
4. Example: "Missing required fields: Story Points" means you need to provide `custom_fields={"story_points": 5}`

### "Invalid transition" Error

**Problem**: Can't move issue to desired status

**Solutions**:
1. Use `jira_workflow_get_transitions` to see valid transitions from current status
2. Workflow transitions are restricted by Jira configuration
3. You may need to transition through intermediate states
4. Example: Can't go from "To Do" to "Done" directly; must go through "In Progress"

### Schema Cache Issues

**Problem**: Custom fields not being recognized after project changes

**Solutions**:
1. Wait 1 hour for automatic cache refresh
2. Or restart the MCP server to clear cache immediately
3. Cache TTL is controlled by `JIRA_MCP_CACHE_TTL` environment variable

---

## Performance Tips

### Use Filters for Repeated Queries

Instead of running the same search multiple times:
```
# Less efficient:
Show me my open tasks
(later) Show me my open tasks again
(later) Show me my open tasks again

# More efficient:
Create a filter "My Open Tasks" for: assignee = currentUser() AND status != Done
Run filter "My Open Tasks"
(later) Run filter "My Open Tasks"
```

Filters are faster because Jira optimizes them.

### Limit Result Sets

Always specify appropriate `max_results` for large queries:
```
Show me first 50 issues in PROJ  # Better
Show me all issues in PROJ         # Could be thousands
```

### Use Specific Searches

More specific searches are faster:
```
# Faster:
Find bugs in PROJ assigned to alice created this week

# Slower:
Find all issues in PROJ
```

---

## Next Steps

1. **Explore Your Projects**: Use `jira_search_issues` to discover your projects
2. **Create Filters**: Save common searches as filters for quick access
3. **Automate Workflows**: Use the MCP tools to automate repetitive Jira tasks
4. **Custom Fields**: Use `jira_project_get_schema` to discover your project's custom fields

---

## Advanced Configuration

### Custom Cache TTL

For projects with frequently changing schemas:
```bash
export JIRA_MCP_CACHE_TTL=1800  # 30 minutes instead of 1 hour
```

For stable schemas:
```bash
export JIRA_MCP_CACHE_TTL=7200  # 2 hours
```

### Custom Timeout

For slow Jira instances:
```bash
export JIRA_MCP_TIMEOUT=60  # 60 seconds instead of default 30
```

---

## Support

- **Documentation**: See `README.md` for full documentation
- **Issues**: Report bugs at [GitHub repository]
- **MCP Tools Reference**: See `contracts/mcp-tools.yaml` for complete tool definitions

---

## Summary

You now have:
✅ Installed jira-mcp-server via pip
✅ Configured authentication with your Jira instance
✅ Verified connection
✅ Created your first issue
✅ Searched for issues
✅ Created and executed a filter

**Total time**: < 5 minutes (well under the 30-second goal for experienced users)

The server automatically handles:
- Custom field discovery and validation
- Schema caching for performance
- Clear error messages
- Type safety and validation

Start using natural language to manage your Jira issues!
