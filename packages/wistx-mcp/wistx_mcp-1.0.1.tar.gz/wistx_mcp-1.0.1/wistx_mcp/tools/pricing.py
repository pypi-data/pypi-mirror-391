"""Pricing tool - calculate infrastructure costs."""

from typing import Any

from wistx_mcp.tools.lib.mongodb_client import MongoDBClient


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
    client = MongoDBClient()
    try:
        await client.connect()

        total_monthly = 0.0
        breakdown = []

        for resource in resources:
            cloud = resource.get("cloud", "aws")
            service = resource.get("service", "")
            instance_type = resource.get("instance_type", "")
            quantity = resource.get("quantity", 1)

            pricing_data = await client.get_pricing(
                cloud=cloud,
                service=service,
                instance_type=instance_type,
            )

            if pricing_data:
                monthly_cost = pricing_data.get("monthly_cost", 0) * quantity
                total_monthly += monthly_cost

                breakdown.append({
                    "resource": f"{cloud}:{service}:{instance_type}",
                    "quantity": quantity,
                    "monthly": round(monthly_cost, 2),
                    "annual": round(monthly_cost * 12, 2),
                })

        optimizations = []
        if total_monthly > 100:
            optimizations.append("Consider Reserved Instances for 30-40% savings")
        if total_monthly > 500:
            optimizations.append("Review instance sizing - may be over-provisioned")

        return {
            "total_monthly": round(total_monthly, 2),
            "total_annual": round(total_monthly * 12, 2),
            "breakdown": breakdown,
            "optimizations": optimizations,
        }
    finally:
        await client.disconnect()

