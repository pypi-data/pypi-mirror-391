"""Best practices tool - search DevOps best practices."""

from typing import Any

from wistx_mcp.tools.lib.mongodb_client import MongoDBClient
from wistx_mcp.tools.lib.vector_search import VectorSearch
from wistx_mcp.config import settings


async def search_best_practices(
    query: str,
    category: str | None = None,
    limit: int = 10,
) -> dict[str, Any]:
    """Search DevOps best practices.

    Args:
        query: Search query
        category: Filter by category
        limit: Maximum number of results

    Returns:
        Dictionary with best practices
    """
    client = MongoDBClient()
    vector_search = VectorSearch(client, openai_api_key=settings.openai_api_key)

    results = await vector_search.search_best_practices(
        query=query,
        category=category,
        limit=limit,
    )

    return {
        "practices": results,
        "total": len(results),
    }

