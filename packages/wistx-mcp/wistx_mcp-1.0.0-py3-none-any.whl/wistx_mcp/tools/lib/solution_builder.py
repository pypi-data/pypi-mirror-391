"""Solution knowledge builder from resolved incidents."""

import logging
import re
import uuid
from datetime import datetime
from typing import Any

from wistx_mcp.models.incident import Incident, IncidentSeverity, SolutionKnowledge
from wistx_mcp.tools.lib.mongodb_client import MongoDBClient
from wistx_mcp.tools.lib.vector_search import VectorSearch

logger = logging.getLogger(__name__)


class SolutionKnowledgeBuilder:
    """Builds solution knowledge base from resolved incidents."""

    def __init__(
        self,
        mongodb_client: MongoDBClient,
        vector_search: VectorSearch | None = None,
    ):
        """Initialize solution knowledge builder.

        Args:
            mongodb_client: MongoDB client instance
            vector_search: Vector search instance (optional, for embeddings)
        """
        self.mongodb_client = mongodb_client
        self.vector_search = vector_search
        self.collection_name = "solution_knowledge"

    async def create_solution_from_incident(
        self,
        incident: Incident,
    ) -> SolutionKnowledge:
        """Create solution knowledge article from resolved incident.

        Args:
            incident: Resolved incident

        Returns:
            SolutionKnowledge instance

        Raises:
            ValueError: If incident not resolved or solution not effective
        """
        if incident.status.value != "resolved":
            raise ValueError("Incident must be resolved to create solution knowledge")

        if not incident.solution_effective:
            raise ValueError("Solution must be effective to create knowledge article")

        if not incident.solution_applied:
            raise ValueError("Solution must be provided")

        problem_pattern = self._extract_problem_pattern(
            incident.issue_description,
            incident.error_messages,
        )

        solution_id = f"solution-{uuid.uuid4().hex[:12]}"

        solution_steps = []
        if incident.solution_code:
            solution_steps.append("Apply the provided solution code")
        if incident.solution_applied:
            solution_steps.append(incident.solution_applied)

        solution = SolutionKnowledge(
            solution_id=solution_id,
            problem_summary=incident.issue_description[:500],
            problem_pattern=problem_pattern,
            infrastructure_type=incident.infrastructure_type,
            cloud_provider=incident.cloud_provider,
            resource_type=incident.resource_type,
            solution_description=incident.solution_applied,
            solution_code=incident.solution_code,
            solution_steps=solution_steps,
            root_cause=incident.root_cause or "Unknown",
            prevention_strategies=incident.prevention_strategies,
            tags=self._extract_tags(incident),
            severity=incident.severity,
            source_incidents=[incident.incident_id],
            success_count=1,
            failure_count=0,
            success_rate=1.0,
            quality_score=self._calculate_quality_score(incident),
            verified=False,
        )

        if self.vector_search:
            try:
                searchable_text = self._create_searchable_text(solution)
                embedding = await self.vector_search._get_query_embedding(searchable_text)
                solution.embedding = embedding
            except Exception as e:
                logger.warning("Failed to generate embedding for solution: %s", e)

        await self._save_solution(solution)

        logger.info(
            "Created solution knowledge: id=%s, pattern=%s",
            solution_id,
            problem_pattern[:50],
        )

        return solution

    async def update_solution_success_rate(
        self,
        solution_id: str,
        successful: bool,
    ) -> SolutionKnowledge:
        """Update solution success rate.

        Args:
            solution_id: Solution identifier
            successful: Whether solution was successful

        Returns:
            Updated SolutionKnowledge instance

        Raises:
            ValueError: If solution not found
        """
        solution = await self._get_solution(solution_id)
        if not solution:
            raise ValueError(f"Solution not found: {solution_id}")

        if successful:
            solution.success_count += 1
        else:
            solution.failure_count += 1

        total = solution.success_count + solution.failure_count
        solution.success_rate = solution.success_count / total if total > 0 else 0.0

        solution.last_used_at = datetime.utcnow()
        solution.updated_at = datetime.utcnow()

        await self._save_solution(solution)

        logger.info(
            "Updated solution success rate: id=%s, success_rate=%.2f",
            solution_id,
            solution.success_rate,
        )

        return solution

    async def search_solutions(
        self,
        query: str,
        infrastructure_type: str | None = None,
        cloud_provider: str | None = None,
        limit: int = 10,
    ) -> list[SolutionKnowledge]:
        """Search solution knowledge base.

        Args:
            query: Search query
            infrastructure_type: Filter by infrastructure type
            cloud_provider: Filter by cloud provider
            limit: Maximum number of results

        Returns:
            List of SolutionKnowledge instances
        """
        if self.vector_search and self.vector_search.openai_api_key:
            return await self._vector_search_solutions(
                query=query,
                infrastructure_type=infrastructure_type,
                cloud_provider=cloud_provider,
                limit=limit,
            )

        return await self._text_search_solutions(
            query=query,
            infrastructure_type=infrastructure_type,
            cloud_provider=cloud_provider,
            limit=limit,
        )

    async def get_solution_by_pattern(
        self,
        problem_pattern: str,
    ) -> SolutionKnowledge | None:
        """Get solution by problem pattern.

        Args:
            problem_pattern: Normalized problem pattern

        Returns:
            SolutionKnowledge instance or None
        """
        db = await self.mongodb_client.get_database()
        collection = db[self.collection_name]

        doc = await collection.find_one({"problem_pattern": problem_pattern})
        if not doc:
            return None

        doc.pop("_id", None)
        try:
            return SolutionKnowledge(**doc)
        except Exception as e:
            logger.warning("Failed to parse solution %s: %s", doc.get("solution_id"), e)
            return None

    async def _vector_search_solutions(
        self,
        query: str,
        infrastructure_type: str | None = None,
        cloud_provider: str | None = None,
        limit: int = 10,
    ) -> list[SolutionKnowledge]:
        """Search solutions using vector search.

        Args:
            query: Search query
            infrastructure_type: Filter by infrastructure type
            cloud_provider: Filter by cloud provider
            limit: Maximum number of results

        Returns:
            List of SolutionKnowledge instances
        """
        db = await self.mongodb_client.get_database()
        collection = db[self.collection_name]

        searchable_text = query
        if infrastructure_type:
            searchable_text += f" {infrastructure_type}"
        if cloud_provider:
            searchable_text += f" {cloud_provider}"

        embedding = await self.vector_search._get_query_embedding(searchable_text)

        filter_dict: dict[str, Any] = {}
        if infrastructure_type:
            filter_dict["infrastructure_type"] = infrastructure_type
        if cloud_provider:
            filter_dict["cloud_provider"] = cloud_provider

        cursor = collection.find(filter_dict).sort("success_rate", -1).limit(limit)

        solutions = []
        async for doc in cursor:
            doc.pop("_id", None)
            try:
                solution = SolutionKnowledge(**doc)
                solutions.append(solution)
            except Exception as e:
                logger.warning("Failed to parse solution %s: %s", doc.get("solution_id"), e)

        return solutions

    async def _text_search_solutions(
        self,
        query: str,
        infrastructure_type: str | None = None,
        cloud_provider: str | None = None,
        limit: int = 10,
    ) -> list[SolutionKnowledge]:
        """Search solutions using text search.

        Args:
            query: Search query
            infrastructure_type: Filter by infrastructure type
            cloud_provider: Filter by cloud provider
            limit: Maximum number of results

        Returns:
            List of SolutionKnowledge instances
        """
        db = await self.mongodb_client.get_database()
        collection = db[self.collection_name]

        search_filter: dict[str, Any] = {"$text": {"$search": query}}

        if infrastructure_type:
            search_filter["infrastructure_type"] = infrastructure_type
        if cloud_provider:
            search_filter["cloud_provider"] = cloud_provider

        cursor = collection.find(search_filter).sort("success_rate", -1).limit(limit)

        solutions = []
        async for doc in cursor:
            doc.pop("_id", None)
            try:
                solution = SolutionKnowledge(**doc)
                solutions.append(solution)
            except Exception as e:
                logger.warning("Failed to parse solution %s: %s", doc.get("solution_id"), e)

        return solutions

    async def _get_solution(self, solution_id: str) -> SolutionKnowledge | None:
        """Get solution by ID (internal).

        Args:
            solution_id: Solution identifier

        Returns:
            SolutionKnowledge instance or None
        """
        db = await self.mongodb_client.get_database()
        collection = db[self.collection_name]

        doc = await collection.find_one({"solution_id": solution_id})
        if not doc:
            return None

        doc.pop("_id", None)
        try:
            return SolutionKnowledge(**doc)
        except Exception as e:
            logger.warning("Failed to parse solution %s: %s", solution_id, e)
            return None

    async def _save_solution(self, solution: SolutionKnowledge) -> None:
        """Save solution to MongoDB.

        Args:
            solution: SolutionKnowledge instance
        """
        db = await self.mongodb_client.get_database()
        collection = db[self.collection_name]

        solution_dict = solution.model_dump()
        solution_dict["updated_at"] = datetime.utcnow()

        await collection.update_one(
            {"solution_id": solution.solution_id},
            {"$set": solution_dict},
            upsert=True,
        )

    def _extract_problem_pattern(
        self,
        issue_description: str,
        error_messages: list[str],
    ) -> str:
        """Extract normalized problem pattern.

        Args:
            issue_description: Issue description
            error_messages: Error messages

        Returns:
            Normalized problem pattern
        """
        text = issue_description.lower()

        for error in error_messages:
            text += " " + error.lower()

        text = re.sub(r"[^a-z0-9\s]+", "", text)
        words = text.split()
        words = [w for w in words if len(w) > 3]

        return " ".join(sorted(set(words)))[:200]

    def _extract_tags(self, incident: Incident) -> list[str]:
        """Extract tags from incident.

        Args:
            incident: Incident instance

        Returns:
            List of tags
        """
        tags = []

        if incident.infrastructure_type:
            tags.append(incident.infrastructure_type)
        if incident.cloud_provider:
            tags.append(incident.cloud_provider)
        if incident.resource_type:
            tags.append(incident.resource_type)

        for error_pattern in incident.error_patterns[:3]:
            if error_pattern:
                tags.append(error_pattern.lower().replace(" ", "-")[:20])

        return tags[:10]

    def _calculate_quality_score(self, incident: Incident) -> int:
        """Calculate quality score for solution.

        Args:
            incident: Incident instance

        Returns:
            Quality score (0-100)
        """
        score = 50

        if incident.root_cause:
            score += 20
        if incident.solution_code:
            score += 15
        if incident.solution_applied:
            score += 10
        if incident.prevention_strategies:
            score += 5

        return min(score, 100)

    def _create_searchable_text(self, solution: SolutionKnowledge) -> str:
        """Create searchable text for embedding.

        Args:
            solution: SolutionKnowledge instance

        Returns:
            Searchable text
        """
        parts = [
            solution.problem_summary,
            solution.problem_pattern,
            solution.solution_description,
            solution.root_cause,
        ]

        if solution.solution_code:
            parts.append(solution.solution_code[:500])

        return " ".join(parts)

