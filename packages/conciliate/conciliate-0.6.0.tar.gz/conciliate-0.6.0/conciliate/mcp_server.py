"""MCP (Model Context Protocol) server for Conciliate."""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime

from mcp.server import Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
import mcp.server.stdio

from .config import ConciliateConfig, load_config, ensure_output_dir
from .spec_generator import SpecGenerator, SpecGeneratorError
from .diff_engine import DiffEngine
from .summarizer import APISummarizer
from .watcher import FileWatcher

logger = logging.getLogger(__name__)


class ConciliateMCPServer:
    """MCP server for exposing Conciliate context to AI assistants."""
    
    def __init__(self, config: ConciliateConfig):
        self.config = config
        self.server = Server("conciliate")
        self.output_dir = ensure_output_dir(config)
        
        # Components
        self.spec_generator = SpecGenerator(config)
        self.diff_engine = DiffEngine()
        self.summarizer = APISummarizer(config.summary_max_tokens)
        
        # State
        self.current_spec: Optional[Dict[str, Any]] = None
        self.file_watcher: Optional[FileWatcher] = None
        self.watcher_task: Optional[asyncio.Task] = None
        
        # Register handlers
        self._setup_handlers()
        
        # Load initial spec
        self._load_spec()
    
    def _setup_handlers(self) -> None:
        """Setup MCP protocol handlers."""
        
        @self.server.list_resources()
        async def list_resources() -> list[Resource]:
            """List available resources."""
            resources = [
                Resource(
                    uri="conciliate://api/spec",
                    name="API Specification",
                    description="Full OpenAPI specification of the backend API",
                    mimeType="application/json",
                ),
                Resource(
                    uri="conciliate://api/summary",
                    name="API Summary",
                    description="Human-readable summary of the API endpoints and models",
                    mimeType="text/plain",
                ),
                Resource(
                    uri="conciliate://api/diff",
                    name="API Changes",
                    description="Latest API changes and differences",
                    mimeType="application/json",
                ),
            ]
            return resources
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read a specific resource."""
            if uri == "conciliate://api/spec":
                return await self._get_spec_resource()
            elif uri == "conciliate://api/summary":
                return await self._get_summary_resource()
            elif uri == "conciliate://api/diff":
                return await self._get_diff_resource()
            else:
                raise ValueError(f"Unknown resource URI: {uri}")
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools."""
            tools = [
                Tool(
                    name="reload_api_spec",
                    description="Manually reload and regenerate the API specification from the backend",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                ),
                Tool(
                    name="get_endpoint_details",
                    description="Get detailed information about a specific API endpoint",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "The endpoint path (e.g., /users, /products/{id})",
                            },
                            "method": {
                                "type": "string",
                                "description": "HTTP method (GET, POST, PUT, DELETE, etc.)",
                                "enum": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
                            },
                        },
                        "required": ["path"],
                    },
                ),
                Tool(
                    name="search_endpoints",
                    description="Search for API endpoints by keyword",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query (searches in paths, summaries, and descriptions)",
                            },
                        },
                        "required": ["query"],
                    },
                ),
            ]
            return tools
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Execute a tool."""
            if name == "reload_api_spec":
                return await self._tool_reload_spec()
            elif name == "get_endpoint_details":
                return await self._tool_get_endpoint_details(arguments)
            elif name == "search_endpoints":
                return await self._tool_search_endpoints(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
    
    def _load_spec(self) -> None:
        """Load spec from cache or generate new one."""
        cache_file = self.output_dir / "api_spec.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    self.current_spec = json.load(f)
                logger.info("Loaded spec from cache for MCP server")
                return
            except Exception as e:
                logger.warning(f"Failed to load cached spec: {e}")
        
        # Generate new spec
        try:
            self.current_spec = self.spec_generator.generate()
            self._save_spec()
            logger.info("Generated new spec for MCP server")
        except SpecGeneratorError as e:
            logger.error(f"Failed to generate spec: {e}")
            self.current_spec = None
    
    def _save_spec(self) -> None:
        """Save current spec to disk."""
        if self.current_spec is None:
            return
        
        spec_file = self.output_dir / "api_spec.json"
        with open(spec_file, "w", encoding="utf-8") as f:
            json.dump(self.current_spec, f, indent=2)
    
    async def _get_spec_resource(self) -> str:
        """Get the full API specification."""
        if self.current_spec is None:
            self._load_spec()
        
        if self.current_spec is None:
            return json.dumps({
                "error": "No API specification available",
                "message": "Try reloading the spec or check your backend configuration"
            })
        
        return json.dumps(self.current_spec, indent=2)
    
    async def _get_summary_resource(self) -> str:
        """Get the API summary."""
        if self.current_spec is None:
            self._load_spec()
        
        if self.current_spec is None:
            return "No API specification available. Try reloading the spec."
        
        summary = self.summarizer.summarize(self.current_spec)
        return summary
    
    async def _get_diff_resource(self) -> str:
        """Get the API diff."""
        diff_file = self.output_dir / "api_diff_summary.txt"
        
        if diff_file.exists():
            return diff_file.read_text(encoding="utf-8")
        else:
            return json.dumps({
                "message": "No API changes detected yet",
                "has_changes": False,
            })
    
    async def _tool_reload_spec(self) -> list[TextContent]:
        """Tool: Reload API specification."""
        try:
            old_spec = self.current_spec
            self.current_spec = self.spec_generator.generate()
            self._save_spec()
            
            # Check for changes
            if old_spec:
                diff_result = self.diff_engine.compare(old_spec, self.current_spec)
                if diff_result.has_changes():
                    summary = self.summarizer.summarize_diff(diff_result.to_dict())
                    message = f"✅ Spec reloaded successfully!\n\n{summary}"
                else:
                    message = "✅ Spec reloaded successfully! No changes detected."
            else:
                message = "✅ Spec loaded successfully!"
            
            return [TextContent(type="text", text=message)]
            
        except Exception as e:
            error_msg = f"❌ Failed to reload spec: {str(e)}"
            logger.error(error_msg)
            return [TextContent(type="text", text=error_msg)]
    
    async def _tool_get_endpoint_details(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """Tool: Get endpoint details."""
        if self.current_spec is None:
            return [TextContent(
                type="text",
                text="No API specification available. Try reloading the spec first."
            )]
        
        path = arguments.get("path")
        method = arguments.get("method", "").upper()
        
        paths = self.current_spec.get("paths", {})
        
        if path not in paths:
            return [TextContent(
                type="text",
                text=f"Endpoint '{path}' not found in API specification."
            )]
        
        path_item = paths[path]
        
        # If method specified, get that specific operation
        if method:
            if method.lower() not in path_item:
                available_methods = [m.upper() for m in path_item.keys() if m.lower() in ["get", "post", "put", "patch", "delete", "options", "head"]]
                return [TextContent(
                    type="text",
                    text=f"Method '{method}' not found for endpoint '{path}'.\nAvailable methods: {', '.join(available_methods)}"
                )]
            
            operation = path_item[method.lower()]
            details = self._format_operation_details(method, path, operation)
        else:
            # Show all methods for this path
            details = f"# {path}\n\n"
            for m, operation in path_item.items():
                if m.lower() in ["get", "post", "put", "patch", "delete", "options", "head"]:
                    details += self._format_operation_details(m.upper(), path, operation)
                    details += "\n---\n\n"
        
        return [TextContent(type="text", text=details)]
    
    async def _tool_search_endpoints(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """Tool: Search for endpoints."""
        if self.current_spec is None:
            return [TextContent(
                type="text",
                text="No API specification available. Try reloading the spec first."
            )]
        
        query = arguments.get("query", "").lower()
        
        if not query:
            return [TextContent(type="text", text="Please provide a search query.")]
        
        results = []
        paths = self.current_spec.get("paths", {})
        
        for path, path_item in paths.items():
            # Check if query matches path
            if query in path.lower():
                for method, operation in path_item.items():
                    if method.lower() in ["get", "post", "put", "patch", "delete"]:
                        summary = operation.get("summary", "")
                        results.append(f"**{method.upper()} {path}** - {summary}")
                continue
            
            # Check if query matches operation summary or description
            for method, operation in path_item.items():
                if method.lower() in ["get", "post", "put", "patch", "delete"]:
                    summary = operation.get("summary", "").lower()
                    description = operation.get("description", "").lower()
                    
                    if query in summary or query in description:
                        op_summary = operation.get("summary", "")
                        results.append(f"**{method.upper()} {path}** - {op_summary}")
        
        if not results:
            return [TextContent(
                type="text",
                text=f"No endpoints found matching '{query}'"
            )]
        
        result_text = f"# Search Results for '{query}'\n\n" + "\n".join(results)
        return [TextContent(type="text", text=result_text)]
    
    def _format_operation_details(self, method: str, path: str, operation: Dict[str, Any]) -> str:
        """Format operation details as text."""
        lines = [f"## {method} {path}"]
        
        if "summary" in operation:
            lines.append(f"\n**Summary:** {operation['summary']}")
        
        if "description" in operation:
            lines.append(f"\n**Description:** {operation['description']}")
        
        # Parameters
        params = operation.get("parameters", [])
        if params:
            lines.append("\n**Parameters:**")
            for param in params:
                name = param.get("name", "unknown")
                location = param.get("in", "")
                required = " (required)" if param.get("required") else ""
                param_type = param.get("schema", {}).get("type", "unknown")
                description = param.get("description", "")
                
                lines.append(f"- `{name}` ({location}){required}: {param_type}")
                if description:
                    lines.append(f"  {description}")
        
        # Request body
        request_body = operation.get("requestBody")
        if request_body:
            lines.append("\n**Request Body:**")
            content = request_body.get("content", {})
            for content_type, schema_info in content.items():
                lines.append(f"- Content-Type: `{content_type}`")
                schema_ref = schema_info.get("schema", {}).get("$ref", "")
                if schema_ref:
                    schema_name = schema_ref.split("/")[-1]
                    lines.append(f"  Schema: `{schema_name}`")
        
        # Responses
        responses = operation.get("responses", {})
        if responses:
            lines.append("\n**Responses:**")
            for code, response in responses.items():
                description = response.get("description", "")
                lines.append(f"- `{code}`: {description}")
        
        return "\n".join(lines)
    
    async def _on_file_change(self) -> None:
        """Handle file change events from the watcher."""
        logger.info("Backend file changed, reloading spec...")
        
        try:
            old_spec = self.current_spec
            new_spec = self.spec_generator.generate()
            
            # Check for changes
            if old_spec:
                diff_result = self.diff_engine.compare(old_spec, new_spec)
                
                if diff_result.has_changes():
                    logger.info("API changes detected")
                    self.current_spec = new_spec
                    self._save_spec()
                    
                    # Save diff
                    diff_file = self.output_dir / "api_diff.json"
                    with open(diff_file, "w", encoding="utf-8") as f:
                        f.write(diff_result.to_json())
                    
                    # Save diff summary
                    diff_summary = self.summarizer.summarize_diff(diff_result.to_dict())
                    diff_summary_file = self.output_dir / "api_diff_summary.txt"
                    with open(diff_summary_file, "w", encoding="utf-8") as f:
                        f.write(diff_summary)
                    
                    # Send notification to MCP clients
                    await self._send_change_notification(diff_result, diff_summary)
                else:
                    logger.debug("No API changes detected")
            else:
                # First load
                self.current_spec = new_spec
                self._save_spec()
                
        except Exception as e:
            logger.error(f"Error handling file change: {e}")
    
    async def _send_change_notification(self, diff_result, summary: str) -> None:
        """Send notification to MCP clients about API changes."""
        try:
            # Log the change for now
            # MCP notifications will be sent when clients re-request resources
            logger.info(f"API changed - notification prepared for next resource request")
            logger.info(f"Change summary: {summary[:200]}...")
            
            # The MCP protocol will automatically serve updated resources
            # when clients request them again. Some MCP implementations
            # support push notifications which can be added here.
            
        except Exception as e:
            logger.warning(f"Error preparing change notification: {e}")
    
    async def _start_file_watcher(self) -> None:
        """Start the file watcher in the background."""
        if self.file_watcher is None:
            self.file_watcher = FileWatcher(
                self.config,
                on_change=lambda: asyncio.create_task(self._on_file_change())
            )
        
        logger.info("Starting file watcher for live updates...")
        await self.file_watcher.start()
    
    async def run(self) -> None:
        """Run the MCP server."""
        logger.info("Starting Conciliate MCP server with live updates")
        
        # Start file watcher in background
        self.watcher_task = asyncio.create_task(self._start_file_watcher())
        
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def run_mcp_server(config: ConciliateConfig) -> None:
    """
    Run the MCP server.
    
    Args:
        config: Conciliate configuration
    """
    server = ConciliateMCPServer(config)
    await server.run()


def main() -> None:
    """Main entry point for MCP server."""
    import sys
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    try:
        # Load config
        config = load_config()
        
        # Run server
        asyncio.run(run_mcp_server(config))
        
    except FileNotFoundError:
        logger.error("No .conciliate.yaml found. Run 'conciliate init' first.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"MCP server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
