"""Response models for indexing endpoints."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from api.models.indexing import ResourceStatus, ResourceType


class IndexResourceResponse(BaseModel):
    """Response model for indexing operations."""

    resource_id: str = Field(..., description="Resource ID")
    status: ResourceStatus = Field(..., description="Current status")
    progress: float = Field(..., ge=0.0, le=100.0, description="Progress percentage")
    message: str = Field(..., description="Status message")


class ResourceDetailResponse(BaseModel):
    """Response model for resource details."""

    resource_id: str = Field(..., description="Resource ID")
    user_id: str = Field(..., description="User ID")
    organization_id: Optional[str] = Field(default=None, description="Organization ID")
    resource_type: ResourceType = Field(..., description="Resource type")
    status: ResourceStatus = Field(..., description="Current status")
    progress: float = Field(..., ge=0.0, le=100.0, description="Progress percentage")

    name: str = Field(..., description="Resource name")
    description: Optional[str] = Field(default=None, description="Resource description")
    tags: list[str] = Field(default_factory=list, description="Tags")

    repo_url: Optional[str] = Field(default=None, description="Repository URL")
    branch: Optional[str] = Field(default=None, description="Branch name")
    documentation_url: Optional[str] = Field(default=None, description="Documentation URL")
    document_url: Optional[str] = Field(default=None, description="Document URL")

    articles_indexed: int = Field(default=0, ge=0, description="Number of articles indexed")
    files_processed: int = Field(default=0, ge=0, description="Number of files processed")
    total_files: Optional[int] = Field(default=None, description="Total files")
    storage_mb: float = Field(default=0.0, ge=0.0, description="Storage used in MB")

    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    error_details: Optional[dict[str, Any]] = Field(default=None, description="Error details")

    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    indexed_at: Optional[datetime] = Field(default=None, description="Indexing completion timestamp")


class ResourceListResponse(BaseModel):
    """Response model for resource list."""

    resources: list[ResourceDetailResponse] = Field(..., description="List of resources")
    total: int = Field(..., ge=0, description="Total number of resources")

