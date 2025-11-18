"""Vector search using Pinecone and MongoDB."""

import logging
from typing import Any

from openai import AsyncOpenAI
from pinecone import Pinecone

from wistx_mcp.config import settings
from wistx_mcp.tools.lib.mongodb_client import MongoDBClient

logger = logging.getLogger(__name__)


class VectorSearch:
    """Vector search using Pinecone for semantic search."""

    def __init__(self, mongodb_client: MongoDBClient, openai_api_key: str | None = None):
        """Initialize vector search.

        Args:
            mongodb_client: MongoDB client instance
            openai_api_key: OpenAI API key for embeddings
        """
        self.mongodb_client = mongodb_client
        self.openai_api_key = openai_api_key or settings.openai_api_key

        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required for vector search")

        if not settings.pinecone_api_key:
            raise ValueError("Pinecone API key is required for vector search. Set PINECONE_API_KEY environment variable.")

        self.embedding_client = AsyncOpenAI(api_key=self.openai_api_key)

        pc = Pinecone(api_key=settings.pinecone_api_key)
        self.index = pc.Index(settings.pinecone_index_name)

    async def _get_query_embedding(self, query: str) -> list[float]:
        """Get embedding for query string.

        Args:
            query: Query string

        Returns:
            Embedding vector

        Raises:
            RuntimeError: If embedding generation fails
            ValueError: If query is empty or invalid
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        try:
            response = await self.embedding_client.embeddings.create(
                model="text-embedding-3-small",
                input=query,
            )
            if not response.data or len(response.data) == 0:
                raise RuntimeError("Empty embedding response from OpenAI")
            return response.data[0].embedding
        except Exception as e:
            logger.error("Failed to generate embedding for query: %s", e, exc_info=True)
            raise RuntimeError(f"Failed to generate embedding: {e}") from e

    async def search_compliance(
        self,
        query: str,
        standards: list[str] | None = None,
        severity: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Search compliance controls using Pinecone vector search.

        Args:
            query: Search query
            standards: Filter by compliance standards
            severity: Filter by severity level
            limit: Maximum number of results

        Returns:
            List of compliance controls with full document data

        Raises:
            RuntimeError: If search operation fails
            ValueError: If query is invalid
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        if limit <= 0 or limit > 1000:
            raise ValueError("Limit must be between 1 and 1000")

        try:
            query_embedding = await self._get_query_embedding(query)
        except (RuntimeError, ValueError) as e:
            logger.error("Failed to generate embedding: %s", e)
            raise

        filter_dict: dict[str, Any] = {"collection": "compliance_controls"}

        if standards:
            if not isinstance(standards, list):
                raise ValueError("Standards must be a list")
            filter_dict["standard"] = {"$in": standards}

        if severity:
            if severity not in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
                raise ValueError(f"Invalid severity: {severity}")
            filter_dict["severity"] = severity

        try:
            query_response = self.index.query(
                vector=query_embedding,
                filter=filter_dict if filter_dict else None,
                top_k=limit,
                include_metadata=True,
            )
        except Exception as e:
            logger.error("Pinecone query failed: %s", e, exc_info=True)
            raise RuntimeError(f"Pinecone query failed: {e}") from e

        if not query_response or not hasattr(query_response, "matches"):
            logger.warning("Invalid Pinecone response structure")
            return []

        control_ids = []
        for match in query_response.matches:
            if match.metadata and match.metadata.get("control_id"):
                control_ids.append(match.metadata["control_id"])

        if not control_ids:
            logger.info("No control IDs found in Pinecone results for query: %s", query[:50])
            return []

        try:
            await self.mongodb_client.connect()

            if self.mongodb_client.database is None:
                logger.error("MongoDB database is None after connection")
                raise RuntimeError("MongoDB database connection failed")

            collection = self.mongodb_client.database.compliance_controls
            cursor = collection.find({"control_id": {"$in": control_ids}})
            results = await cursor.to_list(length=len(control_ids))

            if len(results) != len(control_ids):
                logger.warning(
                    "Mismatch between Pinecone results (%d) and MongoDB results (%d)",
                    len(control_ids),
                    len(results),
                )

            score_map = {
                match.metadata["control_id"]: match.score
                for match in query_response.matches
                if match.metadata and match.metadata.get("control_id")
            }
            results.sort(key=lambda x: score_map.get(x.get("control_id", ""), 0), reverse=True)

            return results
        except Exception as e:
            logger.error("MongoDB query failed: %s", e, exc_info=True)
            raise RuntimeError(f"MongoDB query failed: {e}") from e

    async def search_knowledge_articles(
        self,
        query: str,
        domains: list[str] | None = None,
        content_types: list[str] | None = None,
        user_id: str | None = None,
        organization_id: str | None = None,
        include_global: bool = True,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Search knowledge articles using Pinecone vector search with multi-tenancy support.

        Args:
            query: Search query
            domains: Filter by domains
            content_types: Filter by content types
            user_id: User ID for user-specific content
            organization_id: Organization ID for org-shared content
            include_global: Include global/shared content in results
            limit: Maximum number of results

        Returns:
            List of knowledge articles with full document data
        """
        query_embedding = await self._get_query_embedding(query)

        filter_dict: dict[str, Any] = {"collection": "knowledge_articles"}

        if domains:
            filter_dict["domain"] = {"$in": domains}

        if content_types:
            filter_dict["content_type"] = {"$in": content_types}

        visibility_filters = []
        if include_global:
            visibility_filters.append("global")
        if user_id:
            visibility_filters.append("user")
            if not include_global:
                filter_dict["user_id"] = user_id
        if organization_id:
            visibility_filters.append("organization")
            if not include_global and not user_id:
                filter_dict["organization_id"] = organization_id

        if visibility_filters:
            filter_dict["visibility"] = {"$in": visibility_filters}

        query_response = self.index.query(
            vector=query_embedding,
            filter=filter_dict if filter_dict else None,
            top_k=limit,
            include_metadata=True,
        )

        article_ids = [
            match.metadata["article_id"]
            for match in query_response.matches
            if match.metadata.get("article_id")
        ]

        if not article_ids:
            return []

        await self.mongodb_client.connect()

        if self.mongodb_client.database is None:
            return []

        collection = self.mongodb_client.database.knowledge_articles

        mongo_filter: dict[str, Any] = {"article_id": {"$in": article_ids}}

        visibility_query = []
        if include_global:
            visibility_query.append({"visibility": "global", "user_id": None})
        if user_id:
            visibility_query.append({"visibility": "user", "user_id": user_id})
        if organization_id:
            visibility_query.append({"visibility": "organization", "organization_id": organization_id})

        if visibility_query:
            if len(visibility_query) > 1:
                mongo_filter["$or"] = visibility_query
            else:
                mongo_filter.update(visibility_query[0])

        cursor = collection.find(mongo_filter)
        results = await cursor.to_list(length=len(article_ids))

        score_map = {
            match.metadata["article_id"]: match.score for match in query_response.matches
        }
        results.sort(key=lambda x: score_map.get(x["article_id"], 0), reverse=True)

        return results

