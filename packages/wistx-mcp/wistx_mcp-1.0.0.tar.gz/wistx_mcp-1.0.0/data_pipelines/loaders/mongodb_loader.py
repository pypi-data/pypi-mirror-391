"""MongoDB loader for document storage with Pinecone sync."""

import logging
from typing import Any

from pymongo.errors import DuplicateKeyError
from tqdm import tqdm

from api.database.mongodb import mongodb_manager
from data_pipelines.loaders.pinecone_loader import PineconeLoader
from data_pipelines.utils.config import PipelineSettings
from data_pipelines.utils.sanitization import sanitize_control_id

logger = logging.getLogger(__name__)
settings = PipelineSettings()


class MongoDBLoader:
    """Load documents into MongoDB (without embeddings) and sync vectors to Pinecone.

    This loader implements the sync strategy:
    1. Strip embeddings from documents before MongoDB storage
    2. Upsert documents to MongoDB (idempotent)
    3. Load vectors to Pinecone (with embeddings)
    """

    def __init__(self):
        """Initialize MongoDB loader."""
        mongodb_manager.connect()
        self.db = mongodb_manager.get_database()
        self.pinecone_loader = PineconeLoader()
        self.batch_size = settings.batch_size

    def _strip_embedding(self, document: dict[str, Any]) -> dict[str, Any]:
        """Strip embedding field from document.

        Args:
            document: Document dictionary (may contain embedding)

        Returns:
            Document dictionary without embedding field
        """
        return {k: v for k, v in document.items() if k != "embedding"}

    def save_single_control(self, doc: dict[str, Any]) -> tuple[bool, str]:
        """Save a single control to MongoDB immediately.

        Args:
            doc: Control document dictionary

        Returns:
            Tuple of (success: bool, action: str)
            - success: True if saved successfully
            - action: "inserted" or "updated"
        """
        collection = self.db.compliance_controls
        
        try:
            control_id = doc.get("control_id")
            if not control_id:
                logger.warning("Cannot save control without control_id")
                return False, "error"

            control_id = sanitize_control_id(control_id, max_length=100)
            doc["control_id"] = control_id

            source_hash = doc.pop("_source_hash", None)
            content_hash = doc.pop("_content_hash", None)
            
            if source_hash:
                doc["source_hash"] = source_hash
            if content_hash:
                doc["content_hash"] = content_hash

            doc.pop("embedding", None)

            result = collection.update_one(
                {"control_id": control_id},
                {"$set": doc},
                upsert=True,
            )

            if result.upserted_id:
                logger.debug("Saved control to MongoDB: %s (INSERTED)", control_id)
                return True, "inserted"
            else:
                logger.debug("Saved control to MongoDB: %s (UPDATED)", control_id)
                return True, "updated"
        except Exception as e:
            logger.error("Error saving control %s: %s", doc.get("control_id"), e, exc_info=True)
            return False, "error"

    async def update_control_embedding_streaming(
        self, control_id: str, _embedding: list[float], content_hash: str | None = None
    ) -> bool:
        """Update a single control with embedding immediately.

        Args:
            control_id: Control ID
            _embedding: Embedding vector (not used, kept for API compatibility)
            content_hash: Optional content hash

        Returns:
            True if updated successfully
        """
        collection = self.db.compliance_controls
        
        try:
            update_doc: dict[str, Any] = {}
            if content_hash:
                update_doc["content_hash"] = content_hash
            
            result = collection.update_one(
                {"control_id": control_id},
                {"$set": update_doc}
            )
            return result.modified_count > 0 or result.matched_count > 0
        except (ValueError, KeyError, TypeError) as e:
            logger.error("Error updating embedding for control %s: %s", control_id, e)
            return False

    def load_compliance_controls(
        self, controls: list[dict[str, Any]], batch_size: int | None = None
    ) -> dict[str, int]:
        """Load compliance controls into MongoDB and Pinecone.

        Args:
            controls: List of compliance control documents (with embeddings)
            batch_size: Batch size for MongoDB operations (default: settings.batch_size)

        Returns:
            Dictionary with loading statistics:
            {
                "mongodb_inserted": int,
                "mongodb_updated": int,
                "mongodb_errors": int,
                "pinecone_loaded": int,
                "pinecone_skipped": int
            }
        """
        batch_size = batch_size or self.batch_size
        collection = self.db.compliance_controls

        logger.info("Loading %d compliance controls into MongoDB and Pinecone...", len(controls))

        stats = {
            "mongodb_inserted": 0,
            "mongodb_updated": 0,
            "mongodb_errors": 0,
            "pinecone_loaded": 0,
            "pinecone_skipped": 0,
        }

        documents_without_embeddings = [self._strip_embedding(control) for control in controls]

        for i in tqdm(
            range(0, len(documents_without_embeddings), batch_size),
            desc="Loading compliance controls to MongoDB",
        ):
            batch = documents_without_embeddings[i : i + batch_size]

            for doc in batch:
                try:
                    control_id = doc.get("control_id")
                    if not control_id:
                        logger.warning("Skipping control without control_id: %s", doc.get("title", "unknown"))
                        stats["mongodb_errors"] += 1
                        continue

                    source_hash = doc.pop("_source_hash", None)
                    content_hash = doc.pop("_content_hash", None)
                    
                    if source_hash:
                        doc["source_hash"] = source_hash
                    if content_hash:
                        doc["content_hash"] = content_hash

                    result = collection.update_one(
                        {"control_id": control_id},
                        {"$set": doc},
                        upsert=True,
                    )

                    if result.upserted_id:
                        stats["mongodb_inserted"] += 1
                    else:
                        stats["mongodb_updated"] += 1

                except DuplicateKeyError as e:
                    logger.warning("Duplicate key error for control_id %s: %s", control_id, e)
                    stats["mongodb_errors"] += 1
                except (ValueError, KeyError, TypeError) as e:
                    logger.error("Error loading control %s: %s", control_id, e)
                    stats["mongodb_errors"] += 1

        logger.info(
            "MongoDB: Inserted %d, Updated %d, Errors %d",
            stats["mongodb_inserted"],
            stats["mongodb_updated"],
            stats["mongodb_errors"],
        )

        controls_with_embeddings = [c for c in controls if c.get("embedding")]
        controls_without_embeddings_count = len(controls) - len(controls_with_embeddings)

        if controls_without_embeddings_count > 0:
            logger.info(
                "Skipping %d controls without embeddings for Pinecone",
                controls_without_embeddings_count,
            )
            stats["pinecone_skipped"] = controls_without_embeddings_count

        if controls_with_embeddings:
            try:
                self.pinecone_loader.load_compliance_controls(controls_with_embeddings)
                stats["pinecone_loaded"] = len(controls_with_embeddings)
            except Exception as e:
                logger.error("Error loading compliance controls to Pinecone: %s", e)
                raise

        logger.info(
            "Loaded %d compliance controls: MongoDB (%d docs), Pinecone (%d vectors)",
            len(controls),
            stats["mongodb_inserted"] + stats["mongodb_updated"],
            stats["pinecone_loaded"],
        )

        return stats

    def load_pricing_data(
        self, pricing_items: list[dict[str, Any]], batch_size: int | None = None
    ) -> dict[str, int]:
        """Load pricing data into MongoDB and Pinecone.

        Args:
            pricing_items: List of pricing data documents (with embeddings)
            batch_size: Batch size for MongoDB operations (default: settings.batch_size)

        Returns:
            Dictionary with loading statistics
        """
        batch_size = batch_size or self.batch_size
        collection = self.db.pricing_data

        logger.info("Loading %d pricing items into MongoDB and Pinecone...", len(pricing_items))

        stats = {
            "mongodb_inserted": 0,
            "mongodb_updated": 0,
            "mongodb_errors": 0,
            "pinecone_loaded": 0,
            "pinecone_skipped": 0,
        }

        documents_without_embeddings = [
            self._strip_embedding(item) for item in pricing_items
        ]

        for i in tqdm(
            range(0, len(documents_without_embeddings), batch_size),
            desc="Loading pricing data to MongoDB",
        ):
            batch = documents_without_embeddings[i : i + batch_size]

            for doc in batch:
                try:
                    lookup_key = doc.get("lookup_key")
                    if not lookup_key:
                        logger.warning(
                            "Skipping pricing item without lookup_key: %s",
                            doc.get("resource_type", "unknown"),
                        )
                        stats["mongodb_errors"] += 1
                        continue

                    result = collection.update_one(
                        {"lookup_key": lookup_key},
                        {"$set": doc},
                        upsert=True,
                    )

                    if result.upserted_id:
                        stats["mongodb_inserted"] += 1
                    else:
                        stats["mongodb_updated"] += 1

                except DuplicateKeyError as e:
                    logger.warning("Duplicate key error for lookup_key %s: %s", lookup_key, e)
                    stats["mongodb_errors"] += 1
                except (ValueError, KeyError, TypeError) as e:
                    logger.error("Error loading pricing item %s: %s", lookup_key, e)
                    stats["mongodb_errors"] += 1

        logger.info(
            "MongoDB: Inserted %d, Updated %d, Errors %d",
            stats["mongodb_inserted"],
            stats["mongodb_updated"],
            stats["mongodb_errors"],
        )

        items_with_embeddings = [item for item in pricing_items if item.get("embedding")]
        items_without_embeddings_count = len(pricing_items) - len(items_with_embeddings)

        if items_without_embeddings_count > 0:
            logger.info(
                "Skipping %d pricing items without embeddings for Pinecone",
                items_without_embeddings_count,
            )
            stats["pinecone_skipped"] = items_without_embeddings_count

        if items_with_embeddings:
            try:
                self.pinecone_loader.load_pricing_data(items_with_embeddings)
                stats["pinecone_loaded"] = len(items_with_embeddings)
            except Exception as e:
                logger.error("Error loading pricing data to Pinecone: %s", e)
                raise

        logger.info(
            "Loaded %d pricing items: MongoDB (%d docs), Pinecone (%d vectors)",
            len(pricing_items),
            stats["mongodb_inserted"] + stats["mongodb_updated"],
            stats["pinecone_loaded"],
        )

        return stats

    def load_code_examples(
        self, examples: list[dict[str, Any]], batch_size: int | None = None
    ) -> dict[str, int]:
        """Load code examples into MongoDB and Pinecone.

        Args:
            examples: List of code example documents (with embeddings)
            batch_size: Batch size for MongoDB operations (default: settings.batch_size)

        Returns:
            Dictionary with loading statistics
        """
        batch_size = batch_size or self.batch_size
        collection = self.db.code_examples

        logger.info("Loading %d code examples into MongoDB and Pinecone...", len(examples))

        stats = {
            "mongodb_inserted": 0,
            "mongodb_updated": 0,
            "mongodb_errors": 0,
            "pinecone_loaded": 0,
            "pinecone_skipped": 0,
        }

        documents_without_embeddings = [self._strip_embedding(example) for example in examples]

        for i in tqdm(
            range(0, len(documents_without_embeddings), batch_size),
            desc="Loading code examples to MongoDB",
        ):
            batch = documents_without_embeddings[i : i + batch_size]

            for doc in batch:
                try:
                    example_id = doc.get("example_id")
                    if not example_id:
                        logger.warning(
                            "Skipping code example without example_id: %s",
                            doc.get("title", "unknown"),
                        )
                        stats["mongodb_errors"] += 1
                        continue

                    result = collection.update_one(
                        {"example_id": example_id},
                        {"$set": doc},
                        upsert=True,
                    )

                    if result.upserted_id:
                        stats["mongodb_inserted"] += 1
                    else:
                        stats["mongodb_updated"] += 1

                except DuplicateKeyError as e:
                    logger.warning("Duplicate key error for example_id %s: %s", example_id, e)
                    stats["mongodb_errors"] += 1
                except (ValueError, KeyError, TypeError) as e:
                    logger.error("Error loading code example %s: %s", example_id, e)
                    stats["mongodb_errors"] += 1

        logger.info(
            "MongoDB: Inserted %d, Updated %d, Errors %d",
            stats["mongodb_inserted"],
            stats["mongodb_updated"],
            stats["mongodb_errors"],
        )

        examples_with_embeddings = [ex for ex in examples if ex.get("embedding")]
        examples_without_embeddings_count = len(examples) - len(examples_with_embeddings)

        if examples_without_embeddings_count > 0:
            logger.info(
                "Skipping %d code examples without embeddings for Pinecone",
                examples_without_embeddings_count,
            )
            stats["pinecone_skipped"] = examples_without_embeddings_count

        if examples_with_embeddings:
            try:
                self.pinecone_loader.load_code_examples(examples_with_embeddings)
                stats["pinecone_loaded"] = len(examples_with_embeddings)
            except Exception as e:
                logger.error("Error loading code examples to Pinecone: %s", e)
                raise

        logger.info(
            "Loaded %d code examples: MongoDB (%d docs), Pinecone (%d vectors)",
            len(examples),
            stats["mongodb_inserted"] + stats["mongodb_updated"],
            stats["pinecone_loaded"],
        )

        return stats

    def load_best_practices(
        self, practices: list[dict[str, Any]], batch_size: int | None = None
    ) -> dict[str, int]:
        """Load best practices into MongoDB and Pinecone.

        Args:
            practices: List of best practice documents (with embeddings)
            batch_size: Batch size for MongoDB operations (default: settings.batch_size)

        Returns:
            Dictionary with loading statistics
        """
        batch_size = batch_size or self.batch_size
        collection = self.db.best_practices

        logger.info("Loading %d best practices into MongoDB and Pinecone...", len(practices))

        stats = {
            "mongodb_inserted": 0,
            "mongodb_updated": 0,
            "mongodb_errors": 0,
            "pinecone_loaded": 0,
            "pinecone_skipped": 0,
        }

        documents_without_embeddings = [
            self._strip_embedding(practice) for practice in practices
        ]

        for i in tqdm(
            range(0, len(documents_without_embeddings), batch_size),
            desc="Loading best practices to MongoDB",
        ):
            batch = documents_without_embeddings[i : i + batch_size]

            for doc in batch:
                try:
                    practice_id = doc.get("practice_id")
                    if not practice_id:
                        logger.warning(
                            "Skipping best practice without practice_id: %s",
                            doc.get("title", "unknown"),
                        )
                        stats["mongodb_errors"] += 1
                        continue

                    result = collection.update_one(
                        {"practice_id": practice_id},
                        {"$set": doc},
                        upsert=True,
                    )

                    if result.upserted_id:
                        stats["mongodb_inserted"] += 1
                    else:
                        stats["mongodb_updated"] += 1

                except DuplicateKeyError as e:
                    logger.warning("Duplicate key error for practice_id %s: %s", practice_id, e)
                    stats["mongodb_errors"] += 1
                except (ValueError, KeyError, TypeError) as e:
                    logger.error("Error loading best practice %s: %s", practice_id, e)
                    stats["mongodb_errors"] += 1

        logger.info(
            "MongoDB: Inserted %d, Updated %d, Errors %d",
            stats["mongodb_inserted"],
            stats["mongodb_updated"],
            stats["mongodb_errors"],
        )

        practices_with_embeddings = [p for p in practices if p.get("embedding")]
        practices_without_embeddings_count = len(practices) - len(practices_with_embeddings)

        if practices_without_embeddings_count > 0:
            logger.info(
                "Skipping %d best practices without embeddings for Pinecone",
                practices_without_embeddings_count,
            )
            stats["pinecone_skipped"] = practices_without_embeddings_count

        if practices_with_embeddings:
            try:
                self.pinecone_loader.load_best_practices(practices_with_embeddings)
                stats["pinecone_loaded"] = len(practices_with_embeddings)
            except Exception as e:
                logger.error("Error loading best practices to Pinecone: %s", e)
                raise

        logger.info(
            "Loaded %d best practices: MongoDB (%d docs), Pinecone (%d vectors)",
            len(practices),
            stats["mongodb_inserted"] + stats["mongodb_updated"],
            stats["pinecone_loaded"],
        )

        return stats

    def load_knowledge_articles(
        self, articles: list[dict[str, Any]], batch_size: int | None = None
    ) -> dict[str, int]:
        """Load knowledge articles into MongoDB and Pinecone.
        
        Args:
            articles: List of knowledge article documents (with embeddings)
            batch_size: Batch size for MongoDB operations (default: settings.batch_size)
            
        Returns:
            Dictionary with loading statistics
        """
        batch_size = batch_size or self.batch_size
        collection = self.db.knowledge_articles

        logger.info("Loading %d knowledge articles into MongoDB and Pinecone...", len(articles))

        stats = {
            "mongodb_inserted": 0,
            "mongodb_updated": 0,
            "mongodb_errors": 0,
            "pinecone_loaded": 0,
            "pinecone_skipped": 0,
        }

        documents_without_embeddings = [
            self._strip_embedding(article) for article in articles
        ]

        for i in tqdm(
            range(0, len(documents_without_embeddings), batch_size),
            desc="Loading knowledge articles to MongoDB",
        ):
            batch = documents_without_embeddings[i : i + batch_size]

            for doc in batch:
                try:
                    article_id = doc.get("article_id")
                    if not article_id:
                        logger.warning(
                            "Skipping knowledge article without article_id: %s",
                            doc.get("title", "unknown"),
                        )
                        stats["mongodb_errors"] += 1
                        continue

                    domain = doc.get("domain")
                    if hasattr(domain, "value"):
                        doc["domain"] = domain.value
                    
                    content_type = doc.get("content_type")
                    if hasattr(content_type, "value"):
                        doc["content_type"] = content_type.value

                    result = collection.update_one(
                        {"article_id": article_id},
                        {"$set": doc},
                        upsert=True,
                    )

                    if result.upserted_id:
                        stats["mongodb_inserted"] += 1
                    else:
                        stats["mongodb_updated"] += 1

                except DuplicateKeyError as e:
                    logger.warning("Duplicate key error for article_id %s: %s", article_id, e)
                    stats["mongodb_errors"] += 1
                except (ValueError, KeyError, TypeError) as e:
                    logger.error("Error loading knowledge article %s: %s", article_id, e)
                    stats["mongodb_errors"] += 1

        logger.info(
            "MongoDB: Inserted %d, Updated %d, Errors %d",
            stats["mongodb_inserted"],
            stats["mongodb_updated"],
            stats["mongodb_errors"],
        )

        articles_with_embeddings = [a for a in articles if a.get("embedding")]
        articles_without_embeddings_count = len(articles) - len(articles_with_embeddings)

        if articles_without_embeddings_count > 0:
            logger.info(
                "Skipping %d knowledge articles without embeddings for Pinecone",
                articles_without_embeddings_count,
            )
            stats["pinecone_skipped"] = articles_without_embeddings_count

        if articles_with_embeddings:
            try:
                self.pinecone_loader.load_knowledge_articles(articles_with_embeddings)  # type: ignore[attr-defined]
                stats["pinecone_loaded"] = len(articles_with_embeddings)
            except Exception as e:
                logger.error("Error loading knowledge articles to Pinecone: %s", e)
                raise

        logger.info(
            "Loaded %d knowledge articles: MongoDB (%d docs), Pinecone (%d vectors)",
            len(articles),
            stats["mongodb_inserted"] + stats["mongodb_updated"],
            stats["pinecone_loaded"],
        )

        return stats
