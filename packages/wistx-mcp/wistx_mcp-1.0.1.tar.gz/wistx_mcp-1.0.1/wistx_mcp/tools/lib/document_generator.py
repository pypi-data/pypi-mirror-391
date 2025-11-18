"""Document generator for creating documentation and reports."""

import logging
from datetime import datetime
from typing import Any

from wistx_mcp.tools.lib.mongodb_client import MongoDBClient
from wistx_mcp.tools.lib.vector_search import VectorSearch
from wistx_mcp.tools.lib.api_client import WISTXAPIClient
from wistx_mcp.tools.lib.retry_utils import with_timeout_and_retry
from wistx_mcp.config import settings

logger = logging.getLogger(__name__)

api_client = WISTXAPIClient()


class DocumentGenerator:
    """Generator for various types of documentation."""

    def __init__(self, mongodb_client: MongoDBClient):
        """Initialize document generator.

        Args:
            mongodb_client: MongoDB client for knowledge base access
        """
        self.mongodb_client = mongodb_client
        self.vector_search = VectorSearch(
            mongodb_client,
            openai_api_key=settings.openai_api_key,
        )

    async def generate_architecture_doc(
        self,
        subject: str,
        infrastructure_code: str | None = None,
        configuration: dict[str, Any] | None = None,
        include_compliance: bool = True,
        include_security: bool = True,
    ) -> str:
        """Generate architecture documentation.

        Args:
            subject: Subject name
            infrastructure_code: Infrastructure code
            configuration: Configuration dictionary
            include_compliance: Include compliance information
            include_security: Include security information

        Returns:
            Generated markdown documentation
        """
        markdown = f"# Architecture Documentation: {subject}\n\n"
        markdown += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        markdown += "## Overview\n\n"
        markdown += f"This document describes the architecture for {subject}.\n\n"

        if infrastructure_code:
            markdown += "## Infrastructure Code\n\n"
            markdown += f"```hcl\n{infrastructure_code}\n```\n\n"

        if configuration:
            markdown += "## Configuration\n\n"
            for key, value in configuration.items():
                if isinstance(value, dict):
                    markdown += f"### {key}\n\n"
                    for sub_key, sub_value in value.items():
                        markdown += f"- **{sub_key}**: {sub_value}\n"
                    markdown += "\n"
                else:
                    markdown += f"- **{key}**: {value}\n"
            markdown += "\n"

        if include_security:
            markdown += "## Security Considerations\n\n"
            markdown += "### Security Best Practices\n\n"
            markdown += "- Implement least privilege access\n"
            markdown += "- Enable encryption at rest and in transit\n"
            markdown += "- Regular security audits\n"
            markdown += "- Monitor for security events\n"
            markdown += "- Keep dependencies updated\n\n"

        if include_compliance:
            markdown += "## Compliance\n\n"
            markdown += "### Compliance Standards\n\n"
            markdown += "- Review compliance requirements\n"
            markdown += "- Implement compliance controls\n"
            markdown += "- Regular compliance audits\n\n"

        markdown += "## Architecture Components\n\n"
        markdown += "### Components\n\n"
        markdown += "- Application layer\n"
        markdown += "- Data layer\n"
        markdown += "- Network layer\n"
        markdown += "- Security layer\n\n"

        return markdown

    async def generate_runbook(
        self,
        subject: str,
        operations: list[str] | None = None,
        troubleshooting: list[str] | None = None,
    ) -> str:
        """Generate operational runbook.

        Args:
            subject: Subject name
            operations: List of operations
            troubleshooting: List of troubleshooting steps

        Returns:
            Generated markdown runbook
        """
        markdown = f"# Runbook: {subject}\n\n"
        markdown += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        markdown += "## Operations\n\n"
        if operations:
            for i, op in enumerate(operations, 1):
                markdown += f"### {i}. {op}\n\n"
                markdown += "**Steps**:\n"
                markdown += "1. Verify prerequisites\n"
                markdown += "2. Execute operation\n"
                markdown += "3. Verify success\n\n"
        else:
            markdown += "### Standard Operations\n\n"
            markdown += "1. Monitor system health\n"
            markdown += "2. Check logs for errors\n"
            markdown += "3. Verify resource status\n"
            markdown += "4. Review monitoring metrics\n\n"

        markdown += "## Troubleshooting\n\n"
        if troubleshooting:
            for i, step in enumerate(troubleshooting, 1):
                markdown += f"{i}. {step}\n"
        else:
            markdown += "1. Check error logs\n"
            markdown += "2. Verify configuration\n"
            markdown += "3. Check resource status\n"
            markdown += "4. Review monitoring metrics\n"
            markdown += "5. Check network connectivity\n\n"

        markdown += "## Emergency Procedures\n\n"
        markdown += "### Incident Response\n\n"
        markdown += "1. Identify the issue\n"
        markdown += "2. Assess impact\n"
        markdown += "3. Implement fix\n"
        markdown += "4. Verify resolution\n"
        markdown += "5. Document incident\n\n"

        return markdown

    async def generate_compliance_report(
        self,
        subject: str,
        resource_types: list[str],
        standards: list[str] | None = None,
    ) -> str:
        """Generate compliance report.

        Args:
            subject: Subject name
            resource_types: List of resource types
            standards: List of compliance standards

        Returns:
            Generated markdown compliance report
        """
        markdown = f"# Compliance Report: {subject}\n\n"
        markdown += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        markdown += "## Executive Summary\n\n"
        markdown += f"This report assesses compliance for {subject}.\n\n"

        markdown += f"## Resources Assessed\n\n"
        for resource_type in resource_types:
            markdown += f"- {resource_type}\n"
        markdown += "\n"

        markdown += f"## Compliance Standards\n\n"
        if standards:
            for standard in standards:
                markdown += f"- {standard}\n"
        else:
            markdown += "- Review applicable compliance standards\n"
        markdown += "\n"

        try:
            compliance_results = await with_timeout_and_retry(
                api_client.get_compliance_requirements,
                timeout_seconds=30.0,
                max_attempts=3,
                retryable_exceptions=(RuntimeError, ConnectionError, TimeoutError),
                resource_types=resource_types,
                standards=standards or [],
            )

            controls = compliance_results.get("controls", [])

            markdown += f"## Compliance Controls\n\n"
            markdown += f"**Total Controls**: {len(controls)}\n\n"

            severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
            for control in controls:
                severity = control.get("severity", "MEDIUM")
                severity_counts[severity] = severity_counts.get(severity, 0) + 1

            markdown += "### Severity Breakdown\n\n"
            for severity, count in severity_counts.items():
                if count > 0:
                    markdown += f"- **{severity}**: {count}\n"
            markdown += "\n"

            markdown += "### Controls\n\n"
            for control in controls[:20]:
                standard = control.get("standard", "")
                control_id = control.get("control_id", "")
                severity = control.get("severity", "")
                title = control.get("title", "")

                markdown += f"#### {standard} {control_id}: {title}\n\n"
                markdown += f"**Severity**: {severity}\n\n"
                markdown += f"{control.get('description', '')}\n\n"

                remediation = control.get("remediation", {})
                if remediation.get("guidance"):
                    markdown += f"**Remediation**: {remediation['guidance']}\n\n"

                markdown += "---\n\n"

        except Exception as e:
            logger.warning("Failed to generate compliance report: %s", e)
            markdown += "## Compliance Assessment\n\n"
            markdown += "Unable to generate compliance report. Please check resource types and standards.\n\n"

        return markdown

    async def generate_security_report(
        self,
        subject: str,
        resource_types: list[str] | None = None,
        cloud_provider: str | None = None,
    ) -> str:
        """Generate security report.

        Args:
            subject: Subject name
            resource_types: List of resource types
            cloud_provider: Cloud provider

        Returns:
            Generated markdown security report
        """
        markdown = f"# Security Report: {subject}\n\n"
        markdown += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        markdown += "## Executive Summary\n\n"
        markdown += f"This report assesses security posture for {subject}.\n\n"

        markdown += "## Security Assessment\n\n"
        markdown += "### Security Best Practices\n\n"
        markdown += "- Enable encryption at rest and in transit\n"
        markdown += "- Implement least privilege access\n"
        markdown += "- Regular security audits\n"
        markdown += "- Monitor for security events\n"
        markdown += "- Keep dependencies updated\n"
        markdown += "- Implement network segmentation\n"
        markdown += "- Use security groups and firewalls\n\n"

        if resource_types:
            markdown += "## Resource-Specific Security\n\n"
            for resource_type in resource_types:
                markdown += f"### {resource_type}\n\n"
                markdown += "- Review security configurations\n"
                markdown += "- Check access controls\n"
                markdown += "- Verify encryption settings\n"
                markdown += "- Review audit logs\n\n"

        if cloud_provider:
            markdown += f"## {cloud_provider.upper()} Security\n\n"
            markdown += f"- Review {cloud_provider} security best practices\n"
            markdown += f"- Check {cloud_provider} security groups\n"
            markdown += f"- Verify {cloud_provider} IAM policies\n\n"

        markdown += "## Recommendations\n\n"
        markdown += "1. Implement security monitoring\n"
        markdown += "2. Regular security audits\n"
        markdown += "3. Keep security configurations updated\n"
        markdown += "4. Review access controls regularly\n\n"

        return markdown

    async def generate_cost_report(
        self,
        subject: str,
        resources: list[dict[str, Any]] | None = None,
    ) -> str:
        """Generate cost report.

        Args:
            subject: Subject name
            resources: List of resource specifications

        Returns:
            Generated markdown cost report
        """
        markdown = f"# Cost Report: {subject}\n\n"
        markdown += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        markdown += "## Executive Summary\n\n"
        markdown += f"This report provides cost analysis for {subject}.\n\n"

        if resources:
            try:
                from wistx_mcp.tools import pricing
                cost_results = await with_timeout_and_retry(
                    pricing.calculate_infrastructure_cost,
                    timeout_seconds=30.0,
                    max_attempts=3,
                    retryable_exceptions=(RuntimeError, ConnectionError, TimeoutError),
                    resources=resources,
                )

                total_monthly = cost_results.get("total_monthly", 0)
                total_annual = cost_results.get("total_annual", 0)

                markdown += f"## Cost Summary\n\n"
                markdown += f"**Monthly Cost**: ${total_monthly:.2f}\n\n"
                markdown += f"**Annual Cost**: ${total_annual:.2f}\n\n"

                breakdown = cost_results.get("breakdown", [])
                if breakdown:
                    markdown += "## Cost Breakdown\n\n"
                    markdown += "| Resource | Quantity | Monthly | Annual |\n"
                    markdown += "|----------|----------|---------|--------|\n"
                    for item in breakdown:
                        markdown += f"| {item['resource']} | {item['quantity']} | "
                        markdown += f"${item['monthly']:.2f} | ${item['annual']:.2f} |\n"
                    markdown += "\n"

                optimizations = cost_results.get("optimizations", [])
                if optimizations:
                    markdown += "## Optimization Suggestions\n\n"
                    for opt in optimizations:
                        markdown += f"- {opt}\n"
                    markdown += "\n"

            except Exception as e:
                logger.warning("Failed to generate cost report: %s", e)
                markdown += "## Cost Analysis\n\n"
                markdown += "Unable to generate cost report. Please provide resource specifications.\n\n"
        else:
            markdown += "## Cost Analysis\n\n"
            markdown += "No resource specifications provided.\n\n"
            markdown += "### Cost Estimation Guidelines\n\n"
            markdown += "1. Identify all resources\n"
            markdown += "2. Estimate usage patterns\n"
            markdown += "3. Calculate monthly costs\n"
            markdown += "4. Plan for scaling\n\n"

        return markdown

    async def generate_api_documentation(
        self,
        subject: str,
        api_spec: dict[str, Any] | None = None,
    ) -> str:
        """Generate API documentation.

        Args:
            subject: API name
            api_spec: API specification dictionary

        Returns:
            Generated markdown API documentation
        """
        markdown = f"# API Documentation: {subject}\n\n"
        markdown += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        markdown += "## Overview\n\n"
        markdown += f"This document describes the API for {subject}.\n\n"

        if api_spec:
            markdown += "## Endpoints\n\n"
            endpoints = api_spec.get("endpoints", [])
            for endpoint in endpoints:
                method = endpoint.get("method", "GET")
                path = endpoint.get("path", "")
                markdown += f"### {method} {path}\n\n"
                markdown += f"{endpoint.get('description', '')}\n\n"
        else:
            markdown += "## API Endpoints\n\n"
            markdown += "### Endpoints\n\n"
            markdown += "- List endpoints\n"
            markdown += "- Document request/response formats\n"
            markdown += "- Include authentication requirements\n\n"

        markdown += "## Authentication\n\n"
        markdown += "API authentication requirements.\n\n"

        markdown += "## Examples\n\n"
        markdown += "### Request Example\n\n"
        markdown += "```json\n{}\n```\n\n"

        markdown += "### Response Example\n\n"
        markdown += "```json\n{}\n```\n\n"

        return markdown

    async def generate_deployment_guide(
        self,
        subject: str,
        infrastructure_type: str | None = None,
        cloud_provider: str | None = None,
    ) -> str:
        """Generate deployment guide.

        Args:
            subject: Subject name
            infrastructure_type: Infrastructure type
            cloud_provider: Cloud provider

        Returns:
            Generated markdown deployment guide
        """
        markdown = f"# Deployment Guide: {subject}\n\n"
        markdown += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        markdown += "## Prerequisites\n\n"
        markdown += "- Required tools and access\n"
        markdown += "- Configuration files\n"
        markdown += "- Credentials and permissions\n\n"

        markdown += "## Deployment Steps\n\n"
        markdown += "### 1. Preparation\n\n"
        markdown += "- Review requirements\n"
        markdown += "- Prepare configuration\n"
        markdown += "- Verify access\n\n"

        markdown += "### 2. Infrastructure Setup\n\n"
        if infrastructure_type == "terraform":
            markdown += "```bash\n"
            markdown += "terraform init\n"
            markdown += "terraform plan\n"
            markdown += "terraform apply\n"
            markdown += "```\n\n"
        elif infrastructure_type == "kubernetes":
            markdown += "```bash\n"
            markdown += "kubectl apply -f manifests/\n"
            markdown += "kubectl get pods\n"
            markdown += "```\n\n"
        else:
            markdown += "- Deploy infrastructure\n"
            markdown += "- Verify deployment\n\n"

        markdown += "### 3. Configuration\n\n"
        markdown += "- Configure services\n"
        markdown += "- Set up monitoring\n"
        markdown += "- Configure security\n\n"

        markdown += "### 4. Verification\n\n"
        markdown += "- Verify deployment\n"
        markdown += "- Run health checks\n"
        markdown += "- Test functionality\n\n"

        markdown += "## Rollback Procedures\n\n"
        markdown += "1. Identify rollback point\n"
        markdown += "2. Execute rollback\n"
        markdown += "3. Verify system state\n\n"

        return markdown

