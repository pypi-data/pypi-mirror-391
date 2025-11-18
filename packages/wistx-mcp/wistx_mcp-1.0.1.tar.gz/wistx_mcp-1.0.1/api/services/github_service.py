"""GitHub integration service for repository indexing."""

import asyncio
import logging
import os
import tempfile
from pathlib import Path
from typing import Any, Callable, Optional
from urllib.parse import urlparse

from github import Github
from github.GithubException import GithubException
from git import Repo

from bson import ObjectId

from api.database.mongodb import mongodb_manager
from api.config import settings
from data_pipelines.models.knowledge_article import ContentType, Domain, KnowledgeArticle
from data_pipelines.processors.embedding_generator import EmbeddingGenerator
from openai import OpenAI
from wistx_mcp.tools.lib.retry_utils import with_timeout_and_retry

logger = logging.getLogger(__name__)


class GitHubService:
    """Service for GitHub repository indexing."""

    def __init__(self):
        """Initialize GitHub service."""
        self.embedding_generator = EmbeddingGenerator()

    async def validate_repository_access(
        self,
        repo_url: str,
        github_token: Optional[str] = None,
    ) -> bool:
        """Validate access to repository.

        Args:
            repo_url: GitHub repository URL
            github_token: GitHub personal access token (for private repos)

        Returns:
            True if accessible, False otherwise
        """
        try:
            repo_info = self._parse_repo_url(repo_url)
            if not repo_info:
                return False

            github_client = self._get_github_client(github_token)
            
            async def get_repo():
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(
                    None,
                    github_client.get_repo,
                    f"{repo_info['owner']}/{repo_info['name']}",
                )
            
            repo = await with_timeout_and_retry(
                get_repo,
                timeout_seconds=10.0,
                max_attempts=3,
                retryable_exceptions=(RuntimeError, ConnectionError, TimeoutError),
            )

            return repo is not None
        except GithubException as e:
            logger.warning("GitHub access validation failed: %s", e)
            return False
        except (ValueError, RuntimeError, ConnectionError, TimeoutError) as e:
            logger.error("Error validating repository access: %s", e, exc_info=True)
            return False
        except Exception as e:
            logger.error("Unexpected error validating repository access: %s", e, exc_info=True)
            return False

    async def index_repository(
        self,
        resource_id: str,
        repo_url: str,
        branch: str,
        user_id: str,
        github_token: Optional[str] = None,
        progress_callback: Optional[Callable[[float], None]] = None,
    ) -> None:
        """Index a GitHub repository.

        Args:
            resource_id: Resource ID
            repo_url: GitHub repository URL
            branch: Branch name
            user_id: User ID
            github_token: GitHub token (for private repos)
            progress_callback: Callback for progress updates (0-100)

        Raises:
            ValueError: If repository URL is invalid
            GithubException: If GitHub API fails
        """
        repo_info = self._parse_repo_url(repo_url)
        if not repo_info:
            raise ValueError(f"Invalid repository URL: {repo_url}")

        github_client = self._get_github_client(github_token)
        
        async def get_repo():
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None,
                github_client.get_repo,
                f"{repo_info['owner']}/{repo_info['name']}",
            )
        
        repo = await with_timeout_and_retry(
            get_repo,
            timeout_seconds=10.0,
            max_attempts=3,
            retryable_exceptions=(RuntimeError, ConnectionError, TimeoutError),
        )

        if progress_callback:
            progress_callback(20.0)

        with tempfile.TemporaryDirectory() as temp_dir:
            clone_url = repo.clone_url
            if github_token:
                parsed = urlparse(clone_url)
                clone_url = f"{parsed.scheme}://{github_token}@{parsed.netloc}{parsed.path}"

            logger.info("Cloning repository: %s (branch: %s)", repo_url, branch)

            async def clone_repo():
                loop = asyncio.get_event_loop()
                repo_path = Path(temp_dir) / repo.name
                return await loop.run_in_executor(
                    None,
                    lambda: Repo.clone_from(clone_url, str(repo_path), branch=branch, depth=1),
                )
            
            repo_path = Path(temp_dir) / repo.name
            cloned_repo = await with_timeout_and_retry(
                clone_repo,
                timeout_seconds=60.0,
                max_attempts=2,
                retryable_exceptions=(RuntimeError, ConnectionError, TimeoutError),
            )

            if progress_callback:
                progress_callback(40.0)

            files_processed = 0
            articles_created = 0
            total_size_mb = 0.0

            supported_extensions = {
                ".py",
                ".ts",
                ".js",
                ".tsx",
                ".jsx",
                ".tf",
                ".yaml",
                ".yml",
                ".json",
                ".md",
                ".rst",
                ".txt",
            }

            for file_path in self._get_code_files(repo_path, supported_extensions):
                try:
                    relative_path = file_path.relative_to(repo_path)
                    file_content = file_path.read_text(encoding="utf-8", errors="ignore")
                    file_size_mb = len(file_content.encode("utf-8")) / (1024 * 1024)
                    total_size_mb += file_size_mb

                    article = await self._create_article_from_file(
                        file_path=relative_path,
                        content=file_content,
                        repo_url=repo_url,
                        branch=branch,
                        user_id=user_id,
                        resource_id=resource_id,
                    )

                    if article:
                        articles_created += 1

                    files_processed += 1

                    if files_processed % 10 == 0 and progress_callback:
                        progress = 40.0 + (files_processed / max(1, len(list(repo_path.rglob("*")))) * 50)
                        progress_callback(min(progress, 90.0))

                except Exception as e:
                    logger.warning("Error processing file %s: %s", file_path, e)
                    continue

            if progress_callback:
                progress_callback(95.0)

            db = mongodb_manager.get_database()
            collection = db.indexed_resources

            collection.update_one(
                {"_id": resource_id},
                {
                    "$set": {
                        "articles_indexed": articles_created,
                        "files_processed": files_processed,
                        "total_files": files_processed,
                        "storage_mb": total_size_mb,
                    }
                },
            )

            if progress_callback:
                progress_callback(100.0)

            logger.info(
                "Indexed repository: %s - %d files, %d articles, %.2f MB",
                repo_url,
                files_processed,
                articles_created,
                total_size_mb,
            )

    def _parse_repo_url(self, repo_url: str) -> Optional[dict[str, str]]:
        """Parse GitHub repository URL.

        Args:
            repo_url: Repository URL

        Returns:
            Dictionary with owner and name, or None if invalid
        """
        try:
            parsed = urlparse(repo_url)
            path_parts = parsed.path.strip("/").split("/")

            if len(path_parts) >= 2:
                return {
                    "owner": path_parts[0],
                    "name": path_parts[1].replace(".git", ""),
                }

            return None
        except Exception as e:
            logger.error("Error parsing repo URL: %s", e)
            return None

    def _get_github_client(self, github_token: Optional[str] = None) -> Github:
        """Get GitHub API client.

        Args:
            github_token: GitHub token (optional)

        Returns:
            Github client instance
        """
        if github_token:
            return Github(github_token)
        return Github()

    def _get_code_files(self, repo_path: Path, extensions: set[str]) -> list[Path]:
        """Get all code files from repository.

        Args:
            repo_path: Repository root path
            extensions: Set of file extensions to include

        Returns:
            List of file paths
        """
        files = []
        ignore_dirs = {".git", "__pycache__", "node_modules", ".venv", "venv", ".env"}

        for file_path in repo_path.rglob("*"):
            if file_path.is_file():
                if file_path.suffix.lower() in extensions:
                    relative = file_path.relative_to(repo_path)
                    if not any(part in ignore_dirs for part in relative.parts):
                        files.append(file_path)

        return files

    async def _create_article_from_file(
        self,
        file_path: Path,
        content: str,
        repo_url: str,
        branch: str,
        user_id: str,
        resource_id: str,
    ) -> Optional[KnowledgeArticle]:
        """Create knowledge article from code file.

        Args:
            file_path: File path relative to repo root
            content: File content
            repo_url: Repository URL
            branch: Branch name
            user_id: User ID
            resource_id: Resource ID

        Returns:
            KnowledgeArticle or None
        """
        try:
            file_url = f"{repo_url}/blob/{branch}/{file_path}"

            article_id = f"repo_{resource_id}_{file_path.stem}_{hash(str(file_path)) % 100000}"

            domain = self._detect_domain(file_path, content)
            content_type = self._detect_content_type(file_path)

            title = f"{file_path.name} - {repo_url.split('/')[-1]}"
            summary = self._extract_summary(content, file_path.suffix)

            article = KnowledgeArticle(
                article_id=article_id,
                domain=domain,
                subdomain="code",
                content_type=content_type,
                title=title,
                summary=summary,
                content=content[:10000],
                source_url=file_url,
                user_id=user_id,
                visibility="user",
                source_type="repository",
                resource_id=resource_id,
                tags=[file_path.suffix[1:] if file_path.suffix else "code"],
            )

            await self._store_article(article)

            return article

        except Exception as e:
            logger.warning("Error creating article from file %s: %s", file_path, e)
            return None

    def _detect_domain(self, file_path: Path, content: str) -> Domain:
        """Detect domain from file path and content.

        Args:
            file_path: File path
            content: File content

        Returns:
            Domain enum
        """
        path_str = str(file_path).lower()

        if "terraform" in path_str or file_path.suffix == ".tf":
            return Domain.INFRASTRUCTURE
        if "kubernetes" in path_str or "k8s" in path_str:
            return Domain.DEVOPS
        if "security" in path_str or "auth" in path_str:
            return Domain.SECURITY
        if "cost" in path_str or "billing" in path_str:
            return Domain.FINOPS

        content_lower = content.lower()
        if "compliance" in content_lower or "pci" in content_lower or "hipaa" in content_lower:
            return Domain.COMPLIANCE

        return Domain.DEVOPS

    def _detect_content_type(self, file_path: Path) -> ContentType:
        """Detect content type from file path.

        Args:
            file_path: File path

        Returns:
            ContentType enum
        """
        if file_path.suffix == ".md" or file_path.suffix == ".rst":
            return ContentType.GUIDE
        if file_path.suffix == ".tf":
            return ContentType.REFERENCE
        return ContentType.REFERENCE

    def _extract_summary(self, content: str, extension: str) -> str:
        """Extract summary from file content.

        Args:
            content: File content
            extension: File extension

        Returns:
            Summary string
        """
        lines = content.split("\n")[:20]
        summary = "\n".join(lines)

        if len(summary) > 500:
            summary = summary[:500] + "..."

        return summary or "Code file from repository"

    async def _store_article(self, article: KnowledgeArticle) -> None:
        """Store article in MongoDB and Pinecone.

        Args:
            article: KnowledgeArticle to store
        """
        from pinecone import Pinecone

        db = mongodb_manager.get_database()
        collection = db.knowledge_articles

        searchable_text = article.to_searchable_text()

        embedding = await self._generate_embedding(searchable_text)

        article.embedding = embedding

        article_dict = article.model_dump()
        article_dict["_id"] = article.article_id
        if article.user_id:
            article_dict["user_id"] = ObjectId(article.user_id)
        if article.organization_id:
            article_dict["organization_id"] = ObjectId(article.organization_id)

        collection.replace_one(
            {"_id": article.article_id},
            article_dict,
            upsert=True,
        )

        pc = Pinecone(api_key=settings.pinecone_api_key)
        index = pc.Index(settings.pinecone_index_name)

        metadata = {
            "article_id": article.article_id,
            "domain": article.domain.value,
            "subdomain": article.subdomain,
            "content_type": article.content_type.value,
            "title": article.title,
            "source_url": article.source_url,
            "visibility": article.visibility,
            "source_type": article.source_type,
        }

        if article.user_id:
            metadata["user_id"] = article.user_id
        if article.organization_id:
            metadata["organization_id"] = article.organization_id
        if article.resource_id:
            metadata["resource_id"] = article.resource_id

        index.upsert(
            vectors=[
                {
                    "id": article.article_id,
                    "values": embedding,
                    "metadata": metadata,
                }
            ]
        )

    async def _generate_embedding(self, text: str) -> list[float]:
        """Generate embedding for text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        import asyncio

        client = OpenAI(api_key=settings.openai_api_key)

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.embeddings.create(
                model="text-embedding-3-small",
                input=text,
            ),
        )
        return response.data[0].embedding


github_service = GitHubService()

