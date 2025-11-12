"""Test for tools/__init__.py"""


def test_tools_module_imports() -> None:
    """Test that tools module can be imported."""
    from jira_mcp_server.tools import issue_tools

    assert issue_tools is not None
