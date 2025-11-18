"""Security data client for fetching security information."""

import logging
from datetime import datetime, timedelta
from typing import Any

import httpx

from wistx_mcp.tools.lib.mongodb_client import MongoDBClient
from wistx_mcp.config import settings
from wistx_mcp.tools.lib.retry_utils import with_timeout_and_retry

logger = logging.getLogger(__name__)


class SecurityClient:
    """Client for fetching security data from various sources."""

    def __init__(self, mongodb_client: MongoDBClient):
        """Initialize security client.

        Args:
            mongodb_client: MongoDB client for caching
        """
        self.mongodb_client = mongodb_client
        self.cache_ttl_hours = 24
        self.http_client = httpx.AsyncClient(timeout=30.0)

    async def close(self) -> None:
        """Close HTTP client connection."""
        await self.http_client.aclose()

    async def search_cves(
        self,
        query: str,
        resource_type: str | None = None,
        severity: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Search CVE database.

        Args:
            query: Search query
            resource_type: Filter by resource type
            severity: Filter by severity (CRITICAL, HIGH, MEDIUM, LOW)
            limit: Maximum results

        Returns:
            List of CVE dictionaries
        """
        await self.mongodb_client.connect()

        if self.mongodb_client.database is None:
            logger.warning("MongoDB not connected, returning empty CVE results")
            return []

        collection = self.mongodb_client.database.security_knowledge

        cache_key = f"cve:{query}:{resource_type}:{severity}"
        cached_result = await collection.find_one(
            {"cache_key": cache_key, "cache_expires_at": {"$gt": datetime.utcnow()}}
        )

        if cached_result:
            logger.debug("Using cached CVE results for query: %s", query[:50])
            return cached_result.get("data", [])

        try:
            nvd_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
            params: dict[str, Any] = {
                "keywordSearch": query,
                "resultsPerPage": min(limit, 20),
            }

            if resource_type:
                params["keywordSearch"] = f"{query} {resource_type}"

            response = await with_timeout_and_retry(
                self.http_client.get,
                timeout_seconds=30.0,
                max_attempts=3,
                retryable_exceptions=(httpx.HTTPError, httpx.TimeoutException, httpx.NetworkError),
                url=nvd_url,
                params=params,
            )
            response.raise_for_status()

            nvd_data = response.json()
            cves = []

            for vuln in nvd_data.get("vulnerabilities", []):
                cve_item = vuln.get("cve", {})
                cve_id = cve_item.get("id", "")
                descriptions = cve_item.get("descriptions", [])
                description = descriptions[0].get("value", "") if descriptions else ""

                metrics = cve_item.get("metrics", {})
                cvss_v3 = metrics.get("cvssMetricV31", [{}])[0] if metrics.get("cvssMetricV31") else {}
                base_severity = cvss_v3.get("cvssData", {}).get("baseSeverity", "MEDIUM")

                if severity and base_severity.upper() != severity.upper():
                    continue

                cve_dict = {
                    "cve_id": cve_id,
                    "title": f"{cve_id}: {description[:100]}",
                    "description": description,
                    "severity": base_severity.upper(),
                    "resource_type": resource_type,
                    "source": "nvd",
                    "published_date": cve_item.get("published", ""),
                    "updated_date": cve_item.get("lastModified", ""),
                    "references": [ref.get("url", "") for ref in cve_item.get("references", [])],
                }

                cves.append(cve_dict)

            if cves:
                cache_expires = datetime.utcnow() + timedelta(hours=self.cache_ttl_hours)
                await collection.insert_one({
                    "cache_key": cache_key,
                    "data": cves,
                    "cached_at": datetime.utcnow(),
                    "cache_expires_at": cache_expires,
                })

            logger.info("Found %d CVEs for query: %s", len(cves), query[:50])
            return cves[:limit]

        except httpx.HTTPError as e:
            logger.warning("Failed to fetch CVEs from NVD API: %s", e)
            return []
        except Exception as e:
            logger.error("Error searching CVEs: %s", e, exc_info=True)
            return []

    async def search_advisories(
        self,
        query: str,
        cloud_provider: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Search security advisories.

        Args:
            query: Search query
            cloud_provider: Filter by cloud provider
            limit: Maximum results

        Returns:
            List of advisory dictionaries
        """
        await self.mongodb_client.connect()

        if self.mongodb_client.database is None:
            logger.warning("MongoDB not connected, returning empty advisory results")
            return []

        collection = self.mongodb_client.database.security_knowledge

        advisories = []

        if cloud_provider == "aws" or not cloud_provider:
            try:
                aws_advisories = await self._search_aws_advisories(query, limit)
                advisories.extend(aws_advisories)
            except Exception as e:
                logger.warning("Failed to search AWS advisories: %s", e)

        if cloud_provider == "gcp" or not cloud_provider:
            try:
                gcp_advisories = await self._search_gcp_advisories(query, limit)
                advisories.extend(gcp_advisories)
            except Exception as e:
                logger.warning("Failed to search GCP advisories: %s", e)

        if cloud_provider == "azure" or not cloud_provider:
            try:
                azure_advisories = await self._search_azure_advisories(query, limit)
                advisories.extend(azure_advisories)
            except Exception as e:
                logger.warning("Failed to search Azure advisories: %s", e)

        logger.info("Found %d advisories for query: %s", len(advisories), query[:50])
        return advisories[:limit]

    async def _search_aws_advisories(
        self,
        query: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        """Search AWS security advisories.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of AWS advisory dictionaries
        """
        await self.mongodb_client.connect()

        if self.mongodb_client.database is None:
            return []

        collection = self.mongodb_client.database.security_knowledge

        mongo_query: dict[str, Any] = {
            "source": "aws",
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
            ],
        }

        cursor = collection.find(mongo_query).sort("published_date", -1).limit(limit)
        results = await cursor.to_list(length=limit)

        if results:
            return results

        return []

    async def _search_gcp_advisories(
        self,
        query: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        """Search GCP security advisories.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of GCP advisory dictionaries
        """
        await self.mongodb_client.connect()

        if self.mongodb_client.database is None:
            return []

        collection = self.mongodb_client.database.security_knowledge

        mongo_query: dict[str, Any] = {
            "source": "gcp",
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
            ],
        }

        cursor = collection.find(mongo_query).sort("published_date", -1).limit(limit)
        results = await cursor.to_list(length=limit)

        if results:
            return results

        return []

    async def _search_azure_advisories(
        self,
        query: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        """Search Azure security advisories.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of Azure advisory dictionaries
        """
        await self.mongodb_client.connect()

        if self.mongodb_client.database is None:
            return []

        collection = self.mongodb_client.database.security_knowledge

        mongo_query: dict[str, Any] = {
            "source": "azure",
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
            ],
        }

        cursor = collection.find(mongo_query).sort("published_date", -1).limit(limit)
        results = await cursor.to_list(length=limit)

        if results:
            return results

        return []

    async def search_kubernetes_security(
        self,
        query: str,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Search Kubernetes security information.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of Kubernetes security items
        """
        await self.mongodb_client.connect()

        if self.mongodb_client.database is None:
            logger.warning("MongoDB not connected, returning empty K8s security results")
            return []

        collection = self.mongodb_client.database.security_knowledge

        mongo_query: dict[str, Any] = {
            "$or": [
                {"source": "kubernetes"},
                {"source": "cncf"},
                {"resource_type": {"$regex": "kubernetes|k8s|eks|gke|aks", "$options": "i"}},
            ],
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
            ],
        }

        cursor = collection.find(mongo_query).sort("published_date", -1).limit(limit)
        results = await cursor.to_list(length=limit)

        logger.info("Found %d Kubernetes security items for query: %s", len(results), query[:50])
        return results

