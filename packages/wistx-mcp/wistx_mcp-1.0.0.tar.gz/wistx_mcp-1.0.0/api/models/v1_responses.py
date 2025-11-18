"""Response models for v1 API."""

from typing import Any

from pydantic import BaseModel, Field


class ComplianceControlResponse(BaseModel):
    """Response model for a single compliance control."""

    control_id: str = Field(..., description="Unique control identifier")
    standard: str = Field(..., description="Compliance standard")
    title: str = Field(..., description="Control title")
    description: str = Field(..., description="Control description")
    severity: str = Field(..., description="Severity level")
    category: str | None = Field(default=None, description="Category")
    subcategory: str | None = Field(default=None, description="Subcategory")
    applies_to: list[str] = Field(default_factory=list, description="Applicable resources")
    remediation: dict[str, Any] | None = Field(default=None, description="Remediation guidance")
    verification: dict[str, Any] | None = Field(default=None, description="Verification procedures")
    references: list[dict[str, Any]] = Field(default_factory=list, description="External references")
    source_url: str | None = Field(default=None, description="Source URL")


class ComplianceRequirementsSummary(BaseModel):
    """Summary statistics for compliance requirements."""

    total: int = Field(..., description="Total number of controls")
    by_severity: dict[str, int] = Field(default_factory=dict, description="Count by severity")
    by_standard: dict[str, int] = Field(default_factory=dict, description="Count by standard")


class ComplianceRequirementsResponse(BaseModel):
    """Response model for compliance requirements query."""

    controls: list[ComplianceControlResponse] = Field(default_factory=list, description="List of compliance controls")
    summary: ComplianceRequirementsSummary = Field(..., description="Summary statistics")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Query metadata")


class KnowledgeArticleResponse(BaseModel):
    """Response model for a single knowledge article."""

    article_id: str = Field(..., description="Unique article identifier")
    domain: str = Field(..., description="Knowledge domain")
    subdomain: str = Field(..., description="Subdomain")
    content_type: str = Field(..., description="Content type")
    title: str = Field(..., description="Article title")
    summary: str = Field(..., description="Article summary")
    content: str | None = Field(default=None, description="Full content (if requested)")
    tags: list[str] = Field(default_factory=list, description="Tags")
    categories: list[str] = Field(default_factory=list, description="Categories")
    industries: list[str] = Field(default_factory=list, description="Applicable industries")
    cloud_providers: list[str] = Field(default_factory=list, description="Cloud providers")
    services: list[str] = Field(default_factory=list, description="Services")
    cross_domain_impacts: dict[str, Any] | None = Field(
        default=None,
        description="Cross-domain impacts (compliance, cost, security)",
    )
    source_url: str | None = Field(default=None, description="Source URL")
    quality_score: float | None = Field(default=None, description="Quality score")


class KnowledgeResearchSummary(BaseModel):
    """Summary statistics for knowledge research."""

    total_found: int = Field(..., description="Total number of articles found")
    domains_covered: list[str] = Field(default_factory=list, description="Domains covered in results")
    key_insights: list[str] = Field(default_factory=list, description="Key insights")


class KnowledgeResearchResponse(BaseModel):
    """Response model for knowledge research query."""

    results: list[KnowledgeArticleResponse] = Field(default_factory=list, description="Search results")
    research_summary: KnowledgeResearchSummary = Field(..., description="Research summary")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Query metadata")


class APIResponse(BaseModel):
    """Standard API response wrapper."""

    data: dict[str, Any] | list[Any] = Field(..., description="Response data")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Response metadata")


class APIError(BaseModel):
    """Standard API error response."""

    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: dict[str, Any] | None = Field(default=None, description="Error details")


class ErrorResponse(BaseModel):
    """Error response wrapper."""

    error: APIError = Field(..., description="Error information")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Response metadata")

