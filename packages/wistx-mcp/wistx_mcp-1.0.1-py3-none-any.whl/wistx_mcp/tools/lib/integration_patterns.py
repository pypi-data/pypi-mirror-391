"""Integration patterns library for infrastructure component integration."""

from typing import Any

INTEGRATION_PATTERNS: dict[str, dict[str, dict[str, Any]]] = {
    "networking": {
        "vpc_peering": {
            "description": "VPC peering for cross-VPC communication",
            "providers": ["aws", "gcp", "azure"],
            "components": ["vpc", "subnet", "route_table"],
            "terraform_example": """
resource "aws_vpc_peering_connection" "peer" {
  vpc_id      = var.vpc_id
  peer_vpc_id = var.peer_vpc_id
  auto_accept = true
}

resource "aws_route" "peer_route" {
  route_table_id            = var.route_table_id
  destination_cidr_block    = var.peer_cidr_block
  vpc_peering_connection_id = aws_vpc_peering_connection.peer.id
}
""",
        },
        "vpn": {
            "description": "VPN connection for secure remote access",
            "providers": ["aws", "gcp", "azure"],
            "components": ["vpn_gateway", "customer_gateway", "vpn_connection"],
            "terraform_example": """
resource "aws_vpn_gateway" "vpn_gw" {
  vpc_id = var.vpc_id
}

resource "aws_customer_gateway" "customer_gw" {
  bgp_asn    = 65000
  ip_address = var.customer_gateway_ip
  type      = "ipsec.1"
}

resource "aws_vpn_connection" "vpn" {
  vpc_gateway_id      = aws_vpn_gateway.vpn_gw.id
  customer_gateway_id = aws_customer_gateway.customer_gw.id
  type                = "ipsec.1"
}
""",
        },
        "privatelink": {
            "description": "AWS PrivateLink for private service access",
            "providers": ["aws"],
            "components": ["vpc_endpoint", "service"],
            "terraform_example": """
resource "aws_vpc_endpoint" "s3" {
  vpc_id       = var.vpc_id
  service_name = "com.amazonaws.${var.region}.s3"
  vpc_endpoint_type = "Gateway"
}
""",
        },
    },
    "security": {
        "security_groups": {
            "description": "Security groups for network access control",
            "providers": ["aws"],
            "components": ["security_group", "instance"],
            "terraform_example": """
resource "aws_security_group" "web" {
  name        = "web-sg"
  description = "Security group for web servers"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
""",
        },
        "iam_roles": {
            "description": "IAM roles for service authentication",
            "providers": ["aws", "gcp", "azure"],
            "components": ["iam_role", "service"],
            "terraform_example": """
resource "aws_iam_role" "lambda_role" {
  name = "lambda-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}
""",
        },
        "network_policies": {
            "description": "Kubernetes network policies",
            "providers": ["kubernetes"],
            "components": ["network_policy", "pod"],
            "kubernetes_example": """
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
""",
        },
    },
    "service": {
        "api_gateway_lambda": {
            "description": "API Gateway to Lambda integration",
            "providers": ["aws"],
            "components": ["api_gateway", "lambda"],
            "terraform_example": """
resource "aws_api_gateway_rest_api" "api" {
  name = "my-api"
}

resource "aws_api_gateway_resource" "resource" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "hello"
}

resource "aws_api_gateway_method" "method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.resource.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "integration" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.resource.id
  http_method = aws_api_gateway_method.method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.lambda.invoke_arn
}
""",
        },
        "alb_ecs": {
            "description": "Application Load Balancer to ECS integration",
            "providers": ["aws"],
            "components": ["alb", "ecs_service"],
            "terraform_example": """
resource "aws_lb_target_group" "tg" {
  name     = "ecs-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = var.vpc_id
}

resource "aws_lb_listener" "listener" {
  load_balancer_arn = aws_lb.alb.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.tg.arn
  }
}

resource "aws_ecs_service" "service" {
  name            = "my-service"
  cluster         = aws_ecs_cluster.cluster.id
  task_definition = aws_ecs_task_definition.task.arn
  desired_count   = 2

  load_balancer {
    target_group_arn = aws_lb_target_group.tg.arn
    container_name  = "my-container"
    container_port  = 80
  }
}
""",
        },
        "ingress_kubernetes": {
            "description": "Ingress controller for Kubernetes",
            "providers": ["kubernetes"],
            "components": ["ingress", "service"],
            "kubernetes_example": """
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-ingress
spec:
  rules:
  - host: example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: my-service
            port:
              number: 80
""",
        },
    },
    "monitoring": {
        "cloudwatch": {
            "description": "CloudWatch monitoring integration",
            "providers": ["aws"],
            "components": ["cloudwatch", "resource"],
            "terraform_example": """
resource "aws_cloudwatch_metric_alarm" "cpu_alarm" {
  alarm_name          = "cpu-utilization"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "120"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors ec2 cpu utilization"
}
""",
        },
        "prometheus": {
            "description": "Prometheus monitoring integration",
            "providers": ["kubernetes"],
            "components": ["prometheus", "service"],
            "kubernetes_example": """
apiVersion: v1
kind: ServiceMonitor
metadata:
  name: my-service-monitor
spec:
  selector:
    matchLabels:
      app: my-app
  endpoints:
  - port: metrics
    interval: 30s
""",
        },
    },
}


def get_pattern(
    integration_type: str,
    pattern_name: str,
) -> dict[str, Any] | None:
    """Get integration pattern by type and name.

    Args:
        integration_type: Type of integration (networking, security, service, monitoring)
        pattern_name: Name of the pattern

    Returns:
        Pattern dictionary or None if not found
    """
    return INTEGRATION_PATTERNS.get(integration_type, {}).get(pattern_name)


def list_patterns(integration_type: str | None = None) -> dict[str, Any]:
    """List available integration patterns.

    Args:
        integration_type: Filter by integration type (optional)

    Returns:
        Dictionary of patterns
    """
    if integration_type:
        return INTEGRATION_PATTERNS.get(integration_type, {})
    return INTEGRATION_PATTERNS


def get_patterns_for_provider(cloud_provider: str) -> dict[str, Any]:
    """Get all patterns available for a cloud provider.

    Args:
        cloud_provider: Cloud provider (aws, gcp, azure, kubernetes)

    Returns:
        Dictionary of patterns filtered by provider
    """
    result: dict[str, Any] = {}
    for integration_type, patterns in INTEGRATION_PATTERNS.items():
        for pattern_name, pattern_data in patterns.items():
            providers = pattern_data.get("providers", [])
            if cloud_provider in providers or cloud_provider == "kubernetes":
                if integration_type not in result:
                    result[integration_type] = {}
                result[integration_type][pattern_name] = pattern_data
    return result

