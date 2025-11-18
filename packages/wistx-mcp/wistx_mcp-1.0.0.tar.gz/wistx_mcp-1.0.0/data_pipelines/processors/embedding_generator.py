"""Embedding generator - generates vector embeddings for processed data."""

import asyncio
import json
from typing import Any

from openai import AsyncOpenAI, RateLimitError

from ..utils.config import PipelineSettings
from ..utils.logger import setup_logger
from ..utils.circuit_breaker import CircuitBreaker, CircuitBreakerOpenError

logger = setup_logger(__name__)
settings = PipelineSettings()


class QuotaExceededError(Exception):
    """Raised when OpenAI quota is exceeded and retries exhausted."""


class EmbeddingGenerator:
    """Generate vector embeddings for processed data using OpenAI API.

    Supports both streaming (production) and checkpointing (development) modes.
    """

    def __init__(self, save_intermediate: bool = False):
        """Initialize embedding generator.

        Args:
            save_intermediate: If True, save items with embeddings to disk (checkpointing mode)
        """
        self.save_intermediate = save_intermediate
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = "text-embedding-3-small"
        self.dimension = 1536
        self.batch_size = 100
        self.data_dir = settings.data_dir
        self.rate_limit_delay = 0.02
        self.quota_wait_seconds = 120
        self.rate_limit_wait_seconds = 60
        self.max_quota_retries = 3
        self.max_rate_limit_retries = 5
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60.0,
            success_threshold=2,
        )

    def to_searchable_text(self, item: dict[str, Any], data_type: str) -> str:
        """Convert item to searchable text for embedding.

        Args:
            item: Processed item dictionary
            data_type: Type of data (compliance, pricing, code)

        Returns:
            Searchable text string
        """
        if data_type == "compliance":
            text = f"{item.get('standard', '')} {item.get('control_id', '')}: {item.get('title', '')}\n"
            text += f"{item.get('description', '')}\n"
            if item.get("requirement"):
                text += f"{item['requirement']}\n"
            remediation = item.get("remediation", {})
            if isinstance(remediation, dict):
                text += f"{remediation.get('summary', '')}\n"
                for snippet in remediation.get("code_snippets", [])[:3]:
                    if isinstance(snippet, dict) and snippet.get("description"):
                        text += f"{snippet['description']}\n"
            return text

        elif data_type == "pricing":
            text = f"{item.get('cloud', '')} {item.get('service', '')} {item.get('resource_type', '')}\n"
            text += f"Region: {item.get('region', '')}\n"
            if item.get("specifications"):
                text += f"Specifications: {json.dumps(item['specifications'])}\n"
            if item.get("pricing"):
                pricing_str = json.dumps(
                    {k: v.get("hourly", 0) if isinstance(v, dict) else v for k, v in item["pricing"].items()}
                )
                text += f"Pricing: {pricing_str}\n"
            return text

        elif data_type == "code":
            text = f"{item.get('title', '')}\n{item.get('description', '')}\n"
            text += f"Type: {item.get('code_type', '')}\n"
            text += f"Cloud: {item.get('cloud_provider', '')}\n"
            text += f"Services: {', '.join(item.get('services', []))}\n"
            code = item.get("code", "")
            text += f"Code:\n{code[:1000]}\n"
            return text

        elif data_type == "knowledge":
            from ..models.knowledge_article import KnowledgeArticle
            if isinstance(item, dict):
                article = KnowledgeArticle.model_validate(item)
                return article.to_searchable_text()
            return json.dumps(item)

        else:
            return json.dumps(item)

    async def generate_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a batch of texts.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors (1536 dimensions each)

        Raises:
            RateLimitError: If rate limit exceeded (after retries)
            CircuitBreakerOpenError: If circuit breaker is open
        """
        try:
            return await self.circuit_breaker.call_async(
                self._generate_embeddings_batch_internal,
                texts
            )
        except CircuitBreakerOpenError:
            logger.error("OpenAI circuit breaker is OPEN - skipping embedding generation")
            raise
    
    async def _generate_embeddings_batch_internal(self, texts: list[str]) -> list[list[float]]:
        """Internal method to generate embeddings (wrapped by circuit breaker).

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors (1536 dimensions each)

        Raises:
            RateLimitError: If rate limit exceeded
        """
        response = await self.client.embeddings.create(
            model=self.model,
            input=texts,
        )

        embeddings = [item.embedding for item in response.data]

        if len(embeddings) != len(texts):
            logger.warning(
                "Embedding count mismatch: expected %d, got %d",
                len(texts),
                len(embeddings),
            )

        return embeddings

    async def generate_embeddings(
        self, items: list[dict[str, Any]], data_type: str
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Generate embeddings for processed items.

        Args:
            items: List of processed items (without embeddings)
            data_type: Type of data (compliance, pricing, code)

        Returns:
            Tuple of (items_with_embeddings, failed_items)
        """
        logger.info("Generating embeddings for %d %s items", len(items), data_type)

        if not items:
            return [], []

        texts = [self.to_searchable_text(item, data_type) for item in items]

        items_with_embeddings = []
        failed_items = []
        quota_retry_count = 0
        rate_limit_retry_count = 0

        for i in range(0, len(texts), self.batch_size):
            if quota_retry_count > self.max_quota_retries:
                logger.warning(
                    "Quota exhausted. Skipping remaining %d batches.",
                    (len(texts) - i) // self.batch_size,
                )
                break
            
            batch_texts = texts[i : i + self.batch_size]
            batch_items = items[i : i + self.batch_size]

            retry_attempt = 0
            max_retries = self.max_rate_limit_retries
            
            while retry_attempt <= max_retries:
                try:
                    batch_embeddings = await self.generate_embeddings_batch(batch_texts)

                    for item, embedding in zip(batch_items, batch_embeddings):
                        if len(embedding) != self.dimension:
                            logger.warning(
                                "Invalid embedding dimension: expected %d, got %d",
                                self.dimension,
                                len(embedding),
                            )
                            failed_items.append({"item": item, "error": "Invalid embedding dimension"})
                            continue

                        item["embedding"] = embedding
                        items_with_embeddings.append(item)

                    logger.info(
                        "Generated embeddings for batch %d-%d (%d/%d)",
                        i + 1,
                        min(i + self.batch_size, len(items)),
                        len(items_with_embeddings),
                        len(items),
                    )

                    quota_retry_count = 0
                    rate_limit_retry_count = 0
                    await asyncio.sleep(self.rate_limit_delay)
                    break

                except RateLimitError as e:
                    error_str = str(e).lower()
                    error_body = {}
                    
                    if hasattr(e, "body") and isinstance(e.body, dict):
                        error_body = e.body
                    elif hasattr(e, "response") and hasattr(e.response, "json"):
                        try:
                            error_body = e.response.json()
                        except (ValueError, AttributeError):
                            pass
                    
                    error_code = error_body.get("error", {}).get("code", "")
                    error_type = error_body.get("error", {}).get("type", "")
                    is_quota = error_code == "insufficient_quota" or error_type == "insufficient_quota" or "quota" in error_str
                    
                    if is_quota:
                        quota_retry_count += 1
                        if quota_retry_count > self.max_quota_retries:
                            logger.error(
                                "OpenAI quota exceeded after %d retries. Skipping remaining embedding generation. "
                                "Pipeline will continue with controls saved to MongoDB (without embeddings). "
                                "Please increase OpenAI quota to generate embeddings.",
                                self.max_quota_retries,
                            )
                            failed_items.extend([{"item": item, "error": "Quota exceeded"} for item in batch_items])
                            break
                        
                        wait_time = self.quota_wait_seconds * (2 ** (quota_retry_count - 1))
                        logger.warning(
                            "OpenAI quota exceeded (attempt %d/%d). Waiting %d seconds before retry...",
                            quota_retry_count,
                            self.max_quota_retries,
                            wait_time,
                        )
                        await asyncio.sleep(wait_time)
                        retry_attempt += 1
                        continue
                    else:
                        rate_limit_retry_count += 1
                        if rate_limit_retry_count > self.max_rate_limit_retries:
                            logger.error("Rate limit exceeded after %d retries: %s", self.max_rate_limit_retries, e)
                            failed_items.extend([{"item": item, "error": "Rate limit exceeded"} for item in batch_items])
                            rate_limit_retry_count = 0
                            break
                        
                        wait_time = min(self.rate_limit_wait_seconds * (2 ** (rate_limit_retry_count - 1)), 300)
                        logger.warning(
                            "Rate limit exceeded (attempt %d/%d). Waiting %d seconds before retry...",
                            rate_limit_retry_count,
                            self.max_rate_limit_retries,
                            wait_time,
                        )
                        await asyncio.sleep(wait_time)
                        retry_attempt += 1
                        continue

                except (ValueError, TypeError, KeyError) as e:
                    logger.error("Error generating embeddings for batch: %s", e)
                    failed_items.extend([{"item": item, "error": str(e)} for item in batch_items])
                    break
                
                if retry_attempt > max_retries:
                    failed_items.extend([{"item": item, "error": "Max retries exceeded"} for item in batch_items])
                    break

        logger.info(
            "Generated embeddings for %d items, %d failed (%s)",
            len(items_with_embeddings),
            len(failed_items),
            data_type,
        )

        if self.save_intermediate:
            self.save_with_embeddings(items_with_embeddings, data_type)

        return items_with_embeddings, failed_items

    def save_with_embeddings(self, items: list[dict[str, Any]], data_type: str) -> None:
        """Save items with embeddings to JSON file.

        Args:
            items: List of items with embeddings
            data_type: Type of data (compliance, pricing, code)
        """
        embeddings_dir = self.data_dir / data_type / "embeddings"
        embeddings_dir.mkdir(parents=True, exist_ok=True)

        output_file = embeddings_dir / f"{data_type}_with_embeddings.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2, ensure_ascii=False, default=str)

        logger.info("Saved %d items with embeddings to %s", len(items), output_file)

    def filter_existing_embeddings(
        self, items: list[dict[str, Any]]
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Separate items with and without embeddings.

        Args:
            items: List of items (may or may not have embeddings)

        Returns:
            Tuple of (items_with_embeddings, items_without_embeddings)
        """
        with_embeddings = [item for item in items if item.get("embedding")]
        without_embeddings = [item for item in items if not item.get("embedding")]

        logger.info(
            "Found %d items with embeddings, %d without",
            len(with_embeddings),
            len(without_embeddings),
        )

        return with_embeddings, without_embeddings
