"""Quota enforcement service for plan limits."""

import logging
from datetime import datetime, timedelta
from typing import Any, Optional

from bson import ObjectId
from fastapi import HTTPException, status

from api.database.mongodb import mongodb_manager
from api.models.billing import PlanLimits
from api.services.plan_service import plan_service
from api.services.usage_aggregator import usage_aggregator

logger = logging.getLogger(__name__)


class QuotaExceededError(Exception):
    """Exception raised when quota is exceeded."""

    def __init__(self, message: str, limit_type: str, current: int | float, limit: int | float):
        super().__init__(message)
        self.limit_type = limit_type
        self.current = current
        self.limit = limit


class QuotaService:
    """Service for enforcing plan-based quotas."""

    async def check_query_quota(self, user_id: str, plan: str) -> None:
        """Check if user can make a query (within monthly limit).

        Args:
            user_id: User ID
            plan: User's plan ID

        Raises:
            QuotaExceededError: If quota is exceeded
            HTTPException: If plan not found
        """
        plan_limits = plan_service.get_plan_limits(plan)
        if not plan_limits:
            logger.warning("Plan not found: %s, defaulting to free plan", plan)
            plan_limits = plan_service.get_plan_limits("free")
            if not plan_limits:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Plan configuration error",
                )

        if plan_limits.queries_per_month == -1:
            return

        now = datetime.utcnow()
        start_of_month = datetime(now.year, now.month, 1)
        end_of_month = start_of_month + timedelta(days=32)
        end_of_month = end_of_month.replace(day=1) - timedelta(seconds=1)

        usage = await usage_aggregator.aggregate_user_usage(user_id, start_of_month, end_of_month)
        current_queries = usage.get("total_queries", 0)

        if current_queries >= plan_limits.queries_per_month:
            raise QuotaExceededError(
                f"Query quota exceeded. Current: {current_queries}, Limit: {plan_limits.queries_per_month}",
                "queries_per_month",
                current_queries,
                plan_limits.queries_per_month,
            )

    async def check_indexing_quota(
        self,
        user_id: str,
        plan: str,
        estimated_storage_mb: float = 0.0,
    ) -> None:
        """Check if user can index a resource.

        Args:
            user_id: User ID
            plan: User's plan ID
            estimated_storage_mb: Estimated storage in MB for this operation

        Raises:
            QuotaExceededError: If quota is exceeded
            HTTPException: If plan not found
        """
        plan_limits = plan_service.get_plan_limits(plan)
        if not plan_limits:
            logger.warning("Plan not found: %s, defaulting to free plan", plan)
            plan_limits = plan_service.get_plan_limits("free")
            if not plan_limits:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Plan configuration error",
                )

        plan_features = plan_service.get_plan_features(plan)
        if not plan_features:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Plan features not found",
            )

        if not plan_features.repository_indexing and not plan_features.document_indexing:
            raise QuotaExceededError(
                "Indexing not available on your plan. Please upgrade to a plan that supports indexing.",
                "indexing_feature",
                0,
                0,
            )

        now = datetime.utcnow()
        start_of_month = datetime(now.year, now.month, 1)
        end_of_month = start_of_month + timedelta(days=32)
        end_of_month = end_of_month.replace(day=1) - timedelta(seconds=1)

        usage = await usage_aggregator.aggregate_user_usage(user_id, start_of_month, end_of_month)
        current_indexes = usage.get("total_indexes", 0)
        current_storage_mb = usage.get("total_storage_mb", 0.0)

        if plan_limits.indexes_per_month != -1 and current_indexes >= plan_limits.indexes_per_month:
            raise QuotaExceededError(
                f"Indexing quota exceeded. Current: {current_indexes}, Limit: {plan_limits.indexes_per_month}",
                "indexes_per_month",
                current_indexes,
                plan_limits.indexes_per_month,
            )

        if plan_limits.storage_mb != -1:
            new_storage = current_storage_mb + estimated_storage_mb
            if new_storage > plan_limits.storage_mb:
                raise QuotaExceededError(
                    f"Storage quota exceeded. Current: {current_storage_mb:.2f} MB, "
                    f"Requested: {estimated_storage_mb:.2f} MB, Limit: {plan_limits.storage_mb} MB",
                    "storage_mb",
                    new_storage,
                    plan_limits.storage_mb,
                )

    async def get_storage_usage(self, user_id: str) -> dict[str, Any]:
        """Get current storage usage for user.

        Args:
            user_id: User ID

        Returns:
            Dictionary with storage usage details
        """
        db = mongodb_manager.get_database()

        now = datetime.utcnow()
        start_of_month = datetime(now.year, now.month, 1)
        end_of_month = start_of_month + timedelta(days=32)
        end_of_month = end_of_month.replace(day=1) - timedelta(seconds=1)

        usage = await usage_aggregator.aggregate_user_usage(user_id, start_of_month, end_of_month)

        knowledge_articles_count = db.knowledge_articles.count_documents(
            {"user_id": ObjectId(user_id)}
        )

        indexed_resources_count = 0
        if "indexed_resources" in db.list_collection_names():
            indexed_resources_count = db.indexed_resources.count_documents(
                {"user_id": ObjectId(user_id), "status": {"$ne": "deleted"}}
            )

        return {
            "storage_mb": usage.get("total_storage_mb", 0.0),
            "knowledge_articles": knowledge_articles_count,
            "indexed_resources": indexed_resources_count,
            "total_indexes": usage.get("total_indexes", 0),
            "period": {
                "start": start_of_month.isoformat(),
                "end": end_of_month.isoformat(),
            },
        }

    async def get_quota_status(self, user_id: str, plan: str) -> dict[str, Any]:
        """Get current quota status for user.

        Args:
            user_id: User ID
            plan: User's plan ID

        Returns:
            Dictionary with quota status
        """
        plan_limits = plan_service.get_plan_limits(plan)
        if not plan_limits:
            plan_limits = plan_service.get_plan_limits("free")
            if not plan_limits:
                return {
                    "error": "Plan configuration error",
                }

        now = datetime.utcnow()
        start_of_month = datetime(now.year, now.month, 1)
        end_of_month = start_of_month + timedelta(days=32)
        end_of_month = end_of_month.replace(day=1) - timedelta(seconds=1)

        usage = await usage_aggregator.aggregate_user_usage(user_id, start_of_month, end_of_month)
        storage_usage = await self.get_storage_usage(user_id)

        return {
            "plan": plan,
            "period": {
                "start": start_of_month.isoformat(),
                "end": end_of_month.isoformat(),
            },
            "queries": {
                "used": usage.get("total_queries", 0),
                "limit": plan_limits.queries_per_month,
                "unlimited": plan_limits.queries_per_month == -1,
            },
            "indexes": {
                "used": usage.get("total_indexes", 0),
                "limit": plan_limits.indexes_per_month,
                "unlimited": plan_limits.indexes_per_month == -1,
            },
            "storage": {
                "used_mb": storage_usage.get("storage_mb", 0.0),
                "limit_mb": plan_limits.storage_mb,
                "unlimited": plan_limits.storage_mb == -1,
            },
        }


quota_service = QuotaService()

