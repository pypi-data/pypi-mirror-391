"""Request models for v1 API."""

from pydantic import BaseModel, Field


class ComplianceRequirementsRequest(BaseModel):
    """Request model for compliance requirements query."""

    resource_types: list[str] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="List of resource types (RDS, S3, EC2, Lambda, EKS, etc.)",
        examples=[["RDS", "S3"]],
    )
    standards: list[str] = Field(
        default_factory=list,
        max_length=20,
        description="Compliance standards (PCI-DSS, HIPAA, CIS, SOC2, NIST-800-53, ISO-27001, GDPR, FedRAMP, etc.)",
        examples=[["PCI-DSS", "HIPAA"]],
    )
    severity: str | None = Field(
        default=None,
        enum=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
        description="Filter by severity level",
    )
    include_remediation: bool = Field(
        default=True,
        description="Include remediation guidance and code snippets",
    )
    include_verification: bool = Field(
        default=True,
        description="Include verification procedures",
    )


class KnowledgeResearchRequest(BaseModel):
    """Request model for knowledge base research query."""

    query: str = Field(
        ...,
        min_length=10,
        max_length=10000,
        description="Research query in natural language",
        examples=["What are the best practices for securing RDS databases?"],
    )
    domains: list[str] = Field(
        default_factory=list,
        max_length=20,
        description="Filter by domains: compliance, finops, devops, infrastructure, security, architecture",
        examples=[["compliance", "security"]],
    )
    content_types: list[str] = Field(
        default_factory=list,
        max_length=20,
        description="Filter by content types: guide, pattern, strategy, checklist, reference, best_practice",
        examples=[["guide", "best_practice"]],
    )
    include_cross_domain: bool = Field(
        default=True,
        description="Include cross-domain relationships and impacts",
    )
    include_global: bool = Field(
        default=True,
        description="Include global/shared knowledge base content. Set to False to search only user's indexed content.",
    )
    format: str = Field(
        default="structured",
        enum=["structured", "markdown", "executive_summary"],
        description="Response format",
    )
    max_results: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of results",
    )
