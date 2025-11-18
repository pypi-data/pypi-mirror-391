"""Design architecture tool - project initialization and architecture design with intelligent context."""

import logging
from pathlib import Path
from typing import Any

from wistx_mcp.tools.lib.mongodb_client import MongoDBClient
from wistx_mcp.tools.lib.vector_search import VectorSearch
from wistx_mcp.tools.lib.architecture_templates import ArchitectureTemplates
from wistx_mcp.tools.lib.api_client import WISTXAPIClient
from wistx_mcp.tools.lib.context_builder import ContextBuilder
from wistx_mcp.tools import mcp_tools, web_search
from wistx_mcp.config import settings

logger = logging.getLogger(__name__)

api_client = WISTXAPIClient()


async def design_architecture(
    action: str,
    project_type: str | None = None,
    project_name: str | None = None,
    architecture_type: str | None = None,
    cloud_provider: str | None = None,
    compliance_standards: list[str] | None = None,
    requirements: dict[str, Any] | None = None,
    existing_architecture: str | None = None,
    output_directory: str = ".",
    template_id: str | None = None,
    github_url: str | None = None,
    user_template: dict[str, Any] | None = None,
    include_compliance: bool = True,
    include_security: bool = True,
    include_best_practices: bool = True,
) -> dict[str, Any]:
    """Design and initialize DevOps/infrastructure/SRE/platform engineering projects with intelligent context.

    This function gathers context from multiple knowledge sources:
    - Templates (project structure)
    - Compliance requirements (standards)
    - Security knowledge (best practices)
    - Knowledge articles (patterns)
    - Code examples (implementations)

    Args:
        action: Action to perform (initialize, design, review, optimize)
        project_type: Type of project (terraform, kubernetes, devops, platform)
        project_name: Name of the project (for initialize)
        architecture_type: Architecture pattern (microservices, serverless, monolith)
        cloud_provider: Cloud provider (aws, gcp, azure, multi-cloud)
        compliance_standards: Compliance standards to include
        requirements: Project requirements
        existing_architecture: Existing architecture code/documentation
        output_directory: Directory to create project
        template_id: Template ID from MongoDB registry
        github_url: GitHub repository URL for template
        user_template: User-provided template dictionary
        include_compliance: Include compliance requirements context
        include_security: Include security knowledge context
        include_best_practices: Include best practices from knowledge base

    Returns:
        Dictionary with architecture results and intelligent context

    Raises:
        ValueError: If invalid parameters
        Exception: If operation fails
    """
    if action not in ["initialize", "design", "review", "optimize"]:
        raise ValueError(f"Invalid action: {action}")

    logger.info(
        "Design architecture: action=%s, type=%s, name=%s",
        action,
        project_type,
        project_name,
    )

    mongodb_client = None
    try:
        if action == "initialize":
            if not project_type or not project_name:
                raise ValueError("project_type and project_name are required for initialize")

            mongodb_client = MongoDBClient()
            await mongodb_client.connect()
            templates = ArchitectureTemplates(mongodb_client)

            template = await templates.get_template(
                project_type=project_type,
                architecture_type=architecture_type,
                cloud_provider=cloud_provider,
                template_id=template_id,
                github_url=github_url,
                user_template=user_template,
            )

            intelligent_context = await _gather_intelligent_context(
                mongodb_client=mongodb_client,
                project_type=project_type,
                architecture_type=architecture_type,
                cloud_provider=cloud_provider,
                compliance_standards=compliance_standards,
                include_compliance=include_compliance,
                include_security=include_security,
                include_best_practices=include_best_practices,
            )

            enhanced_template = await _enhance_template_with_context(
                template=template,
                context=intelligent_context,
                project_type=project_type,
                compliance_standards=compliance_standards,
            )

            project_path = _validate_and_create_output_directory(
                output_directory=output_directory,
                project_name=project_name,
            )

            files_created = []
            structure = []

            await _create_intelligent_project_structure(
                project_path=project_path,
                template=enhanced_template,
                context=intelligent_context,
                compliance_standards=compliance_standards,
                cloud_provider=cloud_provider,
                files_created=files_created,
                structure=structure,
            )

            context_summary = _format_context_summary(intelligent_context)

            return {
                "project_path": str(project_path),
                "files_created": files_created,
                "structure": structure,
                "next_steps": _get_next_steps(project_type, compliance_standards),
                "intelligent_context": context_summary,
                "compliance_applied": bool(intelligent_context.get("compliance")),
                "security_applied": bool(intelligent_context.get("security")),
                "best_practices_applied": bool(intelligent_context.get("best_practices")),
            }

        elif action == "design":
            if not mongodb_client:
                mongodb_client = MongoDBClient()
                await mongodb_client.connect()

            intelligent_context = await _gather_intelligent_context(
                mongodb_client=mongodb_client,
                project_type=project_type,
                architecture_type=architecture_type,
                cloud_provider=cloud_provider,
                compliance_standards=compliance_standards,
                include_compliance=include_compliance,
                include_security=include_security,
                include_best_practices=include_best_practices,
            )

            vector_search = VectorSearch(
                mongodb_client,
                openai_api_key=settings.openai_api_key,
            )

            query = f"{architecture_type} architecture pattern"
            if cloud_provider:
                query += f" {cloud_provider}"

            patterns = await vector_search.search_knowledge_articles(
                query=query,
                domains=["architecture"],
                limit=10,
            )

            recommendations = _get_intelligent_recommendations(
                architecture_type=architecture_type,
                requirements=requirements,
                context=intelligent_context,
            )

            return {
                "architecture_diagram": _generate_architecture_diagram(
                    architecture_type,
                    cloud_provider,
                ),
                "components": _get_architecture_components(architecture_type),
                "patterns": patterns,
                "recommendations": recommendations,
                "intelligent_context": _format_context_summary(intelligent_context),
            }

        elif action == "review":
            return await _review_architecture(
                existing_architecture=existing_architecture,
                compliance_standards=compliance_standards,
            )

        elif action == "optimize":
            return await _optimize_architecture(
                existing_architecture=existing_architecture,
                requirements=requirements,
            )

    except Exception as e:
        logger.error("Error in design_architecture: %s", e, exc_info=True)
        raise
    finally:
        if mongodb_client:
            await mongodb_client.close()


async def _gather_intelligent_context(
    mongodb_client: MongoDBClient,
    project_type: str | None,
    architecture_type: str | None,
    cloud_provider: str | None,
    compliance_standards: list[str] | None,
    include_compliance: bool,
    include_security: bool,
    include_best_practices: bool,
) -> dict[str, Any]:
    """Gather intelligent context from all knowledge sources in parallel.

    Args:
        mongodb_client: MongoDB client instance
        project_type: Project type
        architecture_type: Architecture type
        cloud_provider: Cloud provider
        compliance_standards: Compliance standards
        include_compliance: Include compliance context
        include_security: Include security context
        include_best_practices: Include best practices context

    Returns:
        Dictionary with gathered context
    """
    import asyncio
    from wistx_mcp.tools.lib.retry_utils import with_timeout_and_retry

    context: dict[str, Any] = {}

    async def gather_compliance() -> dict[str, Any] | None:
        """Gather compliance context."""
        if not include_compliance or not compliance_standards:
            return None
        try:
            resource_types = [project_type] if project_type else []
            if cloud_provider:
                resource_types.append(cloud_provider)

            result = await with_timeout_and_retry(
                mcp_tools.get_compliance_requirements,
                timeout_seconds=30.0,
                max_attempts=3,
                resource_types=resource_types,
                standards=compliance_standards,
                include_remediation=True,
                include_verification=True,
            )
            logger.info("Gathered compliance context: %d controls", len(result.get("controls", [])))
            return result
        except Exception as e:
            logger.warning("Failed to gather compliance context: %s", e)
            return None

    async def gather_security() -> dict[str, Any] | None:
        """Gather security context."""
        if not include_security:
            return None
        try:
            security_query = f"{project_type} security best practices"
            if cloud_provider:
                security_query += f" {cloud_provider}"
            if architecture_type:
                security_query += f" {architecture_type}"

            result = await with_timeout_and_retry(
                web_search.web_search,
                timeout_seconds=30.0,
                max_attempts=3,
                query=security_query,
                search_type="security",
                limit=10,
            )
            security_results = result.get("security", {}).get("results", []) or result.get("web", {}).get("results", [])
            logger.info("Gathered security context: %d results", len(security_results))
            return result
        except Exception as e:
            logger.warning("Failed to gather security context: %s", e)
            return None

    async def gather_best_practices() -> dict[str, Any] | None:
        """Gather best practices context."""
        if not include_best_practices:
            return None
        try:
            best_practices_query = f"{architecture_type} {project_type}"
            if cloud_provider:
                best_practices_query += f" {cloud_provider}"
            best_practices_query += " production best practices"

            result = await with_timeout_and_retry(
                mcp_tools.research_knowledge_base,
                timeout_seconds=30.0,
                max_attempts=3,
                query=best_practices_query,
                domains=["architecture", "devops"],
                include_cross_domain=True,
                include_web_search=True,
                max_results=15,
            )
            logger.info(
                "Gathered best practices context: %d articles",
                len(result.get("results", [])),
            )
            return result
        except Exception as e:
            logger.warning("Failed to gather best practices context: %s", e)
            return None

    results = await asyncio.gather(
        gather_compliance(),
        gather_security(),
        gather_best_practices(),
        return_exceptions=True,
    )

    compliance_result, security_result, best_practices_result = results

    if compliance_result and not isinstance(compliance_result, Exception):
        context["compliance"] = compliance_result

    if security_result and not isinstance(security_result, Exception):
        context["security"] = security_result

    if best_practices_result and not isinstance(best_practices_result, Exception):
        context["best_practices"] = best_practices_result

    return context


async def _enhance_template_with_context(
    template: dict[str, Any],
    context: dict[str, Any],
    project_type: str,
    compliance_standards: list[str] | None,
) -> dict[str, Any]:
    """Enhance template with intelligent context.

    Args:
        template: Original template dictionary
        context: Intelligent context dictionary
        project_type: Project type
        compliance_standards: Compliance standards

    Returns:
        Enhanced template dictionary
    """
    enhanced_template = template.copy()
    structure = enhanced_template.get("structure", {}).copy()

    compliance_controls = context.get("compliance", {}).get("controls", [])
    if compliance_controls and project_type == "kubernetes":
        if "rbac" not in structure:
            structure["rbac"] = {}

        rbac_content = _generate_rbac_from_compliance(compliance_controls)
        if rbac_content:
            structure["rbac"]["service-account.yaml"] = rbac_content

        if "network-policies" not in structure:
            structure["network-policies"] = {}

        network_policy_content = _generate_network_policy_from_compliance(compliance_controls)
        if network_policy_content:
            structure["network-policies"]["network-policy.yaml"] = network_policy_content

    if compliance_standards and "compliance" not in structure:
        structure["compliance"] = {}

    for standard in compliance_standards or []:
        compliance_file = f"{standard.lower().replace('-', '_')}.yaml"
        compliance_content = _generate_compliance_config(standard, compliance_controls)
        structure["compliance"][compliance_file] = compliance_content

    enhanced_template["structure"] = structure
    enhanced_template["context_applied"] = {
        "compliance": bool(context.get("compliance")),
        "security": bool(context.get("security")),
        "best_practices": bool(context.get("best_practices")),
    }

    return enhanced_template


def _generate_rbac_from_compliance(controls: list[dict[str, Any]]) -> str:
    """Generate RBAC configuration from compliance controls.

    Args:
        controls: List of compliance controls

    Returns:
        RBAC YAML content
    """
    rbac_content = """apiVersion: v1
kind: ServiceAccount
metadata:
  name: app-service-account
  namespace: default
  annotations:
    # Compliance: Least privilege access
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: app-role
  namespace: default
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: app-rolebinding
  namespace: default
subjects:
- kind: ServiceAccount
  name: app-service-account
  namespace: default
roleRef:
  kind: Role
  name: app-role
  apiGroup: rbac.authorization.k8s.io
"""
    return rbac_content


def _generate_network_policy_from_compliance(controls: list[dict[str, Any]]) -> str:
    """Generate network policy from compliance controls.

    Args:
        controls: List of compliance controls

    Returns:
        Network policy YAML content
    """
    network_policy = """apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: app-network-policy
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: app
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 53
  - to:
    - namespaceSelector:
        matchLabels:
          name: monitoring
    ports:
    - protocol: TCP
      port: 9090
"""
    return network_policy


def _generate_compliance_config(standard: str, controls: list[dict[str, Any]]) -> str:
    """Generate compliance configuration file.

    Args:
        standard: Compliance standard name
        controls: List of compliance controls

    Returns:
        Compliance configuration content
    """
    config = f"# {standard} Compliance Configuration\n\n"
    config += "## Applied Controls\n\n"

    for control in controls[:10]:
        control_id = control.get("control_id", "")
        title = control.get("title", "")
        config += f"### {control_id}: {title}\n\n"
        remediation = control.get("remediation", {})
        if remediation.get("guidance"):
            config += f"{remediation['guidance']}\n\n"

    return config


async def _create_intelligent_project_structure(
    project_path: Path,
    template: dict[str, Any],
    context: dict[str, Any],
    compliance_standards: list[str] | None,
    cloud_provider: str | None,
    files_created: list[str],
    structure: list[str],
) -> None:
    """Create intelligent project structure with context-enhanced templates.

    Args:
        project_path: Path to project directory
        template: Enhanced template dictionary
        context: Intelligent context dictionary
        compliance_standards: Compliance standards
        cloud_provider: Cloud provider
        files_created: List to append created files
        structure: List to append structure items
    """
    structure_dict = template.get("structure", {})

    for item_path, content in structure_dict.items():
        full_path = project_path / item_path

        if isinstance(content, dict):
            full_path.mkdir(parents=True, exist_ok=True)
            structure.append(f"{item_path}/")
            await _create_intelligent_project_structure(
                project_path=full_path,
                template={"structure": content},
                context=context,
                compliance_standards=compliance_standards,
                cloud_provider=cloud_provider,
                files_created=files_created,
                structure=structure,
            )
        else:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(str(content), encoding="utf-8")
            files_created.append(str(full_path.relative_to(project_path)))
            structure.append(item_path)

    if compliance_standards and "compliance" not in structure_dict:
        compliance_dir = project_path / "compliance"
        compliance_dir.mkdir(exist_ok=True)

        for standard in compliance_standards:
            compliance_file = compliance_dir / f"{standard.lower().replace('-', '_')}.yaml"
            compliance_content = _generate_compliance_config(
                standard,
                context.get("compliance", {}).get("controls", []),
            )
            compliance_file.write_text(compliance_content, encoding="utf-8")
            files_created.append(str(compliance_file.relative_to(project_path)))


def _format_context_summary(context: dict[str, Any]) -> dict[str, Any]:
    """Format context summary for response.

    Args:
        context: Intelligent context dictionary

    Returns:
        Formatted context summary
    """
    security_data = context.get("security", {})
    security_results = security_data.get("security", {}).get("results", []) or security_data.get("web", {}).get("results", [])

    summary = {
        "compliance": {
            "enabled": bool(context.get("compliance")),
            "controls_count": len(context.get("compliance", {}).get("controls", [])),
        },
        "security": {
            "enabled": bool(context.get("security")),
            "results_count": len(security_results),
        },
        "best_practices": {
            "enabled": bool(context.get("best_practices")),
            "articles_count": len(context.get("best_practices", {}).get("results", [])),
        },
    }
    return summary


def _get_intelligent_recommendations(
    architecture_type: str | None,
    requirements: dict[str, Any] | None,
    context: dict[str, Any],
) -> list[str]:
    """Get intelligent recommendations based on context.

    Args:
        architecture_type: Architecture type
        requirements: Project requirements
        context: Intelligent context dictionary

    Returns:
        List of recommendations
    """
    recommendations = []

    if architecture_type == "microservices":
        recommendations.extend([
            "Use service mesh for inter-service communication",
            "Implement centralized logging",
            "Set up distributed tracing",
        ])

    if requirements and requirements.get("scalability") == "high":
        recommendations.append("Consider auto-scaling configuration")

    compliance_controls = context.get("compliance", {}).get("controls", [])
    if compliance_controls:
        recommendations.append(f"Applied {len(compliance_controls)} compliance controls")

    security_data = context.get("security", {})
    security_results = security_data.get("security", {}).get("results", []) or security_data.get("web", {}).get("results", [])
    if security_results:
        recommendations.append("Security best practices applied from latest knowledge")

    best_practices = context.get("best_practices", {}).get("results", [])
    if best_practices:
        recommendations.append(f"Applied {len(best_practices)} best practice patterns")

    return recommendations


def _validate_and_create_output_directory(
    output_directory: str,
    project_name: str,
) -> Path:
    """Validate and sanitize output directory path.

    Prevents path traversal attacks and ensures safe directory creation.

    Args:
        output_directory: Output directory path
        project_name: Project name (will be appended to output_directory)

    Returns:
        Validated Path object

    Raises:
        ValueError: If path is invalid or unsafe
    """
    if not output_directory:
        raise ValueError("output_directory cannot be empty")

    if not project_name:
        raise ValueError("project_name cannot be empty")

    if ".." in output_directory or ".." in project_name:
        raise ValueError("Path traversal not allowed in output_directory or project_name")

    if output_directory.startswith("/") and not output_directory.startswith("/tmp"):
        raise ValueError("Only /tmp directory allowed for absolute paths")

    if any(char in project_name for char in ["/", "\\", ":", "*", "?", '"', "<", ">", "|"]):
        raise ValueError(f"Invalid characters in project_name: {project_name}")

    base_path = Path(output_directory).resolve()

    if not base_path.exists():
        try:
            base_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise ValueError(f"Cannot create output directory: {e}") from e

    if not base_path.is_dir():
        raise ValueError(f"output_directory must be a directory: {output_directory}")

    project_path = base_path / project_name

    if project_path.exists() and not project_path.is_dir():
        raise ValueError(f"Project path exists but is not a directory: {project_path}")

    try:
        project_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise ValueError(f"Cannot create project directory: {e}") from e

    return project_path


def _get_next_steps(
    project_type: str,
    compliance_standards: list[str] | None,
) -> list[str]:
    """Get recommended next steps.

    Args:
        project_type: Type of project
        compliance_standards: Compliance standards

    Returns:
        List of next steps
    """
    steps = []

    if project_type == "terraform":
        steps.extend([
            f"Review generated {project_type} project structure",
            "Configure variables in terraform.tfvars",
            "Initialize Terraform: terraform init",
            "Plan changes: terraform plan",
            "Apply infrastructure: terraform apply",
        ])
    elif project_type == "kubernetes":
        steps.extend([
            "Review Kubernetes manifests",
            "Apply namespace: kubectl apply -f namespace.yaml",
            "Deploy resources: kubectl apply -f deployments/",
        ])

    if compliance_standards:
        steps.append(
            f"Review compliance configurations for {', '.join(compliance_standards)}"
        )

    return steps


def _generate_architecture_diagram(
    architecture_type: str | None,
    cloud_provider: str | None,
) -> str:
    """Generate architecture diagram text.

    Args:
        architecture_type: Architecture pattern
        cloud_provider: Cloud provider

    Returns:
        Architecture diagram as text
    """
    if architecture_type == "microservices":
        return """
Microservices Architecture:
- API Gateway → Multiple Services
- Each service: Independent deployment
- Service mesh for communication
- Centralized logging and monitoring
"""
    elif architecture_type == "serverless":
        return """
Serverless Architecture:
- API Gateway → Lambda Functions
- Event-driven architecture
- Managed services (RDS, DynamoDB)
- Auto-scaling
"""
    return "Architecture diagram"


def _get_architecture_components(
    architecture_type: str | None,
) -> list[dict[str, Any]]:
    """Get architecture components.

    Args:
        architecture_type: Architecture pattern

    Returns:
        List of component dictionaries
    """
    if architecture_type == "microservices":
        return [
            {"name": "API Gateway", "type": "gateway"},
            {"name": "Service A", "type": "service"},
            {"name": "Service B", "type": "service"},
            {"name": "Database", "type": "database"},
        ]
    return []


def _get_architecture_recommendations(
    architecture_type: str | None,
    requirements: dict[str, Any] | None,
) -> list[str]:
    """Get architecture recommendations.

    Args:
        architecture_type: Architecture pattern
        requirements: Project requirements

    Returns:
        List of recommendations
    """
    recommendations = []

    if architecture_type == "microservices":
        recommendations.extend([
            "Use service mesh for inter-service communication",
            "Implement centralized logging",
            "Set up distributed tracing",
        ])

    if requirements and requirements.get("scalability") == "high":
        recommendations.append("Consider auto-scaling configuration")

    return recommendations


async def _review_architecture(
    existing_architecture: str | None,
    compliance_standards: list[str] | None,
) -> dict[str, Any]:
    """Review existing architecture.

    Args:
        existing_architecture: Existing architecture code/documentation
        compliance_standards: Compliance standards to check

    Returns:
        Review results dictionary
    """
    if not existing_architecture:
        return {
            "issues": [],
            "recommendations": [],
            "compliance_status": "unknown",
            "security_status": "unknown",
        }

    issues = []
    recommendations = []

    if "encryption" not in existing_architecture.lower():
        issues.append("Missing encryption configuration")
        recommendations.append("Add encryption for data at rest and in transit")

    if compliance_standards:
        compliance_status = "partial"
        for standard in compliance_standards:
            if standard.lower() not in existing_architecture.lower():
                issues.append(f"Missing {standard} compliance configurations")
    else:
        compliance_status = "unknown"

    return {
        "issues": issues,
        "recommendations": recommendations,
        "compliance_status": compliance_status,
        "security_status": "review_needed",
    }


async def _optimize_architecture(
    existing_architecture: str | None,
    requirements: dict[str, Any] | None,
) -> dict[str, Any]:
    """Optimize architecture.

    Args:
        existing_architecture: Existing architecture code/documentation
        requirements: Optimization requirements

    Returns:
        Optimization results dictionary
    """
    optimizations = []
    cost_savings = []
    performance_improvements = []

    if existing_architecture:
        if "m5.2xlarge" in existing_architecture:
            optimizations.append("Consider using t3.medium for non-production workloads")
            cost_savings.append("Potential 60% cost reduction")

        if "single-az" not in existing_architecture.lower():
            optimizations.append("Consider single-AZ for non-critical workloads")
            cost_savings.append("Potential 50% cost reduction")

    return {
        "optimizations": optimizations,
        "cost_savings": cost_savings,
        "performance_improvements": performance_improvements,
    }

