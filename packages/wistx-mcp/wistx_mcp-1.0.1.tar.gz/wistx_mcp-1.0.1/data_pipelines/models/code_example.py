"""Code example data models."""

from typing import Optional

from pydantic import BaseModel, Field


class CodeExample(BaseModel):
    """Processed code example."""

    title: str = Field(..., description="Example title")
    description: str = Field(..., description="Example description")
    code_type: str = Field(..., description="Code type (terraform, kubernetes, docker)")
    code: str = Field(..., description="Code content")
    cloud_provider: str = Field(..., description="Cloud provider (aws, gcp, azure)")
    services: list[str] = Field(default_factory=list, description="Cloud services used")
    github_url: str = Field(..., description="GitHub repository URL")
    stars: int = Field(..., description="GitHub stars count")
    quality_score: int = Field(..., description="Quality score (0-80)")
    best_practices: list[str] = Field(
        default_factory=list, description="List of best practices identified"
    )
    embedding: Optional[list[float]] = Field(
        default=None, description="Vector embedding (added in Stage 3)"
    )

