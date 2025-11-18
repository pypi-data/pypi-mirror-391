"""Generate documentation tool - create documentation and reports."""

import logging
import re
from datetime import datetime
from typing import Any

from wistx_mcp.tools.lib.mongodb_client import MongoDBClient
from wistx_mcp.tools.lib.document_generator import DocumentGenerator
from wistx_mcp.tools.lib.report_template_manager import ReportTemplateManager
from wistx_mcp.tools.lib.format_converter import FormatConverter
from wistx_mcp.tools.lib.template_library import TemplateLibrary
from wistx_mcp.models.report_template import OutputFormat
from wistx_mcp.config import settings

logger = logging.getLogger(__name__)


async def generate_documentation(
    document_type: str,
    subject: str,
    infrastructure_code: str | None = None,
    configuration: dict[str, Any] | None = None,
    include_compliance: bool = True,
    include_security: bool = True,
    include_cost: bool = True,
    include_best_practices: bool = True,
    resource_types: list[str] | None = None,
    compliance_standards: list[str] | None = None,
    resources: list[dict[str, Any]] | None = None,
    api_spec: dict[str, Any] | None = None,
    format: str = "markdown",
    template_id: str | None = None,
    custom_template: dict[str, Any] | None = None,
    branding: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Generate documentation and reports.

    Args:
        document_type: Type of document (architecture_diagram, runbook, compliance_report,
                      cost_report, security_report, api_documentation, deployment_guide)
        subject: Subject of the document (project name, resource, topic)
        infrastructure_code: Infrastructure code to document
        configuration: Configuration to document
        include_compliance: Include compliance information
        include_security: Include security information
        include_cost: Include cost information
        include_best_practices: Include best practices
        resource_types: List of resource types (for compliance/security reports)
        compliance_standards: List of compliance standards (for compliance report)
        resources: List of resource specifications (for cost report)
        api_spec: API specification (for api_documentation)
        format: Output format (markdown, pdf, html, json)
        template_id: Custom template ID (for compliance_report)
        custom_template: Custom template dictionary (alternative to template_id)
        branding: Branding configuration (logo, colors, etc.)

    Returns:
        Dictionary with documentation:
        - content: Generated documentation content
        - format: Output format
        - document_type: Type of document
        - sections: Document sections
        - metadata: Document metadata

    Raises:
        ValueError: If invalid document_type or parameters
        Exception: If generation fails
    """
    valid_types = [
        "architecture_diagram",
        "runbook",
        "compliance_report",
        "cost_report",
        "security_report",
        "api_documentation",
        "deployment_guide",
    ]

    if document_type not in valid_types:
        raise ValueError(f"Invalid document_type: {document_type}. Must be one of {valid_types}")

    if format not in ["markdown", "pdf", "html", "json"]:
        raise ValueError(f"Invalid format: {format}. Must be one of markdown, pdf, html, json")

    logger.info(
        "Generating documentation: type=%s, subject=%s, format=%s",
        document_type,
        subject,
        format,
    )

    mongodb_client = None

    try:
        mongodb_client = MongoDBClient()
        await mongodb_client.connect()

        generator = DocumentGenerator(mongodb_client)

        content = ""

        if document_type == "architecture_diagram":
            content = await generator.generate_architecture_doc(
                subject=subject,
                infrastructure_code=infrastructure_code,
                configuration=configuration,
                include_compliance=include_compliance,
                include_security=include_security,
            )

        elif document_type == "runbook":
            operations = configuration.get("operations") if configuration else None
            troubleshooting = configuration.get("troubleshooting") if configuration else None
            content = await generator.generate_runbook(
                subject=subject,
                operations=operations,
                troubleshooting=troubleshooting,
            )

        elif document_type == "compliance_report":
            if not resource_types:
                raise ValueError("resource_types required for compliance_report")

            template_manager = ReportTemplateManager(mongodb_client)
            format_converter = FormatConverter()

            if template_id or custom_template:
                template_data = None
                if template_id:
                    template = await template_manager.get_template(template_id)
                    if not template:
                        raise ValueError(f"Template not found: {template_id}")
                else:
                    template_dict = custom_template or {}
                    template = await template_manager.register_template(
                        name=template_dict.get("name", "Custom Template"),
                        template_content=template_dict.get("template_content", ""),
                        document_type="compliance_report",
                        template_engine=template_dict.get("template_engine", "jinja2"),
                        compliance_standards=compliance_standards or [],
                        resource_types=resource_types or [],
                        variables=template_dict.get("variables", {}),
                        visibility="private",
                        user_id=None,
                    )

                compliance_data = await generator.generate_compliance_report(
                    subject=subject,
                    resource_types=resource_types,
                    standards=compliance_standards,
                )

                from datetime import datetime
                template_data = {
                    "subject": subject,
                    "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "compliance_status": "Assessed",
                    "total_requirements": len(compliance_data.get("controls", [])),
                    "compliant_requirements": 0,
                    "non_compliant_requirements": 0,
                    "compliance_score": 0.0,
                    "resources": [{"type": rt, "name": rt} for rt in resource_types or []],
                    "assessment_start": datetime.now().strftime("%Y-%m-%d"),
                    "assessment_end": datetime.now().strftime("%Y-%m-%d"),
                    "requirements": compliance_data.get("controls", []),
                    "recommendations": [],
                }

                rendered_content = await template_manager.render_template(
                    template_id=template.template_id,
                    data=template_data,
                    output_format=OutputFormat(format.upper()),
                )

                if format == "pdf":
                    pdf_bytes = format_converter.markdown_to_pdf(
                        rendered_content,
                        styles=template.styles,
                        branding=branding or template.branding,
                    )
                    return {
                        "content": pdf_bytes,
                        "format": "pdf",
                        "document_type": document_type,
                        "subject": subject,
                        "sections": _extract_sections(rendered_content),
                        "metadata": {
                            "generated_at": datetime.now().isoformat(),
                            "template_id": template.template_id,
                            "template_name": template.name,
                        },
                    }
                elif format == "html":
                    html_content = format_converter.markdown_to_html(
                        rendered_content,
                        styles=template.styles,
                    )
                    return {
                        "content": html_content,
                        "format": "html",
                        "document_type": document_type,
                        "subject": subject,
                        "sections": _extract_sections(rendered_content),
                        "metadata": {
                            "generated_at": datetime.now().isoformat(),
                            "template_id": template.template_id,
                            "template_name": template.name,
                        },
                    }
                elif format == "docx":
                    docx_bytes = format_converter.markdown_to_docx(
                        rendered_content,
                        branding=branding or template.branding,
                    )
                    return {
                        "content": docx_bytes,
                        "format": "docx",
                        "document_type": document_type,
                        "subject": subject,
                        "sections": _extract_sections(rendered_content),
                        "metadata": {
                            "generated_at": datetime.now().isoformat(),
                            "template_id": template.template_id,
                            "template_name": template.name,
                        },
                    }
                else:
                    content = rendered_content
            else:
                content = await generator.generate_compliance_report(
                    subject=subject,
                    resource_types=resource_types,
                    standards=compliance_standards,
                )

        elif document_type == "security_report":
            cloud_provider = configuration.get("cloud_provider") if configuration else None
            content = await generator.generate_security_report(
                subject=subject,
                resource_types=resource_types,
                cloud_provider=cloud_provider,
            )

        elif document_type == "cost_report":
            content = await generator.generate_cost_report(
                subject=subject,
                resources=resources,
            )

        elif document_type == "api_documentation":
            content = await generator.generate_api_documentation(
                subject=subject,
                api_spec=api_spec,
            )

        elif document_type == "deployment_guide":
            infrastructure_type = configuration.get("infrastructure_type") if configuration else None
            cloud_provider = configuration.get("cloud_provider") if configuration else None
            content = await generator.generate_deployment_guide(
                subject=subject,
                infrastructure_type=infrastructure_type,
                cloud_provider=cloud_provider,
            )

        sections = _extract_sections(content)

        return {
            "content": content,
            "format": format,
            "document_type": document_type,
            "subject": subject,
            "sections": sections,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "includes": {
                    "compliance": include_compliance,
                    "security": include_security,
                    "cost": include_cost,
                    "best_practices": include_best_practices,
                },
            },
        }

    except Exception as e:
        logger.error("Error in generate_documentation: %s", e, exc_info=True)
        raise


def _extract_sections(content: str) -> list[str]:
    """Extract section headers from markdown content.

    Args:
        content: Markdown content

    Returns:
        List of section headers
    """
    sections = re.findall(r"^#+\s+(.+)$", content, re.MULTILINE)
    return sections

