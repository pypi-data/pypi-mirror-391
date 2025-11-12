"""Unit tests for SchemaCache (T009)"""

import time
from datetime import datetime, timedelta
from typing import List

import pytest

from jira_mcp_server.models import FieldSchema, FieldType
from jira_mcp_server.schema_cache import SchemaCache


class TestSchemaCache:
    """Test suite for SchemaCache with TTL logic."""

    @pytest.fixture
    def cache(self) -> SchemaCache:
        """Create a SchemaCache instance with default 1-hour TTL."""
        return SchemaCache(ttl_seconds=3600)

    @pytest.fixture
    def short_ttl_cache(self) -> SchemaCache:
        """Create a SchemaCache instance with 1-second TTL for testing expiration."""
        return SchemaCache(ttl_seconds=1)

    @pytest.fixture
    def sample_schema(self) -> List[FieldSchema]:
        """Create a sample field schema for testing."""
        return [
            FieldSchema(
                key="summary",
                name="Summary",
                type=FieldType.STRING,
                required=True,
                custom=False,
            ),
            FieldSchema(
                key="customfield_10001",
                name="Story Points",
                type=FieldType.NUMBER,
                required=False,
                custom=True,
            ),
        ]

    def test_cache_stores_and_retrieves_schema(self, cache: SchemaCache, sample_schema: List[FieldSchema]) -> None:
        """Test that cache can store and retrieve schema."""
        cache.set("PROJ", "Bug", sample_schema)

        retrieved = cache.get("PROJ", "Bug")

        assert retrieved is not None
        assert len(retrieved) == 2
        assert retrieved[0].key == "summary"
        assert retrieved[1].key == "customfield_10001"

    def test_cache_returns_none_for_missing_key(self, cache: SchemaCache) -> None:
        """Test that cache returns None for non-existent keys."""
        result = cache.get("NONEXISTENT", "Bug")

        assert result is None

    def test_cache_expires_after_ttl(self, short_ttl_cache: SchemaCache, sample_schema: List[FieldSchema]) -> None:
        """Test that cached schemas expire after TTL."""
        short_ttl_cache.set("PROJ", "Bug", sample_schema)

        # Should be available immediately
        assert short_ttl_cache.get("PROJ", "Bug") is not None

        # Wait for expiration
        time.sleep(1.5)

        # Should be expired
        assert short_ttl_cache.get("PROJ", "Bug") is None

    def test_cache_different_projects_separate(self, cache: SchemaCache, sample_schema: List[FieldSchema]) -> None:
        """Test that different projects have separate cache entries."""
        cache.set("PROJ1", "Bug", sample_schema)
        cache.set("PROJ2", "Task", sample_schema)

        proj1_schema = cache.get("PROJ1", "Bug")
        proj2_schema = cache.get("PROJ2", "Task")

        assert proj1_schema is not None
        assert proj2_schema is not None
        assert cache.get("PROJ1", "Task") is None  # Different issue type
        assert cache.get("PROJ2", "Bug") is None  # Different issue type

    def test_cache_different_issue_types_separate(self, cache: SchemaCache, sample_schema: List[FieldSchema]) -> None:
        """Test that different issue types in same project have separate entries."""
        cache.set("PROJ", "Bug", sample_schema)
        cache.set("PROJ", "Task", sample_schema)

        bug_schema = cache.get("PROJ", "Bug")
        task_schema = cache.get("PROJ", "Task")

        assert bug_schema is not None
        assert task_schema is not None

    def test_cache_update_replaces_existing(self, cache: SchemaCache, sample_schema: List[FieldSchema]) -> None:
        """Test that updating cache replaces existing entry."""
        cache.set("PROJ", "Bug", sample_schema)

        new_schema = [
            FieldSchema(
                key="description",
                name="Description",
                type=FieldType.STRING,
                required=False,
                custom=False,
            )
        ]
        cache.set("PROJ", "Bug", new_schema)

        retrieved = cache.get("PROJ", "Bug")
        assert retrieved is not None
        assert len(retrieved) == 1
        assert retrieved[0].key == "description"

    def test_cache_clear_removes_entry(self, cache: SchemaCache, sample_schema: List[FieldSchema]) -> None:
        """Test that clear removes a specific cache entry."""
        cache.set("PROJ", "Bug", sample_schema)
        assert cache.get("PROJ", "Bug") is not None

        cache.clear("PROJ", "Bug")

        assert cache.get("PROJ", "Bug") is None

    def test_cache_clear_all_removes_everything(self, cache: SchemaCache, sample_schema: List[FieldSchema]) -> None:
        """Test that clear_all removes all cache entries."""
        cache.set("PROJ1", "Bug", sample_schema)
        cache.set("PROJ2", "Task", sample_schema)

        cache.clear_all()

        assert cache.get("PROJ1", "Bug") is None
        assert cache.get("PROJ2", "Task") is None

    def test_cache_stats_tracking(self, cache: SchemaCache, sample_schema: List[FieldSchema]) -> None:
        """Test that cache tracks hit/miss statistics."""
        cache.set("PROJ", "Bug", sample_schema)

        # Hits
        cache.get("PROJ", "Bug")
        cache.get("PROJ", "Bug")

        # Misses
        cache.get("NONEXISTENT", "Bug")

        stats = cache.get_stats()
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["total_entries"] == 1

    def test_cache_key_generation(self, cache: SchemaCache) -> None:
        """Test that cache generates correct keys for project+issue_type combinations."""
        # This tests the internal _make_key method behavior
        key1 = cache._make_key("PROJ", "Bug")
        key2 = cache._make_key("PROJ", "Task")
        key3 = cache._make_key("OTHER", "Bug")

        assert key1 != key2  # Different issue types
        assert key1 != key3  # Different projects
        assert key2 != key3  # Different both

    def test_cache_ttl_configurable(self, sample_schema: List[FieldSchema]) -> None:
        """Test that TTL is configurable at initialization."""
        custom_cache = SchemaCache(ttl_seconds=7200)
        custom_cache.set("PROJ", "Bug", sample_schema)

        # Verify TTL is set correctly (check internal state)
        entry = custom_cache._cache[custom_cache._make_key("PROJ", "Bug")]
        expected_expiry = datetime.now() + timedelta(seconds=7200)

        # Allow 1 second tolerance for test execution time
        assert abs((entry.expires_at - expected_expiry).total_seconds()) < 1
