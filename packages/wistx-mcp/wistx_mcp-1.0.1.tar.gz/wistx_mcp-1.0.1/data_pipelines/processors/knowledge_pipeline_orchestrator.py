"""Knowledge pipeline orchestrator - coordinates knowledge article pipeline.

Coordinates Collection → Processing → Quality Validation → Embedding → Loading stages
for knowledge articles across all domains.
"""

from typing import Any

from ..collectors.discovery_helper import get_discovered_urls
from ..loaders.mongodb_loader import MongoDBLoader
from ..processors.base_knowledge_processor import BaseKnowledgeProcessor
from ..processors.quality_validator import ContentQualityValidator
from ..processors.llm_knowledge_extractor import LLMKnowledgeExtractor
from ..processors.embedding_generator import EmbeddingGenerator
from ..utils.change_detector import ChangeDetector
from ..utils.tracing import TracingContext, get_correlation_id
from ..utils.logger import setup_logger
from .monitoring import PipelineMetrics

logger = setup_logger(__name__)


class KnowledgePipelineOrchestrator:
    """Orchestrates the knowledge article processing pipeline.
    
    Coordinates Collection → Processing → Quality Validation → Embedding → Loading stages.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize knowledge pipeline orchestrator.
        
        Args:
            config: Optional configuration dictionary
                - enable_change_detection: Enable change detection (default: True)
        """
        self.config = config or {}
        self.processor: BaseKnowledgeProcessor | None = None
        self.embedder = EmbeddingGenerator(save_intermediate=False)
        self.loader = MongoDBLoader()
        self.quality_validator = ContentQualityValidator()
        self.metrics = PipelineMetrics(enable_prometheus=True)
        self.knowledge_extractor = LLMKnowledgeExtractor()
        self.change_detector: ChangeDetector | None = None
        self.enable_change_detection = self.config.get("enable_change_detection", True)

    async def run_knowledge_pipeline(
        self,
        domain: str,
        subdomain: str | None = None,
        processor: BaseKnowledgeProcessor | None = None,
        run_collection: bool = True,
    ) -> dict[str, Any]:
        """Run complete knowledge pipeline for a domain.
        
        Args:
            domain: Knowledge domain (compliance, finops, architecture, etc.)
            subdomain: Optional subdomain (e.g., "pci-dss", "cost-optimization")
            processor: Domain-specific processor (if None, uses default)
            run_collection: If True, run collection stage first
            
        Returns:
            Dictionary with pipeline results and statistics
        """
        logger.info("=" * 80)
        logger.info("Starting knowledge pipeline for domain: %s", domain)
        if subdomain:
            logger.info("Subdomain: %s", subdomain)
        logger.info("=" * 80)

        correlation_id = get_correlation_id()

        with TracingContext(
            "knowledge_pipeline", domain=domain, subdomain=subdomain, correlation_id=correlation_id
        ):
            stats = {
                "domain": domain,
                "subdomain": subdomain,
                "collected": 0,
                "processed": 0,
                "validated": 0,
                "embedded": 0,
                "loaded_mongodb": 0,
                "loaded_pinecone": 0,
                "quality_rejected": 0,
                "skipped_source_unchanged": 0,
                "skipped_content_unchanged": 0,
                "llm_calls_saved": 0,
                "embedding_calls_saved": 0,
                "errors": [],
            }

            raw_articles = []

            try:
                if run_collection:
                    collection_metrics = self.metrics.start_stage("collection", "knowledge")
                    try:
                        discovered = await get_discovered_urls(domain, subdomain)

                        web_urls = discovered.get("web_urls", [])
                        pdf_urls = discovered.get("pdf_urls", [])

                        logger.info(
                            "Discovered %d web URLs and %d PDF URLs",
                            len(web_urls),
                            len(pdf_urls),
                        )

                        raw_articles = await self._collect_from_urls(
                            web_urls, pdf_urls, domain, subdomain or ""
                        )

                        stats["collected"] = len(raw_articles)

                        for article in raw_articles:
                            self.metrics.record_item_processed("collection", "knowledge", success=True)

                        collection_metrics.items_processed = len(raw_articles)
                        collection_metrics.items_succeeded = len(raw_articles)
                        self.metrics.finish_stage("collection", "knowledge")

                        logger.info(
                            "Collected %d raw articles for domain: %s",
                            len(raw_articles),
                            domain,
                        )
                    except (ValueError, KeyError, AttributeError, RuntimeError) as e:
                        logger.error("Collection failed for domain %s: %s", domain, e)
                        stats["errors"].append({"stage": "collection", "error": str(e)})
                        self.metrics.record_error("collection", type(e).__name__, str(e))
                        self.metrics.finish_stage("collection", "knowledge")

                if not raw_articles:
                    logger.warning("No raw articles collected for domain: %s", domain)
                    return stats

                if self.enable_change_detection and raw_articles:
                    if self.change_detector is None:
                        from api.database.mongodb import mongodb_manager
                        mongodb_manager.connect()
                        db = mongodb_manager.get_database()
                        self.change_detector = ChangeDetector(
                            db.knowledge_articles,
                            enabled=self.enable_change_detection
                        )
                    
                    self.change_detector.batch_check_article_source_hashes(raw_articles)
                    filtered_raw_articles = []
                    
                    for raw_article in raw_articles:
                        article_id = raw_article.get("article_id")
                        should_process, source_hash = self.change_detector.should_process_article_source(
                            raw_article, article_id
                        )
                        
                        if not should_process:
                            stats["skipped_source_unchanged"] += 1
                            stats["llm_calls_saved"] += 1
                            stats["embedding_calls_saved"] += 1
                            logger.debug("Skipping unchanged article: %s", article_id)
                            continue
                        
                        raw_article["_source_hash"] = source_hash
                        filtered_raw_articles.append(raw_article)
                    
                    raw_articles = filtered_raw_articles
                    logger.info(
                        "Change detection: %d articles unchanged, %d articles to process",
                        stats["skipped_source_unchanged"],
                        len(raw_articles),
                    )

                if processor is None:
                    if domain == "compliance":
                        from .compliance_knowledge_processor import ComplianceKnowledgeProcessor

                        processor = ComplianceKnowledgeProcessor()
                    elif domain == "finops":
                        from .finops_knowledge_processor import FinOpsKnowledgeProcessor

                        processor = FinOpsKnowledgeProcessor()
                    elif domain == "devops":
                        from .devops_knowledge_processor import DevOpsKnowledgeProcessor

                        processor = DevOpsKnowledgeProcessor()
                    elif domain == "security":
                        from .security_knowledge_processor import SecurityKnowledgeProcessor

                        processor = SecurityKnowledgeProcessor()
                    elif domain == "infrastructure":
                        from .infrastructure_knowledge_processor import InfrastructureKnowledgeProcessor

                        processor = InfrastructureKnowledgeProcessor()
                    elif domain == "architecture":
                        from .architecture_knowledge_processor import ArchitectureKnowledgeProcessor

                        processor = ArchitectureKnowledgeProcessor()
                    elif domain == "cloud":
                        from .cloud_knowledge_processor import CloudKnowledgeProcessor

                        processor = CloudKnowledgeProcessor()
                    elif domain == "automation":
                        from .automation_knowledge_processor import AutomationKnowledgeProcessor

                        processor = AutomationKnowledgeProcessor()
                    elif domain == "platform":
                        from .platform_knowledge_processor import PlatformKnowledgeProcessor

                        processor = PlatformKnowledgeProcessor()
                    elif domain == "sre":
                        from .sre_knowledge_processor import SREKnowledgeProcessor

                        processor = SREKnowledgeProcessor()
                    else:
                        logger.error("No processor available for domain: %s", domain)
                        stats["errors"].append({"stage": "processing", "error": "No processor available"})
                        return stats

                self.processor = processor

                processing_metrics = self.metrics.start_stage("processing", "knowledge")

                processed_articles = []
                failed_processing = []

                for raw in raw_articles:
                    try:
                        article = processor.process_raw_data(raw)

                        if not processor.validate_article(article):
                            logger.warning(
                                "Validation failed for article: %s",
                                raw.get("title", "unknown"),
                            )
                            failed_processing.append({"raw": raw, "error": "Validation failed"})
                            continue

                        quality_score = self.quality_validator.validate(article)
                        article.quality_score = quality_score.overall_score
                        article.source_credibility = quality_score.source_credibility
                        article.freshness_score = quality_score.freshness

                        if quality_score.overall_score < 70:
                            logger.warning(
                                "Article %s rejected: quality score %.2f < 70 "
                                "(source: %.1f, completeness: %.1f, accuracy: %.1f, actionability: %.1f, freshness: %.1f)",
                                article.article_id,
                                quality_score.overall_score,
                                quality_score.source_credibility,
                                quality_score.completeness,
                                quality_score.accuracy,
                                quality_score.actionability,
                                quality_score.freshness,
                            )
                            stats["quality_rejected"] += 1
                            continue

                        processed_articles.append(article)
                        stats["validated"] += 1

                    except ValueError as e:
                        error_msg = str(e)
                        if "Article filtered out" in error_msg:
                            logger.debug("Article filtered out during processing: %s", error_msg)
                        else:
                            logger.error("Error processing article: %s", e, exc_info=True)
                        failed_processing.append({"raw": raw, "error": str(e)})
                        continue
                    except (TypeError, KeyError, AttributeError, RuntimeError) as e:
                        logger.error("Error processing article: %s", e, exc_info=True)
                        failed_processing.append({"raw": raw, "error": str(e)})
                        continue

                stats["processed"] = len(processed_articles)
                stats["errors"].extend(failed_processing)

                for article in processed_articles:
                    self.metrics.record_item_processed("processing", "knowledge", success=True)

                for failed in failed_processing:
                    self.metrics.record_item_processed("processing", "knowledge", success=False)
                    self.metrics.record_error(
                        "processing", failed.get("error", "Unknown"), str(failed)
                    )

                processing_metrics.items_processed = len(processed_articles) + len(failed_processing)
                processing_metrics.items_succeeded = len(processed_articles)
                processing_metrics.items_failed = len(failed_processing)
                self.metrics.finish_stage("processing", "knowledge")

                if not processed_articles:
                    logger.warning("No articles processed for domain: %s", domain)
                    return stats

                embedding_metrics = self.metrics.start_stage("embedding", "knowledge")
                articles_dict = [article.model_dump(mode="json") for article in processed_articles]

                items_to_embed = []
                items_skipped_embedding = []
                
                if self.enable_change_detection and self.change_detector:
                    for article_dict in articles_dict:
                        article_id = article_dict.get("article_id")
                        if not article_id:
                            items_to_embed.append(article_dict)
                            continue
                        
                        try:
                            if self.change_detector.collection is not None:
                                existing_doc = self.change_detector.collection.find_one(
                                    {"article_id": article_id},
                                    {"content_hash": 1}
                                )
                            else:
                                existing_doc = None
                            
                            should_generate, content_hash = self.change_detector.should_generate_article_embedding(
                                article_dict, article_id, existing_doc
                            )
                            
                            if not should_generate:
                                stats["skipped_content_unchanged"] += 1
                                stats["embedding_calls_saved"] += 1
                                logger.debug("Skipping embedding for unchanged article: %s", article_id)
                                items_skipped_embedding.append(article_dict)
                                continue
                            
                            article_dict["_content_hash"] = content_hash
                            items_to_embed.append(article_dict)
                        except (ValueError, TypeError, KeyError, AttributeError, RuntimeError) as e:
                            logger.warning("Error checking content hash for article %s: %s - generating embedding anyway", article_id, e)
                            items_to_embed.append(article_dict)
                else:
                    items_to_embed = articles_dict

                items_with_embeddings, failed_embedding = await self.embedder.generate_embeddings(
                    items_to_embed, "knowledge"
                )
                
                if items_skipped_embedding:
                    items_with_embeddings.extend(items_skipped_embedding)

                stats["embedded"] = len([a for a in items_with_embeddings if a.get("embedding")])
                stats["errors"].extend(failed_embedding)

                for _ in items_with_embeddings:
                    self.metrics.record_item_processed("embedding", "knowledge", success=True)

                for failed in failed_embedding:
                    self.metrics.record_item_processed("embedding", "knowledge", success=False)
                    self.metrics.record_error(
                        "embedding", failed.get("error", "Unknown"), str(failed)
                    )

                embedding_metrics.items_processed = len(items_with_embeddings) + len(failed_embedding)
                embedding_metrics.items_succeeded = len(items_with_embeddings)
                embedding_metrics.items_failed = len(failed_embedding)
                self.metrics.finish_stage("embedding", "knowledge")

                loading_metrics = self.metrics.start_stage("loading", "knowledge")

                if items_with_embeddings:
                    load_stats = self.loader.load_knowledge_articles(items_with_embeddings)
                else:
                    logger.warning(
                        "No articles with embeddings for domain: %s. "
                        "Loading articles to MongoDB without embeddings.",
                        domain,
                    )
                    articles_dict_no_embedding = [
                        article.model_dump(mode="json") for article in processed_articles
                    ]
                    for article in articles_dict_no_embedding:
                        article.pop("embedding", None)
                    load_stats = self.loader.load_knowledge_articles(articles_dict_no_embedding)

                stats["loaded_mongodb"] = load_stats["mongodb_inserted"] + load_stats["mongodb_updated"]
                stats["loaded_pinecone"] = load_stats["pinecone_loaded"]

                self.metrics.record_item_processed("loading", "knowledge", success=True)
                loading_metrics.items_processed = stats["loaded_mongodb"]
                loading_metrics.items_succeeded = stats["loaded_mongodb"]
                loading_metrics.items_failed = load_stats.get("mongodb_errors", 0)
                self.metrics.finish_stage("loading", "knowledge")

                summary = self.metrics.get_summary()
                stats["metrics_summary"] = summary

                logger.info("=" * 80)
                logger.info("Knowledge pipeline completed for domain: %s", domain)
                logger.info(
                    "Collected: %d, Processed: %d, Validated: %d, Embedded: %d, Loaded: %d",
                    stats["collected"],
                    stats["processed"],
                    stats["validated"],
                    stats["embedded"],
                    stats["loaded_mongodb"],
                )
                if self.enable_change_detection:
                    logger.info(
                        "Change Detection: Skipped %d (source unchanged), %d (content unchanged)",
                        stats["skipped_source_unchanged"],
                        stats["skipped_content_unchanged"],
                    )
                    logger.info(
                        "Cost Savings: %d LLM calls saved, %d embedding calls saved",
                        stats["llm_calls_saved"],
                        stats["embedding_calls_saved"],
                    )
                logger.info("Quality Rejected: %d", stats["quality_rejected"])
                logger.info("Total Duration: %.2fs", summary["total_duration_seconds"])
                logger.info("=" * 80)

                return stats

            except (ValueError, TypeError, KeyError, RuntimeError) as e:
                logger.error("Pipeline failed for domain %s: %s", domain, e, exc_info=True)
                stats["errors"].append({"stage": "pipeline", "error": str(e)})
                self.metrics.record_error("pipeline", type(e).__name__, str(e))
                return stats

    async def _collect_from_urls(
        self,
        web_urls: list[str],
        pdf_urls: list[str],
        domain: str,
        subdomain: str,
        max_concurrent: int = 10,
    ) -> list[dict[str, Any]]:
        """Collect knowledge articles from URLs with parallel processing.
        
        Args:
            web_urls: List of web URLs
            pdf_urls: List of PDF URLs
            domain: Knowledge domain
            subdomain: Subdomain
            max_concurrent: Maximum concurrent URL fetches (default: 10)
            
        Returns:
            List of raw article dictionaries
        """
        import asyncio
        from crawl4ai import AsyncWebCrawler

        all_articles = []
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_web_url(crawler: AsyncWebCrawler, url: str) -> list[dict[str, Any]]:
            """Process a single web URL.
            
            Args:
                crawler: Shared AsyncWebCrawler instance
                url: URL to process
                
            Returns:
                List of extracted articles
            """
            async with semaphore:
                try:
                    crawl_result = await crawler.arun(url=url, bypass_cache=True)
                    markdown_content = crawl_result.markdown or ""
                    html_content = crawl_result.html or ""

                    if markdown_content or html_content:
                        content_to_use = markdown_content if markdown_content else html_content
                        articles = await self.knowledge_extractor.extract_articles(
                            content=content_to_use,
                            domain=domain,
                            subdomain=subdomain,
                            source_url=url,
                            prefer_markdown=True,
                            markdown_content=markdown_content if markdown_content else None,
                        )
                        return articles
                    else:
                        logger.warning("No content extracted from web URL: %s", url)
                        return []
                except (ValueError, TypeError, KeyError, AttributeError, ConnectionError, RuntimeError) as e:
                    logger.error("Error collecting from web URL %s: %s", url, e)
                    return []

        async def process_pdf_url(url: str) -> list[dict[str, Any]]:
            """Process a single PDF URL.
            
            Args:
                url: PDF URL to process
                
            Returns:
                List of extracted articles
            """
            async with semaphore:
                try:
                    from ..processors.document_processor import DocumentProcessor

                    doc_processor = DocumentProcessor()
                    pdf_content = doc_processor.process_pdf(url)

                    if pdf_content.get("text"):
                        articles = await self.knowledge_extractor.extract_articles(
                            content=pdf_content["text"],
                            domain=domain,
                            subdomain=subdomain,
                            source_url=url,
                            prefer_markdown=True,
                            markdown_content=pdf_content.get("markdown"),
                        )
                        return articles
                    return []
                except (ValueError, TypeError, KeyError, AttributeError, ConnectionError) as e:
                    logger.error("Error collecting from PDF URL %s: %s", url, e)
                    return []

        async with AsyncWebCrawler() as crawler:
            if web_urls:
                logger.info("Processing %d web URLs in parallel (max_concurrent=%d)", len(web_urls), max_concurrent)
                web_tasks = [process_web_url(crawler, url) for url in web_urls]
                web_results = await asyncio.gather(*web_tasks, return_exceptions=True)
                
                for result in web_results:
                    if isinstance(result, Exception):
                        logger.error("Exception in parallel web URL processing: %s", result)
                        continue
                    if isinstance(result, list):
                        all_articles.extend(result)

            if pdf_urls:
                logger.info("Processing %d PDF URLs in parallel (max_concurrent=%d)", len(pdf_urls), max_concurrent)
                pdf_tasks = [process_pdf_url(url) for url in pdf_urls]
                pdf_results = await asyncio.gather(*pdf_tasks, return_exceptions=True)
                
                for result in pdf_results:
                    if isinstance(result, Exception):
                        logger.error("Exception in parallel PDF URL processing: %s", result)
                        continue
                    if isinstance(result, list):
                        all_articles.extend(result)

        logger.info("Collected %d articles from %d web URLs and %d PDF URLs", len(all_articles), len(web_urls), len(pdf_urls))
        return all_articles

    def get_metrics_summary(self) -> dict[str, Any]:
        """Get metrics summary.
        
        Returns:
            Dictionary with metrics summary
        """
        return self.metrics.get_summary()

