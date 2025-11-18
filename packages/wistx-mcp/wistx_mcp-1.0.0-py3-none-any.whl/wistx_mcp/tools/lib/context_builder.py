"""Context builder - format data for LLM context using markdown."""

import markdown as markdown_lib
from typing import Any


class MarkdownBuilder:
    """Helper class for building markdown strings consistently."""

    def __init__(self):
        """Initialize markdown builder."""
        self.lines: list[str] = []

    def add_header(self, text: str, level: int = 1) -> "MarkdownBuilder":
        """Add a header.

        Args:
            text: Header text
            level: Header level (1-6)

        Returns:
            Self for method chaining
        """
        prefix = "#" * min(max(level, 1), 6)
        self.lines.append(f"{prefix} {text}\n")
        return self

    def add_paragraph(self, text: str) -> "MarkdownBuilder":
        """Add a paragraph.

        Args:
            text: Paragraph text

        Returns:
            Self for method chaining
        """
        self.lines.append(f"{text}\n")
        return self

    def add_bold(self, text: str) -> "MarkdownBuilder":
        """Add bold text.

        Args:
            text: Text to make bold

        Returns:
            Self for method chaining
        """
        self.lines.append(f"**{text}**")
        return self

    def add_code_block(self, code: str, language: str = "") -> "MarkdownBuilder":
        """Add a code block.

        Args:
            code: Code content
            language: Language identifier

        Returns:
            Self for method chaining
        """
        lang = language if language else ""
        self.lines.append(f"```{lang}\n{code}\n```\n")
        return self

    def add_list_item(self, text: str, indent: int = 0) -> "MarkdownBuilder":
        """Add a list item.

        Args:
            text: List item text
            indent: Indentation level

        Returns:
            Self for method chaining
        """
        prefix = "  " * indent + "- "
        self.lines.append(f"{prefix}{text}\n")
        return self

    def add_separator(self) -> "MarkdownBuilder":
        """Add a horizontal separator.

        Returns:
            Self for method chaining
        """
        self.lines.append("---\n")
        return self

    def add_line_break(self) -> "MarkdownBuilder":
        """Add a line break.

        Returns:
            Self for method chaining
        """
        self.lines.append("\n")
        return self

    def build(self, validate: bool = True) -> str:
        """Build the markdown string.

        Args:
            validate: Whether to validate the markdown syntax

        Returns:
            Formatted markdown string

        Raises:
            ValueError: If markdown validation fails and validate=True
        """
        result = "".join(self.lines)
        
        if not result.strip():
            return ""
        
        if validate:
            try:
                html_output = markdown_lib.markdown(result)
                if not html_output or html_output.strip() == "":
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning("Markdown produced empty HTML output")
            except (ValueError, TypeError, AttributeError) as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning("Markdown validation warning: %s", e)
        
        return result

    def reset(self) -> "MarkdownBuilder":
        """Reset the builder.

        Returns:
            Self for method chaining
        """
        self.lines = []
        return self


class ContextBuilder:
    """Build formatted context for LLM consumption using markdown."""

    @staticmethod
    def format_compliance_as_markdown(controls: list[dict[str, Any]], resource_type: str | None = None) -> str:
        """Format compliance controls as markdown for LLM consumption.

        Args:
            controls: List of compliance control dictionaries
            resource_type: Optional resource type for context

        Returns:
            Formatted markdown string
        """
        import logging
        logger = logging.getLogger(__name__)

        if not controls:
            return "No compliance controls found."

        if not isinstance(controls, list):
            logger.error("Controls must be a list, got %s", type(controls))
            return "Invalid controls format."

        builder = MarkdownBuilder()
        title = "Compliance Requirements"
        if resource_type:
            title += f" for {resource_type}"
        builder.add_header(title, level=1)

        for i, control in enumerate(controls):
            if not isinstance(control, dict):
                logger.warning("Control %d is not a dict, skipping", i)
                continue

            try:
                standard = control.get("standard", "Unknown")
                control_id = control.get("control_id", "")
                severity = control.get("severity", "MEDIUM")
                title_text = control.get("title", "")
                description = control.get("description", "")

                builder.add_header(f"{standard} {control_id}: {title_text}", level=2)
                builder.add_bold(f"Severity: {severity}")
                builder.add_line_break()
                builder.add_paragraph(str(description))

                remediation = control.get("remediation", {})
                if remediation and isinstance(remediation, dict):
                    if remediation.get("guidance"):
                        builder.add_header("Remediation Guidance", level=3)
                        builder.add_paragraph(str(remediation["guidance"]))

                    if remediation.get("code_snippet"):
                        builder.add_header("Code Example", level=3)
                        builder.add_code_block(str(remediation["code_snippet"]), language="hcl")

                verification = control.get("verification", {})
                if verification and isinstance(verification, dict):
                    if verification.get("procedure"):
                        builder.add_header("Verification", level=3)
                        builder.add_paragraph(str(verification["procedure"]))

                builder.add_separator()
            except (ValueError, TypeError, KeyError, AttributeError) as e:
                logger.warning("Error formatting control %d: %s", i, e)
                continue
            except Exception as e:  # noqa: BLE001
                logger.warning("Unexpected error formatting control %d: %s", i, e, exc_info=True)
                continue

        markdown_output = builder.build(validate=True)
        
        if not markdown_output or not markdown_output.strip():
            logger.warning("Generated markdown is empty")
            return "No compliance controls found."
        
        try:
            markdown_lib.markdown(markdown_output)
        except Exception as e:  # noqa: BLE001
            logger.error("Generated markdown failed validation: %s", e)
            return "Error formatting compliance requirements. Please try again."
        
        return markdown_output

    @staticmethod
    def format_compliance_context(controls: list[dict[str, Any]]) -> str:
        """Format compliance controls as context string (legacy method).

        Args:
            controls: List of compliance control dictionaries

        Returns:
            Formatted context string
        """
        return ContextBuilder.format_compliance_as_markdown(controls)

    @staticmethod
    def format_pricing_context(pricing: dict[str, Any]) -> str:
        """Format pricing data as context string.

        Args:
            pricing: Pricing data dictionary

        Returns:
            Formatted context string
        """
        builder = MarkdownBuilder()
        builder.add_header("Infrastructure Cost Estimate", level=2)
        builder.add_bold(f"Total Monthly: ${pricing.get('total_monthly', 0):.2f}")
        builder.add_line_break()
        builder.add_bold(f"Total Annual: ${pricing.get('total_annual', 0):.2f}")
        builder.add_line_break()
        builder.add_header("Breakdown", level=3)

        for item in pricing.get("breakdown", []):
            builder.add_list_item(
                f"{item['resource']} (x{item['quantity']}): "
                f"${item['monthly']:.2f}/month (${item['annual']:.2f}/year)"
            )

        if pricing.get("optimizations"):
            builder.add_header("Optimization Suggestions", level=3)
            for opt in pricing["optimizations"]:
                builder.add_list_item(opt)

        return builder.build()

    @staticmethod
    def format_code_examples_context(examples: list[dict[str, Any]]) -> str:
        """Format code examples as context string.

        Args:
            examples: List of code example dictionaries

        Returns:
            Formatted context string
        """
        if not examples:
            return "No code examples found."

        builder = MarkdownBuilder()
        builder.add_header("Code Examples", level=2)

        for example in examples:
            builder.add_header(example.get("title", "Example"), level=3)
            if example.get("description"):
                builder.add_bold(f"Description: {example['description']}")
                builder.add_line_break()
            builder.add_bold(f"Language: {example.get('language', 'N/A')}")
            builder.add_line_break()
            builder.add_bold(f"Infrastructure: {example.get('infrastructure_type', 'N/A')}")
            builder.add_line_break()
            builder.add_code_block(example.get("code", ""), language=example.get("language", ""))

        return builder.build()

    @staticmethod
    def format_web_search_results(results: dict[str, Any]) -> str:
        """Format web search results as markdown.

        Args:
            results: Web search results dictionary

        Returns:
            Formatted markdown string
        """
        builder = MarkdownBuilder()
        builder.add_header("Web Search Results", level=1)
        builder.add_bold(f"Total Results: {results.get('total', 0)}")
        builder.add_line_break()

        if results.get("web"):
            builder.add_header("Web Search Results", level=2)
            for item in results["web"][:10]:
                if item.get("type") == "answer":
                    builder.add_header(item.get("title", "AI Answer"), level=3)
                    builder.add_paragraph(item.get("content", ""))
                else:
                    builder.add_header(item.get("title", "Result"), level=3)
                    if item.get("url"):
                        builder.add_bold(f"URL: {item['url']}")
                        builder.add_line_break()
                    if item.get("content"):
                        content = item["content"][:500]
                        builder.add_paragraph(content)
                    if item.get("score"):
                        builder.add_bold(f"Relevance Score: {item['score']:.2f}")
                        builder.add_line_break()
                builder.add_separator()

        if results.get("web_results"):
            builder.add_header("Real-Time Web Research", level=2)
            web_results = results["web_results"]
            
            freshness_info = web_results.get("freshness_info", {})
            if freshness_info:
                max_age = freshness_info.get("max_age_days", 0)
                builder.add_bold(f"Data Freshness: Results from last {max_age} days")
                builder.add_line_break()
            
            if web_results.get("answer"):
                builder.add_header("AI Summary", level=3)
                builder.add_paragraph(web_results["answer"])
            if web_results.get("results"):
                builder.add_header("Web Sources", level=3)
                for item in web_results["results"][:5]:
                    builder.add_bold(item.get("title", "Source"))
                    builder.add_line_break()
                    if item.get("url"):
                        builder.add_paragraph(f"URL: {item['url']}")
                    if item.get("published_date"):
                        builder.add_paragraph(f"Published: {item['published_date']}")
                    if item.get("content"):
                        content = item["content"][:300]
                        builder.add_paragraph(content)
                    builder.add_separator()

        if results.get("security"):
            builder.add_header("Security Information", level=2)
            for item in results["security"][:10]:
                title = item.get("title") or item.get("cve_id") or "Security Item"
                builder.add_header(title, level=3)
                if item.get("description"):
                    builder.add_paragraph(item["description"])
                if item.get("severity"):
                    builder.add_bold(f"Severity: {item['severity']}")
                    builder.add_line_break()
                if item.get("source"):
                    builder.add_bold(f"Source: {item['source']}")
                    builder.add_line_break()
                if item.get("published_date"):
                    builder.add_bold(f"Published: {item['published_date']}")
                    builder.add_line_break()
                builder.add_separator()

        if results.get("compliance"):
            builder.add_header("Compliance Requirements", level=2)
            compliance_md = ContextBuilder.format_compliance_as_markdown(results["compliance"])
            builder.add_paragraph(compliance_md)

        if results.get("best_practices"):
            builder.add_header("Best Practices", level=2)
            for item in results["best_practices"][:10]:
                builder.add_header(item.get("title", "Best Practice"), level=3)
                if item.get("summary"):
                    builder.add_paragraph(item["summary"])
                if item.get("domain"):
                    builder.add_bold(f"Domain: {item['domain']}")
                    builder.add_line_break()
                builder.add_separator()

        if results.get("knowledge"):
            builder.add_header("Knowledge Base", level=2)
            for item in results["knowledge"][:10]:
                builder.add_header(item.get("title", "Knowledge Article"), level=3)
                if item.get("summary"):
                    builder.add_paragraph(item["summary"])
                if item.get("domain"):
                    builder.add_bold(f"Domain: {item['domain']}")
                    builder.add_line_break()
                builder.add_separator()

        return builder.build()

    @staticmethod
    def format_codebase_search_results(results: dict[str, Any]) -> str:
        """Format codebase search results as markdown.

        Args:
            results: Codebase search results dictionary

        Returns:
            Formatted markdown string
        """
        builder = MarkdownBuilder()
        builder.add_header("Codebase Search Results", level=1)
        builder.add_bold(f"Total Results: {results.get('total', 0)}")
        builder.add_line_break()

        if results.get("resources"):
            builder.add_header("Resources", level=2)
            for resource in results["resources"]:
                builder.add_list_item(
                    f"**{resource.get('name', 'Unknown')}** "
                    f"({resource.get('resource_type', 'unknown')})"
                )

        if results.get("results"):
            builder.add_header("Search Results", level=2)
            for result in results["results"][:20]:
                builder.add_header(result.get("title", "Result"), level=3)
                builder.add_bold(f"Source: {result.get('source_type', 'unknown')}")
                builder.add_line_break()
                if result.get("summary"):
                    builder.add_paragraph(result["summary"])

                if result.get("content"):
                    content = result.get("content", "")[:500]
                    builder.add_code_block(content)

                if result.get("source_url"):
                    builder.add_bold(f"Source URL: {result['source_url']}")
                    builder.add_line_break()

                builder.add_separator()

        if results.get("highlights"):
            builder.add_header("Code Highlights", level=2)
            for highlight in results["highlights"][:5]:
                if highlight.get("file_path"):
                    builder.add_bold(f"File: {highlight['file_path']}")
                    builder.add_line_break()
                builder.add_code_block(highlight.get("highlight", ""))

        return builder.build()

    @staticmethod
    def format_architecture_results(results: dict[str, Any]) -> str:
        """Format architecture design results as markdown.

        Args:
            results: Architecture results dictionary

        Returns:
            Formatted markdown string
        """
        builder = MarkdownBuilder()
        builder.add_header("Architecture Design Results", level=1)

        if "project_path" in results:
            builder.add_header("Project Initialized", level=2)
            builder.add_bold(f"Project Path: `{results.get('project_path')}`")
            builder.add_line_break()
            builder.add_bold(f"Files Created: {len(results.get('files_created', []))}")
            builder.add_line_break()

            if results.get("structure"):
                builder.add_header("Project Structure", level=3)
                for item in results["structure"][:20]:
                    builder.add_list_item(item)

            if results.get("next_steps"):
                builder.add_header("Next Steps", level=3)
                for step in results["next_steps"]:
                    builder.add_list_item(step)

        if "architecture_diagram" in results:
            builder.add_header("Architecture Diagram", level=2)
            builder.add_code_block(results.get("architecture_diagram", ""))

        if "components" in results:
            builder.add_header("Components", level=2)
            for component in results.get("components", []):
                builder.add_list_item(f"**{component.get('name')}** ({component.get('type')})")

        if "recommendations" in results:
            builder.add_header("Recommendations", level=2)
            for rec in results.get("recommendations", []):
                builder.add_list_item(rec)

        if "issues" in results:
            builder.add_header("Issues Found", level=2)
            for issue in results.get("issues", []):
                builder.add_list_item(f"⚠️ {issue}")

        if "optimizations" in results:
            builder.add_header("Optimizations", level=2)
            for opt in results.get("optimizations", []):
                builder.add_list_item(f"✅ {opt}")

        return builder.build()

    @staticmethod
    def format_troubleshooting_results(results: dict[str, Any]) -> str:
        """Format troubleshooting results as markdown.

        Args:
            results: Troubleshooting results dictionary

        Returns:
            Formatted markdown string
        """
        builder = MarkdownBuilder()
        builder.add_header("Troubleshooting Results", level=1)

        diagnosis = results.get("diagnosis", {})
        if diagnosis:
            builder.add_header("Diagnosis", level=2)
            if diagnosis.get("root_cause"):
                builder.add_bold(f"Root Cause: {diagnosis['root_cause']}")
                builder.add_line_break()
            if diagnosis.get("confidence"):
                builder.add_bold(f"Confidence: {diagnosis['confidence']}")
                builder.add_line_break()

            if diagnosis.get("issues"):
                builder.add_header("Identified Issues", level=3)
                for issue in diagnosis["issues"]:
                    builder.add_list_item(issue)

            if diagnosis.get("error_patterns"):
                builder.add_header("Error Patterns", level=3)
                for pattern in diagnosis["error_patterns"]:
                    builder.add_list_item(pattern)

        if results.get("fixes"):
            builder.add_header("Recommended Fixes", level=2)
            for i, fix in enumerate(results["fixes"][:10], 1):
                builder.add_header(f"{i}. {fix.get('title', 'Fix')}", level=3)
                if fix.get("description"):
                    builder.add_paragraph(fix["description"])
                if fix.get("code_example"):
                    builder.add_code_block(fix["code_example"])
                if fix.get("url"):
                    builder.add_bold(f"Source: {fix['url']}")
                    builder.add_line_break()
                builder.add_separator()

        if results.get("prevention"):
            builder.add_header("Prevention Strategies", level=2)
            for strategy in results["prevention"]:
                builder.add_list_item(strategy)

        if results.get("related_knowledge"):
            builder.add_header("Related Knowledge", level=2)
            for article in results["related_knowledge"][:5]:
                builder.add_header(article.get("title", "Article"), level=3)
                if article.get("summary"):
                    builder.add_paragraph(article["summary"])
                builder.add_separator()

        if results.get("web_sources"):
            builder.add_header("Web Sources", level=2)
            for source in results["web_sources"][:5]:
                builder.add_header(source.get("title", "Source"), level=3)
                if source.get("url"):
                    builder.add_bold(f"URL: {source['url']}")
                    builder.add_line_break()
                if source.get("content"):
                    content = source["content"][:300]
                    builder.add_paragraph(content)
                builder.add_separator()

        return builder.build()

    @staticmethod
    def format_documentation_results(results: dict[str, Any]) -> str:
        """Format documentation generation results as markdown.

        Args:
            results: Documentation results dictionary

        Returns:
            Formatted markdown string
        """
        builder = MarkdownBuilder()
        builder.add_header("Documentation Generated", level=1)

        metadata = results.get("metadata", {})
        if metadata:
            builder.add_bold(f"Generated: {metadata.get('generated_at', '')}")
            builder.add_line_break()
            builder.add_bold(f"Document Type: {results.get('document_type', '')}")
            builder.add_line_break()
            builder.add_bold(f"Subject: {results.get('subject', '')}")
            builder.add_line_break()

        if results.get("sections"):
            builder.add_header("Document Sections", level=2)
            for section in results["sections"][:10]:
                builder.add_list_item(section)

        if results.get("content"):
            builder.add_header("Document Content", level=2)
            builder.add_paragraph(results["content"])

        return builder.build()

    @staticmethod
    def format_integration_results(results: dict[str, Any]) -> str:
        """Format integration management results as markdown.

        Args:
            results: Integration results dictionary

        Returns:
            Formatted markdown string
        """
        builder = MarkdownBuilder()
        builder.add_header(f"Integration Management: {results.get('action', 'unknown')}", level=1)

        action = results.get("action", "")

        if action == "analyze":
            builder.add_header("Analysis Results", level=2)

            if results.get("missing_connections"):
                builder.add_header("Missing Connections", level=3)
                for conn in results["missing_connections"]:
                    builder.add_list_item(f"⚠️ {conn}")

            if results.get("dependency_issues"):
                builder.add_header("Dependency Issues", level=3)
                for issue in results["dependency_issues"]:
                    builder.add_list_item(f"⚠️ {issue}")

            if results.get("security_gaps"):
                builder.add_header("Security Gaps", level=3)
                for gap in results["security_gaps"]:
                    builder.add_list_item(f"🔒 {gap}")

            if results.get("recommendations"):
                builder.add_header("Recommendations", level=3)
                for rec in results["recommendations"]:
                    builder.add_list_item(f"✅ {rec}")

        elif action == "generate":
            builder.add_header("Generated Integration Code", level=2)

            if results.get("description"):
                builder.add_bold(f"Pattern: {results.get('description')}")
                builder.add_line_break()

            if results.get("pattern_used"):
                builder.add_bold(f"Pattern Used: {results['pattern_used']}")
                builder.add_line_break()

            if results.get("integration_code"):
                builder.add_header("Integration Code", level=3)
                builder.add_code_block(results["integration_code"], language="hcl")

            if results.get("dependencies"):
                builder.add_header("Dependencies", level=3)
                for dep in results["dependencies"]:
                    builder.add_list_item(dep)

            if results.get("security_rules"):
                builder.add_header("Security Rules", level=3)
                for rule in results["security_rules"]:
                    builder.add_list_item(f"🔒 {rule}")

            if results.get("monitoring"):
                monitoring = results["monitoring"]
                if monitoring.get("metrics"):
                    builder.add_header("Monitoring Metrics", level=3)
                    for metric in monitoring["metrics"]:
                        builder.add_list_item(metric)

        elif action == "validate":
            builder.add_header("Validation Results", level=2)

            is_valid = results.get("valid", False)
            builder.add_bold(f"Status: {'✅ Valid' if is_valid else '❌ Invalid'}")
            builder.add_line_break()

            if results.get("issues"):
                builder.add_header("Issues", level=3)
                for issue in results["issues"]:
                    builder.add_list_item(f"⚠️ {issue}")

            if results.get("fixes"):
                builder.add_header("Recommended Fixes", level=3)
                for fix in results["fixes"]:
                    builder.add_list_item(f"✅ {fix}")

        return builder.build()

    @staticmethod
    def format_infrastructure_results(results: dict[str, Any]) -> str:
        """Format infrastructure management results as markdown.

        Args:
            results: Infrastructure results dictionary

        Returns:
            Formatted markdown string
        """
        builder = MarkdownBuilder()
        builder.add_header(f"Infrastructure Management: {results.get('action', 'unknown')}", level=1)

        action = results.get("action", "")
        resource_id = results.get("resource_id", "")
        status = results.get("status", "")

        builder.add_bold(f"Resource ID: {resource_id}")
        builder.add_line_break()
        builder.add_bold(f"Status: {status}")
        builder.add_line_break()

        if action == "create":
            if results.get("endpoints"):
                builder.add_header("Endpoints", level=2)
                endpoints = results["endpoints"]
                if isinstance(endpoints, dict):
                    for key, value in endpoints.items():
                        if isinstance(value, dict):
                            builder.add_header(key, level=3)
                            for k, v in value.items():
                                builder.add_list_item(f"**{k}**: {v}")
                        else:
                            builder.add_list_item(f"**{key}**: {value}")

            if results.get("terraform_code"):
                builder.add_header("Terraform Code", level=2)
                builder.add_code_block(results["terraform_code"], language="hcl")

            if results.get("next_steps"):
                builder.add_header("Next Steps", level=2)
                for step in results["next_steps"]:
                    builder.add_list_item(step)

        elif action == "upgrade":
            if results.get("strategy"):
                builder.add_bold(f"Upgrade Strategy: {results['strategy']}")
                builder.add_line_break()

            if results.get("steps"):
                builder.add_header("Upgrade Steps", level=2)
                for i, step in enumerate(results["steps"], 1):
                    builder.add_list_item(f"{i}. {step}")

            if results.get("rollback_plan"):
                builder.add_header("Rollback Plan", level=2)
                for step in results["rollback_plan"]:
                    builder.add_list_item(step)

            if results.get("estimated_downtime"):
                builder.add_bold(f"Estimated Downtime: {results['estimated_downtime']}")
                builder.add_line_break()

        elif action == "backup":
            if results.get("backup_commands"):
                builder.add_header("Backup Commands", level=2)
                backup_cmds = "\n".join(results["backup_commands"])
                builder.add_code_block(backup_cmds, language="bash")

            if results.get("restore_commands"):
                builder.add_header("Restore Commands", level=2)
                restore_cmds = "\n".join(results["restore_commands"])
                builder.add_code_block(restore_cmds, language="bash")

            if results.get("retention_policy"):
                builder.add_bold(f"Retention Policy: {results['retention_policy']}")
                builder.add_line_break()

        elif action == "monitor":
            if results.get("metrics"):
                builder.add_header("Metrics", level=2)
                for metric in results["metrics"]:
                    builder.add_list_item(metric)

            if results.get("alerts"):
                builder.add_header("Alerts", level=2)
                for alert in results["alerts"]:
                    builder.add_list_item(f"⚠️ {alert}")

            if results.get("dashboards"):
                builder.add_header("Dashboards", level=2)
                for dashboard in results["dashboards"]:
                    builder.add_list_item(f"📊 {dashboard}")

        elif action == "optimize":
            if results.get("recommendations"):
                builder.add_header("Optimization Recommendations", level=2)
                for rec in results["recommendations"]:
                    builder.add_list_item(f"💰 {rec}")

            if results.get("estimated_savings"):
                builder.add_bold(f"Estimated Savings: {results['estimated_savings']}")
                builder.add_line_break()

            if results.get("migration_plan"):
                builder.add_header("Migration Plan", level=2)
                for step in results["migration_plan"]:
                    builder.add_list_item(step)

        return builder.build()

    @staticmethod
    def format_indexing_results(results: dict[str, Any], operation: str = "index") -> str:
        """Format indexing operation results as markdown.

        Args:
            results: Indexing results dictionary
            operation: Operation type (index, list, check, delete)

        Returns:
            Formatted markdown string
        """
        builder = MarkdownBuilder()
        builder.add_header(f"{operation.title()} Operation Results", level=1)

        if results.get("resource_id"):
            builder.add_bold(f"Resource ID: `{results['resource_id']}`")
            builder.add_line_break()

        if results.get("status"):
            status = results["status"]
            status_emoji = "✅" if status == "completed" else "⏳" if status == "indexing" else "❌"
            builder.add_bold(f"Status: {status_emoji} {status}")
            builder.add_line_break()

        if results.get("message"):
            builder.add_paragraph(results["message"])

        if results.get("progress"):
            progress = results["progress"]
            builder.add_bold(f"Progress: {progress.get('percentage', 0)}%")
            builder.add_line_break()
            if progress.get("files_processed"):
                builder.add_list_item(f"Files Processed: {progress['files_processed']}")
            if progress.get("total_files"):
                builder.add_list_item(f"Total Files: {progress['total_files']}")

        if results.get("resources"):
            builder.add_header("Resources", level=2)
            for resource in results["resources"]:
                resource_type = resource.get("resource_type", "unknown")
                name = resource.get("name", "Unknown")
                status = resource.get("status", "unknown")
                resource_id = resource.get("resource_id", "")
                
                status_emoji = "✅" if status == "completed" else "⏳" if status == "indexing" else "❌"
                builder.add_list_item(f"**{name}** ({resource_type}) - {status_emoji} {status}")
                if resource_id:
                    builder.add_list_item(f"Resource ID: `{resource_id}`", indent=1)
                if resource.get("created_at"):
                    builder.add_list_item(f"Created: {resource['created_at']}", indent=1)

        if results.get("total"):
            builder.add_bold(f"Total Resources: {results['total']}")
            builder.add_line_break()

        if results.get("next_steps"):
            builder.add_header("Next Steps", level=2)
            for step in results["next_steps"]:
                builder.add_list_item(step)

        return builder.build()

    @staticmethod
    def format_health_check_results(results: dict[str, Any]) -> str:
        """Format health check results as markdown.

        Args:
            results: Health check results dictionary

        Returns:
            Formatted markdown string
        """
        builder = MarkdownBuilder()
        builder.add_header("Health Check Results", level=1)

        overall_status = results.get("status", "unknown")
        status_emoji = "✅" if overall_status == "healthy" else "⚠️" if overall_status == "degraded" else "❌"
        builder.add_bold(f"Overall Status: {status_emoji} {overall_status}")
        builder.add_line_break()

        if results.get("mongodb"):
            mongodb = results["mongodb"]
            mongodb_status = mongodb.get("status", "unknown")
            mongodb_emoji = "✅" if mongodb_status == "healthy" else "❌"
            builder.add_header(f"MongoDB {mongodb_emoji}", level=2)
            builder.add_bold(f"Status: {mongodb_status}")
            builder.add_line_break()
            if mongodb.get("database"):
                builder.add_bold(f"Database: {mongodb['database']}")
                builder.add_line_break()
            if mongodb.get("error"):
                builder.add_bold(f"Error: {mongodb['error']}")
                builder.add_line_break()

        if results.get("pinecone"):
            pinecone = results["pinecone"]
            pinecone_status = pinecone.get("status", "unknown")
            pinecone_emoji = "✅" if pinecone_status == "healthy" else "⚠️" if pinecone_status == "not_configured" else "❌"
            builder.add_header(f"Pinecone {pinecone_emoji}", level=2)
            builder.add_bold(f"Status: {pinecone_status}")
            builder.add_line_break()
            if pinecone.get("index"):
                builder.add_bold(f"Index: {pinecone['index']}")
                builder.add_line_break()
            if pinecone.get("vector_count") is not None:
                builder.add_bold(f"Vector Count: {pinecone['vector_count']}")
                builder.add_line_break()
            if pinecone.get("error"):
                builder.add_bold(f"Error: {pinecone['error']}")
                builder.add_line_break()

        if results.get("api_client"):
            api_client = results["api_client"]
            api_status = api_client.get("status", "unknown")
            api_emoji = "✅" if api_status == "healthy" else "⚠️" if api_status == "not_configured" else "❌"
            builder.add_header(f"API Client {api_emoji}", level=2)
            builder.add_bold(f"Status: {api_status}")
            builder.add_line_break()
            if api_client.get("api_url"):
                builder.add_bold(f"API URL: {api_client['api_url']}")
                builder.add_line_break()
            if api_client.get("error"):
                builder.add_bold(f"Error: {api_client['error']}")
                builder.add_line_break()

        return builder.build()

    @staticmethod
    def format_knowledge_research_results(results: dict[str, Any]) -> str:
        """Format knowledge research results as markdown.

        Args:
            results: Knowledge research results dictionary

        Returns:
            Formatted markdown string
        """
        if results.get("markdown"):
            return results["markdown"]

        builder = MarkdownBuilder()
        builder.add_header("Knowledge Research Results", level=1)

        if results.get("research_summary"):
            summary = results["research_summary"]
            builder.add_header("Research Summary", level=2)
            if summary.get("total_found"):
                builder.add_bold(f"Total Results: {summary['total_found']}")
                builder.add_line_break()
            if summary.get("domains_covered"):
                builder.add_bold(f"Domains Covered: {', '.join(summary['domains_covered'])}")
                builder.add_line_break()
            if summary.get("key_insights"):
                builder.add_header("Key Insights", level=3)
                for insight in summary["key_insights"]:
                    builder.add_list_item(insight)

        if results.get("results"):
            builder.add_header("Knowledge Articles", level=2)
            for article in results["results"][:20]:
                builder.add_header(article.get("title", "Article"), level=3)
                if article.get("summary"):
                    builder.add_paragraph(article["summary"])
                if article.get("domain"):
                    builder.add_bold(f"Domain: {article['domain']}")
                    builder.add_line_break()
                if article.get("subdomain"):
                    builder.add_bold(f"Subdomain: {article['subdomain']}")
                    builder.add_line_break()
                if article.get("source_url"):
                    builder.add_bold(f"Source: {article['source_url']}")
                    builder.add_line_break()
                builder.add_separator()

        if results.get("web_results"):
            web_results = results["web_results"]
            builder.add_header("Web Search Results", level=2)
            
            if web_results.get("freshness_info"):
                freshness = web_results["freshness_info"]
                max_age = freshness.get("max_age_days", 0)
                builder.add_bold(f"Data Freshness: Results from last {max_age} days")
                builder.add_line_break()
            
            if web_results.get("answer"):
                builder.add_header("AI Summary", level=3)
                builder.add_paragraph(web_results["answer"])
            
            if web_results.get("results"):
                builder.add_header("Web Sources", level=3)
                for item in web_results["results"][:10]:
                    builder.add_bold(item.get("title", "Source"))
                    builder.add_line_break()
                    if item.get("url"):
                        builder.add_paragraph(f"URL: {item['url']}")
                    if item.get("published_date"):
                        builder.add_paragraph(f"Published: {item['published_date']}")
                    if item.get("content"):
                        content = item["content"][:300]
                        builder.add_paragraph(content)
                    builder.add_separator()

        return builder.build()

