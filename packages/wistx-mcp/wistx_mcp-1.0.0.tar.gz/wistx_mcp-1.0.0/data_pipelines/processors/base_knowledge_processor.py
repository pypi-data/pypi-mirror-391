"""Base knowledge processor - abstract base class for domain-specific processors."""

from abc import ABC, abstractmethod
from typing import Any

from ..models.knowledge_article import KnowledgeArticle
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class BaseKnowledgeProcessor(ABC):
    """Base class for domain-specific knowledge processors.
    
    Provides shared functionality for processing knowledge articles from raw data.
    Domain-specific processors inherit from this and implement abstract methods.
    """

    def __init__(self, domain: str, save_intermediate: bool = False):
        """Initialize base knowledge processor.
        
        Args:
            domain: Knowledge domain (compliance, finops, architecture, etc.)
            save_intermediate: If True, save intermediate files (checkpointing mode)
        """
        self.domain = domain
        self.save_intermediate = save_intermediate

    @abstractmethod
    def process_raw_data(self, raw_data: dict[str, Any]) -> KnowledgeArticle:
        """Process raw data into KnowledgeArticle.
        
        Args:
            raw_data: Raw data from collector
            
        Returns:
            Processed KnowledgeArticle
        """

    @abstractmethod
    def extract_structured_data(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        """Extract domain-specific structured data.
        
        Args:
            raw_data: Raw data
            
        Returns:
            Structured data dictionary
        """

    def validate_article(self, article: KnowledgeArticle) -> bool:
        """Validate article meets quality standards.
        
        Args:
            article: Article to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not article.title or len(article.title) < 10:
            logger.warning("Article title too short: %s", article.title[:50])
            return False

        if not article.summary or len(article.summary) < 50:
            logger.warning("Article summary too short: %s", article.summary[:50])
            return False

        if not article.content or len(article.content) < 100:
            logger.warning("Article content too short: %s", article.content[:50])
            return False

        if not article.source_url:
            logger.warning("Article missing source_url: %s", article.article_id)
            return False

        if article.quality_score and article.quality_score < 70:
            logger.warning(
                "Article quality score below threshold: %.2f < 70 for %s",
                article.quality_score,
                article.article_id,
            )
            return False

        return True

    def generate_article_id(
        self, title: str, domain: str, subdomain: str, content_type: str
    ) -> str:
        """Generate unique article ID from components.
        
        Args:
            title: Article title
            domain: Knowledge domain
            subdomain: Subdomain
            content_type: Content type
            
        Returns:
            Unique article ID
        """
        import hashlib
        import re

        base_id = f"{domain}-{subdomain}-{content_type}"
        title_slug = re.sub(r"[^a-z0-9]+", "-", title.lower())[:50]
        title_slug = title_slug.strip("-")

        article_id = f"{base_id}-{title_slug}"

        if len(article_id) > 200:
            hash_suffix = hashlib.md5(title.encode()).hexdigest()[:8]
            article_id = f"{base_id}-{hash_suffix}"

        return article_id

    def extract_tags(self, content: str, title: str) -> list[str]:
        """Extract tags from content and title.
        
        Args:
            content: Article content
            title: Article title
            
        Returns:
            List of extracted tags
        """
        import re

        text = f"{title} {content}".lower()
        words = re.findall(r"\b[a-z]{4,}\b", text)
        word_freq: dict[str, int] = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1

        common_words = {
            "the",
            "and",
            "for",
            "are",
            "but",
            "not",
            "you",
            "all",
            "can",
            "her",
            "was",
            "one",
            "our",
            "out",
            "day",
            "get",
            "has",
            "him",
            "his",
            "how",
            "its",
            "may",
            "new",
            "now",
            "old",
            "see",
            "two",
            "way",
            "who",
            "boy",
            "did",
            "use",
            "she",
            "that",
            "with",
            "from",
            "have",
            "will",
        }

        filtered_words = [
            word for word, freq in word_freq.items() if word not in common_words and freq >= 2
        ]
        sorted_words = sorted(filtered_words, key=lambda x: word_freq[x], reverse=True)

        return sorted_words[:10]

