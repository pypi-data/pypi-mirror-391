"""REST API endpoints for documentation and report generation."""

import base64
import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from api.dependencies import get_current_user
from api.models.v1_responses import APIResponse, ErrorResponse
from wistx_mcp.tools.generate_documentation import generate_documentation
from wistx_mcp.tools.lib.mongodb_client import MongoDBClient
from wistx_mcp.tools.lib.report_template_manager import ReportTemplateManager
from wistx_mcp.models.report_template import OutputFormat

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["reports"])


class GenerateReportRequest(BaseModel):
    """Request model for generating a report."""

    document_type: str = Field(
        ...,
        description="Type of document (compliance_report, security_report, cost_report, etc.)",
    )
    subject: str = Field(..., description="Subject of the document")
    resource_types: list[str] | None = Field(default=None, description="List of resource types")
    compliance_standards: list[str] | None = Field(default=None, description="List of compliance standards")
    format: str = Field(default="markdown", description="Output format (markdown, html, pdf, docx)")
    template_id: str | None = Field(default=None, description="Custom template ID")
    custom_template: dict[str, Any] | None = Field(default=None, description="Custom template dictionary")
    branding: dict[str, Any] | None = Field(default=None, description="Branding configuration")
    include_compliance: bool = Field(default=True, description="Include compliance information")
    include_security: bool = Field(default=True, description="Include security information")
    include_cost: bool = Field(default=True, description="Include cost information")
    include_best_practices: bool = Field(default=True, description="Include best practices")


class ReportResponse(BaseModel):
    """Response model for report generation."""

    report_id: str = Field(..., description="Report identifier")
    document_type: str = Field(..., description="Document type")
    subject: str = Field(..., description="Subject")
    format: str = Field(..., description="Output format")
    content: str | bytes = Field(..., description="Report content (base64 for binary formats)")
    content_type: str = Field(..., description="Content type (text/markdown, application/pdf, etc.)")
    sections: list[str] = Field(default_factory=list, description="Document sections")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Report metadata")
    download_url: str = Field(..., description="URL to download the report")
    view_url: str = Field(..., description="URL to view the report")


@router.post(
    "/generate",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate documentation or report",
    description="Generate comprehensive documentation and reports in various formats (Markdown, HTML, PDF, DOCX).",
)
async def generate_report(
    request: GenerateReportRequest,
    http_request: Request,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> APIResponse:
    """Generate a documentation or report.

    Args:
        request: Generate report request
        http_request: HTTP request object
        current_user: Current authenticated user

    Returns:
        API response with report data

    Raises:
        HTTPException: If generation fails
    """
    user_id = current_user.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found",
        )

    try:
        result = await generate_documentation(
            document_type=request.document_type,
            subject=request.subject,
            resource_types=request.resource_types,
            compliance_standards=request.compliance_standards,
            format=request.format,
            template_id=request.template_id,
            custom_template=request.custom_template,
            branding=request.branding,
            include_compliance=request.include_compliance,
            include_security=request.include_security,
            include_cost=request.include_cost,
            include_best_practices=request.include_best_practices,
        )

        report_id = f"report-{datetime.now().strftime('%Y%m%d%H%M%S')}-{user_id[:8]}"

        content = result.get("content", "")
        output_format = result.get("format", "markdown")

        content_type_map = {
            "markdown": "text/markdown",
            "html": "text/html",
            "pdf": "application/pdf",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "json": "application/json",
        }

        content_type = content_type_map.get(output_format, "text/plain")

        if isinstance(content, bytes):
            content_b64 = base64.b64encode(content).decode("utf-8")
        else:
            content_b64 = base64.b64encode(content.encode("utf-8")).decode("utf-8")

        mongodb_client = MongoDBClient()
        await mongodb_client.connect()
        db = await mongodb_client.get_database()
        reports_collection = db.reports

        await reports_collection.insert_one({
            "report_id": report_id,
            "user_id": user_id,
            "document_type": result.get("document_type", request.document_type),
            "subject": result.get("subject", request.subject),
            "format": output_format,
            "content": content_b64,
            "content_type": content_type,
            "sections": result.get("sections", []),
            "metadata": result.get("metadata", {}),
            "created_at": datetime.utcnow(),
        })

        base_url = str(http_request.base_url).rstrip("/")
        download_url = f"{base_url}/v1/reports/{report_id}/download?format={output_format}"
        view_url = f"{base_url}/v1/reports/{report_id}/view?format={output_format}"

        response_data = ReportResponse(
            report_id=report_id,
            document_type=result.get("document_type", request.document_type),
            subject=result.get("subject", request.subject),
            format=output_format,
            content=content_b64,
            content_type=content_type,
            sections=result.get("sections", []),
            metadata=result.get("metadata", {}),
            download_url=download_url,
            view_url=view_url,
        )

        return APIResponse(
            data=response_data.model_dump(),
            metadata={
                "message": "Report generated successfully",
            },
        )

    except ValueError as e:
        logger.warning("Invalid request for report generation: %s", e)
        error_response = ErrorResponse(
            error={
                "code": "INVALID_REQUEST",
                "message": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response.model_dump(),
        ) from e

    except Exception as e:
        logger.error("Error generating report: %s", e, exc_info=True)
        error_response = ErrorResponse(
            error={
                "code": "REPORT_GENERATION_FAILED",
                "message": "Failed to generate report",
                "details": {"error": str(e)},
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response.model_dump(),
        ) from e


@router.get(
    "/{report_id}/download",
    summary="Download report",
    description="Download a generated report in the specified format.",
)
async def download_report(
    report_id: str,
    format: str = Query(default="markdown", description="Output format"),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> StreamingResponse:
    """Download a report in the specified format.

    Args:
        report_id: Report identifier
        format: Output format (markdown, html, pdf, docx)
        current_user: Current authenticated user

    Returns:
        StreamingResponse with report content

    Raises:
        HTTPException: If report not found or download fails
    """
    user_id = current_user.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found",
        )

    try:
        mongodb_client = MongoDBClient()
        await mongodb_client.connect()

        db = await mongodb_client.get_database()
        reports_collection = db.reports

        report_doc = await reports_collection.find_one({"report_id": report_id, "user_id": user_id})
        if not report_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report not found: {report_id}",
            )

        content = report_doc.get("content")
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report content not found",
            )

        if isinstance(content, str):
            content_bytes = base64.b64decode(content)
        else:
            content_bytes = content

        content_type_map = {
            "markdown": "text/markdown",
            "html": "text/html",
            "pdf": "application/pdf",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }

        content_type = content_type_map.get(format, "application/octet-stream")
        filename = f"{report_doc.get('subject', 'report')}.{format}"

        return StreamingResponse(
            iter([content_bytes]),
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error downloading report: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to download report",
        ) from e


@router.get(
    "/{report_id}/view",
    summary="View report",
    description="View a generated report in the browser (HTML format).",
)
async def view_report(
    report_id: str,
    format: str = Query(default="html", description="Output format (html or markdown)"),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> Response:
    """View a report in the browser.

    Args:
        report_id: Report identifier
        format: Output format (html or markdown)
        current_user: Current authenticated user

    Returns:
        Response with report content

    Raises:
        HTTPException: If report not found or view fails
    """
    user_id = current_user.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found",
        )

    try:
        mongodb_client = MongoDBClient()
        await mongodb_client.connect()

        db = await mongodb_client.get_database()
        reports_collection = db.reports

        report_doc = await reports_collection.find_one({"report_id": report_id, "user_id": user_id})
        if not report_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report not found: {report_id}",
            )

        content = report_doc.get("content")
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report content not found",
            )

        if isinstance(content, str):
            content_bytes = base64.b64decode(content)
        else:
            content_bytes = content

        if format == "html":
            content_str = content_bytes.decode("utf-8")
            return Response(content=content_str, media_type="text/html")
        elif format == "markdown":
            content_str = content_bytes.decode("utf-8")
            return Response(content=content_str, media_type="text/markdown")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Format {format} not supported for viewing. Use 'html' or 'markdown'.",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error viewing report: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to view report",
        ) from e


@router.get(
    "/templates",
    response_model=APIResponse,
    summary="List report templates",
    description="List available report templates.",
)
async def list_templates(
    document_type: str | None = Query(default=None, description="Filter by document type"),
    compliance_standard: str | None = Query(default=None, description="Filter by compliance standard"),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> APIResponse:
    """List available report templates.

    Args:
        document_type: Filter by document type
        compliance_standard: Filter by compliance standard
        current_user: Current authenticated user

    Returns:
        API response with list of templates
    """
    user_id = current_user.get("user_id")
    organization_id = current_user.get("organization_id")

    try:
        mongodb_client = MongoDBClient()
        await mongodb_client.connect()

        template_manager = ReportTemplateManager(mongodb_client)

        templates = await template_manager.search_templates(
            document_type=document_type,
            compliance_standard=compliance_standard,
            visibility="public",
            user_id=user_id,
            organization_id=organization_id,
            limit=50,
        )

        templates_data = [
            {
                "template_id": t.template_id,
                "name": t.name,
                "description": t.description,
                "version": t.version,
                "document_type": t.document_type,
                "compliance_standards": t.compliance_standards,
                "output_formats": [f.value for f in t.output_formats],
                "template_engine": t.template_engine.value,
            }
            for t in templates
        ]

        return APIResponse(
            data={"templates": templates_data, "total": len(templates_data)},
            metadata={
                "message": "Templates retrieved successfully",
            },
        )

    except Exception as e:
        logger.error("Error listing templates: %s", e, exc_info=True)
        error_response = ErrorResponse(
            error={
                "code": "TEMPLATE_LIST_FAILED",
                "message": "Failed to list templates",
                "details": {"error": str(e)},
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response.model_dump(),
        ) from e

