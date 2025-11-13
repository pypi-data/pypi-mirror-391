"""Summarizer for generating human-readable API summaries."""

from typing import Dict, Any, List
import json


class APISummarizer:
    """Generates concise summaries of API specifications."""
    
    def __init__(self, max_tokens: int = 1000):
        self.max_tokens = max_tokens
    
    def summarize(self, spec: Dict[str, Any]) -> str:
        """
        Generate a human-readable summary of an API specification.
        
        Args:
            spec: OpenAPI specification dictionary
        
        Returns:
            Human-readable summary string
        """
        lines = []
        
        # API Info
        info = spec.get("info", {})
        if info:
            lines.append(f"# {info.get('title', 'API')}")
            if "description" in info:
                lines.append(f"{info['description']}")
            if "version" in info:
                lines.append(f"Version: {info['version']}")
            lines.append("")
        
        # Endpoints
        paths = spec.get("paths", {})
        if paths:
            lines.append("## Endpoints")
            lines.append("")
            
            for path, path_item in sorted(paths.items()):
                for method, operation in path_item.items():
                    if method.lower() in ["get", "post", "put", "patch", "delete", "options", "head"]:
                        endpoint_summary = self._summarize_endpoint(
                            method.upper(), path, operation
                        )
                        lines.append(endpoint_summary)
                        lines.append("")
        
        # Schemas
        schemas = spec.get("components", {}).get("schemas", {})
        if schemas:
            lines.append("## Data Models")
            lines.append("")
            
            for schema_name, schema_def in sorted(schemas.items()):
                schema_summary = self._summarize_schema(schema_name, schema_def)
                lines.append(schema_summary)
                lines.append("")
        
        summary = "\n".join(lines)
        
        # Truncate if too long (rough token estimation: ~4 chars per token)
        estimated_tokens = len(summary) // 4
        if estimated_tokens > self.max_tokens:
            max_chars = self.max_tokens * 4
            summary = summary[:max_chars] + "\n\n... (truncated)"
        
        return summary
    
    def _summarize_endpoint(
        self, method: str, path: str, operation: Dict[str, Any]
    ) -> str:
        """Summarize a single endpoint."""
        lines = []
        
        # Method and path
        summary_line = f"**{method} {path}**"
        
        # Add operation summary if available
        if "summary" in operation:
            summary_line += f" - {operation['summary']}"
        elif "description" in operation:
            desc = operation["description"].split("\n")[0]  # First line only
            summary_line += f" - {desc}"
        
        lines.append(summary_line)
        
        # Parameters
        params = operation.get("parameters", [])
        if params:
            param_strs = []
            for param in params:
                param_name = param.get("name", "unknown")
                param_in = param.get("in", "")
                required = " (required)" if param.get("required") else ""
                param_strs.append(f"{param_name} ({param_in}){required}")
            lines.append(f"  - Parameters: {', '.join(param_strs)}")
        
        # Request body
        request_body = operation.get("requestBody")
        if request_body:
            content = request_body.get("content", {})
            content_types = list(content.keys())
            if content_types:
                lines.append(f"  - Request: {', '.join(content_types)}")
        
        # Responses
        responses = operation.get("responses", {})
        if responses:
            response_codes = [code for code in responses.keys() if code != "default"]
            if response_codes:
                lines.append(f"  - Responses: {', '.join(response_codes)}")
        
        return "\n".join(lines)
    
    def _summarize_schema(self, name: str, schema: Dict[str, Any]) -> str:
        """Summarize a data model schema."""
        lines = []
        lines.append(f"**{name}**")
        
        if "description" in schema:
            lines.append(f"  {schema['description']}")
        
        properties = schema.get("properties", {})
        if properties:
            required = set(schema.get("required", []))
            prop_lines = []
            for prop_name, prop_def in properties.items():
                prop_type = prop_def.get("type", "unknown")
                required_marker = "*" if prop_name in required else ""
                prop_lines.append(f"{prop_name}{required_marker}: {prop_type}")
            
            lines.append(f"  - Fields: {', '.join(prop_lines)}")
        
        return "\n".join(lines)
    
    def summarize_diff(self, diff_result: Dict[str, Any]) -> str:
        """
        Generate a human-readable summary of API changes.
        
        Args:
            diff_result: Diff result dictionary from DiffEngine
        
        Returns:
            Human-readable change summary
        """
        if not diff_result.get("has_changes"):
            return "No changes detected in API specification."
        
        lines = []
        lines.append("# API Changes")
        lines.append("")
        
        summary = diff_result.get("summary", {})
        
        # Endpoints
        added = summary.get("endpoints_added", [])
        if added:
            lines.append("## New Endpoints")
            for endpoint in added:
                lines.append(f"- ✅ {endpoint}")
            lines.append("")
        
        removed = summary.get("endpoints_removed", [])
        if removed:
            lines.append("## Removed Endpoints")
            for endpoint in removed:
                lines.append(f"- ❌ {endpoint}")
            lines.append("")
        
        modified = summary.get("endpoints_modified", [])
        if modified:
            lines.append("## Modified Endpoints")
            for endpoint in modified:
                lines.append(f"- 🔄 {endpoint}")
            lines.append("")
        
        # Schemas
        schemas_added = summary.get("schemas_added", [])
        if schemas_added:
            lines.append("## New Data Models")
            for schema in schemas_added:
                lines.append(f"- ✅ {schema}")
            lines.append("")
        
        schemas_removed = summary.get("schemas_removed", [])
        if schemas_removed:
            lines.append("## Removed Data Models")
            for schema in schemas_removed:
                lines.append(f"- ❌ {schema}")
            lines.append("")
        
        schemas_modified = summary.get("schemas_modified", [])
        if schemas_modified:
            lines.append("## Modified Data Models")
            for schema in schemas_modified:
                lines.append(f"- 🔄 {schema}")
            lines.append("")
        
        if not lines[2:]:  # Only header, no actual changes listed
            lines.append("Changes detected in API metadata or structure.")
        
        return "\n".join(lines)


def summarize_spec(spec: Dict[str, Any], max_tokens: int = 1000) -> str:
    """
    Convenience function to summarize an API spec.
    
    Args:
        spec: OpenAPI specification dictionary
        max_tokens: Maximum tokens in summary
    
    Returns:
        Human-readable summary
    """
    summarizer = APISummarizer(max_tokens)
    return summarizer.summarize(spec)


def summarize_diff(diff_result: Dict[str, Any]) -> str:
    """
    Convenience function to summarize API changes.
    
    Args:
        diff_result: Diff result dictionary
    
    Returns:
        Human-readable change summary
    """
    summarizer = APISummarizer()
    return summarizer.summarize_diff(diff_result)
