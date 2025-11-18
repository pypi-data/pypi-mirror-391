"""Manage infrastructure tool - Kubernetes and multi-cloud lifecycle management."""

import logging
from typing import Any

from wistx_mcp.tools.lib.mongodb_client import MongoDBClient
from wistx_mcp.tools.lib.kubernetes_manager import KubernetesManager
from wistx_mcp.tools.lib.multi_cloud_manager import MultiCloudManager
from wistx_mcp.tools.lib.api_client import WISTXAPIClient
from wistx_mcp.config import settings

logger = logging.getLogger(__name__)

api_client = WISTXAPIClient()


async def manage_infrastructure(
    action: str,
    infrastructure_type: str,
    resource_name: str,
    cloud_provider: str | list[str] | None = None,
    configuration: dict[str, Any] | None = None,
    compliance_standards: list[str] | None = None,
    current_version: str | None = None,
    target_version: str | None = None,
    backup_type: str = "full",
) -> dict[str, Any]:
    """Manage infrastructure lifecycle (Kubernetes clusters, multi-cloud resources).

    Args:
        action: Action to perform (create, update, upgrade, backup, restore, monitor, optimize)
        infrastructure_type: Type of infrastructure (kubernetes, multi_cloud, hybrid_cloud)
        resource_name: Name of the resource/cluster
        cloud_provider: Cloud provider(s) - single string or list for multi-cloud
        configuration: Infrastructure configuration
            Example for Kubernetes: {
                "node_pools": [...],
                "addons": [...],
                "networking": {...},
                "security": {...}
            }
            Example for Multi-Cloud: {
                "resources": [
                    {"cloud": "aws", "type": "eks", "name": "cluster-1"},
                    {"cloud": "gcp", "type": "gke", "name": "cluster-2"}
                ],
                "integration": {...}
            }
        compliance_standards: Compliance standards to enforce
        current_version: Current version (for upgrade action)
        target_version: Target version (for upgrade action)
        backup_type: Type of backup (for backup action)

    Returns:
        Dictionary with infrastructure status:
        - resource_id: Resource identifier
        - status: Current status
        - endpoints: Access endpoints
        - compliance_status: Compliance status
        - cost_summary: Cost information
        - recommendations: Optimization recommendations

    Raises:
        ValueError: If invalid action or parameters
        Exception: If infrastructure management fails
    """
    valid_actions = ["create", "update", "upgrade", "backup", "restore", "monitor", "optimize"]
    if action not in valid_actions:
        raise ValueError(f"Invalid action: {action}. Must be one of {valid_actions}")

    valid_types = ["kubernetes", "multi_cloud", "hybrid_cloud"]
    if infrastructure_type not in valid_types:
        raise ValueError(f"Invalid infrastructure_type: {infrastructure_type}. Must be one of {valid_types}")

    logger.info(
        "Managing infrastructure: action=%s, type=%s, resource=%s, provider=%s",
        action,
        infrastructure_type,
        resource_name,
        cloud_provider,
    )

    mongodb_client = None

    try:
        mongodb_client = MongoDBClient()
        await mongodb_client.connect()

        k8s_manager = KubernetesManager()
        multi_cloud_manager = MultiCloudManager()

        if action == "create":
            if infrastructure_type == "kubernetes":
                if not cloud_provider:
                    raise ValueError("cloud_provider required for Kubernetes cluster creation")
                if isinstance(cloud_provider, list):
                    cloud_provider = cloud_provider[0]

                cluster_config = k8s_manager.create_cluster_config(
                    cluster_name=resource_name,
                    cloud_provider=cloud_provider,
                    configuration=configuration,
                )

                compliance_status = None
                if compliance_standards:
                    try:
                        compliance_results = await api_client.get_compliance_requirements(
                            resource_types=["EKS", "GKE", "AKS"],
                            standards=compliance_standards,
                        )
                        compliance_status = compliance_results.get("controls", [])
                    except Exception as e:
                        logger.warning("Failed to fetch compliance requirements: %s", e)

                return {
                    "action": "create",
                    "resource_id": f"{resource_name}-{cloud_provider}",
                    "status": "configuration_generated",
                    "endpoints": cluster_config.get("endpoints", {}),
                    "terraform_code": cluster_config.get("terraform_code", ""),
                    "next_steps": cluster_config.get("next_steps", []),
                    "compliance_status": compliance_status,
                }

            elif infrastructure_type in ["multi_cloud", "hybrid_cloud"]:
                if not cloud_provider:
                    raise ValueError("cloud_provider required for multi-cloud setup")
                if isinstance(cloud_provider, str):
                    cloud_provider = [cloud_provider]

                multi_cloud_config = multi_cloud_manager.create_multi_cloud_config(
                    resource_name=resource_name,
                    cloud_providers=cloud_provider,
                    configuration=configuration,
                )

                return {
                    "action": "create",
                    "resource_id": f"{resource_name}-multi-cloud",
                    "status": "configuration_generated",
                    "endpoints": multi_cloud_config.get("endpoints", {}),
                    "terraform_code": multi_cloud_config.get("terraform_code", ""),
                    "resources": multi_cloud_config.get("resources", []),
                    "integration_config": multi_cloud_config.get("integration_config", {}),
                    "next_steps": multi_cloud_config.get("next_steps", []),
                }

        elif action == "upgrade":
            if not current_version or not target_version:
                raise ValueError("current_version and target_version required for upgrade")

            upgrade_strategy = k8s_manager.generate_upgrade_strategy(
                current_version=current_version,
                target_version=target_version,
                strategy=configuration.get("strategy", "rolling") if configuration else "rolling",
            )

            return {
                "action": "upgrade",
                "resource_id": resource_name,
                "status": "upgrade_plan_generated",
                "strategy": upgrade_strategy.get("strategy"),
                "steps": upgrade_strategy.get("steps", []),
                "rollback_plan": upgrade_strategy.get("rollback_plan", []),
                "estimated_downtime": upgrade_strategy.get("estimated_downtime", ""),
            }

        elif action == "backup":
            backup_plan = k8s_manager.generate_backup_plan(
                cluster_name=resource_name,
                backup_type=backup_type,
            )

            return {
                "action": "backup",
                "resource_id": resource_name,
                "status": "backup_plan_generated",
                "backup_commands": backup_plan.get("backup_commands", []),
                "restore_commands": backup_plan.get("restore_commands", []),
                "retention_policy": backup_plan.get("retention_policy", ""),
            }

        elif action == "monitor":
            if infrastructure_type == "kubernetes":
                monitoring_config = k8s_manager.generate_monitoring_config(
                    cluster_name=resource_name,
                )
            else:
                if isinstance(cloud_provider, str):
                    cloud_provider = [cloud_provider]
                elif not cloud_provider:
                    cloud_provider = ["aws", "gcp", "azure"]

                monitoring_config = multi_cloud_manager.generate_unified_monitoring(
                    cloud_providers=cloud_provider,
                )

            return {
                "action": "monitor",
                "resource_id": resource_name,
                "status": "monitoring_config_generated",
                "metrics": monitoring_config.get("metrics", []),
                "alerts": monitoring_config.get("alerts", []),
                "dashboards": monitoring_config.get("dashboards", []),
            }

        elif action == "optimize":
            if infrastructure_type in ["multi_cloud", "hybrid_cloud"]:
                if not configuration or "resources" not in configuration:
                    raise ValueError("configuration with resources required for optimization")

                optimization = multi_cloud_manager.generate_cost_optimization(
                    resources=configuration.get("resources", []),
                )

                return {
                    "action": "optimize",
                    "resource_id": resource_name,
                    "status": "optimization_recommendations_generated",
                    "recommendations": optimization.get("recommendations", []),
                    "estimated_savings": optimization.get("estimated_savings", ""),
                    "migration_plan": optimization.get("migration_plan", []),
                }
            else:
                return {
                    "action": "optimize",
                    "resource_id": resource_name,
                    "status": "optimization_recommendations_generated",
                    "recommendations": [
                        "Review resource utilization",
                        "Right-size instances",
                        "Implement auto-scaling",
                        "Use spot instances for non-critical workloads",
                    ],
                }

        else:
            return {
                "action": action,
                "resource_id": resource_name,
                "status": f"{action}_not_implemented",
                "message": f"Action {action} is not yet fully implemented",
            }

    except Exception as e:
        logger.error("Error in manage_infrastructure: %s", e, exc_info=True)
        raise
    finally:
        if mongodb_client:
            await mongodb_client.disconnect()

