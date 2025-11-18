"""Compliance service - business logic for compliance operations."""

import logging
import time

from api.models.v1_requests import ComplianceRequirementsRequest
from api.models.v1_responses import (
    ComplianceControlResponse,
    ComplianceRequirementsResponse,
    ComplianceRequirementsSummary,
)
from api.database.async_mongodb import async_mongodb_adapter
from wistx_mcp.tools.lib.vector_search import VectorSearch
from wistx_mcp.tools.lib.mongodb_client import MongoDBClient
from wistx_mcp.tools.lib.retry_utils import with_timeout_and_retry
from api.config import settings

logger = logging.getLogger(__name__)


class ComplianceService:
    """Service for compliance operations."""

    def __init__(self):
        """Initialize compliance service."""
        self.mongodb_adapter = async_mongodb_adapter
        mcp_mongodb_client = MongoDBClient()
        self.vector_search = VectorSearch(
            mcp_mongodb_client,
            openai_api_key=settings.openai_api_key,
        )

    async def get_compliance_requirements(
        self, request: ComplianceRequirementsRequest
    ) -> ComplianceRequirementsResponse:
        """Get compliance requirements for infrastructure resources.

        Args:
            request: Compliance requirements request

        Returns:
            Compliance requirements response with controls and summary

        Raises:
            RuntimeError: If operation times out or fails
            ValueError: If request is invalid
        """
        start_time = time.time()

        if not request.resource_types:
            raise ValueError("At least one resource type is required")

        if request.standards:
            valid_standards = {
                "PCI-DSS", "HIPAA", "CIS", "SOC2", "NIST-800-53",
                "ISO-27001", "GDPR", "FedRAMP", "CCPA", "SOX", "GLBA",
            }
            invalid_standards = [s for s in request.standards if s not in valid_standards]
            if invalid_standards:
                logger.error("Invalid standards requested: %s. Valid standards: %s", invalid_standards, sorted(valid_standards))
                raise ValueError(f"Invalid standards: {invalid_standards}. Valid standards: {sorted(valid_standards)}")

        await self.mongodb_adapter.connect()

        query_parts = []
        for resource_type in request.resource_types:
            if not resource_type or not resource_type.strip():
                logger.warning("Empty resource type in request, skipping")
                continue
            query_parts.append(f"{resource_type.strip()} compliance")
        if request.standards:
            query_parts.extend([s.strip() for s in request.standards if s.strip()])

        if not query_parts:
            raise ValueError("No valid query parts generated from request")

        query = " ".join(query_parts)

        limit = getattr(request, "limit", None) or getattr(settings, "compliance_query_limit", 100)
        limit = min(max(limit, 1), 1000)

        try:
            results = await with_timeout_and_retry(
                self.vector_search.search_compliance,
                timeout_seconds=30.0,
                max_attempts=3,
                retryable_exceptions=(RuntimeError, ConnectionError, TimeoutError),
                query=query,
                standards=request.standards if request.standards else None,
                severity=request.severity,
                limit=limit,
            )
        except (RuntimeError, ConnectionError, TimeoutError) as e:
            logger.error("Vector search failed: %s", e, exc_info=True)
            raise RuntimeError(f"Search operation failed: {e}") from e

        if not results:
            logger.info("No compliance controls found for query: %s", query[:100])

        controls = []
        failed_count = 0
        for result in results:
            if not isinstance(result, dict):
                logger.warning("Invalid result type: %s", type(result))
                failed_count += 1
                continue

            try:
                control_id = result.get("control_id") or ""
                standard = result.get("standard") or ""
                title = result.get("title") or ""
                description = result.get("description") or ""

                if not control_id or not standard:
                    logger.warning("Missing required fields in result: control_id=%s, standard=%s", control_id, standard)
                    failed_count += 1
                    continue

                control = ComplianceControlResponse(
                    control_id=control_id,
                    standard=standard,
                    title=title,
                    description=description,
                    severity=result.get("severity", "MEDIUM"),
                    category=result.get("category"),
                    subcategory=result.get("subcategory"),
                    applies_to=result.get("applies_to", []) if isinstance(result.get("applies_to"), list) else [],
                    remediation=result.get("remediation") if request.include_remediation else None,
                    verification=result.get("verification") if request.include_verification else None,
                    references=result.get("references", []) if isinstance(result.get("references"), list) else [],
                    source_url=result.get("source_url"),
                )
                controls.append(control)
            except (ValueError, TypeError, KeyError, AttributeError) as e:
                logger.warning("Failed to create control response: %s", e, exc_info=True)
                failed_count += 1
                continue

        if failed_count > 0:
            failure_rate = failed_count / len(results) if results else 0.0
            logger.warning("Failed to process %d out of %d results (%.1f%% failure rate)", 
                          failed_count, len(results), failure_rate * 100)
            
            if failure_rate > 0.5:
                logger.error("High failure rate detected: %.1f%% (threshold: 50%%)", failure_rate * 100)

        by_severity: dict[str, int] = {}
        by_standard: dict[str, int] = {}

        for control in controls:
            by_severity[control.severity] = by_severity.get(control.severity, 0) + 1
            by_standard[control.standard] = by_standard.get(control.standard, 0) + 1

        summary = ComplianceRequirementsSummary(
            total=len(controls),
            by_severity=by_severity,
            by_standard=by_standard,
        )

        query_time_ms = int((time.time() - start_time) * 1000)

        return ComplianceRequirementsResponse(
            controls=controls,
            summary=summary,
            metadata={
                "query_time_ms": query_time_ms,
                "sources": list(set(control.source_url for control in controls if control.source_url)),
            },
        )
