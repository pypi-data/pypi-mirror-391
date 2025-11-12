"""Jira REST API client (T018-T019)"""

from typing import Any, Dict, List

import httpx

from jira_mcp_server.config import JiraConfig


class JiraClient:
    """HTTP client for Jira REST API v2.

    Handles authentication, requests, and error handling for all Jira API interactions.
    """

    def __init__(self, config: JiraConfig):
        """Initialize Jira client.

        Args:
            config: JiraConfig with URL and authentication token
        """
        self.base_url = config.url
        self.timeout = config.timeout
        self._token = config.token

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers with authentication.

        Returns:
            Dictionary of HTTP headers
        """
        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _handle_error(self, response: httpx.Response) -> None:
        """Handle HTTP error responses with actionable messages.

        Args:
            response: HTTP response object

        Raises:
            ValueError: With context-specific error message
        """
        status = response.status_code

        if status == 401:
            raise ValueError("Authentication failed. Check your JIRA_MCP_TOKEN is valid and hasn't expired.")
        elif status == 403:
            raise ValueError("Permission denied. Your token doesn't have access to this resource.")
        elif status == 404:
            raise ValueError(f"Resource not found. The requested {self._get_resource_type(response)} does not exist.")
        elif status == 429:
            raise ValueError("Rate limit exceeded. Too many requests to Jira API. Please wait before retrying.")
        elif status == 400:
            # Parse validation errors from response
            try:
                error_data = response.json()
                errors = error_data.get("errors", {})
                messages = error_data.get("errorMessages", [])

                if errors:
                    error_str = ", ".join(f"{field}: {msg}" for field, msg in errors.items())
                    raise ValueError(f"Validation error: {error_str}")
                elif messages:
                    raise ValueError(f"Validation error: {', '.join(messages)}")
            except (ValueError, KeyError) as e:
                # Re-raise ValueError from validation, catch only JSON parsing errors
                if "Validation error" in str(e):
                    raise
                pass

            raise ValueError(f"Bad request: {response.text[:200]}")
        else:
            raise ValueError(f"Jira API error ({status}): {response.text[:200]}")

    def _get_resource_type(self, response: httpx.Response) -> str:
        """Determine resource type from URL for better error messages.

        Args:
            response: HTTP response object

        Returns:
            Resource type string (e.g., "issue", "project")
        """
        url = str(response.request.url)
        if "/issue/" in url:
            return "issue"
        elif "/project/" in url:
            return "project"
        elif "/filter/" in url:
            return "filter"
        else:
            return "resource"

    def health_check(self) -> Dict[str, Any]:
        """Verify connectivity to Jira instance (T019).

        Returns:
            Dictionary with connection status and server info

        Raises:
            ValueError: If connection fails or authentication error
        """
        url = f"{self.base_url}/rest/api/2/serverInfo"

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=self._get_headers())

                if response.status_code != 200:
                    self._handle_error(response)

                server_info = response.json()
                return {
                    "connected": True,
                    "server_version": server_info.get("version", "unknown"),
                    "base_url": server_info.get("baseUrl", self.base_url),
                }

        except httpx.TimeoutException:
            raise ValueError(
                f"Connection timeout. Could not reach Jira at {self.base_url} within {self.timeout} seconds."
            )
        except httpx.NetworkError as e:
            raise ValueError(f"Network error connecting to Jira: {str(e)}")

    def get_issue(self, issue_key: str) -> Dict[str, Any]:
        """Get issue details by key.

        Args:
            issue_key: Issue key (e.g., "PROJ-123")

        Returns:
            Issue data dictionary

        Raises:
            ValueError: If issue not found or API error
        """
        url = f"{self.base_url}/rest/api/2/issue/{issue_key}"

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=self._get_headers())

                if response.status_code != 200:
                    if response.status_code == 404:
                        raise ValueError(f"Issue {issue_key} not found.")
                    self._handle_error(response)

                return response.json()  # type: ignore[no-any-return]

        except httpx.TimeoutException:
            raise ValueError(f"Timeout getting issue {issue_key}")

    def create_issue(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new issue.

        Args:
            issue_data: Issue fields and metadata

        Returns:
            Created issue data with key and ID

        Raises:
            ValueError: If validation fails or API error
        """
        url = f"{self.base_url}/rest/api/2/issue"

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, headers=self._get_headers(), json=issue_data)

                if response.status_code not in (200, 201):
                    self._handle_error(response)

                return response.json()  # type: ignore[no-any-return]

        except httpx.TimeoutException:
            raise ValueError("Timeout creating issue")

    def update_issue(self, issue_key: str, update_data: Dict[str, Any]) -> None:
        """Update an existing issue.

        Args:
            issue_key: Issue key (e.g., "PROJ-123")
            update_data: Fields to update

        Raises:
            ValueError: If issue not found or validation fails
        """
        url = f"{self.base_url}/rest/api/2/issue/{issue_key}"

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.put(url, headers=self._get_headers(), json=update_data)

                if response.status_code not in (200, 204):
                    self._handle_error(response)

        except httpx.TimeoutException:
            raise ValueError(f"Timeout updating issue {issue_key}")

    def get_project_schema(self, project_key: str, issue_type: str) -> List[Dict[str, Any]]:
        """Get field schema for a project and issue type.

        Args:
            project_key: Project key
            issue_type: Issue type name

        Returns:
            List of field definitions

        Raises:
            ValueError: If project not found or API error
        """
        url = f"{self.base_url}/rest/api/2/issue/createmeta"
        params = {
            "projectKeys": project_key,
            "issuetypeNames": issue_type,
            "expand": "projects.issuetypes.fields",
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=self._get_headers(), params=params)

                if response.status_code != 200:
                    self._handle_error(response)

                data = response.json()
                projects = data.get("projects", [])

                if not projects:
                    raise ValueError(f"Project {project_key} not found or no issue types available")

                issue_types = projects[0].get("issuetypes", [])
                if not issue_types:
                    raise ValueError(f"Issue type {issue_type} not found in project {project_key}")

                fields = issue_types[0].get("fields", {})
                return [{"key": k, **v} for k, v in fields.items()]

        except httpx.TimeoutException:
            raise ValueError(f"Timeout getting schema for {project_key}/{issue_type}")

    def search_issues(self, jql: str, max_results: int = 100, start_at: int = 0) -> Dict[str, Any]:
        """Search issues using JQL.

        Args:
            jql: JQL query string
            max_results: Maximum results to return
            start_at: Starting offset for pagination

        Returns:
            Search results with issues and pagination info

        Raises:
            ValueError: If JQL invalid or API error
        """
        url = f"{self.base_url}/rest/api/2/search"
        data = {"jql": jql, "maxResults": max_results, "startAt": start_at}

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, headers=self._get_headers(), json=data)

                if response.status_code != 200:
                    self._handle_error(response)

                return response.json()  # type: ignore[no-any-return]

        except httpx.TimeoutException:
            raise ValueError("Timeout executing search query")

    def create_filter(
        self, name: str, jql: str, description: str | None = None, favourite: bool = False
    ) -> Dict[str, Any]:
        """Create a new saved filter.

        Args:
            name: Filter name
            jql: JQL query string
            description: Optional filter description
            favourite: Whether to mark as favorite

        Returns:
            Created filter data

        Raises:
            ValueError: If filter creation fails
        """
        url = f"{self.base_url}/rest/api/2/filter"
        data = {"name": name, "jql": jql, "favourite": favourite}
        if description:
            data["description"] = description

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, headers=self._get_headers(), json=data)

                if response.status_code not in (200, 201):
                    self._handle_error(response)

                return response.json()  # type: ignore[no-any-return]

        except httpx.TimeoutException:
            raise ValueError("Timeout creating filter")

    def list_filters(self) -> Dict[str, Any]:
        """List all accessible filters.

        Returns:
            List of filter metadata

        Raises:
            ValueError: If filter listing fails
        """
        url = f"{self.base_url}/rest/api/2/filter/my"

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=self._get_headers())

                if response.status_code != 200:
                    self._handle_error(response)

                return response.json()  # type: ignore[no-any-return]

        except httpx.TimeoutException:
            raise ValueError("Timeout listing filters")

    def get_filter(self, filter_id: str) -> Dict[str, Any]:
        """Get filter details by ID.

        Args:
            filter_id: Filter ID

        Returns:
            Filter details

        Raises:
            ValueError: If filter not found or access denied
        """
        url = f"{self.base_url}/rest/api/2/filter/{filter_id}"

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=self._get_headers())

                if response.status_code != 200:
                    self._handle_error(response)

                return response.json()  # type: ignore[no-any-return]

        except httpx.TimeoutException:
            raise ValueError(f"Timeout getting filter {filter_id}")

    def update_filter(
        self,
        filter_id: str,
        name: str | None = None,
        jql: str | None = None,
        description: str | None = None,
        favourite: bool | None = None,
    ) -> Dict[str, Any]:
        """Update an existing filter.

        Args:
            filter_id: Filter ID
            name: New filter name
            jql: New JQL query
            description: New description
            favourite: Whether to mark as favorite

        Returns:
            Updated filter data

        Raises:
            ValueError: If filter update fails
        """
        url = f"{self.base_url}/rest/api/2/filter/{filter_id}"
        data: Dict[str, Any] = {}
        if name is not None:
            data["name"] = name
        if jql is not None:
            data["jql"] = jql
        if description is not None:
            data["description"] = description
        if favourite is not None:
            data["favourite"] = favourite

        if not data:
            raise ValueError("At least one field must be provided to update")

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.put(url, headers=self._get_headers(), json=data)

                if response.status_code != 200:
                    self._handle_error(response)

                return response.json()  # type: ignore[no-any-return]

        except httpx.TimeoutException:
            raise ValueError(f"Timeout updating filter {filter_id}")

    def delete_filter(self, filter_id: str) -> None:
        """Delete a filter.

        Args:
            filter_id: Filter ID

        Raises:
            ValueError: If filter deletion fails or permission denied
        """
        url = f"{self.base_url}/rest/api/2/filter/{filter_id}"

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.delete(url, headers=self._get_headers())

                if response.status_code != 204:
                    self._handle_error(response)

        except httpx.TimeoutException:
            raise ValueError(f"Timeout deleting filter {filter_id}")

    def get_transitions(self, issue_key: str) -> Dict[str, Any]:
        """Get available transitions for an issue.

        Args:
            issue_key: Issue key (e.g., "PROJ-123")

        Returns:
            Available transitions with IDs, names, and destination statuses

        Raises:
            ValueError: If issue not found or API error
        """
        url = f"{self.base_url}/rest/api/2/issue/{issue_key}/transitions"

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=self._get_headers())

                if response.status_code != 200:
                    self._handle_error(response)

                return response.json()  # type: ignore[no-any-return]

        except httpx.TimeoutException:
            raise ValueError(f"Timeout getting transitions for {issue_key}")

    def transition_issue(self, issue_key: str, transition_id: str, fields: Dict[str, Any] | None = None) -> None:
        """Transition an issue through workflow.

        Args:
            issue_key: Issue key (e.g., "PROJ-123")
            transition_id: Transition ID to execute
            fields: Optional fields required by the transition

        Raises:
            ValueError: If transition invalid or API error
        """
        url = f"{self.base_url}/rest/api/2/issue/{issue_key}/transitions"
        data: Dict[str, Any] = {"transition": {"id": transition_id}}
        if fields:
            data["fields"] = fields

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, headers=self._get_headers(), json=data)

                if response.status_code != 204:
                    self._handle_error(response)

        except httpx.TimeoutException:
            raise ValueError(f"Timeout transitioning issue {issue_key}")

    def add_comment(self, issue_key: str, body: str) -> Dict[str, Any]:
        """Add a comment to an issue.

        Args:
            issue_key: Issue key (e.g., "PROJ-123")
            body: Comment text

        Returns:
            Created comment data with ID, author, and timestamp

        Raises:
            ValueError: If issue not found or API error
        """
        url = f"{self.base_url}/rest/api/2/issue/{issue_key}/comment"
        data = {"body": body}

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, headers=self._get_headers(), json=data)

                if response.status_code not in (200, 201):
                    self._handle_error(response)

                return response.json()  # type: ignore[no-any-return]

        except httpx.TimeoutException:
            raise ValueError(f"Timeout adding comment to issue {issue_key}")

    def list_comments(self, issue_key: str) -> Dict[str, Any]:
        """List all comments on an issue.

        Args:
            issue_key: Issue key (e.g., "PROJ-123")

        Returns:
            Comments list with total count

        Raises:
            ValueError: If issue not found or API error
        """
        url = f"{self.base_url}/rest/api/2/issue/{issue_key}/comment"

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=self._get_headers())

                if response.status_code != 200:
                    self._handle_error(response)

                return response.json()  # type: ignore[no-any-return]

        except httpx.TimeoutException:
            raise ValueError(f"Timeout listing comments for issue {issue_key}")

    def update_comment(self, issue_key: str, comment_id: str, body: str) -> Dict[str, Any]:
        """Update an existing comment.

        Args:
            issue_key: Issue key (e.g., "PROJ-123")
            comment_id: Comment ID to update
            body: New comment text

        Returns:
            Updated comment data

        Raises:
            ValueError: If comment not found or permission denied
        """
        url = f"{self.base_url}/rest/api/2/issue/{issue_key}/comment/{comment_id}"
        data = {"body": body}

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.put(url, headers=self._get_headers(), json=data)

                if response.status_code != 200:
                    self._handle_error(response)

                return response.json()  # type: ignore[no-any-return]

        except httpx.TimeoutException:
            raise ValueError(f"Timeout updating comment {comment_id} on issue {issue_key}")

    def delete_comment(self, issue_key: str, comment_id: str) -> None:
        """Delete a comment.

        Args:
            issue_key: Issue key (e.g., "PROJ-123")
            comment_id: Comment ID to delete

        Raises:
            ValueError: If comment not found or permission denied
        """
        url = f"{self.base_url}/rest/api/2/issue/{issue_key}/comment/{comment_id}"

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.delete(url, headers=self._get_headers())

                if response.status_code != 204:
                    self._handle_error(response)

        except httpx.TimeoutException:
            raise ValueError(f"Timeout deleting comment {comment_id} on issue {issue_key}")
