"""Compliance tool - get compliance requirements for infrastructure resources."""

from typing import Any

from wistx_mcp.tools.lib.mongodb_client import MongoDBClient
from wistx_mcp.tools.lib.vector_search import VectorSearch
from wistx_mcp.config import settings


async def get_compliance_requirements(
    resource_type: str,
    standards: list[str] | None = None,
    severity: str | None = None,
) -> dict[str, Any]:
    """Get compliance requirements for a resource.

    Args:
        resource_type: AWS resource type (e.g., RDS, S3, EC2)
        standards: Compliance standards to check (e.g., ["PCI-DSS", "HIPAA"])
        severity: Filter by severity (CRITICAL, HIGH, MEDIUM, LOW)

    Returns:
        Dictionary with compliance controls and summary
    """
    client = MongoDBClient()
    vector_search = VectorSearch(client, openai_api_key=settings.openai_api_key)

    query = f"{resource_type} compliance"
    if standards:
        query += " " + " ".join(standards)

    results = await vector_search.search_compliance(
        query=query,
        standards=standards,
        severity=severity,
        limit=20,
    )

    return {
        "controls": results,
        "summary": f"Found {len(results)} compliance controls for {resource_type}",
        "total": len(results),
    }

