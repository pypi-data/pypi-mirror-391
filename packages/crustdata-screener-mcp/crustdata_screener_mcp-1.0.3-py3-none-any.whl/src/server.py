#!/usr/bin/env python3
"""
CrustData Screener MCP Server

This MCP server wraps CrustData's existing REST APIs, exposing them as MCP tools
that can be consumed by MCP clients like Claude Code, Warp, and other AI assistants.
"""

import os
import sys
import asyncio
import logging
from typing import Any, Dict, Optional, Sequence
from urllib.parse import urljoin, urlencode

import httpx
import yaml
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

# Import validation utilities
try:
    from validators import validate_tool_params, ValidationError
except ImportError:
    from src.validators import validate_tool_params, ValidationError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("crustdata-mcp-server")


class CrustDataMCPServer:
    """MCP Server that wraps CrustData Screener APIs."""
    
    def __init__(self, config_path: str):
        """Initialize the MCP server with configuration."""
        self.config = self._load_config(config_path)
        self.base_url = self._resolve_env_vars(self.config["base_url"])
        self.auth_token = self._resolve_env_vars(self.config["auth"]["value"])
        self.server = Server("crustdata-screener")
        self.client = httpx.AsyncClient(timeout=60.0)
        
        # Register handlers
        self._register_handlers()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _resolve_env_vars(self, value: str) -> str:
        """Resolve environment variables in config values."""
        # Handle ${VAR:-default} syntax
        import re
        pattern = r'\$\{([^:}]+)(?::-(.*?))?\}'
        
        def replacer(match):
            var_name = match.group(1)
            default_value = match.group(2) or ""
            return os.environ.get(var_name, default_value)
        
        return re.sub(pattern, replacer, value)
    
    def _register_handlers(self):
        """Register MCP protocol handlers."""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List all available tools from the configuration."""
            tools = []
            for tool_config in self.config["tools"]:
                # Build input schema from parameters
                properties = {}
                required = []
                
                for param in tool_config.get("parameters", []):
                    param_name = param["name"]
                    param_type = param["type"]
                    
                    # Map YAML types to JSON Schema types
                    type_mapping = {
                        "string": "string",
                        "integer": "integer",
                        "boolean": "boolean",
                        "number": "number",
                        "array": "array",
                        "object": "object"
                    }
                    
                    properties[param_name] = {
                        "type": type_mapping.get(param_type, "string"),
                        "description": param.get("description", "")
                    }
                    
                    if param.get("example"):
                        properties[param_name]["examples"] = [param["example"]]
                    
                    if param.get("default") is not None:
                        properties[param_name]["default"] = param["default"]
                    
                    if param.get("required", False):
                        required.append(param_name)
                
                input_schema = {
                    "type": "object",
                    "properties": properties
                }
                
                if required:
                    input_schema["required"] = required
                
                tools.append(Tool(
                    name=tool_config["name"],
                    description=tool_config["description"],
                    inputSchema=input_schema
                ))
            
            return tools
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
            """Execute a tool by calling the corresponding API endpoint."""
            logger.info(f"Calling tool: {name} with arguments: {arguments}")
            
            # Find tool configuration
            tool_config = None
            for tool in self.config["tools"]:
                if tool["name"] == name:
                    tool_config = tool
                    break
            
            if not tool_config:
                error_msg = f"Tool '{name}' not found"
                logger.error(error_msg)
                return [TextContent(
                    type="text",
                    text=f"Error: {error_msg}"
                )]
            
            # Validate arguments before making API request
            try:
                validated_arguments = validate_tool_params(name, arguments)
                logger.info(f"Validation passed for tool: {name}")
            except ValidationError as e:
                error_msg = f"Validation error for {name}: {str(e)}"
                logger.warning(error_msg)
                return [TextContent(
                    type="text",
                    text=f"Validation Error: {str(e)}"
                )]
            except Exception as e:
                # Unexpected validation error, log but continue
                logger.error(f"Unexpected validation error for {name}: {e}", exc_info=True)
                validated_arguments = arguments
            
            # Make API request
            try:
                result = await self._call_api(tool_config, validated_arguments)
                
                # Format response as text
                import json
                response_text = json.dumps(result, indent=2)
                
                return [TextContent(
                    type="text",
                    text=response_text
                )]
                
            except Exception as e:
                error_msg = f"Error calling {name}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                return [TextContent(
                    type="text",
                    text=f"Error: {error_msg}"
                )]
    
    async def _call_api(self, tool_config: Dict[str, Any], arguments: Dict[str, Any]) -> Any:
        """Make an HTTP request to the API endpoint."""
        endpoint = tool_config["endpoint"]
        method = tool_config.get("method", "GET").upper()
        
        # Build full URL
        url = urljoin(self.base_url, endpoint)
        
        # Prepare headers
        headers = {
            self.config["auth"]["header"]: self.auth_token,
            "Content-Type": "application/json",
            "User-Agent": "CrustData-MCP-Server/1.0"
        }
        
        # Prepare request parameters
        if method == "GET":
            # Add query parameters
            params = {k: v for k, v in arguments.items() if v is not None}
            logger.info(f"Making GET request to {url} with params: {params}")
            response = await self.client.get(url, params=params, headers=headers)
        else:
            # POST/PUT/PATCH - send as JSON body
            logger.info(f"Making {method} request to {url} with body: {arguments}")
            response = await self.client.request(
                method,
                url,
                json=arguments,
                headers=headers
            )
        
        # Check response status
        if response.status_code >= 400:
            error_detail = response.text
            logger.error(f"API error {response.status_code}: {error_detail}")
            raise Exception(f"API returned status {response.status_code}: {error_detail}")
        
        # Parse response
        try:
            return response.json()
        except Exception as e:
            logger.warning(f"Could not parse JSON response: {e}")
            return {"text": response.text}
    
    async def run(self):
        """Run the MCP server."""
        logger.info("Starting CrustData MCP Server...")
        logger.info(f"Base URL: {self.base_url}")
        logger.info(f"Registered {len(self.config['tools'])} tools")
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )
    
    async def cleanup(self):
        """Clean up resources."""
        await self.client.aclose()


async def main():
    """Main entry point."""
    # Get config path from environment or use default
    config_path = os.environ.get(
        "CRUSTDATA_MCP_CONFIG",
        os.path.join(os.path.dirname(__file__), "../config/api_endpoints.yaml")
    )
    
    if not os.path.exists(config_path):
        logger.error(f"Configuration file not found: {config_path}")
        sys.exit(1)
    
    # Validate required environment variables
    if not os.environ.get("CRUSTDATA_API_TOKEN"):
        logger.error("CRUSTDATA_API_TOKEN environment variable is required")
        sys.exit(1)
    
    server = CrustDataMCPServer(config_path)
    
    try:
        await server.run()
    finally:
        await server.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
