"""MCP tools for compliance and knowledge research."""

import logging
from typing import Any

import httpx

from wistx_mcp.tools.lib.api_client import WISTXAPIClient
from wistx_mcp.tools.lib.web_search_client import WebSearchClient
from wistx_mcp.config import settings
from wistx_mcp.tools import pricing

logger = logging.getLogger(__name__)

api_client = WISTXAPIClient()


async def get_compliance_requirements(
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

    Raises:
        ValueError: If input validation fails
        RuntimeError: If API call fails
        ConnectionError: If network connection fails
        TimeoutError: If request times out
    """
    if not resource_types:
        raise ValueError("At least one resource type is required")

    if not isinstance(resource_types, list):
        raise ValueError("resource_types must be a list")

    if len(resource_types) > 50:
        raise ValueError("Maximum 50 resource types allowed")

    sanitized_resource_types = []
    for rt in resource_types:
        if not isinstance(rt, str):
            raise ValueError(f"Resource type must be string, got {type(rt)}")
        rt_clean = rt.strip().upper()[:50]
        if not rt_clean or len(rt_clean) < 2:
            raise ValueError(f"Invalid resource type: {rt}")
        sanitized_resource_types.append(rt_clean)

    resource_types = sanitized_resource_types

    if standards is not None:
        if not isinstance(standards, list):
            raise ValueError("standards must be a list")
        if len(standards) > 20:
            raise ValueError("Maximum 20 standards allowed")

        sanitized_standards = []
        for std in standards:
            if not isinstance(std, str):
                raise ValueError(f"Standard must be string, got {type(std)}")
            std_clean = std.strip().upper()[:50]
            if not std_clean or len(std_clean) < 2:
                raise ValueError(f"Invalid standard: {std}")
            sanitized_standards.append(std_clean)

        standards = sanitized_standards

    if severity is not None:
        valid_severities = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        if severity not in valid_severities:
            raise ValueError(f"severity must be one of {valid_severities}")
        severity = severity.upper()

    try:
        result = await api_client.get_compliance_requirements(
            resource_types=resource_types,
            standards=standards or [],
            severity=severity,
            include_remediation=include_remediation,
            include_verification=include_verification,
        )

        if not isinstance(result, dict):
            logger.error("Invalid response type from API: %s", type(result))
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

                required_fields = ["control_id", "standard"]
                missing = [f for f in required_fields if f not in control]
                if missing:
                    logger.warning("Control %d missing fields: %s", i, missing)

        if "data" in result and isinstance(result["data"], dict):
            if "controls" in result["data"]:
                if not isinstance(result["data"]["controls"], list):
                    logger.error("Data.controls field is not a list: %s", type(result["data"]["controls"]))
                    raise RuntimeError("Invalid data.controls structure: expected list")

        return result
    except ValueError as e:
        logger.error("Validation error in get_compliance_requirements: %s", e)
        raise
    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code if e.response else None
        logger.error("HTTP status error: %s (status: %s)", e, status_code)
        if status_code == 401:
            raise ValueError("Invalid API key") from e
        elif status_code == 429:
            raise RuntimeError("Rate limit exceeded") from e
        elif status_code >= 500:
            raise RuntimeError(f"Server error: {status_code}") from e
        raise RuntimeError(f"HTTP error: {status_code}") from e
    except httpx.TimeoutException as e:
        logger.error("Request timeout: %s", e)
        raise TimeoutError("Request timeout") from e
    except httpx.NetworkError as e:
        logger.error("Network error: %s", e)
        raise ConnectionError("Network connection failed") from e
    except httpx.HTTPError as e:
        logger.error("HTTP error in get_compliance_requirements: %s", e, exc_info=True)
        raise RuntimeError(f"HTTP error: {e}") from e
    except (RuntimeError, ConnectionError, TimeoutError) as e:
        logger.error("Error in get_compliance_requirements: %s", e, exc_info=True)
        raise
    except Exception as e:
        logger.error("Unexpected error in get_compliance_requirements: %s", e, exc_info=True)
        raise RuntimeError(f"Unexpected error getting compliance requirements: {e}") from e


async def research_knowledge_base(
    query: str,
    domains: list[str] | None = None,
    content_types: list[str] | None = None,
    include_cross_domain: bool = True,
    include_web_search: bool = True,
    format: str = "structured",
    max_results: int = 20,
) -> dict[str, Any]:
    """Research knowledge base across all domains with optional web search.

    Deep research tool that searches internal knowledge base and optionally
    includes real-time web search results for comprehensive coverage.

    Args:
        query: Research query in natural language
        domains: Filter by domains (compliance, finops, devops, infrastructure, security, etc.)
        content_types: Filter by content types (guide, pattern, strategy, etc.)
        include_cross_domain: Include cross-domain relationships
        include_web_search: Include web search results (Tavily) for real-time information
        format: Response format (structured, markdown, executive_summary)
        max_results: Maximum number of results

    Returns:
        Dictionary with research results and summary:
        - results: Knowledge articles from internal database
        - web_results: Web search results (if include_web_search=True)
        - research_summary: Summary of findings

    Raises:
        ValueError: If query validation fails
        RuntimeError: If API call fails
        ConnectionError: If network connection fails
        TimeoutError: If request times out
    """
    if not query or not isinstance(query, str):
        raise ValueError("Query must be a non-empty string")
    
    query = query.strip()
    if len(query) < 10:
        raise ValueError("Query must be at least 10 characters")
    
    if len(query) > 10000:
        raise ValueError("Query must be less than 10000 characters")
    
    if max_results < 1 or max_results > 100:
        raise ValueError("max_results must be between 1 and 100")
    
    if format not in ["structured", "markdown", "executive_summary"]:
        raise ValueError(f"Invalid format: {format}. Must be one of: structured, markdown, executive_summary")

    web_search_client = None
    web_results = None

    try:
        result = await api_client.research_knowledge_base(
            query=query,
            domains=domains or [],
            content_types=content_types or [],
            include_cross_domain=include_cross_domain,
            response_format=format,
            max_results=max_results,
        )

        if include_web_search and settings.tavily_api_key:
            try:
                web_search_client = WebSearchClient(api_key=settings.tavily_api_key)
                
                if domains:
                    web_search_data = await web_search_client.search_by_domain(
                        query=query,
                        domains=domains,
                        max_results=max_results,
                        max_age_days=None,
                    )
                else:
                    web_search_data = await web_search_client.search_devops(
                        query=query,
                        max_results=max_results,
                        max_age_days=90,
                    )

                web_results = {
                    "answer": web_search_data.get("answer"),
                    "results": web_search_data.get("results", []),
                    "domains_searched": domains if domains else ["devops", "infrastructure"],
                    "freshness_info": web_search_data.get("freshness_info", {}),
                }

                logger.info(
                    "Added web search results to knowledge research: %d web results for domains %s",
                    len(web_search_data.get("results", [])),
                    domains if domains else ["devops", "infrastructure"],
                )
            except (ValueError, RuntimeError, ConnectionError, TimeoutError) as e:
                logger.warning("Failed to include web search in research: %s", e)

        if web_results:
            result["web_results"] = web_results

        return result
    except (ValueError, RuntimeError, ConnectionError, TimeoutError) as e:
        logger.error("Error in research_knowledge_base: %s", e, exc_info=True)
        raise
    except Exception as e:
        logger.error("Unexpected error in research_knowledge_base: %s", e, exc_info=True)
        raise RuntimeError(f"Unexpected error researching knowledge base: {e}") from e
    finally:
        if web_search_client:
            await web_search_client.close()


async def calculate_infrastructure_cost(
    resources: list[dict[str, Any]],
) -> dict[str, Any]:
    """Calculate infrastructure costs.

    Args:
        resources: List of resource specifications
            Example: [{"cloud": "aws", "service": "rds", "instance_type": "db.t3.medium", "quantity": 1}]

    Returns:
        Dictionary with cost breakdown and optimizations
    """
    try:
        result = await pricing.calculate_infrastructure_cost(resources)
        return result
    except (ValueError, RuntimeError, ConnectionError, TimeoutError) as e:
        logger.error("Error in calculate_infrastructure_cost: %s", e, exc_info=True)
        raise
    except Exception as e:
        logger.error("Unexpected error in calculate_infrastructure_cost: %s", e, exc_info=True)
        raise RuntimeError(f"Unexpected error calculating infrastructure cost: {e}") from e

