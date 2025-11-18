"""Indexing service for managing user-provided resource indexing jobs."""

import asyncio
import logging
from datetime import datetime
from typing import Any, Optional

from bson import ObjectId

from api.database.mongodb import mongodb_manager
from api.models.indexing import IndexedResource, ResourceStatus, ResourceType, generate_resource_id
from api.services.quota_service import QuotaExceededError, quota_service

logger = logging.getLogger(__name__)


class IndexingService:
    """Service for managing indexing jobs and background processing."""

    def __init__(self):
        """Initialize indexing service."""
        self.running_jobs: dict[str, asyncio.Task] = {}

    async def create_resource(
        self,
        user_id: str,
        resource_type: ResourceType,
        name: str,
        organization_id: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[list[str]] = None,
        repo_url: Optional[str] = None,
        branch: Optional[str] = None,
        documentation_url: Optional[str] = None,
        include_patterns: Optional[list[str]] = None,
        exclude_patterns: Optional[list[str]] = None,
        document_url: Optional[str] = None,
        document_type: Optional[str] = None,
        github_token: Optional[str] = None,
    ) -> IndexedResource:
        """Create a new indexed resource.

        Args:
            user_id: User ID
            resource_type: Type of resource
            name: Resource name
            organization_id: Organization ID (optional)
            description: Resource description
            tags: Tags for categorization
            repo_url: GitHub repository URL (for repository type)
            branch: GitHub branch name
            documentation_url: Documentation URL (for documentation type)
            include_patterns: URL patterns to include
            exclude_patterns: URL patterns to exclude
            document_url: Document URL (for document type)
            document_type: Document type
            github_token: GitHub token (for private repos)

        Returns:
            Created IndexedResource

        Raises:
            ValueError: If required fields are missing for resource type
        """
        resource_id = generate_resource_id()

        if resource_type == ResourceType.REPOSITORY and not repo_url:
            raise ValueError("repo_url is required for repository type")
        if resource_type == ResourceType.DOCUMENTATION and not documentation_url:
            raise ValueError("documentation_url is required for documentation type")
        if resource_type == ResourceType.DOCUMENT and not document_url:
            raise ValueError("document_url is required for document type")

        github_token_encrypted = None
        if github_token:
            github_token_encrypted = self._encrypt_token(github_token)

        resource = IndexedResource(
            resource_id=resource_id,
            user_id=user_id,
            organization_id=organization_id,
            resource_type=resource_type,
            status=ResourceStatus.PENDING,
            progress=0.0,
            name=name,
            description=description,
            tags=tags or [],
            repo_url=repo_url,
            branch=branch or "main",
            documentation_url=documentation_url,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            document_url=document_url,
            document_type=document_type,
            github_token_encrypted=github_token_encrypted,
        )

        db = mongodb_manager.get_database()
        collection = db.indexed_resources

        resource_dict = resource.to_dict()
        collection.insert_one(resource_dict)

        logger.info(
            "Created indexed resource: %s (type: %s, user: %s)",
            resource_id,
            resource_type,
            user_id,
        )

        return resource

    async def start_indexing_job(
        self,
        resource_id: str,
        user_id: str,
        plan: str,
    ) -> None:
        """Start indexing job in background.

        Args:
            resource_id: Resource ID
            user_id: User ID
            plan: User's plan

        Raises:
            ValueError: If resource not found
            QuotaExceededError: If quota exceeded
        """
        resource = await self.get_resource(resource_id, user_id)
        if not resource:
            raise ValueError(f"Resource not found: {resource_id}")

        if resource.status in [ResourceStatus.INDEXING, ResourceStatus.COMPLETED]:
            logger.warning(
                "Resource %s already in status: %s",
                resource_id,
                resource.status,
            )
            return

        await quota_service.check_indexing_quota(
            user_id=user_id,
            plan=plan,
            estimated_storage_mb=0.0,
        )

        await self._update_resource_status(
            resource_id,
            status=ResourceStatus.INDEXING,
            progress=0.0,
        )

        task = asyncio.create_task(
            self._run_indexing_job(resource_id, resource, user_id, plan)
        )
        self.running_jobs[resource_id] = task

        logger.info("Started indexing job: %s", resource_id)

    async def _run_indexing_job(
        self,
        resource_id: str,
        resource: IndexedResource,
        user_id: str,
        plan: str,
    ) -> None:
        """Run indexing job with progress updates.

        Args:
            resource_id: Resource ID
            resource: IndexedResource instance
            user_id: User ID
            plan: User's plan
        """
        try:
            if resource.resource_type == ResourceType.REPOSITORY:
                await self._index_repository(resource_id, resource, user_id, plan)
            elif resource.resource_type == ResourceType.DOCUMENTATION:
                await self._index_documentation(resource_id, resource, user_id, plan)
            elif resource.resource_type == ResourceType.DOCUMENT:
                await self._index_document(resource_id, resource, user_id, plan)
            else:
                raise ValueError(f"Unsupported resource type: {resource.resource_type}")

            await self._update_resource_status(
                resource_id,
                status=ResourceStatus.COMPLETED,
                progress=100.0,
                indexed_at=datetime.utcnow(),
            )

            logger.info("Completed indexing job: %s", resource_id)

        except QuotaExceededError as e:
            await self._update_resource_status(
                resource_id,
                status=ResourceStatus.FAILED,
                error_message=str(e),
                error_details={"error_type": "quota_exceeded"},
            )
            logger.error("Indexing job failed due to quota: %s", resource_id)
            raise
        except (ValueError, RuntimeError, ConnectionError, TimeoutError) as e:
            await self._update_resource_status(
                resource_id,
                status=ResourceStatus.FAILED,
                error_message=str(e),
                error_details={"error_type": type(e).__name__},
            )
            logger.error("Indexing job failed: %s - %s", resource_id, e, exc_info=True)
            raise
        except Exception as e:
            await self._update_resource_status(
                resource_id,
                status=ResourceStatus.FAILED,
                error_message="Unexpected error occurred",
                error_details={"error_type": "unexpected_error"},
            )
            logger.error("Unexpected error in indexing job %s: %s", resource_id, e, exc_info=True)
            raise RuntimeError(f"Unexpected error in indexing job: {e}") from e

        finally:
            if resource_id in self.running_jobs:
                del self.running_jobs[resource_id]

    async def _index_repository(
        self,
        resource_id: str,
        resource: IndexedResource,
        user_id: str,
        plan: str,
    ) -> None:
        """Index a GitHub repository.

        Args:
            resource_id: Resource ID
            resource: IndexedResource instance
            user_id: User ID
            plan: User's plan
        """
        from api.services.github_service import github_service

        github_token = None
        if resource.github_token_encrypted:
            github_token = self._decrypt_token(resource.github_token_encrypted)

        await self._update_resource_status(resource_id, progress=10.0)

        await github_service.index_repository(
            resource_id=resource_id,
            repo_url=resource.repo_url or "",
            branch=resource.branch or "main",
            user_id=user_id,
            github_token=github_token,
            progress_callback=lambda p: self._update_resource_progress(resource_id, p),
        )

    async def _index_documentation(
        self,
        resource_id: str,
        resource: IndexedResource,
        user_id: str,
        plan: str,
    ) -> None:
        """Index a documentation website.

        Args:
            resource_id: Resource ID
            resource: IndexedResource instance
            user_id: User ID
            plan: User's plan
        """
        import asyncio

        await self._update_resource_status(resource_id, progress=10.0)

        from crawl4ai import AsyncWebCrawler
        from data_pipelines.processors.llm_knowledge_extractor import LLMKnowledgeExtractor
        from data_pipelines.models.knowledge_article import Domain, ContentType
        from api.services.github_service import github_service

        url = resource.documentation_url or ""
        articles_created = 0

        async with AsyncWebCrawler() as crawler:
            try:
                crawl_result = await crawler.arun(url=url, bypass_cache=True)
                markdown_content = crawl_result.markdown or ""
                html_content = crawl_result.html or ""

                if markdown_content or html_content:
                    content = markdown_content if markdown_content else html_content

                    extractor = LLMKnowledgeExtractor()
                    articles = await extractor.extract_articles(
                        content=content,
                        domain=Domain.DEVOPS.value,
                        subdomain="documentation",
                        source_url=url,
                        prefer_markdown=True,
                        markdown_content=markdown_content if markdown_content else None,
                    )

                    await self._update_resource_status(resource_id, progress=50.0)

                    for article_data in articles:
                        article = article_data
                        if isinstance(article_data, dict):
                            from data_pipelines.models.knowledge_article import KnowledgeArticle

                            article = KnowledgeArticle(
                                article_id=f"doc_{resource_id}_{articles_created}",
                                domain=Domain.DEVOPS,
                                subdomain="documentation",
                                content_type=ContentType.GUIDE,
                                title=article_data.get("title", "Documentation Page"),
                                summary=article_data.get("summary", ""),
                                content=article_data.get("content", ""),
                                source_url=url,
                                user_id=user_id,
                                visibility="user",
                                source_type="documentation",
                                resource_id=resource_id,
                            )

                        await github_service._store_article(article)
                        articles_created += 1

                    await self._update_resource_status(
                        resource_id,
                        progress=90.0,
                        articles_indexed=articles_created,
                    )

            except (ValueError, RuntimeError, ConnectionError, TimeoutError, AttributeError) as e:
                logger.error("Error indexing documentation: %s", e, exc_info=True)
                raise
            except Exception as e:
                logger.error("Unexpected error indexing documentation: %s", e, exc_info=True)
                raise RuntimeError(f"Unexpected error indexing documentation: {e}") from e

        await self._update_resource_status(
            resource_id,
            articles_indexed=articles_created,
            storage_mb=0.0,
        )

    async def _index_document(
        self,
        resource_id: str,
        resource: IndexedResource,
        user_id: str,
        plan: str,
    ) -> None:
        """Index a single document.

        Args:
            resource_id: Resource ID
            resource: IndexedResource instance
            user_id: User ID
            plan: User's plan
        """
        import asyncio
        import tempfile
        from pathlib import Path

        await self._update_resource_status(resource_id, progress=10.0)

        from data_pipelines.processors.document_processor import DocumentProcessor
        from data_pipelines.processors.llm_knowledge_extractor import LLMKnowledgeExtractor
        from data_pipelines.models.knowledge_article import Domain, ContentType, KnowledgeArticle
        from api.services.github_service import github_service
        from api.utils.file_handler import file_handler

        file_path = Path(resource.document_url or "")

        if not file_path.exists():
            raise ValueError(f"Document file not found: {file_path}")

        is_temporary_file = file_handler.is_temporary_file(file_path)

        try:
            processor = DocumentProcessor()

            loop = asyncio.get_event_loop()
            doc_content = await loop.run_in_executor(
                None,
                lambda: processor.process_document(
                    content=file_path,
                    source_url=str(file_path),
                    content_type=resource.document_type or "auto",
                ),
            )

            await self._update_resource_status(resource_id, progress=50.0)

            extractor = LLMKnowledgeExtractor()
            articles = await extractor.extract_articles(
                content=doc_content.get("text", "") or doc_content.get("markdown", ""),
                domain=Domain.DEVOPS.value,
                subdomain="document",
                source_url=str(file_path),
                prefer_markdown=True,
                markdown_content=doc_content.get("markdown"),
            )

            articles_created = 0
            for idx, article_data in enumerate(articles):
                if isinstance(article_data, dict):
                    article = KnowledgeArticle(
                        article_id=f"doc_{resource_id}_{idx}",
                        domain=Domain.DEVOPS,
                        subdomain="document",
                        content_type=ContentType.GUIDE,
                        title=article_data.get("title", file_path.name),
                        summary=article_data.get("summary", ""),
                        content=article_data.get("content", ""),
                        source_url=str(file_path),
                        user_id=user_id,
                        visibility="user",
                        source_type="document",
                        resource_id=resource_id,
                    )
                else:
                    article = article_data
                    article.user_id = user_id
                    article.visibility = "user"
                    article.source_type = "document"
                    article.resource_id = resource_id

                await github_service._store_article(article)
                articles_created += 1

            file_size_mb = file_path.stat().st_size / (1024 * 1024) if file_path.exists() else 0.0

            await self._update_resource_status(
                resource_id,
                articles_indexed=articles_created,
                storage_mb=file_size_mb,
            )

        finally:
            if is_temporary_file and file_path.exists():
                file_handler.cleanup_file(file_path)
                logger.info("Cleaned up temporary file after indexing: %s", file_path)

    async def get_resource(self, resource_id: str, user_id: str) -> Optional[IndexedResource]:
        """Get resource by ID (with user ownership check).

        Args:
            resource_id: Resource ID
            user_id: User ID

        Returns:
            IndexedResource or None
        """
        db = mongodb_manager.get_database()
        collection = db.indexed_resources

        doc = collection.find_one(
            {
                "_id": resource_id,
                "user_id": ObjectId(user_id),
            }
        )

        if not doc:
            return None

        return IndexedResource.from_dict(doc)

    async def list_resources(
        self,
        user_id: str,
        organization_id: Optional[str] = None,
        resource_type: Optional[ResourceType] = None,
        status: Optional[ResourceStatus] = None,
    ) -> list[IndexedResource]:
        """List resources for user.

        Args:
            user_id: User ID
            organization_id: Organization ID (optional)
            resource_type: Filter by resource type
            status: Filter by status

        Returns:
            List of IndexedResource
        """
        db = mongodb_manager.get_database()
        collection = db.indexed_resources

        query: dict[str, Any] = {"user_id": ObjectId(user_id)}

        if organization_id:
            query["organization_id"] = ObjectId(organization_id)

        if resource_type:
            query["resource_type"] = resource_type.value

        if status:
            query["status"] = status.value

        docs = list(collection.find(query).sort("created_at", -1))

        return [IndexedResource.from_dict(doc) for doc in docs]

    async def delete_resource(self, resource_id: str, user_id: str) -> bool:
        """Delete a resource and its indexed content.

        Args:
            resource_id: Resource ID
            user_id: User ID

        Returns:
            True if deleted, False otherwise
        """
        resource = await self.get_resource(resource_id, user_id)
        if not resource:
            return False

        if resource_id in self.running_jobs:
            task = self.running_jobs[resource_id]
            task.cancel()
            del self.running_jobs[resource_id]

        await self._update_resource_status(resource_id, status=ResourceStatus.DELETED)

        db = mongodb_manager.get_database()

        knowledge_collection = db.knowledge_articles
        knowledge_collection.delete_many({"resource_id": resource_id})

        resources_collection = db.indexed_resources
        resources_collection.delete_one({"_id": resource_id})

        logger.info("Deleted resource: %s", resource_id)

        return True

    async def _update_resource_status(
        self,
        resource_id: str,
        status: Optional[ResourceStatus] = None,
        progress: Optional[float] = None,
        error_message: Optional[str] = None,
        error_details: Optional[dict[str, Any]] = None,
        indexed_at: Optional[datetime] = None,
        articles_indexed: Optional[int] = None,
        storage_mb: Optional[float] = None,
    ) -> None:
        """Update resource status and progress.

        Args:
            resource_id: Resource ID
            status: New status
            progress: New progress percentage
            error_message: Error message (if failed)
            error_details: Error details
            indexed_at: Indexing completion time
        """
        db = mongodb_manager.get_database()
        collection = db.indexed_resources

        update: dict[str, Any] = {"updated_at": datetime.utcnow()}

        if status:
            update["status"] = status.value

        if progress is not None:
            update["progress"] = progress

        if error_message:
            update["error_message"] = error_message

        if error_details:
            update["error_details"] = error_details

        if indexed_at:
            update["indexed_at"] = indexed_at

        if articles_indexed is not None:
            update["articles_indexed"] = articles_indexed

        if storage_mb is not None:
            update["storage_mb"] = storage_mb

        collection.update_one({"_id": resource_id}, {"$set": update})

    async def _update_resource_progress(self, resource_id: str, progress: float) -> None:
        """Update resource progress.

        Args:
            resource_id: Resource ID
            progress: Progress percentage (0-100)
        """
        await self._update_resource_status(resource_id, progress=progress)

    def _encrypt_token(self, token: str) -> str:
        """Encrypt GitHub token for storage.

        Args:
            token: Plain token

        Returns:
            Encrypted token

        Note: Uses Fernet symmetric encryption with secret key.
        """
        from api.config import settings
        from cryptography.fernet import Fernet
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        import base64

        password = settings.secret_key.encode()
        salt = b"wistx_github_token_salt"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        fernet = Fernet(key)
        return fernet.encrypt(token.encode()).decode()

    def _decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt GitHub token.

        Args:
            encrypted_token: Encrypted token

        Returns:
            Plain token
        """
        from api.config import settings
        from cryptography.fernet import Fernet
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        import base64

        password = settings.secret_key.encode()
        salt = b"wistx_github_token_salt"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        fernet = Fernet(key)
        return fernet.decrypt(encrypted_token.encode()).decode()


indexing_service = IndexingService()

