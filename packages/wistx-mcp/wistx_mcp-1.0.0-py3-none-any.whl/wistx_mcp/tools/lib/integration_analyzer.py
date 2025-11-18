"""Integration analyzer for detecting missing connections and dependency issues."""

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


class IntegrationAnalyzer:
    """Analyzer for detecting integration issues in infrastructure code."""

    def analyze(
        self,
        infrastructure_code: str,
        cloud_provider: str | None = None,
    ) -> dict[str, Any]:
        """Analyze infrastructure code for integration issues.

        Args:
            infrastructure_code: Infrastructure code to analyze
            cloud_provider: Cloud provider (aws, gcp, azure)

        Returns:
            Dictionary with analysis results:
            - missing_connections: List of missing connections
            - dependency_issues: List of dependency issues
            - security_gaps: List of security gaps
            - recommendations: List of recommendations
        """
        missing_connections = []
        dependency_issues = []
        security_gaps = []
        recommendations = []

        if cloud_provider == "aws":
            missing_connections.extend(self._analyze_aws_connections(infrastructure_code))
            dependency_issues.extend(self._analyze_aws_dependencies(infrastructure_code))
            security_gaps.extend(self._analyze_aws_security(infrastructure_code))

        if cloud_provider == "kubernetes" or "kubernetes" in infrastructure_code.lower():
            missing_connections.extend(self._analyze_k8s_connections(infrastructure_code))
            dependency_issues.extend(self._analyze_k8s_dependencies(infrastructure_code))
            security_gaps.extend(self._analyze_k8s_security(infrastructure_code))

        if missing_connections:
            recommendations.append("Add missing connections between components")
        if dependency_issues:
            recommendations.append("Resolve dependency issues")
        if security_gaps:
            recommendations.append("Address security gaps")

        return {
            "missing_connections": missing_connections,
            "dependency_issues": dependency_issues,
            "security_gaps": security_gaps,
            "recommendations": recommendations,
        }

    def _analyze_aws_connections(self, code: str) -> list[str]:
        """Analyze AWS infrastructure for missing connections.

        Args:
            code: Infrastructure code

        Returns:
            List of missing connection issues
        """
        issues = []

        if "aws_instance" in code and "aws_security_group" not in code:
            issues.append("EC2 instances without security groups")

        if "aws_lambda_function" in code and "aws_api_gateway" not in code:
            if "aws_apigatewayv2" not in code:
                issues.append("Lambda functions without API Gateway integration")

        if "aws_ecs_service" in code and "aws_lb" not in code:
            if "aws_lb_target_group" not in code:
                issues.append("ECS services without load balancer")

        if "aws_rds_instance" in code:
            if "aws_db_subnet_group" not in code:
                issues.append("RDS instances without subnet group")
            if "aws_security_group" not in code or "db" not in code.lower():
                issues.append("RDS instances without database security group")

        return issues

    def _analyze_aws_dependencies(self, code: str) -> list[str]:
        """Analyze AWS infrastructure for dependency issues.

        Args:
            code: Infrastructure code

        Returns:
            List of dependency issues
        """
        issues = []

        if "aws_subnet" in code and "aws_vpc" not in code:
            issues.append("Subnets without VPC reference")

        if "aws_route_table" in code and "aws_vpc" not in code:
            issues.append("Route tables without VPC reference")

        if "aws_internet_gateway" in code and "aws_vpc" not in code:
            issues.append("Internet gateway without VPC attachment")

        return issues

    def _analyze_aws_security(self, code: str) -> list[str]:
        """Analyze AWS infrastructure for security gaps.

        Args:
            code: Infrastructure code

        Returns:
            List of security gaps
        """
        gaps = []

        if "aws_instance" in code:
            if re.search(r'user_data\s*=', code, re.IGNORECASE):
                if re.search(r'password\s*=\s*["\']', code, re.IGNORECASE):
                    gaps.append("Hardcoded passwords in user_data")
            if "aws_iam_role" not in code:
                gaps.append("EC2 instances without IAM roles")

        if "aws_s3_bucket" in code:
            if "aws_s3_bucket_public_access_block" not in code:
                gaps.append("S3 buckets without public access block")
            if "aws_s3_bucket_versioning" not in code:
                gaps.append("S3 buckets without versioning")

        if "aws_rds_instance" in code:
            if "publicly_accessible" in code and "true" in code.lower():
                gaps.append("Publicly accessible RDS instances")

        return gaps

    def _analyze_k8s_connections(self, code: str) -> list[str]:
        """Analyze Kubernetes manifests for missing connections.

        Args:
            code: Kubernetes manifest code

        Returns:
            List of missing connection issues
        """
        issues = []

        if "kind: Deployment" in code or "kind: Pod" in code:
            if "kind: Service" not in code:
                issues.append("Deployments/Pods without Service")

        if "kind: Service" in code:
            if "kind: Ingress" not in code:
                if "type: LoadBalancer" not in code and "type: NodePort" not in code:
                    issues.append("Services without Ingress or LoadBalancer")

        return issues

    def _analyze_k8s_dependencies(self, code: str) -> list[str]:
        """Analyze Kubernetes manifests for dependency issues.

        Args:
            code: Kubernetes manifest code

        Returns:
            List of dependency issues
        """
        issues = []

        if "kind: Deployment" in code:
            if "image:" not in code:
                issues.append("Deployments without container images")

        if "kind: Service" in code:
            if "selector:" not in code:
                issues.append("Services without selectors")

        return issues

    def _analyze_k8s_security(self, code: str) -> list[str]:
        """Analyze Kubernetes manifests for security gaps.

        Args:
            code: Kubernetes manifest code

        Returns:
            List of security gaps
        """
        gaps = []

        if "kind: Deployment" in code or "kind: Pod" in code:
            if "securityContext:" not in code:
                gaps.append("Pods without security context")
            if "runAsNonRoot:" not in code:
                gaps.append("Pods not running as non-root")
            if "readOnlyRootFilesystem:" not in code:
                gaps.append("Pods without read-only root filesystem")

        if "kind: NetworkPolicy" not in code:
            gaps.append("Missing network policies for pod isolation")

        if "kind: Secret" in code:
            if "type: Opaque" in code:
                gaps.append("Using generic Opaque secrets - consider specific secret types")

        return gaps

    def validate_integration(
        self,
        components: list[dict[str, Any]],
        integration_type: str,
    ) -> dict[str, Any]:
        """Validate integration between components.

        Args:
            components: List of component dictionaries
            integration_type: Type of integration (networking, security, service, monitoring)

        Returns:
            Dictionary with validation results:
            - valid: Whether integration is valid
            - issues: List of validation issues
            - fixes: List of recommended fixes
        """
        issues = []
        fixes = []

        component_types = [comp.get("type", "").lower() for comp in components]

        if integration_type == "networking":
            if "vpc" not in component_types and "aws" in str(component_types):
                issues.append("Missing VPC for networking integration")
                fixes.append("Add VPC resource")

        if integration_type == "security":
            if "security_group" not in component_types and "aws" in str(component_types):
                issues.append("Missing security groups for security integration")
                fixes.append("Add security group resources")

        if integration_type == "service":
            if "service" not in component_types and "kubernetes" in str(component_types):
                issues.append("Missing Kubernetes Service for service integration")
                fixes.append("Add Service resource")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "fixes": fixes,
        }

