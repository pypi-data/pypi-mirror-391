"""Configuration management for Jira MCP Server (T011)"""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class JiraConfig(BaseSettings):
    """Configuration for Jira MCP Server loaded from environment variables.

    Required environment variables:
    - JIRA_MCP_URL: Jira instance URL
    - JIRA_MCP_TOKEN: API authentication token

    Optional environment variables:
    - JIRA_MCP_CACHE_TTL: Schema cache TTL in seconds (default: 3600)
    - JIRA_MCP_TIMEOUT: HTTP request timeout in seconds (default: 30)
    """

    url: str = Field(..., description="Jira instance URL")
    token: str = Field(..., description="API authentication token")
    cache_ttl: int = Field(default=3600, description="Schema cache TTL in seconds", gt=0)
    timeout: int = Field(default=30, description="HTTP request timeout in seconds", gt=0)

    model_config = SettingsConfigDict(
        env_prefix="JIRA_MCP_",
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields
    )

    @field_validator("url")
    @classmethod
    def remove_trailing_slash(cls, v: str) -> str:
        """Remove trailing slash from URL for consistency."""
        return v.rstrip("/")

    # Note: cache_ttl and timeout validation handled by gt=0 constraint in Field definitions
