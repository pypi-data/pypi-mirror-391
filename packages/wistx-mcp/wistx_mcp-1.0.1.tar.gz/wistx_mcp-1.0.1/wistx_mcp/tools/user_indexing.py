"""MCP tools for user-provided resource indexing."""

import logging
from typing import Any, Optional

from wistx_mcp.tools.lib.api_client import WISTXAPIClient
from wistx_mcp.tools.lib.retry_utils import with_timeout_and_retry

logger = logging.getLogger(__name__)

api_client = WISTXAPIClient()


async def index_repository(
    repo_url: str,
    branch: str = "main",
    name: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[list[str]] = None,
    github_token: Optional[str] = None,
    api_key: Optional[str] = None,
) -> dict[str, Any]:
    """Index a GitHub repository for user-specific search.

    Args:
        repo_url: GitHub repository URL
        branch: Branch to index (default: main)
        name: Custom name for the resource
        description: Resource description
        tags: Tags for categorization
        github_token: GitHub personal access token (for private repos)
        api_key: WISTX API key (required for authentication)

    Returns:
        Dictionary with resource_id and status

    Raises:
        ValueError: If api_key is not provided
    """
    if not api_key:
        raise ValueError("api_key is required for indexing operations")

    try:
        result = await with_timeout_and_retry(
            api_client.index_repository,
            timeout_seconds=120.0,
            max_attempts=2,
            retryable_exceptions=(RuntimeError, ConnectionError, TimeoutError),
            repo_url=repo_url,
            branch=branch,
            name=name,
            description=description,
            tags=tags or [],
            github_token=github_token,
            api_key=api_key,
        )
        return result
    except (ValueError, RuntimeError, ConnectionError, TimeoutError) as e:
        logger.error("Error indexing repository: %s", e, exc_info=True)
        raise
    except Exception as e:
        logger.error("Unexpected error indexing repository: %s", e, exc_info=True)
        raise RuntimeError(f"Unexpected error indexing repository: {e}") from e


async def index_content(
    content_url: Optional[str] = None,
    file_path: Optional[str] = None,
    content_type: Optional[str] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[list[str]] = None,
    include_patterns: Optional[list[str]] = None,
    exclude_patterns: Optional[list[str]] = None,
    api_key: Optional[str] = None,
) -> dict[str, Any]:
    """Index content (documentation website or document file) for user-specific search.

    Unified function that handles both:
    1. Documentation websites: Provide content_url (website URL) - crawls multiple pages
    2. Document files: Provide file_path or content_url (file URL/path) - processes single file

    Args:
        content_url: Content URL - can be:
            - Documentation website URL (for website crawling)
            - Document URL (http/https) or local file path (for single file)
        file_path: Local file path for direct upload (for single file, optional)
        content_type: Content type - can be:
            - "documentation" for website crawling
            - "pdf", "docx", "markdown", "md", "txt" for single files
            - Auto-detected from file_path or URL if not provided
        name: Custom name for the resource
        description: Resource description
        tags: Tags for categorization
        include_patterns: URL patterns to include (for documentation websites)
        exclude_patterns: URL patterns to exclude (for documentation websites)
        api_key: WISTX API key (required for authentication)

    Returns:
        Dictionary with resource_id and status

    Raises:
        ValueError: If api_key is not provided or required parameters missing
    """
    if not api_key:
        raise ValueError("api_key is required for indexing operations")

    if not content_url and not file_path:
        raise ValueError("Either 'content_url' or 'file_path' must be provided")

    document_extensions = {".pdf", ".docx", ".md", ".markdown", ".txt"}
    
    is_documentation = False
    if content_type == "documentation":
        is_documentation = True
    elif content_type and content_type not in ["documentation"]:
        is_documentation = False
    elif file_path:
        is_documentation = False
    elif content_url:
        from pathlib import Path
        url_path = Path(content_url)
        has_file_extension = url_path.suffix.lower() in document_extensions
        is_documentation = not has_file_extension

    if is_documentation:
        if not content_url:
            raise ValueError("content_url is required for documentation indexing")
        
        try:
            result = await with_timeout_and_retry(
                api_client.index_documentation,
                timeout_seconds=120.0,
                max_attempts=2,
                retryable_exceptions=(RuntimeError, ConnectionError, TimeoutError),
                documentation_url=content_url,
                name=name,
                description=description,
                tags=tags or [],
                include_patterns=include_patterns,
                exclude_patterns=exclude_patterns,
                api_key=api_key,
            )
            return result
        except (ValueError, RuntimeError, ConnectionError, TimeoutError) as e:
            logger.error("Error indexing documentation: %s", e, exc_info=True)
            raise
        except Exception as e:
            logger.error("Unexpected error indexing documentation: %s", e, exc_info=True)
            raise RuntimeError(f"Unexpected error indexing documentation: {e}") from e
    else:
        try:
            result = await with_timeout_and_retry(
                api_client.index_document,
                timeout_seconds=60.0,
                max_attempts=2,
                retryable_exceptions=(RuntimeError, ConnectionError, TimeoutError),
                document_url=content_url,
                file_path=file_path,
                document_type=content_type,
                name=name,
                description=description,
                tags=tags or [],
                api_key=api_key,
            )
            return result
        except (ValueError, RuntimeError, ConnectionError, TimeoutError) as e:
            logger.error("Error indexing document: %s", e, exc_info=True)
            raise
        except Exception as e:
            logger.error("Unexpected error indexing document: %s", e, exc_info=True)
            raise RuntimeError(f"Unexpected error indexing document: {e}") from e


async def index_documentation(
    documentation_url: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[list[str]] = None,
    include_patterns: Optional[list[str]] = None,
    exclude_patterns: Optional[list[str]] = None,
    api_key: Optional[str] = None,
) -> dict[str, Any]:
    """Index a documentation website for user-specific search.

    Legacy function - use index_content instead.

    Args:
        documentation_url: Documentation website URL
        name: Custom name for the resource
        description: Resource description
        tags: Tags for categorization
        include_patterns: URL patterns to include
        exclude_patterns: URL patterns to exclude
        api_key: WISTX API key (required for authentication)

    Returns:
        Dictionary with resource_id and status
    """
    return await index_content(
        content_url=documentation_url,
        content_type="documentation",
        name=name,
        description=description,
        tags=tags,
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
        api_key=api_key,
    )


async def index_document(
    document_url: Optional[str] = None,
    file_path: Optional[str] = None,
    document_type: Optional[str] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[list[str]] = None,
    api_key: Optional[str] = None,
) -> dict[str, Any]:
    """Index a document for user-specific search.

    Legacy function - use index_content instead.

    Args:
        document_url: Document URL (http/https) or local file path (optional)
        file_path: Local file path for direct upload (optional)
        document_type: Document type (pdf, docx, markdown, txt)
        name: Custom name for the resource
        description: Resource description
        tags: Tags for categorization
        api_key: WISTX API key (required for authentication)

    Returns:
        Dictionary with resource_id and status
    """
    return await index_content(
        content_url=document_url,
        file_path=file_path,
        content_type=document_type,
        name=name,
        description=description,
        tags=tags,
        api_key=api_key,
    )


async def list_resources(
    resource_type: Optional[str] = None,
    status: Optional[str] = None,
    api_key: Optional[str] = None,
) -> dict[str, Any]:
    """List all indexed resources for the user.

    Args:
        resource_type: Filter by resource type (repository, documentation, document)
        status: Filter by status (pending, indexing, completed, failed)
        api_key: WISTX API key (required for authentication)

    Returns:
        Dictionary with list of resources

    Raises:
        ValueError: If api_key is not provided
    """
    if not api_key:
        raise ValueError("api_key is required for listing resources")

    try:
        result = await api_client.list_resources(
            resource_type=resource_type,
            status=status,
            api_key=api_key,
        )
        return result
    except Exception as e:
        logger.error("Error listing resources: %s", e, exc_info=True)
        raise


async def check_resource_status(
    resource_id: str,
    api_key: Optional[str] = None,
) -> dict[str, Any]:
    """Check indexing status and progress for a resource.

    Args:
        resource_id: Resource ID
        api_key: WISTX API key (required for authentication)

    Returns:
        Dictionary with resource status and progress

    Raises:
        ValueError: If api_key is not provided
    """
    if not api_key:
        raise ValueError("api_key is required for checking resource status")

    try:
        result = await api_client.get_resource(
            resource_id=resource_id,
            api_key=api_key,
        )
        return result
    except Exception as e:
        logger.error("Error checking resource status: %s", e, exc_info=True)
        raise


async def delete_resource(
    resource_id: str,
    api_key: Optional[str] = None,
) -> dict[str, Any]:
    """Delete an indexed resource and all associated knowledge articles.

    Args:
        resource_id: Resource ID
        api_key: WISTX API key (required for authentication)

    Returns:
        Dictionary with deletion status

    Raises:
        ValueError: If api_key is not provided
    """
    if not api_key:
        raise ValueError("api_key is required for deleting resources")

    try:
        result = await api_client.delete_resource(
            resource_id=resource_id,
            api_key=api_key,
        )
        return result
    except Exception as e:
        logger.error("Error deleting resource: %s", e, exc_info=True)
        raise

