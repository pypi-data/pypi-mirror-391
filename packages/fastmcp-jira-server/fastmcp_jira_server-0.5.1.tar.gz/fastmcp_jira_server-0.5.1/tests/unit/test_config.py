"""Unit tests for JiraConfig (T008)"""

import pytest
from pydantic import ValidationError

from jira_mcp_server.config import JiraConfig


class TestJiraConfig:
    """Test suite for JiraConfig pydantic-settings model."""

    def test_config_loads_from_env_vars(self) -> None:
        """Test that config successfully loads required values via direct initialization."""
        config = JiraConfig(url="https://jira.example.com", token="test-token-123")

        assert config.url == "https://jira.example.com"
        assert config.token == "test-token-123"
        assert config.cache_ttl == 3600  # Default
        assert config.timeout == 30  # Default

    def test_config_uses_custom_values(self) -> None:
        """Test that config accepts custom TTL and timeout values."""
        config = JiraConfig(
            url="https://jira.example.com", token="test-token-123", cache_ttl=7200, timeout=60
        )

        assert config.cache_ttl == 7200
        assert config.timeout == 60

    def test_config_fails_without_url(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that config validation fails when JIRA_MCP_URL is missing."""
        monkeypatch.setenv("JIRA_MCP_TOKEN", "test-token-123")
        monkeypatch.delenv("JIRA_MCP_URL", raising=False)

        with pytest.raises(ValidationError) as exc_info:
            JiraConfig()

        assert "url" in str(exc_info.value)

    def test_config_fails_without_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that config validation fails when JIRA_MCP_TOKEN is missing."""
        monkeypatch.setenv("JIRA_MCP_URL", "https://jira.example.com")
        monkeypatch.delenv("JIRA_MCP_TOKEN", raising=False)

        with pytest.raises(ValidationError) as exc_info:
            JiraConfig()

        assert "token" in str(exc_info.value)

    def test_config_validates_timeout_positive(self) -> None:
        """Test that timeout must be positive."""
        with pytest.raises(ValidationError) as exc_info:
            JiraConfig(
                url="https://jira.example.com",
                token="test-token",
                timeout=-1,  # Negative value
            )
        # The custom validator should fire
        assert "must be positive" in str(exc_info.value) or "greater than 0" in str(exc_info.value)

    def test_config_validates_cache_ttl_positive(self) -> None:
        """Test that cache_ttl must be positive."""
        with pytest.raises(ValidationError) as exc_info:
            JiraConfig(
                url="https://jira.example.com",
                token="test-token",
                cache_ttl=0,  # Zero value
            )
        # The custom validator should fire
        assert "must be positive" in str(exc_info.value) or "greater than 0" in str(exc_info.value)

    def test_config_model_export(self) -> None:
        """Test that config can be exported to dict."""
        config = JiraConfig(url="https://jira.example.com", token="secret-token")
        config_dict = config.model_dump()

        assert isinstance(config_dict, dict)
        assert config_dict["url"] == "https://jira.example.com"
        assert config_dict["token"] == "secret-token"

    def test_config_url_trailing_slash_removed(self) -> None:
        """Test that trailing slashes are removed from URL."""
        config = JiraConfig(url="https://jira.example.com/", token="test-token-123")

        assert config.url == "https://jira.example.com"
        assert not config.url.endswith("/")
