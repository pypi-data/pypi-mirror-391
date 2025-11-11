"""
AgenticWerx MCP Client - Simple rule retrieval client

This module implements a simple MCP server that connects to your
AgenticWerx MCP server to retrieve rules.
"""

import json
import logging
from typing import Any

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Resource, TextContent, Tool

from .api import AgenticWerxAPI, AgenticWerxAPIError

logger = logging.getLogger(__name__)


class AgenticWerxMCPClient:
    """
    Simple AgenticWerx MCP Client for rule retrieval.

    This client connects to your AgenticWerx MCP server and provides
    a simple interface to get rules through the MCP protocol.
    """

    def __init__(self, api_key: str, debug: bool = False):
        """
        Initialize the MCP client.

        Args:
            api_key: AgenticWerx API key
            debug: Enable debug logging
        """
        self.api_key = api_key
        self.debug = debug

        # Initialize the API client
        self.api = AgenticWerxAPI(api_key)

        # Initialize the MCP server
        self.server = Server("agenticwerx")

        # Configure logging
        if debug:
            logging.getLogger().setLevel(logging.DEBUG)

        logger.info("Initializing AgenticWerx MCP Client")

        # Set up MCP handlers
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Set up MCP server handlers."""

        @self.server.list_resources()
        async def list_resources() -> list[Resource]:
            """List available rule resources."""
            logger.debug("Listing available rule resources")

            try:
                # Test if we can get rules from the Lambda MCP server
                await self.api.get_rules()

                # Create a single resource for all rules
                resource = Resource(
                    uri="agenticwerx://rules",
                    name="AgenticWerx Rules",
                    description="All available AgenticWerx rules from Lambda MCP server",
                    mimeType="application/json",
                )

                logger.info("Listed rule resources from Lambda MCP server")
                return [resource]

            except AgenticWerxAPIError as e:
                logger.error(f"API error listing resources: {e}")
                return []
            except Exception as e:
                logger.error(f"Unexpected error listing resources: {e}")
                return []

        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read rule resource."""
            logger.debug(f"Reading resource: {uri}")

            if uri != "agenticwerx://rules":
                raise ValueError(f"Unknown resource URI: {uri}")

            try:
                rules_data = await self.api.get_rules()
                logger.debug("Successfully read rules resource from Lambda MCP server")
                return json.dumps(rules_data, indent=2)

            except AgenticWerxAPIError as e:
                logger.error(f"API error reading resource: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error reading resource: {e}")
                raise ValueError(f"Failed to read resource: {str(e)}") from e

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools."""
            logger.debug("Listing available tools")

            # Provide get_rules and analyze_code tools
            tools = [
                Tool(
                    name="get_rules",
                    description=(
                        "Get available rules for subscribed packages.\n\n"
                        "📋 Response Modes:\n"
                        "  • Summary (default): Just id, title, category, severity\n"
                        "  • Detailed (detailed=true): Includes instructions, rationale, tags, references\n"
                        "  • With Content (includeContent=true): Full markdown/JSON content\n"
                        "  • With Patterns (includePatterns=true + detailed=true): Regex patterns\n\n"
                        "💡 Tip: Start with summary mode, then use detailed=true or includeContent=true "
                        "when you need more information about specific rules."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "packageId": {
                                "type": "string",
                                "description": "Specific package ID (optional)",
                            },
                            "language": {
                                "type": "string",
                                "description": "Filter by programming language (e.g., typescript, python, go)",
                            },
                            "framework": {
                                "type": "string",
                                "description": "Filter by framework (e.g., react, nextjs, express)",
                            },
                            "category": {
                                "type": "string",
                                "description": "Filter by category (e.g., security, api-design, testing)",
                            },
                            "severity": {
                                "type": "string",
                                "description": "Filter by severity (critical, high, medium, low)",
                            },
                            "appliesTo": {
                                "type": "string",
                                "description": "Filter by applies to (e.g., frontend, backend, api, all)",
                            },
                            "search": {
                                "type": "string",
                                "description": "Search in rule titles and descriptions",
                            },
                            "ruleIds": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Get specific rules by ID",
                            },
                            "detailed": {
                                "type": "boolean",
                                "description": "⭐ Get full rule details (instructions, rationale, tags). Default: false",
                            },
                            "includeContent": {
                                "type": "boolean",
                                "description": "⭐ Get complete rule content (markdown/JSON). Warning: Large responses. Default: false",
                            },
                            "includePatterns": {
                                "type": "boolean",
                                "description": "⭐ Include regex patterns (requires detailed=true). Default: false",
                            },
                            "limit": {
                                "type": "number",
                                "description": "Maximum rules to return (1-200). Default: 50",
                            },
                            "offset": {
                                "type": "number",
                                "description": "Skip N rules for pagination. Default: 0",
                            },
                        },
                        "additionalProperties": False,
                    },
                ),
                Tool(
                    name="analyze_code",
                    description="Analyze code using AgenticWerx rules. Provide code snippet, optional language, and optional package IDs.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "Code to analyze",
                            },
                            "language": {
                                "type": "string",
                                "description": "Programming language (optional, will be auto-detected)",
                            },
                            "packageIds": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of package IDs to use for analysis (optional)",
                            },
                        },
                        "required": ["code"],
                        "additionalProperties": False,
                    },
                ),
            ]

            logger.info(f"Listed {len(tools)} available tools")
            return tools

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
            """Execute a tool."""
            logger.debug(f"Executing tool: {name}")

            try:
                if name == "get_rules":
                    # Handle get_rules tool with enhanced parameters
                    detailed = arguments.get("detailed", False)
                    include_content = arguments.get("includeContent", False)
                    include_patterns = arguments.get("includePatterns", False)

                    # Build params dict with all parameters
                    params = {
                        "packageId": arguments.get("packageId"),
                        "language": arguments.get("language"),
                        "framework": arguments.get("framework"),
                        "category": arguments.get("category"),
                        "severity": arguments.get("severity"),
                        "appliesTo": arguments.get("appliesTo"),
                        "search": arguments.get("search"),
                        "ruleIds": arguments.get("ruleIds"),
                        "limit": arguments.get("limit", 50),
                        "offset": arguments.get("offset", 0),
                        "detailed": detailed,
                        "includePatterns": include_patterns,
                        "includeContent": include_content,
                    }

                    # Remove None values
                    params = {k: v for k, v in params.items() if v is not None}

                    # Call the API with all parameters
                    result = await self.api.call_tool("get_rules", params)

                    # Parse the response - Lambda returns content array
                    content = result.get("content", [])

                    # Extract message and rules data from content array
                    message_text = ""
                    rules_data = None

                    for item in content:
                        if item.get("type") == "text":
                            text = item.get("text", "")
                            # Try to parse as JSON (second content item)
                            try:
                                parsed = json.loads(text)
                                if "rules" in parsed and "summary" in parsed:
                                    rules_data = parsed
                            except json.JSONDecodeError:
                                # First content item - the message from Lambda
                                message_text = text

                    # If no rules data found, return just the message
                    if not rules_data:
                        return [
                            TextContent(
                                type="text",
                                text=message_text or "No rules found",
                            )
                        ]

                    # Extract summary for hints
                    summary = rules_data.get("summary", {})
                    has_more = summary.get("hasMore", False)
                    offset = summary.get("offset", 0)
                    limit = summary.get("limit", 50)

                    # Build response with contextual hints
                    response_parts = [message_text]

                    # Add contextual hints based on current mode
                    if not detailed and not include_content:
                        response_parts.append(
                            "\n\n💡 Tip: You're viewing summary mode (minimal info). "
                            "To get more details, use:\n"
                            "  • detailed=true - Get full rule details (instructions, rationale, tags)\n"
                            "  • includeContent=true - Get complete rule content (markdown/JSON)\n"
                            "  • includePatterns=true - Get regex patterns (requires detailed=true)"
                        )
                    elif detailed and not include_content:
                        response_parts.append(
                            "\n\n💡 Tip: Use includeContent=true to get the full rule content (markdown/JSON)"
                        )

                    # Add pagination hint if there are more results
                    if has_more:
                        next_offset = offset + limit
                        response_parts.append(
                            f"\n\n📄 More results available. Use offset={next_offset} to get the next page."
                        )

                    # Build final response
                    response_text = "".join(response_parts)

                    logger.debug("Successfully retrieved rules")
                    return [
                        TextContent(type="text", text=response_text),
                        TextContent(
                            type="text", text=json.dumps(rules_data, indent=2)
                        ),
                    ]

                elif name == "analyze_code":
                    # Handle analyze_code tool
                    code = arguments.get("code")
                    if not code:
                        error_msg = "Missing required parameter: code"
                        logger.warning(error_msg)
                        return [
                            TextContent(
                                type="text",
                                text=json.dumps({"error": error_msg}, indent=2),
                            )
                        ]

                    language = arguments.get("language")
                    package_ids = arguments.get("packageIds") or arguments.get(
                        "package_ids"
                    )

                    result = await self.api.analyze_code(code, language, package_ids)

                    response = {
                        "tool": "analyze_code",
                        "language": language,
                        "packageIds": package_ids,
                        "analysis": result,
                    }

                    logger.debug("Successfully analyzed code")
                    return [
                        TextContent(type="text", text=json.dumps(response, indent=2))
                    ]

                else:
                    # Unsupported tool
                    error_msg = f"Tool '{name}' is not supported. Available tools: get_rules, analyze_code"
                    logger.warning(f"Unsupported tool requested: {name}")
                    return [
                        TextContent(
                            type="text", text=json.dumps({"error": error_msg}, indent=2)
                        )
                    ]

            except AgenticWerxAPIError as e:
                error_msg = f"AgenticWerx API Error: {str(e)}"
                logger.error(f"API error in tool {name}: {e}")
                return [
                    TextContent(
                        type="text", text=json.dumps({"error": error_msg}, indent=2)
                    )
                ]

            except Exception as e:
                error_msg = f"Tool execution error: {str(e)}"
                logger.error(f"Unexpected error in tool {name}: {e}")
                return [
                    TextContent(
                        type="text", text=json.dumps({"error": error_msg}, indent=2)
                    )
                ]

    async def test_connection(self) -> bool:
        """Test connection to the Lambda MCP server."""
        return await self.api.test_connection()

    async def run(self) -> None:
        """Run the MCP server."""
        logger.info("Starting AgenticWerx MCP Client")

        # Test connection to Lambda MCP server on startup
        logger.info("Testing connection to Lambda MCP server...")
        connection_ok = await self.test_connection()
        if not connection_ok:
            logger.error("Failed to connect to Lambda MCP server")
            # Continue anyway - the client might still work for some operations
        else:
            logger.info("Successfully connected to Lambda MCP server")

        try:
            from mcp.server.stdio import stdio_server

            async with stdio_server() as (read_stream, write_stream):
                logger.info("MCP Client started, waiting for connections...")

                from mcp.types import (
                    ResourcesCapability,
                    ServerCapabilities,
                    ToolsCapability,
                )

                init_options = InitializationOptions(
                    server_name="agenticwerx",
                    server_version="1.0.0",
                    capabilities=ServerCapabilities(
                        resources=ResourcesCapability(
                            subscribe=False, listChanged=False
                        ),
                        tools=ToolsCapability(listChanged=False),
                    ),
                )

                await self.server.run(read_stream, write_stream, init_options)

        except Exception as e:
            logger.error(f"Error running MCP server: {e}")
            raise
        finally:
            await self.api.close()
            logger.info("AgenticWerx MCP Client stopped")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.api.close()
