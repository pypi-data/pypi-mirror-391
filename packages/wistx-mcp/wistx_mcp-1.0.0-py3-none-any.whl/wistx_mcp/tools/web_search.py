"""Web search tool - unified search for DevOps/infrastructure/compliance/finops/SRE."""

import logging
from typing import Any

from wistx_mcp.tools.lib.mongodb_client import MongoDBClient
from wistx_mcp.tools.lib.security_client import SecurityClient
from wistx_mcp.tools.lib.web_search_client import WebSearchClient
from wistx_mcp.config import settings

logger = logging.getLogger(__name__)


async def web_search(
    query: str,
    search_type: str = "general",
    resource_type: str | None = None,
    cloud_provider: str | None = None,
    severity: str | None = None,
    include_cves: bool = True,
    include_advisories: bool = True,
    limit: int = 20,
) -> dict[str, Any]:
    """Web search for security information and general web content.

    Focused on security searches (CVEs, advisories) and general web search.
    For compliance requirements, use get_compliance_requirements tool.
    For deep research, use research_knowledge_base tool.

    Args:
        query: Search query
        search_type: Type of search (general, security)
        resource_type: Filter by resource type (RDS, S3, EKS, etc.)
        cloud_provider: Filter by cloud provider (aws, gcp, azure)
        severity: Filter by severity (for security searches)
        include_cves: Include CVE database results
        include_advisories: Include security advisories
        limit: Maximum number of results

    Returns:
        Dictionary with search results:
        - web: Web search results (Tavily)
        - security: Security-related results (CVEs, advisories)
        - total: Total results count

    Raises:
        ValueError: If invalid search_type or parameters
        Exception: If search fails
    """
    if search_type not in ["general", "security"]:
        raise ValueError(f"Invalid search_type: {search_type}. Use 'general' or 'security'")

    if limit < 1 or limit > 100:
        raise ValueError("limit must be between 1 and 100")

    logger.info(
        "Web search: query='%s', type=%s, resource=%s, cloud=%s",
        query[:100],
        search_type,
        resource_type,
        cloud_provider,
    )

    results: dict[str, Any] = {
        "web": [],
        "security": [],
        "total": 0,
    }

    mongodb_client = None
    security_client = None
    web_search_client = None

    try:
        mongodb_client = MongoDBClient()
        await mongodb_client.connect()

        security_client = SecurityClient(mongodb_client)

        if settings.tavily_api_key:
            web_search_client = WebSearchClient(api_key=settings.tavily_api_key)

        if search_type == "general" and web_search_client:
            try:
                web_results = await web_search_client.search_devops(
                    query=query,
                    max_results=limit,
                )

                web_items = []
                if web_results.get("answer"):
                    web_items.append({
                        "title": "AI Answer",
                        "content": web_results["answer"],
                        "source": "tavily",
                        "type": "answer",
                    })

                for result in web_results.get("results", []):
                    web_items.append({
                        "title": result.get("title", ""),
                        "content": result.get("content", ""),
                        "url": result.get("url", ""),
                        "score": result.get("score", 0),
                        "source": "tavily",
                        "type": "web_result",
                    })

                results["web"] = web_items
            except Exception as e:
                logger.warning("Failed to perform web search: %s", e)

        if search_type in ["general", "security"] and include_cves:
            try:
                cves = await security_client.search_cves(
                    query=query,
                    resource_type=resource_type,
                    severity=severity,
                    limit=limit,
                )
                results["security"].extend(cves)
            except Exception as e:
                logger.warning("Failed to search CVEs: %s", e)

        if search_type in ["general", "security"] and include_advisories:
            try:
                advisories = await security_client.search_advisories(
                    query=query,
                    cloud_provider=cloud_provider,
                    limit=limit,
                )
                results["security"].extend(advisories)
            except Exception as e:
                logger.warning("Failed to search advisories: %s", e)

        if search_type in ["general", "security"]:
            try:
                k8s_security = await security_client.search_kubernetes_security(
                    query=query,
                    limit=limit,
                )
                results["security"].extend(k8s_security)
            except Exception as e:
                logger.warning("Failed to search Kubernetes security: %s", e)


        results["total"] = len(results["web"]) + len(results["security"])

        logger.info("Web search completed: %d total results", results["total"])

        return results

    except Exception as e:
        logger.error("Error in web_search: %s", e, exc_info=True)
        raise
    finally:
        if mongodb_client:
            await mongodb_client.disconnect()
        if security_client:
            await security_client.close()
        if web_search_client:
            await web_search_client.close()

