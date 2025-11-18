"""Integration generator for creating integration code."""

import logging
from typing import Any

from wistx_mcp.tools.lib.integration_patterns import get_pattern, get_patterns_for_provider

logger = logging.getLogger(__name__)


class IntegrationGenerator:
    """Generator for integration code."""

    def generate(
        self,
        components: list[dict[str, Any]],
        integration_type: str,
        cloud_provider: str,
        pattern_name: str | None = None,
    ) -> dict[str, Any]:
        """Generate integration code for components.

        Args:
            components: List of components to integrate
            integration_type: Type of integration (networking, security, service, monitoring)
            cloud_provider: Cloud provider (aws, gcp, azure)
            pattern_name: Specific pattern to use (optional)

        Returns:
            Dictionary with generated code:
            - integration_code: Generated integration code
            - dependencies: List of dependencies
            - security_rules: Security rules to apply
            - monitoring: Monitoring configuration
        """
        if pattern_name:
            pattern = get_pattern(integration_type, pattern_name)
            if not pattern:
                raise ValueError(f"Pattern {pattern_name} not found for {integration_type}")
        else:
            patterns = get_patterns_for_provider(cloud_provider)
            pattern_type = patterns.get(integration_type, {})
            if not pattern_type:
                raise ValueError(f"No patterns found for {integration_type} on {cloud_provider}")

            pattern_name = list(pattern_type.keys())[0] if pattern_type else None
            pattern = pattern_type.get(pattern_name) if pattern_name else None

            if not pattern:
                raise ValueError(f"No suitable pattern found for {integration_type}")

        if cloud_provider == "aws" or cloud_provider in pattern.get("providers", []):
            code_key = "terraform_example"
        elif cloud_provider == "kubernetes":
            code_key = "kubernetes_example"
        else:
            code_key = "terraform_example"

        integration_code = pattern.get(code_key, "")

        if not integration_code:
            integration_code = self._generate_generic_code(
                components,
                integration_type,
                cloud_provider,
            )

        dependencies = pattern.get("components", [])
        security_rules = self._generate_security_rules(integration_type, cloud_provider)
        monitoring = self._generate_monitoring_config(integration_type, cloud_provider)

        return {
            "integration_code": integration_code,
            "dependencies": dependencies,
            "security_rules": security_rules,
            "monitoring": monitoring,
            "pattern_used": pattern_name,
            "description": pattern.get("description", ""),
        }

    def _generate_generic_code(
        self,
        components: list[dict[str, Any]],
        integration_type: str,
        cloud_provider: str,
    ) -> str:
        """Generate generic integration code when no pattern matches.

        Args:
            components: List of components
            integration_type: Type of integration
            cloud_provider: Cloud provider

        Returns:
            Generic integration code
        """
        component_names = [comp.get("id", comp.get("type", "component")) for comp in components]

        if cloud_provider == "aws":
            return f"""
# Integration between {', '.join(component_names)}
# Integration type: {integration_type}

# TODO: Add integration code for {integration_type} integration
# Components: {', '.join(component_names)}
"""
        elif cloud_provider == "kubernetes":
            return f"""
# Integration between {', '.join(component_names)}
# Integration type: {integration_type}

# TODO: Add Kubernetes integration code for {integration_type} integration
# Components: {', '.join(component_names)}
"""
        else:
            return f"""
# Integration between {', '.join(component_names)}
# Integration type: {integration_type}
# Cloud provider: {cloud_provider}

# TODO: Add integration code
"""

    def _generate_security_rules(
        self,
        integration_type: str,
        cloud_provider: str,
    ) -> list[str]:
        """Generate security rules for integration.

        Args:
            integration_type: Type of integration
            cloud_provider: Cloud provider

        Returns:
            List of security rules
        """
        rules = []

        if integration_type == "networking":
            rules.append("Restrict network access to necessary ports only")
            rules.append("Use security groups/network policies for access control")
            rules.append("Enable encryption in transit")

        if integration_type == "security":
            rules.append("Implement least privilege access")
            rules.append("Use IAM roles/service accounts")
            rules.append("Enable audit logging")

        if integration_type == "service":
            rules.append("Use secure communication protocols")
            rules.append("Implement authentication and authorization")
            rules.append("Enable request validation")

        return rules

    def _generate_monitoring_config(
        self,
        integration_type: str,
        cloud_provider: str,
    ) -> dict[str, Any]:
        """Generate monitoring configuration for integration.

        Args:
            integration_type: Type of integration
            cloud_provider: Cloud provider

        Returns:
            Monitoring configuration dictionary
        """
        config = {
            "metrics": [],
            "alarms": [],
            "logs": [],
        }

        if cloud_provider == "aws":
            config["metrics"].append("Integration latency")
            config["metrics"].append("Error rate")
            config["alarms"].append("High error rate alarm")
            config["logs"].append("CloudWatch Logs")

        if cloud_provider == "kubernetes":
            config["metrics"].append("Request rate")
            config["metrics"].append("Response time")
            config["alarms"].append("Pod restart alarm")
            config["logs"].append("Kubernetes logs")

        return config

