"""Resolve incident tool - mark incident as resolved and build solution knowledge."""

import logging
from typing import Any

from wistx_mcp.tools.lib.mongodb_client import MongoDBClient
from wistx_mcp.tools.lib.incident_tracker import IncidentTracker
from wistx_mcp.tools.lib.solution_builder import SolutionKnowledgeBuilder
from wistx_mcp.tools.lib.vector_search import VectorSearch
from wistx_mcp.config import settings

logger = logging.getLogger(__name__)


async def resolve_incident(
    incident_id: str,
    solution_applied: str,
    solution_effective: bool,
    solution_code: str | None = None,
    solution_source: str | None = None,
) -> dict[str, Any]:
    """Mark incident as resolved and build solution knowledge.

    Args:
        incident_id: Incident identifier
        solution_applied: Solution that was applied
        solution_effective: Whether solution was effective
        solution_code: Solution code (optional)
        solution_source: Solution source (optional)

    Returns:
        Dictionary with incident and solution information

    Raises:
        ValueError: If incident not found
        Exception: If resolution fails
    """
    if not incident_id:
        raise ValueError("incident_id is required")

    logger.info(
        "Resolving incident: id=%s, effective=%s",
        incident_id,
        solution_effective,
    )

    mongodb_client = None

    try:
        mongodb_client = MongoDBClient()
        await mongodb_client.connect()

        vector_search = VectorSearch(
            mongodb_client,
            openai_api_key=settings.openai_api_key,
        )

        incident_tracker = IncidentTracker(mongodb_client)
        solution_builder = SolutionKnowledgeBuilder(
            mongodb_client,
            vector_search=vector_search,
        )

        incident = await incident_tracker.update_incident(
            incident_id=incident_id,
            solution_applied=solution_applied,
            solution_effective=solution_effective,
            solution_code=solution_code,
            solution_source=solution_source,
        )

        solution = None
        if solution_effective:
            try:
                solution = await solution_builder.create_solution_from_incident(incident)
                logger.info(
                    "Created solution knowledge: id=%s, pattern=%s",
                    solution.solution_id,
                    solution.problem_pattern[:50],
                )
            except Exception as e:
                logger.warning("Failed to create solution knowledge: %s", e)

        return {
            "incident": {
                "incident_id": incident.incident_id,
                "status": incident.status.value,
                "resolved_at": incident.resolved_at.isoformat() if incident.resolved_at else None,
                "resolution_time_minutes": incident.resolution_time_minutes,
            },
            "solution": {
                "solution_id": solution.solution_id,
                "problem_pattern": solution.problem_pattern,
                "success_rate": solution.success_rate,
            } if solution else None,
            "message": "Incident resolved and solution added to knowledge base" if solution else "Incident resolved",
        }

    except Exception as e:
        logger.error("Error in resolve_incident: %s", e, exc_info=True)
        raise
    finally:
        if mongodb_client:
            await mongodb_client.close()

