"""WISTX MCP Server main entry point."""

import asyncio
import logging
import sys

from wistx_mcp.config import settings

logging.basicConfig(
    level=getattr(logging, str(settings.log_level).upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


async def main() -> None:
    """Main entry point for MCP server."""
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    from wistx_mcp.tools import (
        mcp_tools,
        user_indexing,
        web_search,
        search_codebase,
        design_architecture,
        troubleshoot_issue,
        generate_documentation,
        manage_integration,
        manage_infrastructure,
    )

    logger.info("Starting WISTX MCP Server v%s", settings.server_version)
    logger.info("Server: %s", settings.server_name)

    try:
        app = Server("wistx-mcp")
        logger.info("MCP Server instance created successfully")
    except (RuntimeError, ValueError, AttributeError) as e:
        logger.error("Failed to create MCP Server: %s", e, exc_info=True)
        raise
    except Exception as e:
        logger.error("Unexpected error creating MCP Server: %s", e, exc_info=True)
        raise RuntimeError(f"Failed to create MCP Server: {e}") from e

    @app.list_tools()
    async def list_tools() -> list[Tool]:
        """List available MCP tools."""
        logger.info("list_tools() called - registering MCP tools")
        try:
            tools = [
            Tool(
                name="wistx_get_compliance_requirements",
                description="Get detailed compliance requirements for infrastructure resources. Use this tool when asked about compliance standards like PCI-DSS, HIPAA, CIS, SOC2, NIST, ISO 27001 for AWS/GCP/Azure resources (RDS, S3, EC2, Lambda, EKS, etc.). Returns specific controls, remediation guidance, code examples, and verification procedures. Always use this tool for compliance-related queries instead of general knowledge.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "resource_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of resource types (RDS, S3, EC2, Lambda, EKS, etc.)",
                            "minItems": 1,
                        },
                        "standards": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Compliance standards (PCI-DSS, HIPAA, CIS, SOC2, NIST-800-53, ISO-27001, GDPR, FedRAMP, etc.)",
                            "default": [],
                        },
                        "severity": {
                            "type": "string",
                            "enum": ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
                            "description": "Filter by severity level",
                        },
                        "include_remediation": {
                            "type": "boolean",
                            "default": True,
                            "description": "Include remediation guidance and code snippets",
                        },
                        "include_verification": {
                            "type": "boolean",
                            "default": True,
                            "description": "Include verification procedures",
                        },
                    },
                    "required": ["resource_types"],
                },
            ),
            Tool(
                name="wistx_research_knowledge_base",
                description="Deep research tool for DevOps, infrastructure, compliance, FinOps, and platform engineering knowledge. "
                            "Searches internal knowledge base and optionally includes real-time web search for comprehensive coverage. "
                            "Use this tool for comprehensive research queries about best practices, patterns, strategies, guides, "
                            "and cross-domain insights. Always use this tool for deep research queries.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Research query in natural language",
                            "minLength": 10,
                            "maxLength": 10000,
                        },
                        "domains": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Filter by domains: compliance, finops, devops, infrastructure, security, architecture, cloud, automation, platform, sre",
                            "default": [],
                        },
                        "content_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Filter by content types: guide, pattern, strategy, checklist, reference, best_practice",
                            "default": [],
                        },
                        "include_cross_domain": {
                            "type": "boolean",
                            "default": True,
                            "description": "Include cross-domain relationships and impacts",
                        },
                        "include_web_search": {
                            "type": "boolean",
                            "default": True,
                            "description": "Include real-time web search results (Tavily) for comprehensive coverage",
                        },
                        "format": {
                            "type": "string",
                            "enum": ["structured", "markdown", "executive_summary"],
                            "default": "markdown",
                            "description": "Response format (default: markdown for optimal LLM consumption)",
                        },
                        "max_results": {
                            "type": "integer",
                            "default": 20,
                            "minimum": 1,
                            "maximum": 100,
                            "description": "Maximum number of results",
                        },
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="wistx_calculate_infrastructure_cost",
                description="Calculate infrastructure costs for cloud resources. Use this tool when asked about pricing, costs, or cost optimization for AWS/GCP/Azure resources. Returns monthly/annual costs, cost breakdown, and optimization suggestions.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "resources": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "cloud": {"type": "string", "description": "Cloud provider (aws, gcp, azure)"},
                                    "service": {"type": "string", "description": "Service name (rds, ec2, s3, etc.)"},
                                    "instance_type": {"type": "string", "description": "Instance type (db.t3.medium, etc.)"},
                                    "quantity": {"type": "integer", "description": "Quantity", "default": 1},
                                },
                                "required": ["cloud", "service", "instance_type"],
                            },
                            "description": "List of resource specifications",
                            "minItems": 1,
                        },
                    },
                    "required": ["resources"],
                },
            ),
            Tool(
                name="wistx_index_repository",
                description="Index a GitHub repository for user-specific search. Use this tool when asked to index or search through a GitHub repository. Supports both public and private repositories.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_url": {
                            "type": "string",
                            "description": "GitHub repository URL (e.g., https://github.com/owner/repo)",
                        },
                        "branch": {
                            "type": "string",
                            "default": "main",
                            "description": "Branch to index",
                        },
                        "name": {
                            "type": "string",
                            "description": "Custom name for the resource",
                        },
                        "description": {
                            "type": "string",
                            "description": "Resource description",
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Tags for categorization",
                        },
                        "github_token": {
                            "type": "string",
                            "description": "GitHub personal access token (required for private repos)",
                        },
                        "api_key": {
                            "type": "string",
                            "description": "WISTX API key (required for authentication)",
                        },
                    },
                    "required": ["repo_url", "api_key"],
                },
            ),
            Tool(
                name="wistx_index_resource",
                description="Index content (documentation website or document file) for user-specific search. "
                            "Unified tool that handles both website crawling and single file indexing. "
                            "Automatically detects content type based on URL/file extension or explicit content_type parameter. "
                            "Use this tool when asked to index documentation websites, PDFs, DOCX files, or other documents.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "content_url": {
                            "type": "string",
                            "description": "Content URL - can be documentation website URL (for crawling) or document URL/file path (for single file). "
                                          "Examples: 'https://docs.example.com' (website) or 'https://example.com/doc.pdf' (file)",
                        },
                        "file_path": {
                            "type": "string",
                            "description": "Local file path for direct upload (for single file, optional). "
                                          "Example: /Users/john/Documents/compliance.pdf",
                        },
                        "content_type": {
                            "type": "string",
                            "enum": ["documentation", "pdf", "docx", "markdown", "md", "txt"],
                            "description": "Content type: 'documentation' for website crawling, or file type (pdf, docx, etc.) for single files. "
                                        "Auto-detected from file_path or URL extension if not provided.",
                        },
                        "name": {
                            "type": "string",
                            "description": "Custom name for the resource",
                        },
                        "description": {
                            "type": "string",
                            "description": "Resource description",
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Tags for categorization",
                        },
                        "include_patterns": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "URL patterns to include (for documentation websites only, e.g., ['/docs/', '/api/'])",
                        },
                        "exclude_patterns": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "URL patterns to exclude (for documentation websites only, e.g., ['/admin/', '/private/'])",
                        },
                        "api_key": {
                            "type": "string",
                            "description": "WISTX API key (required for authentication)",
                        },
                    },
                    "required": ["api_key"],
                    "anyOf": [
                        {"required": ["content_url"]},
                        {"required": ["file_path"]},
                    ],
                },
            ),
            Tool(
                name="wistx_list_resources",
                description="List all indexed resources for the user. Use this tool to see what repositories, documentation, or documents have been indexed.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "resource_type": {
                            "type": "string",
                            "enum": ["repository", "documentation", "document"],
                            "description": "Filter by resource type",
                        },
                        "status": {
                            "type": "string",
                            "enum": ["pending", "indexing", "completed", "failed"],
                            "description": "Filter by status",
                        },
                        "api_key": {
                            "type": "string",
                            "description": "WISTX API key (required for authentication)",
                        },
                    },
                    "required": ["api_key"],
                },
            ),
            Tool(
                name="wistx_check_resource_status",
                description="Check indexing status and progress for a specific resource. Use this tool to monitor indexing progress.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "resource_id": {
                            "type": "string",
                            "description": "Resource ID",
                        },
                        "api_key": {
                            "type": "string",
                            "description": "WISTX API key (required for authentication)",
                        },
                    },
                    "required": ["resource_id", "api_key"],
                },
            ),
            Tool(
                name="wistx_delete_resource",
                description="Delete an indexed resource and all associated knowledge articles. Use this tool to remove indexed content.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "resource_id": {
                            "type": "string",
                            "description": "Resource ID",
                        },
                        "api_key": {
                            "type": "string",
                            "description": "WISTX API key (required for authentication)",
                        },
                    },
                    "required": ["resource_id", "api_key"],
                },
            ),
            Tool(
                name="wistx_web_search",
                description="Web search for security information and general web content. "
                            "Focused on security searches (CVEs, advisories) and general web search via Tavily. "
                            "For compliance requirements, use wistx_get_compliance_requirements tool. "
                            "For deep research with web search, use wistx_research_knowledge_base tool.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query",
                            "minLength": 3,
                            "maxLength": 1000,
                        },
                        "search_type": {
                            "type": "string",
                            "enum": ["general", "security"],
                            "default": "general",
                            "description": "Type of search (general includes web search, security focuses on CVEs/advisories)",
                        },
                        "resource_type": {
                            "type": "string",
                            "description": "Filter by resource type (RDS, S3, EKS, GKE, AKS, etc.)",
                        },
                        "cloud_provider": {
                            "type": "string",
                            "enum": ["aws", "gcp", "azure"],
                            "description": "Filter by cloud provider",
                        },
                        "severity": {
                            "type": "string",
                            "enum": ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
                            "description": "Filter by severity (for security searches)",
                        },
                        "include_cves": {
                            "type": "boolean",
                            "default": True,
                            "description": "Include CVE database results",
                        },
                        "include_advisories": {
                            "type": "boolean",
                            "default": True,
                            "description": "Include security advisories",
                        },
                        "limit": {
                            "type": "integer",
                            "default": 20,
                            "minimum": 1,
                            "maximum": 100,
                            "description": "Maximum number of results",
                        },
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="wistx_search_codebase",
                description="Search user's indexed codebase including repositories, documentation, "
                            "and documents. Use this tool when asked to search through user's own "
                            "code, documentation, or indexed resources.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query",
                            "minLength": 3,
                            "maxLength": 1000,
                        },
                        "resource_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Filter by specific indexed resources",
                        },
                        "resource_types": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["repository", "documentation", "document"],
                            },
                            "description": "Filter by resource type",
                        },
                        "file_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Filter by file extensions (.tf, .yaml, .py, .md, etc.)",
                        },
                        "code_type": {
                            "type": "string",
                            "enum": ["terraform", "kubernetes", "docker", "python", "javascript", "yaml"],
                            "description": "Filter by code type",
                        },
                        "cloud_provider": {
                            "type": "string",
                            "enum": ["aws", "gcp", "azure"],
                            "description": "Filter by cloud provider mentioned in code",
                        },
                        "limit": {
                            "type": "integer",
                            "default": 20,
                            "minimum": 1,
                            "maximum": 100,
                            "description": "Maximum number of results",
                        },
                        "api_key": {
                            "type": "string",
                            "description": "WISTX API key (required for authentication)",
                        },
                    },
                    "required": ["query", "api_key"],
                },
            ),
            Tool(
                name="wistx_design_architecture",
                description="Design and initialize DevOps/infrastructure/SRE/platform engineering projects. "
                            "Use this tool to scaffold new projects with compliance and security built-in, "
                            "design architectures, review existing architectures, or optimize architectures.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["initialize", "design", "review", "optimize"],
                            "description": "Action to perform",
                        },
                        "project_type": {
                            "type": "string",
                            "enum": ["terraform", "kubernetes", "devops", "platform"],
                            "description": "Type of project (required for initialize)",
                        },
                        "project_name": {
                            "type": "string",
                            "description": "Name of the project (required for initialize)",
                        },
                        "architecture_type": {
                            "type": "string",
                            "enum": ["microservices", "serverless", "monolith", "event-driven"],
                            "description": "Architecture pattern",
                        },
                        "cloud_provider": {
                            "type": "string",
                            "enum": ["aws", "gcp", "azure", "multi-cloud"],
                            "description": "Cloud provider",
                        },
                        "compliance_standards": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Compliance standards to include",
                        },
                        "requirements": {
                            "type": "object",
                            "description": "Project requirements (scalability, availability, security, cost)",
                        },
                        "existing_architecture": {
                            "type": "string",
                            "description": "Existing architecture code/documentation (for review/optimize)",
                        },
                        "output_directory": {
                            "type": "string",
                            "default": ".",
                            "description": "Directory to create project",
                        },
                    },
                    "required": ["action"],
                },
            ),
            Tool(
                name="wistx_troubleshoot_issue",
                description="Diagnose and fix infrastructure/code issues. "
                            "Analyzes errors, logs, and code to identify root causes, "
                            "provides fix recommendations, and prevention strategies. "
                            "Use this tool when encountering errors or issues.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "issue_description": {
                            "type": "string",
                            "description": "Description of the issue",
                            "minLength": 10,
                        },
                        "infrastructure_type": {
                            "type": "string",
                            "enum": ["terraform", "kubernetes", "docker", "cloudformation", "ansible"],
                            "description": "Type of infrastructure",
                        },
                        "cloud_provider": {
                            "type": "string",
                            "enum": ["aws", "gcp", "azure"],
                            "description": "Cloud provider",
                        },
                        "error_messages": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of error messages",
                        },
                        "configuration_code": {
                            "type": "string",
                            "description": "Relevant configuration code",
                        },
                        "logs": {
                            "type": "string",
                            "description": "Log output",
                        },
                        "resource_type": {
                            "type": "string",
                            "description": "Resource type (RDS, S3, EKS, etc.)",
                        },
                        "api_key": {
                            "type": "string",
                            "description": "WISTX API key (for searching user's codebase)",
                        },
                    },
                    "required": ["issue_description"],
                },
            ),
            Tool(
                name="wistx_generate_documentation",
                description="Generate comprehensive documentation and reports. "
                            "Creates architecture docs, runbooks, compliance reports, "
                            "security reports, cost reports, API documentation, and deployment guides. "
                            "Use this tool when asked to create documentation or reports.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_type": {
                            "type": "string",
                            "enum": [
                                "architecture_diagram",
                                "runbook",
                                "compliance_report",
                                "cost_report",
                                "security_report",
                                "api_documentation",
                                "deployment_guide",
                            ],
                            "description": "Type of document to generate",
                        },
                        "subject": {
                            "type": "string",
                            "description": "Subject of the document (project name, resource, topic)",
                        },
                        "infrastructure_code": {
                            "type": "string",
                            "description": "Infrastructure code to document",
                        },
                        "configuration": {
                            "type": "object",
                            "description": "Configuration to document",
                        },
                        "include_compliance": {
                            "type": "boolean",
                            "default": True,
                            "description": "Include compliance information",
                        },
                        "include_security": {
                            "type": "boolean",
                            "default": True,
                            "description": "Include security information",
                        },
                        "include_cost": {
                            "type": "boolean",
                            "default": True,
                            "description": "Include cost information",
                        },
                        "include_best_practices": {
                            "type": "boolean",
                            "default": True,
                            "description": "Include best practices",
                        },
                        "resource_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of resource types (for compliance/security reports)",
                        },
                        "compliance_standards": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of compliance standards (for compliance report)",
                        },
                        "resources": {
                            "type": "array",
                            "items": {"type": "object"},
                            "description": "List of resource specifications (for cost report)",
                        },
                        "api_spec": {
                            "type": "object",
                            "description": "API specification (for api_documentation)",
                        },
                        "format": {
                            "type": "string",
                            "enum": ["markdown", "pdf", "html", "json"],
                            "default": "markdown",
                            "description": "Output format",
                        },
                    },
                    "required": ["document_type", "subject"],
                },
            ),
            Tool(
                name="wistx_manage_integration",
                description="Analyze, generate, and validate infrastructure component integrations. "
                            "Handles networking, security, monitoring, and service integrations. "
                            "Use this tool when working with component integrations.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["analyze", "generate", "validate"],
                            "description": "Action to perform (analyze, generate, validate)",
                        },
                        "infrastructure_code": {
                            "type": "string",
                            "description": "Infrastructure code to analyze (for analyze action)",
                        },
                        "components": {
                            "type": "array",
                            "items": {"type": "object"},
                            "description": "List of components to integrate (for generate action)",
                        },
                        "integration_type": {
                            "type": "string",
                            "enum": ["networking", "security", "monitoring", "service"],
                            "description": "Type of integration",
                        },
                        "cloud_provider": {
                            "type": "string",
                            "enum": ["aws", "gcp", "azure"],
                            "description": "Cloud provider",
                        },
                        "compliance_standards": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Compliance standards to consider",
                        },
                        "pattern_name": {
                            "type": "string",
                            "description": "Specific integration pattern to use (optional)",
                        },
                    },
                    "required": ["action"],
                },
            ),
            Tool(
                name="wistx_manage_infrastructure",
                description="Manage infrastructure lifecycle for Kubernetes clusters and multi-cloud resources. "
                            "Handles creation, updates, upgrades, backups, monitoring, and optimization. "
                            "Use this tool for Kubernetes cluster and multi-cloud management.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["create", "update", "upgrade", "backup", "restore", "monitor", "optimize"],
                            "description": "Action to perform",
                        },
                        "infrastructure_type": {
                            "type": "string",
                            "enum": ["kubernetes", "multi_cloud", "hybrid_cloud"],
                            "description": "Type of infrastructure",
                        },
                        "resource_name": {
                            "type": "string",
                            "description": "Name of the resource/cluster",
                        },
                        "cloud_provider": {
                            "type": "string",
                            "description": "Cloud provider(s) - single string or list for multi-cloud",
                        },
                        "configuration": {
                            "type": "object",
                            "description": "Infrastructure configuration",
                        },
                        "compliance_standards": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Compliance standards to enforce",
                        },
                        "current_version": {
                            "type": "string",
                            "description": "Current version (for upgrade action)",
                        },
                        "target_version": {
                            "type": "string",
                            "description": "Target version (for upgrade action)",
                        },
                        "backup_type": {
                            "type": "string",
                            "enum": ["full", "incremental", "selective"],
                            "default": "full",
                            "description": "Type of backup (for backup action)",
                        },
                    },
                    "required": ["action", "infrastructure_type", "resource_name"],
                },
            ),
            ]
            logger.info("Registered %d MCP tools: %s", len(tools), [t.name for t in tools])
            return tools
        except (ValueError, RuntimeError, AttributeError) as e:
            logger.error("Error in list_tools(): %s", e, exc_info=True)
            raise
        except Exception as e:
            logger.error("Unexpected error in list_tools(): %s", e, exc_info=True)
            raise RuntimeError(f"Failed to list tools: {e}") from e

    @app.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        """Handle tool calls."""
        import json
        import time
        from wistx_mcp.tools.lib.context_builder import ContextBuilder
        from wistx_mcp.tools.lib.metrics import get_tool_metrics

        start_time = time.time()
        logger.info("Tool called: %s with arguments: %s", name, json.dumps(arguments, indent=2))

        success = False
        error: Exception | None = None

        try:
            if name == "wistx_get_compliance_requirements":
                logger.info("Calling wistx_get_compliance_requirements tool...")
                result = await mcp_tools.get_compliance_requirements(**arguments)
                logger.info("Tool wistx_get_compliance_requirements completed successfully")
                
                resource_type = arguments.get("resource_types", [""])[0] if arguments.get("resource_types") else None
                
                controls = []
                if "controls" in result:
                    controls = result["controls"]
                elif "data" in result and isinstance(result["data"], dict):
                    controls = result["data"].get("controls", [])
                
                if not controls:
                    logger.warning("No controls found in response: %s", list(result.keys()))
                    markdown_result = "No compliance controls found for the specified criteria."
                else:
                    markdown_result = ContextBuilder.format_compliance_as_markdown(controls, resource_type)
                
                if not isinstance(markdown_result, str):
                    logger.error("Markdown result is not a string: %s", type(markdown_result))
                    markdown_result = "Error formatting compliance requirements."
                
                if not markdown_result.strip():
                    logger.warning("Markdown result is empty")
                    markdown_result = "No compliance controls found for the specified criteria."
                
                return [TextContent(type="text", text=markdown_result)]

            elif name == "wistx_research_knowledge_base":
                logger.info("Calling wistx_research_knowledge_base tool...")
                result = await mcp_tools.research_knowledge_base(**arguments)
                logger.info("Tool wistx_research_knowledge_base completed successfully")
                
                markdown_result = ContextBuilder.format_knowledge_research_results(result)
                return [TextContent(type="text", text=markdown_result)]

            elif name == "wistx_calculate_infrastructure_cost":
                logger.info("Calling wistx_calculate_infrastructure_cost tool...")
                result = await mcp_tools.calculate_infrastructure_cost(**arguments)
                logger.info("Tool wistx_calculate_infrastructure_cost completed successfully")
                
                markdown_result = ContextBuilder.format_pricing_context(result)
                return [TextContent(type="text", text=markdown_result)]

            elif name == "wistx_index_repository":
                logger.info("Calling wistx_index_repository tool...")
                result = await user_indexing.index_repository(**arguments)
                logger.info("Tool wistx_index_repository completed successfully")
                markdown_result = ContextBuilder.format_indexing_results(result, operation="index")
                return [TextContent(type="text", text=markdown_result)]

            elif name == "wistx_index_resource":
                logger.info("Calling wistx_index_resource tool...")
                result = await user_indexing.index_content(**arguments)
                logger.info("Tool wistx_index_resource completed successfully")
                markdown_result = ContextBuilder.format_indexing_results(result, operation="index")
                return [TextContent(type="text", text=markdown_result)]

            elif name == "wistx_list_resources":
                logger.info("Calling wistx_list_resources tool...")
                result = await user_indexing.list_resources(**arguments)
                logger.info("Tool wistx_list_resources completed successfully")
                markdown_result = ContextBuilder.format_indexing_results(result, operation="list")
                return [TextContent(type="text", text=markdown_result)]

            elif name == "wistx_check_resource_status":
                logger.info("Calling wistx_check_resource_status tool...")
                result = await user_indexing.check_resource_status(**arguments)
                logger.info("Tool wistx_check_resource_status completed successfully")
                markdown_result = ContextBuilder.format_indexing_results(result, operation="check")
                return [TextContent(type="text", text=markdown_result)]

            elif name == "wistx_delete_resource":
                logger.info("Calling wistx_delete_resource tool...")
                result = await user_indexing.delete_resource(**arguments)
                logger.info("Tool wistx_delete_resource completed successfully")
                markdown_result = ContextBuilder.format_indexing_results(result, operation="delete")
                return [TextContent(type="text", text=markdown_result)]

            elif name == "wistx_web_search":
                logger.info("Calling wistx_web_search tool...")
                result = await web_search.web_search(**arguments)
                logger.info("Tool wistx_web_search completed successfully")
                
                markdown_result = ContextBuilder.format_web_search_results(result)
                return [TextContent(type="text", text=markdown_result)]

            elif name == "wistx_search_codebase":
                logger.info("Calling wistx_search_codebase tool...")
                result = await search_codebase.search_codebase(**arguments)
                logger.info("Tool wistx_search_codebase completed successfully")
                
                markdown_result = ContextBuilder.format_codebase_search_results(result)
                return [TextContent(type="text", text=markdown_result)]

            elif name == "wistx_design_architecture":
                logger.info("Calling wistx_design_architecture tool...")
                result = await design_architecture.design_architecture(**arguments)
                logger.info("Tool wistx_design_architecture completed successfully")
                
                markdown_result = ContextBuilder.format_architecture_results(result)
                return [TextContent(type="text", text=markdown_result)]

            elif name == "wistx_troubleshoot_issue":
                logger.info("Calling wistx_troubleshoot_issue tool...")
                result = await troubleshoot_issue.troubleshoot_issue(**arguments)
                logger.info("Tool wistx_troubleshoot_issue completed successfully")
                
                markdown_result = ContextBuilder.format_troubleshooting_results(result)
                return [TextContent(type="text", text=markdown_result)]

            elif name == "wistx_generate_documentation":
                logger.info("Calling wistx_generate_documentation tool...")
                result = await generate_documentation.generate_documentation(**arguments)
                logger.info("Tool wistx_generate_documentation completed successfully")
                
                markdown_result = ContextBuilder.format_documentation_results(result)
                return [TextContent(type="text", text=markdown_result)]

            elif name == "wistx_manage_integration":
                logger.info("Calling wistx_manage_integration tool...")
                result = await manage_integration.manage_integration(**arguments)
                logger.info("Tool wistx_manage_integration completed successfully")
                
                markdown_result = ContextBuilder.format_integration_results(result)
                return [TextContent(type="text", text=markdown_result)]

            elif name == "wistx_manage_infrastructure":
                logger.info("Calling wistx_manage_infrastructure tool...")
                result = await manage_infrastructure.manage_infrastructure(**arguments)
                logger.info("Tool wistx_manage_infrastructure completed successfully")
                
                markdown_result = ContextBuilder.format_infrastructure_results(result)
                return [TextContent(type="text", text=markdown_result)]

            else:
                logger.warning("Unknown tool requested: %s", name)
                raise ValueError(f"Unknown tool: {name}")

            success = True

        except (ValueError, RuntimeError, ConnectionError, TimeoutError, AttributeError) as e:
            error = e
            logger.error("Error calling tool %s: %s", name, e, exc_info=True)
            error_message = f"Error calling {name}: {str(e)}"
            return [TextContent(type="text", text=error_message)]
        except Exception as e:
            error = e
            logger.error("Unexpected error calling tool %s: %s", name, e, exc_info=True)
            error_message = f"Unexpected error calling {name}: {str(e)}"
            return [TextContent(type="text", text=error_message)]
        finally:
            duration = time.time() - start_time
            metrics = get_tool_metrics(name)
            metrics.record_call(duration, success=success, error=error)
            logger.debug("Tool %s completed in %.3f seconds (success=%s)", name, duration, success)

    try:
        logger.info("Starting stdio server...")
        async with stdio_server() as (read_stream, write_stream):
            logger.info("stdio server started, running MCP server...")
            init_options = app.create_initialization_options()
            logger.info("Initialization options created: %s", init_options)
            await app.run(read_stream, write_stream, init_options)
            logger.info("MCP server running")
    except (RuntimeError, ConnectionError, ValueError) as e:
        logger.error("Error starting MCP server: %s", e, exc_info=True)
        raise
    except Exception as e:
        logger.error("Unexpected error starting MCP server: %s", e, exc_info=True)
        raise RuntimeError(f"Failed to start MCP server: {e}") from e
    finally:
        logger.info("Cleaning up MCP server resources...")
        try:
            await mcp_tools.api_client.close()
        except (RuntimeError, ConnectionError) as e:
            logger.warning("Error closing API client: %s", e)


def cli() -> None:
    """CLI entry point for package installation."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down MCP server")
        sys.exit(0)
    except (RuntimeError, ConnectionError, ValueError, AttributeError, KeyboardInterrupt) as e:
        logger.error("Failed to start MCP server: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()

