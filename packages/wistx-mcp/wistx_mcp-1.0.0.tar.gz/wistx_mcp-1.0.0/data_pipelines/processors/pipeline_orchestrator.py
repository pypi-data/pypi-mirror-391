"""Pipeline orchestrator - coordinates all pipeline stages."""

from typing import Any

from ..collectors.compliance_collector import ComplianceCollector
from ..config.compliance_urls import COMPLIANCE_URLS
from ..loaders.mongodb_loader import MongoDBLoader
from ..utils.change_detector import ChangeDetector, extract_control_id
from ..utils.tracing import TracingContext, get_correlation_id
from .compliance_processor import ComplianceProcessor
from .embedding_generator import EmbeddingGenerator
from .monitoring import HealthCheck, PipelineMetrics
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class PipelineConfig:
    """Pipeline configuration."""

    def __init__(
        self,
        mode: str = "streaming",
        save_intermediate: bool = False,
        save_raw_data: bool = True,
        enable_change_detection: bool = True,
        enable_streaming_saves: bool = True,
        streaming_batch_size: int = 10,
        embedding_batch_size: int = 20,
    ):
        """Initialize pipeline configuration.

        Args:
            mode: Pipeline mode ("streaming" or "checkpointing")
            save_intermediate: Save intermediate files (checkpointing mode)
            save_raw_data: Save raw data (always recommended)
            enable_change_detection: Enable source-level change detection (default: True)
            enable_streaming_saves: Enable streaming saves to MongoDB (default: True)
            streaming_batch_size: Batch size for streaming saves progress logging (default: 10)
            embedding_batch_size: Batch size for embedding generation (default: 20)
        """
        self.mode = mode
        self.save_intermediate = save_intermediate if mode == "checkpointing" else False
        self.save_raw_data = save_raw_data
        self.enable_change_detection = enable_change_detection
        self.enable_streaming_saves = enable_streaming_saves
        self.streaming_batch_size = streaming_batch_size
        self.embedding_batch_size = embedding_batch_size


class PipelineOrchestrator:
    """Orchestrates the complete data processing pipeline.

    Coordinates Collection → Processing → Embedding → Loading stages.
    """

    def __init__(self, config: PipelineConfig):
        """Initialize pipeline orchestrator.

        Args:
            config: Pipeline configuration
        """
        self.config = config
        self.collector = ComplianceCollector()
        self.processor = ComplianceProcessor(save_intermediate=config.save_intermediate)
        self.embedder = EmbeddingGenerator(save_intermediate=config.save_intermediate)
        self.loader: MongoDBLoader | None = None
        self.metrics = PipelineMetrics(enable_prometheus=True)
        self.health_check = HealthCheck()
        self.change_detector: ChangeDetector | None = None
        self._streaming_stats: dict[str, int] = {}

        self._check_dependencies()

    def _check_dependencies(self) -> None:
        """Check required dependencies and provide helpful error messages."""
        issues = []

        try:
            import playwright
            _ = playwright
        except ImportError:
            issues.append("Playwright not installed. Install: pip install playwright")
        else:
            logger.debug("Playwright package found (browser check will happen at runtime)")

        try:
            from docling.document_converter import DocumentConverter
            _ = DocumentConverter
            logger.info("Docling package found and importable")
        except ImportError:
            issues.append("Docling not installed. Install: pip install docling")
        except (AttributeError, RuntimeError, ValueError, TypeError) as e:
            issues.append(f"Docling import error: {e}. Try: pip install --upgrade docling")

        if issues:
            logger.warning("=" * 80)
            logger.warning("DEPENDENCY WARNINGS:")
            for issue in issues:
                logger.warning("  - %s", issue)
            logger.warning("=" * 80)
            logger.warning(
                "Some features may not work. Install missing dependencies to enable full functionality."
            )

    def _calculate_control_priority_score(self, control: dict[str, Any]) -> float:
        """Calculate priority score for a control to determine which to keep when limiting.
        
        Higher score = higher priority (keep this control).
        
        Args:
            control: Control dictionary
            
        Returns:
            Priority score (higher = better)
        """
        score = 0.0
        
        source_url = control.get("source_url", "")
        if not source_url:
            return score
        
        official_domains = [
            "pcisecuritystandards.org",
            "cisecurity.org",
            "hhs.gov",
            "aicpa.org",
            "nist.gov",
            "iso.org",
            "gdpr.eu",
            "fedramp.gov",
            "oag.ca.gov",
            "sec.gov",
            "ftc.gov",
        ]
        
        for domain in official_domains:
            if domain in source_url.lower():
                score += 100.0
                break
        
        if source_url.endswith(".pdf"):
            score += 20.0
        
        control_id = control.get("control_id", "")
        if control_id and len(control_id) > 5:
            score += 10.0
        
        title = control.get("title", "")
        if title and len(title) > 10:
            score += 10.0
        
        description = control.get("description", "")
        if description:
            desc_len = len(description)
            if desc_len > 100:
                score += 20.0
            elif desc_len > 50:
                score += 10.0
        
        remediation = control.get("remediation")
        if remediation:
            score += 15.0
        
        verification = control.get("verification")
        if verification:
            score += 15.0
        
        severity = control.get("severity", "").upper()
        severity_scores = {
            "CRITICAL": 30.0,
            "HIGH": 20.0,
            "MEDIUM": 10.0,
            "LOW": 5.0,
        }
        score += severity_scores.get(severity, 0.0)
        
        return score

    def _enforce_expected_controls_count(
        self, raw_controls: list[dict[str, Any]], standard: str, stats: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Enforce expected controls count by prioritizing and limiting controls.
        
        If more than expected: prioritize by quality and limit to expected count.
        If less than expected: log warning but use all available controls.
        If exactly expected: perfect match.
        
        Args:
            raw_controls: List of raw control dictionaries
            standard: Compliance standard name
            stats: Statistics dictionary to update
            
        Returns:
            List of controls (limited to expected count if over, all if under)
        """
        standard_config = COMPLIANCE_URLS.get(standard)
        if not standard_config:
            logger.debug("No config found for standard %s, skipping expected controls enforcement", standard)
            return raw_controls
        
        expected_count = standard_config.get("expected_controls")
        if expected_count is None:
            logger.debug("No expected_controls specified for standard %s", standard)
            return raw_controls
        
        collected_count = len(raw_controls)
        stats["expected_controls"] = expected_count
        stats["collected_before_enforcement"] = collected_count
        
        if collected_count == expected_count:
            logger.info(
                "✅ Perfect match for %s: Collected exactly %d controls (expected: %d)",
                standard, collected_count, expected_count
            )
            stats["enforcement_action"] = "none"
            return raw_controls
        
        if collected_count < expected_count:
            percentage = (collected_count / expected_count) * 100
            logger.warning(
                "⚠️ Collection incomplete for %s: Collected %d controls, expected %d (%.1f%% of expected). "
                "Using all available controls.",
                standard, collected_count, expected_count, percentage
            )
            stats["enforcement_action"] = "under_limit"
            stats["collection_percentage"] = percentage
            return raw_controls
        
        logger.info(
            "📊 Collected %d controls for %s, expected %d. Prioritizing and limiting to expected count.",
            collected_count, standard, expected_count
        )
        
        prioritized_controls = sorted(
            raw_controls,
            key=self._calculate_control_priority_score,
            reverse=True
        )
        
        limited_controls = prioritized_controls[:expected_count]
        removed_count = collected_count - expected_count
        
        logger.info(
            "✅ Limited %s controls from %d to %d (removed %d lower-priority controls)",
            standard, collected_count, expected_count, removed_count
        )
        
        stats["enforcement_action"] = "limited"
        stats["controls_removed"] = removed_count
        stats["collection_percentage"] = 100.0
        
        return limited_controls

    async def run_compliance_pipeline(
        self, standard: str, version: str = "latest", run_collection: bool = True
    ) -> dict[str, Any]:
        """Run complete pipeline for a compliance standard.

        Full pipeline: Collection → Processing → Embedding → Loading

        Args:
            standard: Compliance standard name
            version: Standard version
            run_collection: If True, run collection stage first (default: True)

        Returns:
            Dictionary with pipeline results and statistics
        """
        logger.info("=" * 80)
        logger.info("Starting compliance pipeline for: %s (version: %s)", standard, version)
        logger.info("Mode: %s", self.config.mode)
        logger.info("Run Collection: %s", run_collection)
        logger.info("=" * 80)

        correlation_id = get_correlation_id()
        
        with TracingContext("compliance_pipeline", standard=standard, version=version, correlation_id=correlation_id):
            stats = {
                "standard": standard,
                "version": version,
                "mode": self.config.mode,
                "collected": 0,
                "processed": 0,
                "embedded": 0,
                "loaded_mongodb": 0,
                "loaded_pinecone": 0,
                "skipped_source_unchanged": 0,
                "skipped_content_unchanged": 0,
                "llm_calls_saved": 0,
                "embedding_calls_saved": 0,
                "mongodb_inserted": 0,
                "mongodb_updated": 0,
                "mongodb_errors": 0,
                "pinecone_skipped": 0,
                "errors": [],
            }
            
            raw_controls = []

            try:
                if run_collection:
                    collection_metrics = self.metrics.start_stage("collection", "compliance")
                    try:
                        standard_mapping = {
                            "PCI-DSS": "pci-dss",
                            "CIS": "cis-aws",
                            "HIPAA": "hipaa",
                            "SOC2": "soc2",
                            "NIST-800-53": "nist-800-53",
                            "ISO-27001": "iso-27001",
                            "GDPR": "gdpr",
                            "FedRAMP": "fedramp",
                            "CCPA": "ccpa",
                            "SOX": "sox",
                            "GLBA": "glba",
                        }
                        standard_key = standard_mapping.get(standard, standard.lower().replace("_", "-"))
                        raw_controls = await self.collector.collect_standard_async(standard_key)
                        
                        raw_controls = self._enforce_expected_controls_count(raw_controls, standard, stats)
                        
                        stats["collected"] = len(raw_controls)

                        for control in raw_controls:
                            self.metrics.record_item_processed("collection", "compliance", success=True)

                        collection_metrics.items_processed = len(raw_controls)
                        collection_metrics.items_succeeded = len(raw_controls)
                        self.metrics.finish_stage("collection", "compliance")

                        logger.info("Collected %d raw controls for standard: %s", len(raw_controls), standard)
                    except (ValueError, KeyError, AttributeError, RuntimeError) as e:
                        logger.error("Collection failed for standard %s: %s", standard, e)
                        stats["errors"].append({"stage": "collection", "error": str(e)})
                        self.metrics.record_error("collection", type(e).__name__, str(e))
                        self.metrics.finish_stage("collection", "compliance")

                if self.config.enable_change_detection and raw_controls:
                    if self.loader is None:
                        self.loader = MongoDBLoader()
                    if self.change_detector is None:
                        from api.database.mongodb import mongodb_manager
                        mongodb_manager.connect()
                        db = mongodb_manager.get_database()
                        self.change_detector = ChangeDetector(
                            db.compliance_controls,
                            enabled=self.config.enable_change_detection
                        )
                    
                    self.change_detector.batch_check_source_hashes(raw_controls)
                    filtered_raw_controls = []
                    
                    for raw_control in raw_controls:
                        control_id = extract_control_id(raw_control)
                        should_process, source_hash = self.change_detector.should_process_source(
                            raw_control, control_id
                        )
                        
                        if not should_process:
                            stats["skipped_source_unchanged"] += 1
                            stats["llm_calls_saved"] += 1
                            stats["embedding_calls_saved"] += 1
                            logger.debug("Skipping unchanged control: %s", control_id)
                            continue
                        
                        raw_control["_source_hash"] = source_hash
                        filtered_raw_controls.append(raw_control)
                    
                    if filtered_raw_controls:
                        logger.info(
                            "Change detection: Processing %d of %d controls (%d skipped)",
                            len(filtered_raw_controls),
                            len(raw_controls),
                            stats["skipped_source_unchanged"]
                        )
                        raw_controls = filtered_raw_controls
                    else:
                        logger.info("All controls unchanged - skipping processing")
                        return stats
                else:
                    filtered_raw_controls = raw_controls if run_collection else []

                processing_metrics = self.metrics.start_stage("processing", "compliance")
                
                if self.config.enable_streaming_saves:
                    processed_controls, failed_processing, items_with_embeddings, failed_embedding = await self._process_embed_and_save_streaming(
                        standard, version, filtered_raw_controls if run_collection else []
                    )
                else:
                    processed_controls, failed_processing = await self.processor.process_standard_async(standard, version)
                    stats["processed"] = len(processed_controls)
                    stats["errors"].extend(failed_processing)

                    for control in processed_controls:
                        self.metrics.record_item_processed("processing", "compliance", success=True)

                    for failed in failed_processing:
                        self.metrics.record_item_processed("processing", "compliance", success=False)
                        self.metrics.record_error("processing", failed.get("error", "Unknown"), str(failed))

                    processing_metrics.items_processed = len(processed_controls) + len(failed_processing)
                    processing_metrics.items_succeeded = len(processed_controls)
                    processing_metrics.items_failed = len(failed_processing)
                    self.metrics.finish_stage("processing", "compliance")

                    if not processed_controls:
                        logger.warning("No controls processed for standard: %s", standard)
                        return stats

                    embedding_metrics = self.metrics.start_stage("embedding", "compliance")
                    controls_dict = [control.model_dump(mode="json") for control in processed_controls]

                    if self.config.enable_change_detection and self.change_detector:
                        filtered_for_embedding = []
                        for control_dict in controls_dict:
                            control_id = control_dict.get("control_id")
                            if not control_id:
                                filtered_for_embedding.append(control_dict)
                                continue
                            
                            existing_doc = None
                            if self.change_detector.collection is not None:
                                try:
                                    existing_doc = self.change_detector.collection.find_one(
                                        {"control_id": control_id},
                                        {"content_hash": 1}
                                    )
                                except (ValueError, TypeError, KeyError, AttributeError, RuntimeError) as e:
                                    logger.warning("Failed to check content hash for %s: %s - generating embedding", control_id, e)
                                    filtered_for_embedding.append(control_dict)
                                    continue
                            
                            should_generate, content_hash = self.change_detector.should_generate_embedding(
                                control_dict, control_id, existing_doc
                            )
                            
                            if not should_generate:
                                stats["skipped_content_unchanged"] += 1
                                stats["embedding_calls_saved"] += 1
                                control_dict["_content_hash"] = content_hash
                                logger.debug("Skipping embedding for unchanged content: %s", control_id)
                            else:
                                control_dict["_content_hash"] = content_hash
                                filtered_for_embedding.append(control_dict)
                        
                        if filtered_for_embedding:
                            logger.info(
                                "Change detection: Generating embeddings for %d of %d controls (%d skipped)",
                                len(filtered_for_embedding),
                                len(controls_dict),
                                stats["skipped_content_unchanged"]
                            )
                            controls_dict = filtered_for_embedding
                        else:
                            logger.info("All content unchanged - skipping embedding generation")
                            controls_dict = []

                    items_with_embeddings, failed_embedding = await self.embedder.generate_embeddings(
                        controls_dict, "compliance"
                    )
                    
                    stats["embedded"] = len(items_with_embeddings)
                    stats["errors"].extend(failed_embedding)

                    for _ in items_with_embeddings:
                        self.metrics.record_item_processed("embedding", "compliance", success=True)

                    for failed in failed_embedding:
                        self.metrics.record_item_processed("embedding", "compliance", success=False)
                        self.metrics.record_error("embedding", failed.get("error", "Unknown"), str(failed))

                    embedding_metrics.items_processed = len(items_with_embeddings) + len(failed_embedding)
                    embedding_metrics.items_succeeded = len(items_with_embeddings)
                    embedding_metrics.items_failed = len(failed_embedding)
                    self.metrics.finish_stage("embedding", "compliance")
                
                if self.config.enable_streaming_saves:
                    stats["processed"] = len(processed_controls)
                    stats["errors"].extend(failed_processing)
                    stats["embedded"] = len(items_with_embeddings)
                    stats["errors"].extend(failed_embedding)

                    for control in processed_controls:
                        self.metrics.record_item_processed("processing", "compliance", success=True)

                    for failed in failed_processing:
                        self.metrics.record_item_processed("processing", "compliance", success=False)
                        self.metrics.record_error("processing", failed.get("error", "Unknown"), str(failed))

                    processing_metrics.items_processed = len(processed_controls) + len(failed_processing)
                    processing_metrics.items_succeeded = len(processed_controls)
                    processing_metrics.items_failed = len(failed_processing)
                    self.metrics.finish_stage("processing", "compliance")

                    embedding_metrics = self.metrics.start_stage("embedding", "compliance")
                    
                    for _ in items_with_embeddings:
                        self.metrics.record_item_processed("embedding", "compliance", success=True)

                    for failed in failed_embedding:
                        self.metrics.record_item_processed("embedding", "compliance", success=False)
                        self.metrics.record_error("embedding", failed.get("error", "Unknown"), str(failed))

                    embedding_metrics.items_processed = len(items_with_embeddings) + len(failed_embedding)
                    embedding_metrics.items_succeeded = len(items_with_embeddings)
                    embedding_metrics.items_failed = len(failed_embedding)
                    self.metrics.finish_stage("embedding", "compliance")

                loading_metrics = self.metrics.start_stage("loading", "compliance")
                if self.loader is None:
                    self.loader = MongoDBLoader()
                
                if self.config.enable_streaming_saves:
                    logger.info("Streaming saves enabled - data already saved incrementally")
                    load_stats = {
                        "mongodb_inserted": stats.get("mongodb_inserted", 0),
                        "mongodb_updated": stats.get("mongodb_updated", 0),
                        "mongodb_errors": stats.get("mongodb_errors", 0),
                        "pinecone_loaded": stats.get("pinecone_loaded", 0),
                        "pinecone_skipped": stats.get("pinecone_skipped", 0),
                    }
                else:
                    if items_with_embeddings:
                        load_stats = self.loader.load_compliance_controls(items_with_embeddings)
                    else:
                        logger.warning(
                            "No controls with embeddings for standard: %s. "
                            "Loading controls to MongoDB without embeddings (Pinecone will be skipped).",
                            standard,
                        )
                        controls_dict = [control.model_dump(mode="json") for control in processed_controls]
                        for control in controls_dict:
                            control.pop("embedding", None)
                        load_stats = self.loader.load_compliance_controls(controls_dict)
                
                stats["loaded_mongodb"] = load_stats["mongodb_inserted"] + load_stats["mongodb_updated"]
                stats["loaded_pinecone"] = load_stats["pinecone_loaded"]
                stats["mongodb_errors"] = load_stats["mongodb_errors"]
                stats["pinecone_skipped"] = load_stats["pinecone_skipped"]

                self.metrics.record_item_processed("loading", "compliance", success=True)
                loading_metrics.items_processed = stats["loaded_mongodb"]
                loading_metrics.items_succeeded = stats["loaded_mongodb"]
                loading_metrics.items_failed = load_stats["mongodb_errors"]
                self.metrics.finish_stage("loading", "compliance")

                summary = self.metrics.get_summary()
                stats["metrics_summary"] = summary

                if self.config.enable_streaming_saves:
                    stats["mongodb_inserted"] = self._streaming_stats.get("mongodb_inserted", 0)
                    stats["mongodb_updated"] = self._streaming_stats.get("mongodb_updated", 0)
                    stats["mongodb_errors"] = self._streaming_stats.get("mongodb_errors", 0)
                    stats["pinecone_loaded"] = self._streaming_stats.get("pinecone_loaded", 0)
                    stats["pinecone_skipped"] = self._streaming_stats.get("pinecone_skipped", 0)
                    stats["skipped_content_unchanged"] = self._streaming_stats.get("skipped_content_unchanged", 0)
                    stats["embedding_calls_saved"] = self._streaming_stats.get("embedding_calls_saved", 0)
                    stats["loaded_mongodb"] = stats["mongodb_inserted"] + stats["mongodb_updated"]
                
                logger.info("=" * 80)
                logger.info("Pipeline completed for: %s", standard)
                logger.info("Collected: %d, Processed: %d, Embedded: %d, Loaded: %d", 
                           stats["collected"], stats["processed"], stats["embedded"], stats["loaded_mongodb"])
                if self.config.enable_change_detection:
                    logger.info("Change Detection: Skipped %d (source), %d (content) - Saved %d LLM calls, %d embedding calls",
                               stats["skipped_source_unchanged"], stats["skipped_content_unchanged"],
                               stats["llm_calls_saved"], stats["embedding_calls_saved"])
                if self.config.enable_streaming_saves:
                    logger.info("Streaming Saves: MongoDB (%d inserted, %d updated), Pinecone (%d loaded)",
                               stats["mongodb_inserted"], stats["mongodb_updated"], stats["pinecone_loaded"])
                logger.info("Total Duration: %.2fs", summary["total_duration_seconds"])
                logger.info("=" * 80)

                return stats

            except (ValueError, TypeError, KeyError, RuntimeError) as e:
                logger.error("Pipeline failed for standard %s: %s", standard, e, exc_info=True)
                stats["errors"].append({"stage": "pipeline", "error": str(e)})
                self.metrics.record_error("pipeline", type(e).__name__, str(e))
                return stats

    async def check_health(self) -> dict[str, Any]:
        """Perform health check on all pipeline components.

        Returns:
            Dictionary with health status
        """
        from ..loaders.pinecone_loader import PineconeLoader
        from api.database.mongodb import mongodb_manager
        from openai import AsyncOpenAI

        await self.health_check.check_mongodb(mongodb_manager)

        pinecone_loader = PineconeLoader()
        await self.health_check.check_pinecone(pinecone_loader)

        openai_client = AsyncOpenAI(api_key=self.embedder.client.api_key)
        await self.health_check.check_openai(openai_client)

        return self.health_check.get_health_status()

    async def run_all_standards(self) -> dict[str, dict[str, Any]]:
        """Run pipeline for all compliance standards.

        Dynamically discovers standards from configuration.

        Returns:
            Dictionary mapping standard names to pipeline results
        """
        from ..config.compliance_urls import COMPLIANCE_URLS
        
        standards = list(COMPLIANCE_URLS.keys())

        results = {}

        for standard in standards:
            try:
                result = await self.run_compliance_pipeline(standard)
                results[standard] = result
            except (ValueError, TypeError, KeyError, RuntimeError) as e:
                logger.error("Error running pipeline for %s: %s", standard, e)
                results[standard] = {"error": str(e)}

        return results

    async def run_single_standard(
        self, standard: str, version: str = "latest", run_collection: bool = True
    ) -> dict[str, Any]:
        """Run pipeline for a single compliance standard.

        Args:
            standard: Compliance standard name
            version: Standard version
            run_collection: If True, run collection stage first

        Returns:
            Pipeline results dictionary
        """
        return await self.run_compliance_pipeline(standard, version, run_collection=run_collection)

    def get_metrics_summary(self) -> dict[str, Any]:
        """Get metrics summary.

        Returns:
            Dictionary with metrics summary
        """
        return self.metrics.get_summary()

    async def _process_embed_and_save_streaming(
        self, standard: str, version: str, raw_controls: list[dict[str, Any]]
    ) -> tuple[list[Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
        """Process, embed, and save controls in true streaming fashion (one control at a time).

        This method processes controls one at a time: process → save → embed → save.
        This minimizes memory usage and ensures data is saved immediately.

        Args:
            standard: Compliance standard name
            version: Standard version
            raw_controls: List of raw control dictionaries (if available from collection)

        Returns:
            Tuple of (processed_controls, failed_processing, items_with_embeddings, failed_embedding)
        """
        if self.loader is None:
            self.loader = MongoDBLoader()

        processed_controls = []
        failed_processing = []
        items_with_embeddings = []
        failed_embedding = []
        streaming_batch_size = self.config.streaming_batch_size
        embedding_batch_size = self.config.embedding_batch_size

        if raw_controls:
            raw_data = raw_controls.copy()
            logger.info("Using %d controls from collection - processing these first", len(raw_data))
        else:
            raw_data_result = await self.processor._load_raw_data_async(standard)  # noqa: SLF001
            raw_data = raw_data_result if isinstance(raw_data_result, list) else []
            logger.info("Loaded %d controls from JSON files", len(raw_data))

        logger.info("Processing %d web-collected controls first (PDFs will be loaded separately)", len(raw_data))

        embedding_batch = []

        for i, raw in enumerate(raw_data):
            try:
                control = self.processor.standardize_control(raw, standard, version)

                if not self.processor.validate_control(control):
                    logger.warning("Validation failed for control: %s", raw.get("control_id", "unknown"))
                    failed_processing.append({"raw": raw, "error": "Validation failed"})
                    continue

                doc = control.model_dump(mode="json")
                source_hash = raw.get("_source_hash")
                if source_hash:
                    doc["_source_hash"] = source_hash

                control_id = doc.get("control_id", "unknown")
                logger.debug("Saving control %d/%d: %s", i + 1, len(raw_data), control_id)
                
                success, action = self.loader.save_single_control(doc)
                if success:
                    if action == "inserted":
                        self._streaming_stats["mongodb_inserted"] = self._streaming_stats.get("mongodb_inserted", 0) + 1
                        logger.info("✓ Inserted control %d/%d to MongoDB: %s", i + 1, len(raw_data), control_id)
                    else:
                        self._streaming_stats["mongodb_updated"] = self._streaming_stats.get("mongodb_updated", 0) + 1
                        logger.info("✓ Updated control %d/%d in MongoDB: %s", i + 1, len(raw_data), control_id)
                    
                    processed_controls.append(control)
                    control_dict = doc.copy()
                    embedding_batch.append(control_dict)
                    
                    if len(embedding_batch) >= embedding_batch_size or i == len(raw_data) - 1:
                        logger.info("Processing embedding batch %d (size: %d)", 
                                   len(items_with_embeddings) // embedding_batch_size + 1,
                                   len(embedding_batch))
                        batch_with_embeddings, batch_failed = await self._process_embedding_batch(
                            embedding_batch, []
                        )
                        items_with_embeddings.extend(batch_with_embeddings)
                        failed_embedding.extend(batch_failed)
                        embedding_batch.clear()
                else:
                    control_id = doc.get("control_id", "unknown")
                    logger.error("✗ Failed to save control to MongoDB: %s", control_id)
                    failed_processing.append({"raw": raw, "error": "Failed to save to MongoDB"})

            except Exception as e:  # noqa: BLE001
                logger.error("Error processing control %d/%d: %s", i + 1, len(raw_data), e, exc_info=True)
                failed_processing.append({"raw": raw, "error": str(e)})
                continue

            if (i + 1) % streaming_batch_size == 0:
                logger.info("Progress: Processed and saved %d/%d controls (%d inserted, %d updated)", 
                           i + 1, len(raw_data),
                           self._streaming_stats.get("mongodb_inserted", 0),
                           self._streaming_stats.get("mongodb_updated", 0))

        logger.info("Completed processing %d web-collected controls. Now loading PDFs...", len(processed_controls))
        
        logger.info("Loading PDF controls for standard: %s...", standard)
        pdf_data = await self.processor._load_pdf_data_async(standard)
        if pdf_data:
            logger.info("Loaded %d controls from PDFs, processing now", len(pdf_data))
            
            for i, raw in enumerate(pdf_data):
                try:
                    control = self.processor.standardize_control(raw, standard, version)

                    if not self.processor.validate_control(control):
                        logger.warning("Validation failed for PDF control: %s", raw.get("control_id", "unknown"))
                        failed_processing.append({"raw": raw, "error": "Validation failed"})
                        continue

                    doc = control.model_dump(mode="json")
                    source_hash = raw.get("_source_hash")
                    if source_hash:
                        doc["_source_hash"] = source_hash

                    control_id = doc.get("control_id", "unknown")
                    logger.debug("Saving PDF control %d/%d: %s", i + 1, len(pdf_data), control_id)
                    
                    success, action = self.loader.save_single_control(doc)
                    if success:
                        if action == "inserted":
                            self._streaming_stats["mongodb_inserted"] = self._streaming_stats.get("mongodb_inserted", 0) + 1
                            logger.info("✓ Inserted PDF control %d/%d to MongoDB: %s", i + 1, len(pdf_data), control_id)
                        else:
                            self._streaming_stats["mongodb_updated"] = self._streaming_stats.get("mongodb_updated", 0) + 1
                            logger.info("✓ Updated PDF control %d/%d in MongoDB: %s", i + 1, len(pdf_data), control_id)
                        
                        processed_controls.append(control)
                        control_dict = doc.copy()
                        embedding_batch.append(control_dict)
                        
                        if len(embedding_batch) >= embedding_batch_size or i == len(pdf_data) - 1:
                            logger.info("Processing PDF embedding batch (size: %d)", len(embedding_batch))
                            batch_with_embeddings, batch_failed = await self._process_embedding_batch(
                                embedding_batch, []
                            )
                            items_with_embeddings.extend(batch_with_embeddings)
                            failed_embedding.extend(batch_failed)
                            embedding_batch.clear()
                    else:
                        control_id = doc.get("control_id", "unknown")
                        logger.error("✗ Failed to save PDF control to MongoDB: %s", control_id)
                        failed_processing.append({"raw": raw, "error": "Failed to save to MongoDB"})

                except Exception as e:  # noqa: BLE001
                    logger.error("Error processing PDF control %d/%d: %s", i + 1, len(pdf_data), e, exc_info=True)
                    failed_processing.append({"raw": raw, "error": str(e)})
                    continue
        else:
            logger.debug("No PDF data found for standard: %s (PDF directory: %s)", standard, self.processor.pdf_dir)

        if not raw_data and not pdf_data:
            logger.warning("No raw data found for standard: %s", standard)
            return [], [], [], []

        logger.info("Processed %d controls with streaming saves, %d failed", len(processed_controls), len(failed_processing))
        logger.info("Generated embeddings for %d controls, %d failed", len(items_with_embeddings), len(failed_embedding))
        return processed_controls, failed_processing, items_with_embeddings, failed_embedding

    async def _process_embedding_batch(
        self, batch_dicts: list[dict[str, Any]], _batch_controls: list[Any]
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Process a batch of controls for embedding generation.

        Args:
            batch_dicts: List of control dictionaries
            _batch_controls: List of ComplianceControl objects (unused, kept for API compatibility)

        Returns:
            Tuple of (items_with_embeddings, failed_items)
        """
        if self.config.enable_change_detection and self.change_detector:
            filtered_for_embedding = []
            for control_dict in batch_dicts:
                control_id = control_dict.get("control_id")
                if not control_id:
                    filtered_for_embedding.append(control_dict)
                    continue
                
                existing_doc = None
                if self.change_detector.collection is not None:
                    try:
                        existing_doc = self.change_detector.collection.find_one(
                            {"control_id": control_id},
                            {"content_hash": 1}
                        )
                    except (ValueError, TypeError, KeyError, AttributeError, RuntimeError) as e:
                        logger.warning("Failed to check content hash for %s: %s - generating embedding", control_id, e)
                        filtered_for_embedding.append(control_dict)
                        continue
                
                should_generate, content_hash = self.change_detector.should_generate_embedding(
                    control_dict, control_id, existing_doc
                )
                
                if not should_generate:
                    self._streaming_stats["skipped_content_unchanged"] = self._streaming_stats.get("skipped_content_unchanged", 0) + 1
                    self._streaming_stats["embedding_calls_saved"] = self._streaming_stats.get("embedding_calls_saved", 0) + 1
                    control_dict["_content_hash"] = content_hash
                    logger.debug("Skipping embedding for unchanged content: %s", control_id)
                else:
                    control_dict["_content_hash"] = content_hash
                    filtered_for_embedding.append(control_dict)
            
            batch_dicts = filtered_for_embedding

        if not batch_dicts:
            return [], []

        batch_with_embeddings, batch_failed = await self.embedder.generate_embeddings(batch_dicts, "compliance")
        
        items_with_embeddings = []
        for item in batch_with_embeddings:
            control_id = item.get("control_id")
            if not control_id:
                continue

            embedding = item.get("embedding")
            content_hash = item.get("_content_hash")

            if embedding:
                await self.loader.update_control_embedding_streaming(control_id, embedding, content_hash)
                
                if self.loader.pinecone_loader:
                    success = self.loader.pinecone_loader.upsert_single_control(item)
                    if success:
                        self._streaming_stats["pinecone_loaded"] = self._streaming_stats.get("pinecone_loaded", 0) + 1

            items_with_embeddings.append(item)

        return items_with_embeddings, batch_failed

