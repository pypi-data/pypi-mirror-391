"""Schema caching with TTL logic (T017)"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from jira_mcp_server.models import CachedSchema, FieldSchema


class SchemaCache:
    """In-memory cache for Jira project schemas with TTL expiration.

    Caches field schemas by project key and issue type combination.
    Automatically expires entries after TTL to ensure freshness.
    """

    def __init__(self, ttl_seconds: int = 3600):
        """Initialize schema cache.

        Args:
            ttl_seconds: Time-to-live for cached schemas in seconds (default: 1 hour)
        """
        self._cache: Dict[str, CachedSchema] = {}
        self._ttl = timedelta(seconds=ttl_seconds)
        self._hits = 0
        self._misses = 0

    def _make_key(self, project_key: str, issue_type: str) -> str:
        """Generate cache key from project and issue type.

        Args:
            project_key: Jira project key
            issue_type: Issue type name

        Returns:
            Cache key string
        """
        return f"{project_key}:{issue_type}"

    def get(self, project_key: str, issue_type: str) -> Optional[List[FieldSchema]]:
        """Retrieve schema from cache if not expired.

        Args:
            project_key: Jira project key
            issue_type: Issue type name

        Returns:
            List of FieldSchema if cached and not expired, None otherwise
        """
        key = self._make_key(project_key, issue_type)
        entry = self._cache.get(key)

        if entry is None:
            self._misses += 1
            return None

        # Check if expired
        if datetime.now() >= entry.expires_at:
            # Remove expired entry
            del self._cache[key]
            self._misses += 1
            return None

        self._hits += 1
        return entry.fields

    def set(self, project_key: str, issue_type: str, fields: List[FieldSchema]) -> None:
        """Store schema in cache with TTL.

        Args:
            project_key: Jira project key
            issue_type: Issue type name
            fields: List of field schemas to cache
        """
        key = self._make_key(project_key, issue_type)
        now = datetime.now()

        cached_schema = CachedSchema(
            project_key=project_key,
            issue_type=issue_type,
            fields=fields,
            cached_at=now,
            expires_at=now + self._ttl,
        )

        self._cache[key] = cached_schema

    def clear(self, project_key: str, issue_type: str) -> None:
        """Remove a specific cache entry.

        Args:
            project_key: Jira project key
            issue_type: Issue type name
        """
        key = self._make_key(project_key, issue_type)
        self._cache.pop(key, None)

    def clear_all(self) -> None:
        """Remove all cache entries."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics.

        Returns:
            Dictionary with hits, misses, and total_entries
        """
        return {
            "hits": self._hits,
            "misses": self._misses,
            "total_entries": len(self._cache),
        }
