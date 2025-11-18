"""Indexing models for user-provided resources."""

import secrets
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from bson import ObjectId
from pydantic import BaseModel, Field


class ResourceType(str, Enum):
    """Type of indexed resource."""

    REPOSITORY = "repository"
    DOCUMENTATION = "documentation"
    DOCUMENT = "document"
    URL = "url"


class ResourceStatus(str, Enum):
    """Status of indexing resource."""

    PENDING = "pending"
    INDEXING = "indexing"
    COMPLETED = "completed"
    FAILED = "failed"
    DELETED = "deleted"
    CANCELLED = "cancelled"


class IndexedResource(BaseModel):
    """Model for tracking user-indexed resources."""

    resource_id: str = Field(
        ...,
        description="Unique resource identifier (e.g., 'res_abc123')",
        min_length=10,
        max_length=100,
    )
    user_id: str = Field(..., description="User ID who owns this resource")
    organization_id: Optional[str] = Field(
        default=None,
        description="Organization ID (if resource is shared within org)",
    )
    resource_type: ResourceType = Field(..., description="Type of resource")
    status: ResourceStatus = Field(
        default=ResourceStatus.PENDING,
        description="Current indexing status",
    )
    progress: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Indexing progress percentage (0-100)",
    )

    name: str = Field(..., description="Resource name", min_length=1, max_length=200)
    description: Optional[str] = Field(
        default=None,
        description="Resource description",
        max_length=1000,
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags for categorization",
        max_items=20,
    )

    repo_url: Optional[str] = Field(
        default=None,
        description="GitHub repository URL (for repository type)",
    )
    branch: Optional[str] = Field(
        default=None,
        description="GitHub branch name (default: main)",
    )
    documentation_url: Optional[str] = Field(
        default=None,
        description="Documentation website URL (for documentation type)",
    )
    include_patterns: Optional[list[str]] = Field(
        default=None,
        description="URL patterns to include (for documentation)",
    )
    exclude_patterns: Optional[list[str]] = Field(
        default=None,
        description="URL patterns to exclude (for documentation)",
    )
    document_url: Optional[str] = Field(
        default=None,
        description="Document URL or file path (for document type)",
    )
    document_type: Optional[str] = Field(
        default=None,
        description="Document type (pdf, docx, markdown, etc.)",
    )

    articles_indexed: int = Field(
        default=0,
        ge=0,
        description="Number of knowledge articles created from this resource",
    )
    files_processed: int = Field(
        default=0,
        ge=0,
        description="Number of files processed",
    )
    total_files: Optional[int] = Field(
        default=None,
        description="Total number of files to process (if known)",
    )
    storage_mb: float = Field(
        default=0.0,
        ge=0.0,
        description="Storage used by this resource in MB",
    )

    error_message: Optional[str] = Field(
        default=None,
        description="Error message if indexing failed",
    )
    error_details: Optional[dict[str, Any]] = Field(
        default=None,
        description="Detailed error information",
    )

    github_token_encrypted: Optional[str] = Field(
        default=None,
        description="Encrypted GitHub token (for private repos)",
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp",
    )
    indexed_at: Optional[datetime] = Field(
        default=None,
        description="Completion timestamp",
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for MongoDB storage.

        Returns:
            Dictionary representation
        """
        data = self.model_dump(exclude={"resource_id"})
        data["_id"] = self.resource_id
        data["user_id"] = ObjectId(self.user_id) if self.user_id else None
        data["organization_id"] = ObjectId(self.organization_id) if self.organization_id else None
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "IndexedResource":
        """Create from MongoDB document.

        Args:
            data: MongoDB document

        Returns:
            IndexedResource instance
        """
        if "_id" in data:
            data["resource_id"] = str(data["_id"])
        if "user_id" in data and isinstance(data["user_id"], ObjectId):
            data["user_id"] = str(data["user_id"])
        if "organization_id" in data and isinstance(data["organization_id"], ObjectId):
            data["organization_id"] = str(data["organization_id"])
        return cls(**data)


def generate_resource_id() -> str:
    """Generate unique resource ID.

    Returns:
        Resource ID string (e.g., 'res_abc123def456')
    """
    return f"res_{secrets.token_hex(12)}"

