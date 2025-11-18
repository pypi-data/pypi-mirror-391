"""Request models for indexing endpoints."""

from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class IndexRepositoryRequest(BaseModel):
    """Request model for indexing a GitHub repository."""

    repo_url: HttpUrl = Field(..., description="GitHub repository URL")
    branch: str = Field(default="main", description="Branch to index")
    name: Optional[str] = Field(default=None, description="Custom name for the resource")
    description: Optional[str] = Field(default=None, max_length=1000, description="Resource description")
    tags: list[str] = Field(default_factory=list, max_items=20, description="Tags for categorization")
    github_token: Optional[str] = Field(default=None, description="GitHub personal access token (for private repos)")


class IndexDocumentationRequest(BaseModel):
    """Request model for indexing a documentation website."""

    documentation_url: HttpUrl = Field(..., description="Documentation website URL")
    name: Optional[str] = Field(default=None, description="Custom name for the resource")
    description: Optional[str] = Field(default=None, max_length=1000, description="Resource description")
    tags: list[str] = Field(default_factory=list, max_items=20, description="Tags for categorization")
    include_patterns: Optional[list[str]] = Field(
        default=None,
        description="URL patterns to include (e.g., ['/docs/', '/api/'])",
    )
    exclude_patterns: Optional[list[str]] = Field(
        default=None,
        description="URL patterns to exclude (e.g., ['/admin/', '/private/'])",
    )


class IndexDocumentRequest(BaseModel):
    """Request model for indexing a document."""

    document_url: str = Field(..., description="Document URL or file path")
    document_type: str = Field(..., description="Document type: pdf, docx, markdown, txt")
    name: Optional[str] = Field(default=None, description="Custom name for the resource")
    description: Optional[str] = Field(default=None, max_length=1000, description="Resource description")
    tags: list[str] = Field(default_factory=list, max_items=20, description="Tags for categorization")

