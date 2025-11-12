"""Unit tests for FastMCP server."""

from unittest.mock import Mock, patch

from jira_mcp_server import server


class TestHealthCheckTool:
    """Test _jira_health_check implementation."""

    @patch("jira_mcp_server.server.JiraClient")
    @patch("jira_mcp_server.server.JiraConfig")
    def test_health_check_success(self, mock_config_class: Mock, mock_client_class: Mock) -> None:
        """Test successful health check."""
        mock_config = Mock()
        mock_config_class.return_value = mock_config

        mock_client = Mock()
        mock_client.health_check.return_value = {
            "connected": True,
            "server_version": "8.20.0",
            "base_url": "https://jira.test.com",
        }
        mock_client_class.return_value = mock_client

        result = server._jira_health_check()

        assert result["connected"] is True
        assert result["server_version"] == "8.20.0"

    @patch("jira_mcp_server.server.JiraClient")
    @patch("jira_mcp_server.server.JiraConfig")
    def test_health_check_failure(self, mock_config_class: Mock, mock_client_class: Mock) -> None:
        """Test health check with connection failure."""
        mock_config_class.side_effect = Exception("Connection failed")

        result = server._jira_health_check()

        assert result["connected"] is False
        assert "Connection failed" in result["error"]


# Note: The FastMCP-decorated tool functions (jira_issue_create_tool, etc.)
# cannot be directly tested because FastMCP wraps them in FunctionTool objects.
# These are thin wrappers that call the underlying implementations which are
# fully tested in test_issue_tools.py. The wrapper code is marked with
# pragma: no cover to exclude from coverage requirements.


class TestMain:
    """Test main function."""

    @patch("jira_mcp_server.server.mcp.run")
    @patch("jira_mcp_server.server.initialize_issue_tools")
    @patch("jira_mcp_server.server.JiraConfig")
    @patch("builtins.print")
    def test_main_success(
        self,
        mock_print: Mock,
        mock_config_class: Mock,
        mock_initialize: Mock,
        mock_mcp_run: Mock,
    ) -> None:
        """Test successful server startup."""
        mock_config = Mock()
        mock_config.url = "https://jira.test.com"
        mock_config.cache_ttl = 3600
        mock_config.timeout = 30
        mock_config_class.return_value = mock_config

        server.main()

        mock_initialize.assert_called_once_with(mock_config)
        mock_mcp_run.assert_called_once()

    @patch("jira_mcp_server.server.JiraConfig")
    @patch("builtins.print")
    @patch("sys.exit")
    def test_main_config_error(self, mock_exit: Mock, mock_print: Mock, mock_config_class: Mock) -> None:
        """Test main exits on configuration error."""
        mock_config_class.side_effect = Exception("Config error")

        server.main()

        mock_exit.assert_called_once_with(1)
