"""Pinecone loader for vector data."""

import logging
import re
from typing import Any

from pinecone import Pinecone
from tqdm import tqdm

from data_pipelines.utils.config import PipelineSettings
from data_pipelines.utils.circuit_breaker import CircuitBreaker, CircuitBreakerOpenError

logger = logging.getLogger(__name__)
settings = PipelineSettings()


class PineconeLoader:
    """Load vector data into Pinecone."""

    def __init__(self):
        """Initialize Pinecone loader."""
        pc = Pinecone(api_key=settings.pinecone_api_key)
        self.index = pc.Index(settings.pinecone_index_name)
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60.0,
            success_threshold=2,
        )

    def _safe_str(self, value: Any) -> str:
        """Safely convert value to string, handling None.

        Args:
            value: Value to convert (can be None)

        Returns:
            String representation, or empty string if None
        """
        if value is None:
            return ""
        return str(value)

    def upsert_single_control(self, control: dict[str, Any]) -> bool:
        """Upsert a single compliance control to Pinecone immediately.

        Args:
            control: Control document with embedding

        Returns:
            True if upserted successfully
        """
        control_id = control.get("control_id")
        if not control_id:
            logger.warning("Cannot upsert control without control_id")
            return False

        if not control.get("embedding"):
            logger.warning("Skipping control %s - no embedding", control_id)
            return False

        pinecone_id = self._sanitize_id(f"compliance_{control_id}")
        if not pinecone_id:
            logger.error("Failed to generate valid Pinecone ID for control_id: %s", control_id)
            return False

        metadata = self._clean_metadata({
            "collection": "compliance_controls",
            "control_id": str(control_id),
            "standard": str(control.get("standard", "")),
            "version": str(control.get("version", "")),
            "severity": str(control.get("severity", "")),
            "title": str(control.get("title", ""))[:500],
            "description": str(control.get("description", ""))[:1000],
            "category": self._safe_str(control.get("category")),
            "subcategory": self._safe_str(control.get("subcategory")),
        })

        vector = {
            "id": pinecone_id,
            "values": control["embedding"],
            "metadata": metadata,
        }

        try:
            self.circuit_breaker.call(
                self.index.upsert,
                vectors=[vector]
            )
            return True
        except CircuitBreakerOpenError:
            logger.error("Pinecone circuit breaker is OPEN - skipping upsert")
            return False
        except (ValueError, TypeError, KeyError, AttributeError) as e:
            logger.error("Failed to upsert control %s to Pinecone: %s", control_id, e)
            return False

    def load_compliance_controls(
        self, controls: list[dict[str, Any]], batch_size: int = 100
    ) -> None:
        """Load compliance controls into Pinecone.

        Args:
            controls: List of compliance control documents
            batch_size: Batch size for upsert operations
        """
        logger.info("Loading %d compliance controls into Pinecone...", len(controls))

        vectors = []
        skipped = []
        for control in controls:
            control_id = control.get("control_id")
            if not control_id:
                logger.warning("Skipping control without control_id: %s", control.get("title", "unknown"))
                skipped.append("no_control_id")
                continue

            if not control.get("embedding"):
                logger.warning("Skipping control %s - no embedding", control_id)
                skipped.append(control_id)
                continue

            pinecone_id = self._sanitize_id(f"compliance_{control_id}")
            if not pinecone_id:
                logger.error("Failed to generate valid Pinecone ID for control_id: %s", control_id)
                skipped.append(control_id)
                continue

            metadata = self._clean_metadata({
                "collection": "compliance_controls",
                "control_id": str(control_id),
                "standard": str(control.get("standard", "")),
                "version": str(control.get("version", "")),
                "severity": str(control.get("severity", "")),
                "title": str(control.get("title", ""))[:500],
                "description": str(control.get("description", ""))[:1000],
                "category": self._safe_str(control.get("category")),
                "subcategory": self._safe_str(control.get("subcategory")),
            })

            vector = {
                "id": pinecone_id,
                "values": control["embedding"],
                "metadata": metadata,
            }
            vectors.append(vector)

        if skipped:
            logger.warning("Skipped %d controls: %s", len(skipped), ", ".join(skipped[:5]))

        if not vectors:
            logger.warning("No vectors to load to Pinecone")
            return

        logger.info("Prepared %d vectors for Pinecone upsert", len(vectors))

        failed_count = 0
        for i in tqdm(range(0, len(vectors), batch_size), desc="Loading compliance controls"):
            batch = vectors[i : i + batch_size]
            try:
                self.index.upsert(vectors=batch)
            except (ValueError, TypeError, KeyError, AttributeError) as e:
                logger.error("Failed to upsert batch %d-%d: %s", i, min(i + batch_size, len(vectors)), e)
                failed_count += len(batch)
                continue
            except Exception as e:
                logger.error("Unexpected error upserting batch %d-%d: %s", i, min(i + batch_size, len(vectors)), e, exc_info=True)
                failed_count += len(batch)
                continue

        if failed_count > 0:
            logger.error("Failed to load %d controls to Pinecone", failed_count)
        else:
            logger.info("Successfully loaded %d compliance controls into Pinecone", len(vectors))

    def _sanitize_id(self, raw_id: str) -> str:
        """Sanitize ID for Pinecone compatibility.

        Pinecone IDs must:
        - Be alphanumeric, hyphens, underscores
        - Not contain spaces or special characters
        - Be under 100 characters

        Args:
            raw_id: Raw ID string

        Returns:
            Sanitized ID string
        """
        if not raw_id:
            return ""

        sanitized = str(raw_id).strip()

        sanitized = re.sub(r"[^a-zA-Z0-9_-]", "_", sanitized)

        sanitized = re.sub(r"_+", "_", sanitized)

        sanitized = sanitized.strip("_")

        if len(sanitized) > 100:
            sanitized = sanitized[:100]

        if not sanitized:
            sanitized = "unknown"

        return sanitized

    def _clean_metadata(self, metadata: dict[str, Any]) -> dict[str, Any]:
        """Clean metadata to ensure Pinecone compatibility.

        Removes None/null values and ensures all values are valid types:
        - string, number, boolean, or list of strings

        Args:
            metadata: Raw metadata dictionary

        Returns:
            Cleaned metadata dictionary
        """
        cleaned = {}
        for key, value in metadata.items():
            if value is None:
                continue
            
            if isinstance(value, (str, int, float, bool)):
                if isinstance(value, str) and not value.strip():
                    continue
                cleaned[key] = value
            elif isinstance(value, list):
                cleaned_list = [str(v) for v in value if v is not None]
                if cleaned_list:
                    cleaned[key] = cleaned_list
            else:
                cleaned[key] = str(value)
        
        return cleaned

    def load_pricing_data(
        self, pricing_items: list[dict[str, Any]], batch_size: int = 100
    ) -> None:
        """Load pricing data into Pinecone.

        Args:
            pricing_items: List of pricing data documents
            batch_size: Batch size for upsert operations
        """
        logger.info("Loading %d pricing items into Pinecone...", len(pricing_items))

        vectors = []
        for item in pricing_items:
            if not item.get("embedding"):
                logger.warning("Skipping pricing item %s - no embedding", item.get("lookup_key"))
                continue

            metadata = self._clean_metadata({
                "collection": "pricing_data",
                "lookup_key": str(item["lookup_key"]),
                "cloud": str(item.get("cloud", "")),
                "service": str(item.get("service", "")),
                "resource_type": str(item.get("resource_type", "")),
                "region": str(item.get("region", "")),
            })

            vector = {
                "id": f"pricing_{item['lookup_key']}",
                "values": item["embedding"],
                "metadata": metadata,
            }
            vectors.append(vector)

        if not vectors:
            logger.warning("No vectors to load to Pinecone")
            return

        for i in tqdm(range(0, len(vectors), batch_size), desc="Loading pricing data"):
            batch = vectors[i : i + batch_size]
            self.index.upsert(vectors=batch)

        logger.info("Loaded %d pricing items into Pinecone", len(vectors))

    def load_code_examples(
        self, examples: list[dict[str, Any]], batch_size: int = 100
    ) -> None:
        """Load code examples into Pinecone.

        Args:
            examples: List of code example documents
            batch_size: Batch size for upsert operations
        """
        logger.info("Loading %d code examples into Pinecone...", len(examples))

        vectors = []
        for example in examples:
            if not example.get("embedding"):
                logger.warning("Skipping example %s - no embedding", example.get("example_id"))
                continue

            services_list = example.get("services", [])
            if isinstance(services_list, str):
                services_list = [services_list]

            metadata = self._clean_metadata({
                "collection": "code_examples",
                "example_id": str(example["example_id"]),
                "infrastructure_type": str(example.get("code_type", "")),
                "cloud_provider": str(example.get("cloud_provider", "")),
                "title": str(example.get("title", ""))[:500],
                "description": str(example.get("description", ""))[:1000],
                "services": services_list,
                "quality_score": int(example.get("quality_score", 0)),
            })

            vector = {
                "id": f"code_{example['example_id']}",
                "values": example["embedding"],
                "metadata": metadata,
            }
            vectors.append(vector)

        if not vectors:
            logger.warning("No vectors to load to Pinecone")
            return

        for i in tqdm(range(0, len(vectors), batch_size), desc="Loading code examples"):
            batch = vectors[i : i + batch_size]
            self.index.upsert(vectors=batch)

        logger.info("Loaded %d code examples into Pinecone", len(vectors))

    def load_best_practices(
        self, practices: list[dict[str, Any]], batch_size: int = 100
    ) -> None:
        """Load best practices into Pinecone.

        Args:
            practices: List of best practice documents
            batch_size: Batch size for upsert operations
        """
        logger.info("Loading %d best practices into Pinecone...", len(practices))

        vectors = []
        for practice in practices:
            if not practice.get("embedding"):
                logger.warning("Skipping practice %s - no embedding", practice.get("practice_id"))
                continue

            metadata = self._clean_metadata({
                "collection": "best_practices",
                "practice_id": str(practice["practice_id"]),
                "category": self._safe_str(practice.get("category")),
                "title": str(practice.get("title", ""))[:500],
                "description": str(practice.get("description", ""))[:1000],
            })

            vector = {
                "id": f"practice_{practice['practice_id']}",
                "values": practice["embedding"],
                "metadata": metadata,
            }
            vectors.append(vector)

        if not vectors:
            logger.warning("No vectors to load to Pinecone")
            return

        for i in tqdm(range(0, len(vectors), batch_size), desc="Loading best practices"):
            batch = vectors[i : i + batch_size]
            self.index.upsert(vectors=batch)

        logger.info("Loaded %d best practices into Pinecone", len(vectors))

    def load_knowledge_articles(
        self, articles: list[dict[str, Any]], batch_size: int = 100
    ) -> None:
        """Load knowledge articles into Pinecone.
        
        Args:
            articles: List of knowledge article documents
            batch_size: Batch size for upsert operations
        """
        logger.info("Loading %d knowledge articles into Pinecone...", len(articles))

        vectors = []
        for article in articles:
            if not article.get("embedding"):
                logger.warning("Skipping article %s - no embedding", article.get("article_id"))
                continue

            article_id = article.get("article_id", "")
            domain = article.get("domain", "")
            if hasattr(domain, "value"):
                domain = domain.value
            domain = str(domain) if domain else ""
            
            subdomain = article.get("subdomain", "")
            content_type = article.get("content_type", "")
            if hasattr(content_type, "value"):
                content_type = content_type.value
            content_type = str(content_type) if content_type else ""

            metadata = self._clean_metadata({
                "collection": "knowledge_articles",
                "article_id": str(article_id),
                "domain": self._safe_str(domain),
                "subdomain": self._safe_str(subdomain),
                "content_type": self._safe_str(content_type),
                "title": str(article.get("title", ""))[:200],
                "summary": str(article.get("summary", ""))[:1000],
                "tags": ",".join(article.get("tags", [])[:10]),
                "industries": ",".join(article.get("industries", [])[:5]),
                "cloud_providers": ",".join(article.get("cloud_providers", [])[:5]),
            })

            pinecone_id = self._sanitize_id(f"knowledge_{article_id}")
            if not pinecone_id:
                logger.error("Failed to generate valid Pinecone ID for article_id: %s", article_id)
                continue

            vector = {
                "id": pinecone_id,
                "values": article["embedding"],
                "metadata": metadata,
            }
            vectors.append(vector)

        if not vectors:
            logger.warning("No vectors to load to Pinecone")
            return

        for i in tqdm(range(0, len(vectors), batch_size), desc="Loading knowledge articles"):
            batch = vectors[i : i + batch_size]
            try:
                self.circuit_breaker.call(
                    self.index.upsert,
                    vectors=batch
                )
            except CircuitBreakerOpenError:
                logger.error("Pinecone circuit breaker is OPEN - skipping batch")
                break
            except (ValueError, TypeError, KeyError, AttributeError) as e:
                logger.error("Failed to upsert knowledge articles batch: %s", e)
                continue

        logger.info("Loaded %d knowledge articles into Pinecone", len(vectors))

