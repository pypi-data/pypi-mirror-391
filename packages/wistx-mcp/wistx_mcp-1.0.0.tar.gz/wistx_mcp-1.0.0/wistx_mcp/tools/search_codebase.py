"""Search codebase tool - search user's indexed repositories, documentation, and documents."""

import logging
from typing import Any

from wistx_mcp.tools.lib.mongodb_client import MongoDBClient
from wistx_mcp.tools.lib.vector_search import VectorSearch
from wistx_mcp.tools.lib.api_client import WISTXAPIClient
from wistx_mcp.config import settings

logger = logging.getLogger(__name__)

api_client = WISTXAPIClient()


async def search_codebase(
    query: str,
    api_key: str,
    resource_ids: list[str] | None = None,
    resource_types: list[str] | None = None,
    file_types: list[str] | None = None,
    code_type: str | None = None,
    cloud_provider: str | None = None,
    limit: int = 20,
) -> dict[str, Any]:
    """Search user's indexed codebase (repositories, documentation, documents).

    Args:
        query: Search query
        api_key: WISTX API key for authentication
        resource_ids: Filter by specific indexed resources
        resource_types: Filter by resource type (repository, documentation, document)
        file_types: Filter by file extensions (.tf, .yaml, .py, .md, etc.)
        code_type: Filter by code type (terraform, kubernetes, docker, python)
        cloud_provider: Filter by cloud provider mentioned in code
        limit: Maximum number of results

    Returns:
        Dictionary with search results:
        - results: List of matching code/documentation
        - resources: Resource information
        - total: Total results count
        - highlights: Code highlights

    Raises:
        ValueError: If api_key is not provided or invalid parameters
        Exception: If search fails
    """
    if not api_key:
        raise ValueError("api_key is required for codebase search")

    if limit < 1 or limit > 100:
        raise ValueError("limit must be between 1 and 100")

    logger.info(
        "Codebase search: query='%s', resources=%s, types=%s",
        query[:100],
        resource_ids,
        resource_types,
    )

    mongodb_client = None

    try:
        user_info = await api_client.get_current_user(api_key=api_key)
        user_id = user_info.get("user_id")

        if not user_id:
            raise ValueError("Invalid API key or user not found")

        mongodb_client = MongoDBClient()
        await mongodb_client.connect()

        if mongodb_client.database is None:
            raise RuntimeError("Failed to connect to MongoDB")

        vector_search = VectorSearch(
            mongodb_client,
            openai_api_key=settings.openai_api_key,
        )

        mongo_filter: dict[str, Any] = {}

        if resource_ids:
            mongo_filter["resource_id"] = {"$in": resource_ids}

        if resource_types:
            mongo_filter["source_type"] = {"$in": resource_types}

        results = await vector_search.search_knowledge_articles(
            query=query,
            user_id=str(user_id),
            include_global=False,
            limit=limit,
        )

        if file_types:
            filtered_results = []
            for result in results:
                tags = result.get("tags", [])
                if any(ft in tags for ft in file_types):
                    filtered_results.append(result)
            results = filtered_results

        if code_type:
            filtered_results = []
            for result in results:
                tags = result.get("tags", [])
                content = result.get("content", "").lower()
                if code_type.lower() in tags or code_type.lower() in content:
                    filtered_results.append(result)
            results = filtered_results

        if cloud_provider:
            filtered_results = []
            for result in results:
                content = result.get("content", "").lower()
                tags_str = " ".join(result.get("tags", [])).lower()
                if cloud_provider.lower() in content or cloud_provider.lower() in tags_str:
                    filtered_results.append(result)
            results = filtered_results

        resources_info = []
        if results:
            resource_ids_found = set(
                r.get("resource_id") for r in results if r.get("resource_id")
            )
            if resource_ids_found and mongodb_client.database:
                resources_collection = mongodb_client.database.indexed_resources
                resources_cursor = resources_collection.find(
                    {"_id": {"$in": list(resource_ids_found)}}
                )
                resources_info = await resources_cursor.to_list(length=len(resource_ids_found))

        highlights = []
        query_lower = query.lower()
        for result in results[:5]:
            content = result.get("content", "")
            if query_lower in content.lower():
                start_idx = content.lower().find(query_lower)
                highlight_start = max(0, start_idx - 50)
                highlight_end = min(len(content), start_idx + len(query) + 50)
                highlight = content[highlight_start:highlight_end]
                highlights.append({
                    "article_id": result.get("article_id"),
                    "highlight": highlight,
                    "file_path": result.get("source_url", ""),
                })

        logger.info("Codebase search completed: %d results", len(results))

        return {
            "results": results,
            "resources": resources_info,
            "total": len(results),
            "highlights": highlights,
        }

    except Exception as e:
        logger.error("Error in search_codebase: %s", e, exc_info=True)
        raise
    finally:
        if mongodb_client:
            await mongodb_client.disconnect()

