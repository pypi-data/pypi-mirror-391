"""Integration tests for JiraClient (T010)"""

from unittest.mock import Mock, patch

import httpx
import pytest

from jira_mcp_server.config import JiraConfig
from jira_mcp_server.jira_client import JiraClient


@pytest.fixture
def mock_config() -> JiraConfig:
    """Create a mock JiraConfig for testing."""
    return JiraConfig(url="https://jira.test.com", token="test-token-123")


@pytest.fixture
def mock_httpx_client() -> Mock:
    """Create a mock httpx.Client for testing."""
    return Mock(spec=httpx.Client)


class TestJiraClient:
    """Integration tests for JiraClient with mocked HTTP responses."""

    def test_client_initialization(self, mock_config: JiraConfig) -> None:
        """Test that JiraClient initializes with correct configuration."""
        client = JiraClient(mock_config)

        assert client.base_url == "https://jira.test.com"
        assert client.timeout == 30

    @patch("httpx.Client")
    def test_health_check_success(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test successful health check returns server info."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"version": "8.20.0", "baseUrl": "https://jira.test.com"}

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)
        result = client.health_check()

        assert result["connected"] is True
        assert result["server_version"] == "8.20.0"
        assert result["base_url"] == "https://jira.test.com"

    @patch("httpx.Client")
    def test_health_check_authentication_failure(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test health check handles 401 authentication errors."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "401 Unauthorized", request=Mock(), response=mock_response
        )

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="Authentication failed"):
            client.health_check()

    @patch("httpx.Client")
    def test_get_issue_success(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test getting an issue returns correct data."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "key": "PROJ-123",
            "id": "10001",
            "fields": {"summary": "Test issue", "status": {"name": "Open"}},
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)
        issue = client.get_issue("PROJ-123")

        assert issue["key"] == "PROJ-123"
        assert issue["fields"]["summary"] == "Test issue"

    @patch("httpx.Client")
    def test_get_issue_not_found(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test getting non-existent issue returns proper error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404 Not Found", request=Mock(), response=mock_response
        )
        mock_response.json.return_value = {"errorMessages": ["Issue does not exist"]}

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="Issue.*not found"):
            client.get_issue("NONEXISTENT-999")

    @patch("httpx.Client")
    def test_create_issue_success(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test creating an issue returns the created issue data."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "key": "PROJ-124",
            "id": "10002",
            "self": "https://jira.test.com/rest/api/2/issue/10002",
        }

        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)
        issue_data = {"fields": {"project": {"key": "PROJ"}, "summary": "New issue", "issuetype": {"name": "Bug"}}}
        result = client.create_issue(issue_data)

        assert result["key"] == "PROJ-124"
        assert result["id"] == "10002"

    @patch("httpx.Client")
    def test_create_issue_validation_error(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test creating issue with validation errors returns proper error."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad request error"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "400 Bad Request", request=Mock(), response=mock_response
        )
        mock_response.json.return_value = {"errorMessages": [], "errors": {"summary": "Summary is required"}}

        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="Validation error.*summary.*Summary is required"):
            client.create_issue({"fields": {}})

    @patch("httpx.Client")
    def test_get_project_schema_success(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test getting project schema returns field definitions."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "projects": [
                {
                    "issuetypes": [
                        {
                            "fields": {
                                "summary": {"name": "Summary", "required": True, "schema": {"type": "string"}},
                                "customfield_10001": {
                                    "name": "Story Points",
                                    "required": False,
                                    "schema": {
                                        "type": "number",
                                        "custom": "com.atlassian.jira.plugin.system.customfieldtypes:float",
                                    },
                                },
                            }
                        }
                    ]
                }
            ]
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)
        schema = client.get_project_schema("PROJ", "Bug")

        assert len(schema) == 2
        assert schema[0]["key"] == "summary"
        assert schema[1]["key"] == "customfield_10001"

    @patch("httpx.Client")
    def test_get_project_schema_project_not_found(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test getting schema when project not found."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"projects": []}

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="Project.*not found"):
            client.get_project_schema("INVALID", "Bug")

    @patch("httpx.Client")
    def test_get_project_schema_issue_type_not_found(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test getting schema when issue type not found."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"projects": [{"issuetypes": []}]}

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="Issue type.*not found"):
            client.get_project_schema("PROJ", "InvalidType")

    @patch("httpx.Client")
    def test_get_project_schema_timeout(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test getting schema handles timeout."""
        mock_client_instance = Mock()
        mock_client_instance.get.side_effect = httpx.TimeoutException("Timed out")
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="Timeout getting schema"):
            client.get_project_schema("PROJ", "Bug")

    @patch("httpx.Client")
    def test_get_project_schema_error_response(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test getting schema handles error response."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Server error"

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError):
            client.get_project_schema("PROJ", "Bug")

    @patch("httpx.Client")
    def test_client_handles_network_timeout(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test client handles network timeouts gracefully."""
        mock_client_instance = Mock()
        mock_client_instance.get.side_effect = httpx.TimeoutException("Request timed out")
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="timeout|timed out"):
            client.health_check()

    @patch("httpx.Client")
    def test_client_handles_network_error(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test client handles network errors."""
        mock_client_instance = Mock()
        mock_client_instance.get.side_effect = httpx.NetworkError("Connection refused")
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="Network error"):
            client.health_check()

    @patch("httpx.Client")
    def test_get_issue_timeout(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test get_issue handles timeout."""
        mock_client_instance = Mock()
        mock_client_instance.get.side_effect = httpx.TimeoutException("Timed out")
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="Timeout getting issue"):
            client.get_issue("PROJ-123")

    @patch("httpx.Client")
    def test_create_issue_timeout(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test create_issue handles timeout."""
        mock_client_instance = Mock()
        mock_client_instance.post.side_effect = httpx.TimeoutException("Timed out")
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="Timeout creating issue"):
            client.create_issue({"fields": {"summary": "Test"}})

    @patch("httpx.Client")
    def test_update_issue_timeout(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test update_issue handles timeout."""
        mock_client_instance = Mock()
        mock_client_instance.put.side_effect = httpx.TimeoutException("Timed out")
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="Timeout updating issue"):
            client.update_issue("PROJ-123", {"fields": {"summary": "Updated"}})

    @patch("httpx.Client")
    def test_update_issue_error(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test update_issue handles API errors."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad request"
        mock_response.json.return_value = {"errorMessages": ["Invalid field value"], "errors": {}}

        mock_client_instance = Mock()
        mock_client_instance.put.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="Validation error.*Invalid field"):
            client.update_issue("PROJ-123", {"fields": {"summary": "Updated"}})

    @patch("httpx.Client")
    def test_client_rate_limiting(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test client handles rate limiting (429) responses."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.text = "Too many requests"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "429 Too Many Requests", request=Mock(), response=mock_response
        )

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="Rate limit"):
            client.get_issue("PROJ-123")

    @patch("httpx.Client")
    def test_client_403_permission_denied(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test client handles 403 permission denied."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="Permission denied"):
            client.get_issue("PROJ-123")

    @patch("httpx.Client")
    def test_client_404_with_resource_type(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test client handles 404 with resource type detection."""
        mock_request = Mock()
        mock_request.url = "https://jira.test.com/rest/api/2/issue/PROJ-123"

        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_response.request = mock_request

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        # get_issue has a special case for 404, so use health_check to test _handle_error
        with pytest.raises(ValueError, match="Issue PROJ-123 not found"):
            client.get_issue("PROJ-123")

    @patch("httpx.Client")
    def test_client_400_with_error_messages(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test client handles 400 with errorMessages array."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad request"
        mock_response.json.return_value = {
            "errorMessages": ["Field 'summary' is required", "Priority must be set"],
            "errors": {},
        }

        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="Validation error.*summary.*Priority"):
            client.create_issue({"fields": {}})

    @patch("httpx.Client")
    def test_client_400_json_parse_failure(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test client handles 400 when JSON parsing fails."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad request - invalid JSON response"
        # Raise KeyError (which is caught) instead of generic Exception
        mock_response.json.side_effect = KeyError("Invalid JSON")

        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="Bad request"):
            client.create_issue({"fields": {}})

    @patch("httpx.Client")
    def test_client_500_server_error(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test client handles 500 server errors."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="Jira API error.*500"):
            client.health_check()

    @patch("httpx.Client")
    def test_get_resource_type_issue(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test _get_resource_type detects issue URLs."""
        mock_request = Mock()
        mock_request.url = "https://jira.test.com/rest/api/2/issue/PROJ-123"

        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_response.request = mock_request

        client = JiraClient(mock_config)

        # Call _handle_error directly to test resource type detection
        with pytest.raises(ValueError, match="issue.*does not exist"):
            client._handle_error(mock_response)

    @patch("httpx.Client")
    def test_get_resource_type_project(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test _get_resource_type detects project URLs."""
        mock_request = Mock()
        mock_request.url = "https://jira.test.com/rest/api/2/project/PROJ"

        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_response.request = mock_request

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        # Trigger via health_check to test the _get_resource_type path
        # We need to use a different method since we don't have a get_project method
        # Instead, let's test via _handle_error directly
        with pytest.raises(ValueError, match="project.*does not exist"):
            client._handle_error(mock_response)

    @patch("httpx.Client")
    def test_get_resource_type_filter(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test _get_resource_type detects filter URLs."""
        mock_request = Mock()
        mock_request.url = "https://jira.test.com/rest/api/2/filter/123"

        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_response.request = mock_request

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="filter.*does not exist"):
            client._handle_error(mock_response)

    @patch("httpx.Client")
    def test_get_resource_type_generic(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test _get_resource_type returns 'resource' for unknown URLs."""
        mock_request = Mock()
        mock_request.url = "https://jira.test.com/rest/api/2/other/path"

        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_response.request = mock_request

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="resource.*does not exist"):
            client._handle_error(mock_response)

    @patch("httpx.Client")
    def test_search_issues_success(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test successful issue search."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "total": 2,
            "maxResults": 100,
            "startAt": 0,
            "issues": [
                {"key": "PROJ-123", "fields": {"summary": "Issue 1"}},
                {"key": "PROJ-124", "fields": {"summary": "Issue 2"}},
            ],
        }

        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)
        result = client.search_issues("project = PROJ")

        assert result["total"] == 2
        assert len(result["issues"]) == 2
        assert result["issues"][0]["key"] == "PROJ-123"

    @patch("httpx.Client")
    def test_search_issues_with_pagination(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test issue search with pagination parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "total": 100,
            "maxResults": 50,
            "startAt": 50,
            "issues": [],
        }

        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)
        result = client.search_issues("project = PROJ", max_results=50, start_at=50)

        assert result["startAt"] == 50
        assert result["maxResults"] == 50

        # Verify the request was made with correct parameters
        call_kwargs = mock_client_instance.post.call_args[1]
        assert call_kwargs["json"]["maxResults"] == 50
        assert call_kwargs["json"]["startAt"] == 50

    @patch("httpx.Client")
    def test_search_issues_error(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test search handles JQL errors."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Invalid JQL"
        mock_response.json.return_value = {
            "errorMessages": ["JQL syntax error"],
            "errors": {},
        }

        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="Validation error.*JQL syntax"):
            client.search_issues("invalid jql query")

    @patch("httpx.Client")
    def test_search_issues_timeout(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test search handles timeout."""
        mock_client_instance = Mock()
        mock_client_instance.post.side_effect = httpx.TimeoutException("Timed out")
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="Timeout executing search query"):
            client.search_issues("project = PROJ")

    @patch("httpx.Client")
    def test_create_filter_success(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test creating a filter."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "10000", "name": "Test Filter", "jql": "project = PROJ"}

        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)
        result = client.create_filter(name="Test Filter", jql="project = PROJ")

        assert result["id"] == "10000"
        assert result["name"] == "Test Filter"

    @patch("httpx.Client")
    def test_list_filters_success(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test listing filters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": "10000", "name": "Filter 1"}]

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)
        result = client.list_filters()

        assert len(result) == 1
        assert result[0]["id"] == "10000"

    @patch("httpx.Client")
    def test_get_filter_success(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test getting a filter."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "10000", "name": "Test Filter", "jql": "project = PROJ"}

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)
        result = client.get_filter(filter_id="10000")

        assert result["id"] == "10000"

    @patch("httpx.Client")
    def test_update_filter_success(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test updating a filter."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "10000", "name": "Updated Filter"}

        mock_client_instance = Mock()
        mock_client_instance.put.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)
        result = client.update_filter(filter_id="10000", name="Updated Filter")

        assert result["name"] == "Updated Filter"

    @patch("httpx.Client")
    def test_delete_filter_success(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test deleting a filter."""
        mock_response = Mock()
        mock_response.status_code = 204

        mock_client_instance = Mock()
        mock_client_instance.delete.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)
        client.delete_filter(filter_id="10000")

        # No exception means success

    @patch("httpx.Client")
    def test_create_filter_timeout(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test create filter handles timeout."""
        mock_client_instance = Mock()
        mock_client_instance.post.side_effect = httpx.TimeoutException("Timed out")
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="Timeout creating filter"):
            client.create_filter(name="Test", jql="project = PROJ")

    @patch("httpx.Client")
    def test_create_filter_with_description(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test creating a filter with description."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "10000"}

        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)
        client.create_filter(name="Test", jql="project = PROJ", description="Test description")

        # Verify description was passed
        call_kwargs = mock_client_instance.post.call_args[1]
        assert call_kwargs["json"]["description"] == "Test description"

    @patch("httpx.Client")
    def test_list_filters_timeout(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test list filters handles timeout."""
        mock_client_instance = Mock()
        mock_client_instance.get.side_effect = httpx.TimeoutException("Timed out")
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="Timeout listing filters"):
            client.list_filters()

    @patch("httpx.Client")
    def test_get_filter_timeout(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test get filter handles timeout."""
        mock_client_instance = Mock()
        mock_client_instance.get.side_effect = httpx.TimeoutException("Timed out")
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="Timeout getting filter 10000"):
            client.get_filter(filter_id="10000")

    @patch("httpx.Client")
    def test_update_filter_no_fields_error(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test update filter requires at least one field."""
        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="At least one field must be provided to update"):
            client.update_filter(filter_id="10000")

    @patch("httpx.Client")
    def test_update_filter_all_fields(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test update filter with all fields."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "10000"}

        mock_client_instance = Mock()
        mock_client_instance.put.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)
        client.update_filter(filter_id="10000", name="New Name", jql="new jql", description="New Desc", favourite=True)

        call_kwargs = mock_client_instance.put.call_args[1]
        assert call_kwargs["json"]["name"] == "New Name"
        assert call_kwargs["json"]["jql"] == "new jql"
        assert call_kwargs["json"]["description"] == "New Desc"
        assert call_kwargs["json"]["favourite"] is True

    @patch("httpx.Client")
    def test_update_filter_timeout(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test update filter handles timeout."""
        mock_client_instance = Mock()
        mock_client_instance.put.side_effect = httpx.TimeoutException("Timed out")
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="Timeout updating filter 10000"):
            client.update_filter(filter_id="10000", name="Updated")

    @patch("httpx.Client")
    def test_delete_filter_timeout(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test delete filter handles timeout."""
        mock_client_instance = Mock()
        mock_client_instance.delete.side_effect = httpx.TimeoutException("Timed out")
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="Timeout deleting filter 10000"):
            client.delete_filter(filter_id="10000")

    @patch("httpx.Client")
    def test_create_filter_error(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test create filter handles API errors."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad request"
        mock_response.json.return_value = {"errorMessages": ["Invalid JQL"], "errors": {}}

        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="Validation error"):
            client.create_filter(name="Test", jql="invalid")

    @patch("httpx.Client")
    def test_list_filters_error(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test list filters handles API errors."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="Permission denied"):
            client.list_filters()

    @patch("httpx.Client")
    def test_get_filter_error(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test get filter handles API errors."""
        mock_request = Mock()
        mock_request.url = "https://jira.test.com/rest/api/2/filter/10000"

        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_response.request = mock_request

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="filter.*does not exist"):
            client.get_filter(filter_id="10000")

    @patch("httpx.Client")
    def test_update_filter_error(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test update filter handles API errors."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"

        mock_client_instance = Mock()
        mock_client_instance.put.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="Permission denied"):
            client.update_filter(filter_id="10000", name="Updated")

    @patch("httpx.Client")
    def test_delete_filter_error(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test delete filter handles API errors."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"

        mock_client_instance = Mock()
        mock_client_instance.delete.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="Permission denied"):
            client.delete_filter(filter_id="10000")

    @patch("httpx.Client")
    def test_get_transitions_success(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test getting available transitions."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "transitions": [
                {"id": "21", "name": "In Progress", "to": {"name": "In Progress"}},
                {"id": "31", "name": "Done", "to": {"name": "Done"}},
            ]
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)
        result = client.get_transitions(issue_key="PROJ-123")

        assert len(result["transitions"]) == 2
        assert result["transitions"][0]["id"] == "21"

    @patch("httpx.Client")
    def test_get_transitions_timeout(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test get transitions handles timeout."""
        mock_client_instance = Mock()
        mock_client_instance.get.side_effect = httpx.TimeoutException("Timed out")
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="Timeout getting transitions for PROJ-123"):
            client.get_transitions(issue_key="PROJ-123")

    @patch("httpx.Client")
    def test_get_transitions_error(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test get transitions handles API errors."""
        mock_request = Mock()
        mock_request.url = "https://jira.test.com/rest/api/2/issue/PROJ-123/transitions"

        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_response.request = mock_request

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="issue.*does not exist"):
            client.get_transitions(issue_key="PROJ-123")

    @patch("httpx.Client")
    def test_transition_issue_success(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test transitioning an issue."""
        mock_response = Mock()
        mock_response.status_code = 204

        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)
        client.transition_issue(issue_key="PROJ-123", transition_id="21")

        # No exception means success

    @patch("httpx.Client")
    def test_transition_issue_with_fields(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test transition with required fields."""
        mock_response = Mock()
        mock_response.status_code = 204

        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)
        fields = {"resolution": {"name": "Done"}}
        client.transition_issue(issue_key="PROJ-123", transition_id="31", fields=fields)

        # Verify fields were passed
        call_kwargs = mock_client_instance.post.call_args[1]
        assert call_kwargs["json"]["fields"] == fields

    @patch("httpx.Client")
    def test_transition_issue_timeout(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test transition handles timeout."""
        mock_client_instance = Mock()
        mock_client_instance.post.side_effect = httpx.TimeoutException("Timed out")
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="Timeout transitioning issue PROJ-123"):
            client.transition_issue(issue_key="PROJ-123", transition_id="21")

    @patch("httpx.Client")
    def test_transition_issue_error(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test transition handles API errors."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad request"
        mock_response.json.return_value = {"errorMessages": ["Invalid transition"], "errors": {}}

        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="Validation error"):
            client.transition_issue(issue_key="PROJ-123", transition_id="99")

    @patch("httpx.Client")
    def test_add_comment_success(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test adding a comment to an issue."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": "10001",
            "body": "Test comment",
            "author": {"displayName": "John Doe"},
            "created": "2025-01-15T10:00:00.000+0000",
        }

        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)
        result = client.add_comment(issue_key="PROJ-123", body="Test comment")

        assert result["id"] == "10001"
        assert result["body"] == "Test comment"

    @patch("httpx.Client")
    def test_add_comment_timeout(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test add comment handles timeout."""
        mock_client_instance = Mock()
        mock_client_instance.post.side_effect = httpx.TimeoutException("Timed out")
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="Timeout adding comment to issue PROJ-123"):
            client.add_comment(issue_key="PROJ-123", body="Test comment")

    @patch("httpx.Client")
    def test_add_comment_error(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test add comment handles API errors."""
        mock_request = Mock()
        mock_request.url = "https://jira.test.com/rest/api/2/issue/PROJ-123/comment"

        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_response.request = mock_request

        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="issue.*does not exist"):
            client.add_comment(issue_key="PROJ-999", body="Test comment")

    @patch("httpx.Client")
    def test_list_comments_success(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test listing all comments on an issue."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "comments": [
                {
                    "id": "10001",
                    "body": "First comment",
                    "author": {"displayName": "John Doe"},
                    "created": "2025-01-15T10:00:00.000+0000",
                },
                {
                    "id": "10002",
                    "body": "Second comment",
                    "author": {"displayName": "Jane Smith"},
                    "created": "2025-01-15T11:00:00.000+0000",
                },
            ],
            "total": 2,
            "maxResults": 50,
            "startAt": 0,
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)
        result = client.list_comments(issue_key="PROJ-123")

        assert result["total"] == 2
        assert len(result["comments"]) == 2

    @patch("httpx.Client")
    def test_list_comments_no_comments(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test listing comments when issue has no comments."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "comments": [],
            "total": 0,
            "maxResults": 50,
            "startAt": 0,
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)
        result = client.list_comments(issue_key="PROJ-123")

        assert result["total"] == 0
        assert len(result["comments"]) == 0

    @patch("httpx.Client")
    def test_list_comments_timeout(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test list comments handles timeout."""
        mock_client_instance = Mock()
        mock_client_instance.get.side_effect = httpx.TimeoutException("Timed out")
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="Timeout listing comments for issue PROJ-123"):
            client.list_comments(issue_key="PROJ-123")

    @patch("httpx.Client")
    def test_list_comments_error(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test list comments handles API errors."""
        mock_request = Mock()
        mock_request.url = "https://jira.test.com/rest/api/2/issue/PROJ-999/comment"

        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_response.request = mock_request

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="issue.*does not exist"):
            client.list_comments(issue_key="PROJ-999")

    @patch("httpx.Client")
    def test_update_comment_success(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test updating a comment."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "10001",
            "body": "Updated comment",
            "author": {"displayName": "John Doe"},
            "updated": "2025-01-15T12:00:00.000+0000",
        }

        mock_client_instance = Mock()
        mock_client_instance.put.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)
        result = client.update_comment(issue_key="PROJ-123", comment_id="10001", body="Updated comment")

        assert result["id"] == "10001"
        assert result["body"] == "Updated comment"

    @patch("httpx.Client")
    def test_update_comment_timeout(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test update comment handles timeout."""
        mock_client_instance = Mock()
        mock_client_instance.put.side_effect = httpx.TimeoutException("Timed out")
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="Timeout updating comment 10001 on issue PROJ-123"):
            client.update_comment(issue_key="PROJ-123", comment_id="10001", body="Updated")

    @patch("httpx.Client")
    def test_update_comment_error(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test update comment handles API errors."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"

        mock_client_instance = Mock()
        mock_client_instance.put.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="Permission denied"):
            client.update_comment(issue_key="PROJ-123", comment_id="10001", body="Updated")

    @patch("httpx.Client")
    def test_delete_comment_success(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test deleting a comment."""
        mock_response = Mock()
        mock_response.status_code = 204

        mock_client_instance = Mock()
        mock_client_instance.delete.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)
        client.delete_comment(issue_key="PROJ-123", comment_id="10001")

        # No exception means success

    @patch("httpx.Client")
    def test_delete_comment_timeout(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test delete comment handles timeout."""
        mock_client_instance = Mock()
        mock_client_instance.delete.side_effect = httpx.TimeoutException("Timed out")
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="Timeout deleting comment 10001 on issue PROJ-123"):
            client.delete_comment(issue_key="PROJ-123", comment_id="10001")

    @patch("httpx.Client")
    def test_delete_comment_error(self, mock_client_class: Mock, mock_config: JiraConfig) -> None:
        """Test delete comment handles API errors."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_request = Mock()
        mock_request.url = "https://jira.test.com/rest/api/2/issue/PROJ-123/comment/10001"
        mock_response.request = mock_request

        mock_client_instance = Mock()
        mock_client_instance.delete.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        client = JiraClient(mock_config)

        with pytest.raises(ValueError, match="does not exist"):
            client.delete_comment(issue_key="PROJ-123", comment_id="10001")
