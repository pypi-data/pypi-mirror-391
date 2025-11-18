"""Manage integration tool - analyze, generate, and validate integrations."""

import logging
from typing import Any

from wistx_mcp.tools.lib.mongodb_client import MongoDBClient
from wistx_mcp.tools.lib.integration_analyzer import IntegrationAnalyzer
from wistx_mcp.tools.lib.integration_generator import IntegrationGenerator
from wistx_mcp.tools.lib.api_client import WISTXAPIClient
from wistx_mcp.config import settings

logger = logging.getLogger(__name__)

api_client = WISTXAPIClient()


async def manage_integration(
    action: str,
    infrastructure_code: str | None = None,
    components: list[dict[str, Any]] | None = None,
    integration_type: str | None = None,
    cloud_provider: str | None = None,
    compliance_standards: list[str] | None = None,
    pattern_name: str | None = None,
) -> dict[str, Any]:
    """Manage infrastructure component integration.

    Args:
        action: Action to perform (analyze, generate, validate)
        infrastructure_code: Infrastructure code to analyze (for analyze action)
        components: List of components to integrate (for generate action)
            Example: [
                {"type": "ec2", "id": "web-server"},
                {"type": "rds", "id": "database"},
                {"type": "alb", "id": "load-balancer"}
            ]
        integration_type: Type of integration (networking, security, monitoring, service)
        cloud_provider: Cloud provider (aws, gcp, azure)
        compliance_standards: Compliance standards to consider
        pattern_name: Specific integration pattern to use (optional)

    Returns:
        Dictionary with integration results:
        - For analyze: missing_connections, dependency_issues, recommendations
        - For generate: integration_code, dependencies, security_rules, monitoring
        - For validate: validation_results, issues, fixes

    Raises:
        ValueError: If invalid action or parameters
        Exception: If integration management fails
    """
    valid_actions = ["analyze", "generate", "validate"]
    if action not in valid_actions:
        raise ValueError(f"Invalid action: {action}. Must be one of {valid_actions}")

    logger.info(
        "Managing integration: action=%s, type=%s, provider=%s",
        action,
        integration_type,
        cloud_provider,
    )

    mongodb_client = None

    try:
        mongodb_client = MongoDBClient()
        await mongodb_client.connect()

        analyzer = IntegrationAnalyzer()
        generator = IntegrationGenerator()

        if action == "analyze":
            if not infrastructure_code:
                raise ValueError("infrastructure_code required for analyze action")

            analysis = analyzer.analyze(
                infrastructure_code=infrastructure_code,
                cloud_provider=cloud_provider,
            )

            if compliance_standards:
                try:
                    from wistx_mcp.tools.lib.retry_utils import with_timeout_and_retry
                    
                    resource_types = _extract_resource_types(infrastructure_code)
                    compliance_results = await with_timeout_and_retry(
                        api_client.get_compliance_requirements,
                        timeout_seconds=30.0,
                        max_attempts=3,
                        retryable_exceptions=(RuntimeError, ConnectionError, TimeoutError),
                        resource_types=resource_types,
                        standards=compliance_standards,
                    )
                    analysis["compliance_status"] = compliance_results.get("controls", [])
                except (RuntimeError, ConnectionError, TimeoutError) as e:
                    logger.warning("Failed to fetch compliance requirements: %s", e)

            return {
                "action": "analyze",
                "missing_connections": analysis.get("missing_connections", []),
                "dependency_issues": analysis.get("dependency_issues", []),
                "security_gaps": analysis.get("security_gaps", []),
                "recommendations": analysis.get("recommendations", []),
                "compliance_status": analysis.get("compliance_status"),
            }

        elif action == "generate":
            if not components:
                raise ValueError("components required for generate action")
            if not integration_type:
                raise ValueError("integration_type required for generate action")
            if not cloud_provider:
                raise ValueError("cloud_provider required for generate action")

            generated = generator.generate(
                components=components,
                integration_type=integration_type,
                cloud_provider=cloud_provider,
                pattern_name=pattern_name,
            )

            return {
                "action": "generate",
                "integration_code": generated.get("integration_code", ""),
                "dependencies": generated.get("dependencies", []),
                "security_rules": generated.get("security_rules", []),
                "monitoring": generated.get("monitoring", {}),
                "pattern_used": generated.get("pattern_used", ""),
                "description": generated.get("description", ""),
            }

        elif action == "validate":
            if not components:
                raise ValueError("components required for validate action")
            if not integration_type:
                raise ValueError("integration_type required for validate action")

            validation = analyzer.validate_integration(
                components=components,
                integration_type=integration_type,
            )

            return {
                "action": "validate",
                "valid": validation.get("valid", False),
                "issues": validation.get("issues", []),
                "fixes": validation.get("fixes", []),
            }

        else:
            raise ValueError(f"Unknown action: {action}")

    except Exception as e:
        logger.error("Error in manage_integration: %s", e, exc_info=True)
        raise
    finally:
        if mongodb_client:
            await mongodb_client.disconnect()


def _extract_resource_types(infrastructure_code: str) -> list[str]:
    """Extract resource types from infrastructure code.

    Args:
        infrastructure_code: Infrastructure code

    Returns:
        List of resource types
    """
    resource_types = []

    aws_resources = [
        ("aws_instance", "EC2"),
        ("aws_rds_instance", "RDS"),
        ("aws_s3_bucket", "S3"),
        ("aws_lambda_function", "Lambda"),
        ("aws_eks_cluster", "EKS"),
        ("aws_ecs_service", "ECS"),
    ]

    for pattern, resource_type in aws_resources:
        if pattern in infrastructure_code:
            resource_types.append(resource_type)

    if "kubernetes" in infrastructure_code.lower() or "kind:" in infrastructure_code.lower():
        resource_types.append("EKS")
        resource_types.append("GKE")
        resource_types.append("AKS")

    return resource_types if resource_types else ["EC2"]

