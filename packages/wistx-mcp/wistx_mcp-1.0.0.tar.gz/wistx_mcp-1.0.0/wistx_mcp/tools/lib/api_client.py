"""REST API client for MCP server."""

import json
import logging
import os
from pathlib import Path
from typing import Any, BinaryIO

import httpx

from wistx_mcp.config import settings
from wistx_mcp.tools.lib.retry_utils import with_timeout_and_retry

logger = logging.getLogger(__name__)


class WISTXAPIClient:
    """HTTP client for calling WISTX REST API."""

    def __init__(self, api_key: str | None = None, api_url: str | None = None):
        """Initialize API client.

        Args:
            api_key: API key for authentication (defaults to WISTX_API_KEY env var)
            api_url: Base URL for API (defaults to WISTX_API_URL env var or config)
        """
        self.api_key = api_key or settings.api_key or os.getenv("WISTX_API_KEY", "")
        self.api_url = (api_url or settings.api_url or os.getenv("WISTX_API_URL", "http://localhost:8000")).rstrip("/")

        self.client = httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(
                max_connections=100,
                max_keepalive_connections=20,
                keepalive_expiry=30.0,
            ),
            headers={
                "Authorization": f"Bearer {self.api_key}" if self.api_key else "",
                "Content-Type": "application/json",
            },
        )

    async def close(self) -> None:
        """Close HTTP client connection."""
        await self.client.aclose()

    async def get_compliance_requirements(
        self,
        resource_types: list[str],
        standards: list[str] | None = None,
        severity: str | None = None,
        include_remediation: bool = True,
        include_verification: bool = True,
    ) -> dict[str, Any]:
        """Get compliance requirements for infrastructure resources.

        Args:
            resource_types: List of resource types (RDS, S3, EC2, etc.)
            standards: List of compliance standards (PCI-DSS, HIPAA, etc.)
            severity: Filter by severity level
            include_remediation: Include remediation guidance
            include_verification: Include verification procedures

        Returns:
            Dictionary with compliance controls and summary
        """
        url = f"{self.api_url}/v1/compliance/requirements"
        payload = {
            "resource_types": resource_types,
            "standards": standards or [],
            "severity": severity,
            "include_remediation": include_remediation,
            "include_verification": include_verification,
        }

        import json
        payload_size = len(json.dumps(payload))
        if payload_size > 100000:
            raise ValueError(f"Request payload too large: {payload_size} bytes (max 100KB)")

        try:
            response = await with_timeout_and_retry(
                self.client.post,
                timeout_seconds=30.0,
                max_attempts=3,
                retryable_exceptions=(httpx.HTTPError, httpx.TimeoutException, httpx.NetworkError),
                url=url,
                json=payload,
            )
            response.raise_for_status()

            try:
                result = response.json()
            except ValueError as e:
                logger.error("Invalid JSON response from compliance API: %s", e)
                raise RuntimeError("Invalid JSON response from API") from e

            if not isinstance(result, dict):
                logger.error("Unexpected response type from compliance API: %s", type(result))
                raise RuntimeError("Invalid response format from API")

            if "data" not in result and "controls" not in result:
                logger.error("Response missing required fields: %s", list(result.keys()))
                raise RuntimeError("Invalid response structure: missing 'data' or 'controls'")

            if "controls" in result:
                if not isinstance(result["controls"], list):
                    logger.error("Controls field is not a list: %s", type(result["controls"]))
                    raise RuntimeError("Invalid controls structure: expected list")

                for i, control in enumerate(result["controls"]):
                    if not isinstance(control, dict):
                        logger.error("Control %d is not a dict: %s", i, type(control))
                        raise RuntimeError(f"Invalid control structure at index {i}")

            if "data" in result and isinstance(result["data"], dict):
                if "controls" in result["data"]:
                    if not isinstance(result["data"]["controls"], list):
                        logger.error("Data.controls field is not a list: %s", type(result["data"]["controls"]))
                        raise RuntimeError("Invalid data.controls structure: expected list")

            return result
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code if e.response else None
            logger.error(
                "HTTP error calling compliance API: %s (status: %s)",
                e,
                status_code,
            )
            if status_code == 401:
                raise ValueError("Invalid API key") from e
            elif status_code == 429:
                raise RuntimeError("Rate limit exceeded") from e
            elif status_code >= 500:
                raise RuntimeError(f"Server error: {status_code}") from e
            else:
                raise RuntimeError(f"API error: {status_code}") from e
        except httpx.HTTPError as e:
            logger.error("HTTP error calling compliance API: %s", e)
            raise RuntimeError(f"HTTP error: {e}") from e
        except httpx.TimeoutException as e:
            logger.error("Timeout calling compliance API: %s", e)
            raise RuntimeError("Request timeout") from e

    async def research_knowledge_base(
        self,
        query: str,
        domains: list[str] | None = None,
        content_types: list[str] | None = None,
        include_cross_domain: bool = True,
        response_format: str = "structured",
        max_results: int = 20,
    ) -> dict[str, Any]:
        """Research knowledge base across all domains.

        Args:
            query: Research query in natural language
            domains: Filter by domains (compliance, finops, devops, etc.)
            content_types: Filter by content types (guide, pattern, etc.)
            include_cross_domain: Include cross-domain relationships
            response_format: Response format (structured, markdown, executive_summary)
            max_results: Maximum number of results

        Returns:
            Dictionary with research results and summary
        """
        url = f"{self.api_url}/v1/knowledge/research"
        payload = {
            "query": query,
            "domains": domains or [],
            "content_types": content_types or [],
            "include_cross_domain": include_cross_domain,
            "format": response_format,
            "max_results": max_results,
        }

        try:
            response = await with_timeout_and_retry(
                self.client.post,
                timeout_seconds=30.0,
                max_attempts=3,
                retryable_exceptions=(httpx.HTTPError, httpx.TimeoutException, httpx.NetworkError),
                url=url,
                json=payload,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error("Error calling knowledge API: %s", e)
            raise

    async def index_repository(
        self,
        repo_url: str,
        branch: str = "main",
        name: str | None = None,
        description: str | None = None,
        tags: list[str] | None = None,
        github_token: str | None = None,
        api_key: str | None = None,
    ) -> dict[str, Any]:
        """Index a GitHub repository.

        Args:
            repo_url: GitHub repository URL
            branch: Branch to index
            name: Custom name for the resource
            description: Resource description
            tags: Tags for categorization
            github_token: GitHub token for private repos
            api_key: API key (overrides default)

        Returns:
            Dictionary with resource_id and status
        """
        url = f"{self.api_url}/v1/indexing/repositories"
        payload = {
            "repo_url": repo_url,
            "branch": branch,
        }
        if name:
            payload["name"] = name
        if description:
            payload["description"] = description
        if tags:
            payload["tags"] = tags
        if github_token:
            payload["github_token"] = github_token

        headers = self.client.headers.copy()
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        try:
            response = await with_timeout_and_retry(
                self.client.post,
                timeout_seconds=60.0,
                max_attempts=3,
                retryable_exceptions=(httpx.HTTPError, httpx.TimeoutException, httpx.NetworkError),
                url=url,
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error("Error calling indexing API: %s", e)
            raise

    async def index_documentation(
        self,
        documentation_url: str,
        name: str | None = None,
        description: str | None = None,
        tags: list[str] | None = None,
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
        api_key: str | None = None,
    ) -> dict[str, Any]:
        """Index a documentation website.

        Args:
            documentation_url: Documentation website URL
            name: Custom name for the resource
            description: Resource description
            tags: Tags for categorization
            include_patterns: URL patterns to include
            exclude_patterns: URL patterns to exclude
            api_key: API key (overrides default)

        Returns:
            Dictionary with resource_id and status
        """
        url = f"{self.api_url}/v1/indexing/documentation"
        payload = {"documentation_url": documentation_url}
        if name:
            payload["name"] = name
        if description:
            payload["description"] = description
        if tags:
            payload["tags"] = tags
        if include_patterns:
            payload["include_patterns"] = include_patterns
        if exclude_patterns:
            payload["exclude_patterns"] = exclude_patterns

        headers = self.client.headers.copy()
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        try:
            response = await with_timeout_and_retry(
                self.client.post,
                timeout_seconds=60.0,
                max_attempts=3,
                retryable_exceptions=(httpx.HTTPError, httpx.TimeoutException, httpx.NetworkError),
                url=url,
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error("Error calling indexing API: %s", e)
            raise

    async def index_document(
        self,
        document_url: str | None = None,
        file_path: str | None = None,
        document_type: str | None = None,
        name: str | None = None,
        description: str | None = None,
        tags: list[str] | None = None,
        api_key: str | None = None,
    ) -> dict[str, Any]:
        """Index a document.

        Supports two modes:
        1. File upload (multipart): Provide file_path
        2. URL download (multipart): Provide document_url

        Args:
            document_url: Document URL (http/https) or local file path
            file_path: Local file path for direct upload (optional)
            document_type: Document type (pdf, docx, markdown, txt). Auto-detected from file_path if not provided.
            name: Custom name for the resource
            description: Resource description
            tags: Tags for categorization
            api_key: API key (overrides default)

        Returns:
            Dictionary with resource_id and status

        Raises:
            ValueError: If neither file_path nor document_url provided
            FileNotFoundError: If file_path provided but file doesn't exist
        """
        if not file_path and not document_url:
            raise ValueError("Either 'file_path' or 'document_url' must be provided")

        url = f"{self.api_url}/v1/indexing/documents"

        headers = self.client.headers.copy()
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        headers.pop("Content-Type", None)

        try:
            if file_path:
                file_path_obj = Path(file_path)
                if not file_path_obj.exists():
                    raise FileNotFoundError(f"File not found: {file_path}")

                detected_type = document_type
                if not detected_type:
                    file_ext = file_path_obj.suffix.lower()
                    extension_to_type = {
                        ".pdf": "pdf",
                        ".docx": "docx",
                        ".md": "markdown",
                        ".markdown": "markdown",
                        ".txt": "txt",
                    }
                    detected_type = extension_to_type.get(file_ext)

                if not detected_type:
                    raise ValueError(
                        f"Could not determine document type from file: {file_path}. "
                        "Please provide 'document_type' parameter."
                    )

                with open(file_path_obj, "rb") as f:
                    files = {"file": (file_path_obj.name, f, "application/octet-stream")}
                    data = {
                        "document_type": detected_type,
                    }
                    if name:
                        data["name"] = name
                    if description:
                        data["description"] = description
                    if tags:
                        data["tags"] = json.dumps(tags)

                    response = await with_timeout_and_retry(
                        self.client.post,
                        timeout_seconds=120.0,
                        max_attempts=3,
                        retryable_exceptions=(httpx.HTTPError, httpx.TimeoutException, httpx.NetworkError),
                        url=url,
                        files=files,
                        data=data,
                        headers=headers,
                    )

            elif document_url:
                data = {
                    "document_url": document_url,
                }
                if document_type:
                    data["document_type"] = document_type
                if name:
                    data["name"] = name
                if description:
                    data["description"] = description
                if tags:
                    data["tags"] = json.dumps(tags)

                response = await with_timeout_and_retry(
                    self.client.post,
                    timeout_seconds=60.0,
                    max_attempts=3,
                    retryable_exceptions=(httpx.HTTPError, httpx.TimeoutException, httpx.NetworkError),
                    url=url,
                    data=data,
                    headers=headers,
                )

            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error("Error calling indexing API: %s", e)
            raise

    async def list_resources(
        self,
        resource_type: str | None = None,
        status: str | None = None,
        api_key: str | None = None,
    ) -> dict[str, Any]:
        """List indexed resources.

        Args:
            resource_type: Filter by resource type
            status: Filter by status
            api_key: API key (overrides default)

        Returns:
            Dictionary with list of resources
        """
        url = f"{self.api_url}/v1/indexing/resources"
        params = {}
        if resource_type:
            params["resource_type"] = resource_type
        if status:
            params["status"] = status

        headers = self.client.headers.copy()
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        try:
            response = await with_timeout_and_retry(
                self.client.get,
                timeout_seconds=30.0,
                max_attempts=3,
                retryable_exceptions=(httpx.HTTPError, httpx.TimeoutException, httpx.NetworkError),
                url=url,
                params=params,
                headers=headers,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error("Error calling indexing API: %s", e)
            raise

    async def get_resource(
        self,
        resource_id: str,
        api_key: str | None = None,
    ) -> dict[str, Any]:
        """Get resource details.

        Args:
            resource_id: Resource ID
            api_key: API key (overrides default)

        Returns:
            Dictionary with resource details
        """
        url = f"{self.api_url}/v1/indexing/resources/{resource_id}"

        headers = self.client.headers.copy()
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        try:
            response = await with_timeout_and_retry(
                self.client.get,
                timeout_seconds=30.0,
                max_attempts=3,
                retryable_exceptions=(httpx.HTTPError, httpx.TimeoutException, httpx.NetworkError),
                url=url,
                headers=headers,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error("Error calling indexing API: %s", e)
            raise

    async def delete_resource(
        self,
        resource_id: str,
        api_key: str | None = None,
    ) -> dict[str, Any]:
        """Delete indexed resource.

        Args:
            resource_id: Resource ID
            api_key: API key (overrides default)

        Returns:
            Empty dict (204 No Content)
        """
        url = f"{self.api_url}/v1/indexing/resources/{resource_id}"

        headers = self.client.headers.copy()
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        try:
            response = await with_timeout_and_retry(
                self.client.delete,
                timeout_seconds=30.0,
                max_attempts=3,
                retryable_exceptions=(httpx.HTTPError, httpx.TimeoutException, httpx.NetworkError),
                url=url,
                headers=headers,
            )
            response.raise_for_status()
            return {}
        except httpx.HTTPError as e:
            logger.error("Error calling indexing API: %s", e)
            raise

    async def get_current_user(
        self,
        api_key: str | None = None,
    ) -> dict[str, Any]:
        """Get current user information from API key.

        Args:
            api_key: API key (overrides default)

        Returns:
            Dictionary with user information (user_id, organization_id, plan, etc.)

        Raises:
            ValueError: If API key is invalid
        """
        url = f"{self.api_url}/v1/indexing/resources"
        params = {"limit": 1}

        headers = self.client.headers.copy()
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        try:
            response = await with_timeout_and_retry(
                self.client.get,
                timeout_seconds=30.0,
                max_attempts=3,
                retryable_exceptions=(httpx.HTTPError, httpx.TimeoutException, httpx.NetworkError),
                url=url,
                params=params,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()

            resources = data.get("resources", [])
            if not resources:
                raise ValueError("No resources found - invalid API key or user has no resources")

            first_resource = resources[0]
            user_id = first_resource.get("user_id")

            if not user_id:
                raise ValueError("Could not determine user_id from API key")

            return {
                "user_id": str(user_id),
                "organization_id": first_resource.get("organization_id"),
                "plan": data.get("plan", "free"),
            }
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ValueError("Invalid or expired API key") from e
            logger.error("Error calling resources API: %s", e)
            raise
        except httpx.HTTPError as e:
            logger.error("Error calling resources API: %s", e)
            raise

