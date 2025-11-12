"""MCP client implementation."""

from typing import Any, TypeVar, Callable
import httpx
import logging
import json
from pydantic import BaseModel, Field

from ..tools import ToolClient, Tool, convert_to_strict_schema
from ..openrouter import OpenRouterClient

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class MCPTool(Tool):
    """A tool from the MCP server."""
    inputSchema: dict[str, Any]
    internal_url: str
    service: str
    strict: bool = True
    function: Callable[..., Any] | None = None  # Make function optional during initialization

    def to_openai_function(self) -> dict[str, Any]:
        """Convert the tool to an OpenAI function definition."""
        # Convert schema to strict format, keeping input wrapper
        strict_schema = convert_to_strict_schema(self.inputSchema, strict=self.strict, keep_input_wrapper=True)
        
        function_def = {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": strict_schema,
                "strict": True
            }
        }
        
        logger.debug(f"(client) Created function definition for {self.name}: {json.dumps(function_def, indent=2)}")
        return function_def


class MCPClient(ToolClient):
    """MCP client that extends ToolClient to support MCP tool servers."""

    def __init__(self, openrouter_client: OpenRouterClient):
        """Initialize the MCP client."""
        super().__init__(openrouter_client)
        self._mcp_servers: dict[str, str] = {}
        self._mcp_tokens: dict[str, str] = {}  # Store Bearer tokens per server
        self._http_client = httpx.Client()
        self._async_http_client = httpx.AsyncClient()

    def __enter__(self):
        """Enter the context."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context."""
        self._http_client.close()
    
    async def __aenter__(self):
        """Enter the async context."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async context."""
        await self._async_http_client.aclose()
        self._http_client.close()

    def _create_tool_function(self, tool: MCPTool) -> Callable[..., Any]:
        """Create a function that invokes an MCP tool."""
        def tool_function(**kwargs: Any) -> Any:
            # If kwargs has input wrapper, unwrap it (for backward compatibility)
            if "input" in kwargs and len(kwargs) == 1 and isinstance(kwargs["input"], dict):
                kwargs = kwargs["input"]

            # Get the URL to use for the tool
            # Prefer using the registered MCP server URL over internal_url
            # as internal_url might be a Kubernetes internal endpoint
            server_url = self._mcp_servers.get(tool.service)
            if server_url:
                # Use the unified MCP endpoint that handles all methods
                url = f"{server_url}/mcp"
            elif tool.internal_url:
                # Fallback to internal URL if no server is registered
                url = tool.internal_url
            else:
                raise ValueError(f"No URL available for tool {tool.name}")

            # Prepare JSON-RPC 2.0 request
            # Note: The server now returns flattened schemas, so we always use flat arguments
            jsonrpc_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": tool.name,
                    "arguments": kwargs
                },
                "id": 1
            }

            # Prepare headers with authentication if available
            headers = {"Content-Type": "application/json"}
            token = self._mcp_tokens.get(tool.service)
            if token:
                headers["Authorization"] = f"Bearer {token}"

            # Make the HTTP request to the tool's URL
            response = self._http_client.post(
                url,
                json=jsonrpc_request,
                headers=headers,
                timeout=300.0  # 5 minutes timeout
            )
            
            # Log response details for debugging
            logger.debug(f"Tool {tool.name} response status: {response.status_code}")
            logger.debug(f"Tool {tool.name} response headers: {response.headers}")
            
            try:
                result = response.json()
                logger.debug(f"Tool {tool.name} response parsed successfully: {json.dumps(result, indent=2)}")
                
                # Handle JSON-RPC 2.0 response format
                if "jsonrpc" in result and result["jsonrpc"] == "2.0":
                    if "error" in result:
                        # Handle JSON-RPC 2.0 error response
                        error = result["error"]
                        error_msg = f"JSON-RPC Error {error.get('code', 'unknown')}: {error.get('message', 'Unknown error')}"
                        if "data" in error:
                            error_msg += f" - Data: {error['data']}"
                        logger.error(f"Tool {tool.name} returned error: {error_msg}")
                        raise ValueError(error_msg)
                    elif "result" in result:
                        # Return the result from JSON-RPC 2.0 success response
                        return result["result"]
                    else:
                        logger.warning(f"Tool {tool.name} returned JSON-RPC 2.0 response without result or error")
                        return result
                else:
                    # Fallback to non-JSON-RPC response for backward compatibility
                    logger.debug(f"Tool {tool.name} returned non-JSON-RPC response")
                    return result
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse tool {tool.name} response: {str(e)}")
                logger.error(f"Response content: {response.text[:1000]}...")  # Log first 1000 chars
                raise
        
        return tool_function

    def _create_async_tool_function(self, tool: MCPTool) -> Callable[..., Any]:
        """Create an async function that invokes an MCP tool."""
        async def async_tool_function(**kwargs: Any) -> Any:
            # If kwargs has input wrapper, unwrap it (for backward compatibility)
            if "input" in kwargs and len(kwargs) == 1 and isinstance(kwargs["input"], dict):
                kwargs = kwargs["input"]

            # Get the URL to use for the tool
            # Prefer using the registered MCP server URL over internal_url
            # as internal_url might be a Kubernetes internal endpoint
            server_url = self._mcp_servers.get(tool.service)
            if server_url:
                # Use the unified MCP endpoint that handles all methods
                url = f"{server_url}/mcp"
            elif tool.internal_url:
                # Fallback to internal URL if no server is registered
                url = tool.internal_url
            else:
                raise ValueError(f"No URL available for tool {tool.name}")

            # Prepare JSON-RPC 2.0 request
            # Note: The server now returns flattened schemas, so we always use flat arguments
            jsonrpc_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": tool.name,
                    "arguments": kwargs
                },
                "id": 1
            }

            # Prepare headers with authentication if available
            headers = {"Content-Type": "application/json"}
            token = self._mcp_tokens.get(tool.service)
            if token:
                headers["Authorization"] = f"Bearer {token}"

            # Make the async HTTP request to the tool's URL
            response = await self._async_http_client.post(
                url,
                json=jsonrpc_request,
                headers=headers,
                timeout=300.0  # 5 minutes timeout
            )
            
            # Log response details for debugging
            logger.debug(f"Tool {tool.name} async response status: {response.status_code}")
            logger.debug(f"Tool {tool.name} async response headers: {response.headers}")
            
            try:
                result = response.json()
                logger.debug(f"Tool {tool.name} async response parsed successfully: {json.dumps(result, indent=2)}")
                
                # Handle JSON-RPC 2.0 response format
                if "jsonrpc" in result and result["jsonrpc"] == "2.0":
                    if "error" in result:
                        # Handle JSON-RPC 2.0 error response
                        error = result["error"]
                        error_msg = f"JSON-RPC Error {error.get('code', 'unknown')}: {error.get('message', 'Unknown error')}"
                        if "data" in error:
                            error_msg += f" - Data: {error['data']}"
                        logger.error(f"Tool {tool.name} returned error: {error_msg}")
                        raise ValueError(error_msg)
                    elif "result" in result:
                        # Return the result from JSON-RPC 2.0 success response
                        return result["result"]
                    else:
                        logger.warning(f"Tool {tool.name} returned JSON-RPC 2.0 response without result or error")
                        return result
                else:
                    # Fallback to non-JSON-RPC response for backward compatibility
                    logger.debug(f"Tool {tool.name} returned non-JSON-RPC response")
                    return result
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse tool {tool.name} async response: {str(e)}")
                logger.error(f"Response content: {response.text[:1000]}...")  # Log first 1000 chars
                raise
        
        return async_tool_function

    def register_mcp_server(self, name: str, base_url: str, token: str | None = None) -> None:
        """Register an MCP server and load its tools.
        
        Args:
            name: A friendly name for the server
            base_url: The base URL of the MCP server (e.g., "https://api.mbxai.cloud/api")
            token: Optional Bearer token for authentication
        """
        base_url = base_url.rstrip("/")
        self._mcp_servers[name] = base_url
        
        # Prepare JSON-RPC 2.0 request for tools list
        jsonrpc_request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 1
        }
        
        # Prepare headers with authentication if token is provided
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
            self._mcp_tokens[name] = token  # Store token for this server
        
        # Fetch tools from the server using the unified MCP endpoint
        response = self._http_client.post(f"{base_url}/mcp", json=jsonrpc_request, headers=headers)
        response_data = response.json()
        
        # Handle JSON-RPC 2.0 response format
        if "jsonrpc" in response_data and response_data["jsonrpc"] == "2.0":
            if "error" in response_data:
                error = response_data["error"]
                raise ValueError(f"JSON-RPC Error {error.get('code')}: {error.get('message')}")
            elif "result" in response_data:
                # Extract tools from JSON-RPC 2.0 result
                result = response_data["result"]
                tools_data = result.get("tools", []) if isinstance(result, dict) else []
            else:
                tools_data = []
        else:
            # Fallback to non-JSON-RPC response for backward compatibility
            tools_data = response_data.get("tools", [])
        
        logger.debug(f"Received {len(tools_data)} tools from server {name}")
        
        # Also register the base URL and token for each service to enable service-based lookups
        services_seen = set()
        for tool_data in tools_data:
            if isinstance(tool_data, dict) and "service" in tool_data:
                service_name = tool_data["service"]
                if service_name not in services_seen:
                    self._mcp_servers[service_name] = base_url
                    if token:
                        self._mcp_tokens[service_name] = token
                    services_seen.add(service_name)
                    logger.debug(f"Registered service '{service_name}' -> {base_url}")
        
        # Register each tool
        for idx, tool_data in enumerate(tools_data):
            logger.debug(f"Processing tool {idx}: {json.dumps(tool_data, indent=2)}")
            
            # Ensure tool_data is a dictionary
            if not isinstance(tool_data, dict):
                logger.error(f"Invalid tool data type: {type(tool_data)}. Expected dict, got {tool_data}")
                continue
                
            try:
                # Create MCPTool instance with proper dictionary unpacking
                tool = MCPTool(**tool_data)
                
                # Create the tool function
                tool_function = self._create_tool_function(tool)
                
                # Set the function after creation
                tool.function = tool_function
                
                # Register the tool with ToolClient
                self._tools[tool.name] = tool
                logger.debug(f"Successfully registered tool: {tool.name}")
            except Exception as e:
                logger.error(f"Failed to register tool: {str(e)}")
                logger.error(f"Tool data that caused the error: {json.dumps(tool_data, indent=2)}")

    async def aregister_mcp_server(self, name: str, base_url: str, token: str | None = None) -> None:
        """Register an MCP server and load its tools (async version).
        
        Args:
            name: A friendly name for the server
            base_url: The base URL of the MCP server (e.g., "https://api.mbxai.cloud/api")
            token: Optional Bearer token for authentication
        """
        base_url = base_url.rstrip("/")
        self._mcp_servers[name] = base_url
        
        # Prepare JSON-RPC 2.0 request for tools list
        jsonrpc_request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 1
        }
        
        # Prepare headers with authentication if token is provided
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
            self._mcp_tokens[name] = token  # Store token for this server
        
        # Fetch tools from the server using the unified MCP endpoint
        response = await self._async_http_client.post(f"{base_url}/mcp", json=jsonrpc_request, headers=headers)
        response_data = response.json()
        
        # Handle JSON-RPC 2.0 response format
        if "jsonrpc" in response_data and response_data["jsonrpc"] == "2.0":
            if "error" in response_data:
                error = response_data["error"]
                raise ValueError(f"JSON-RPC Error {error.get('code')}: {error.get('message')}")
            elif "result" in response_data:
                # Extract tools from JSON-RPC 2.0 result
                result = response_data["result"]
                tools_data = result.get("tools", []) if isinstance(result, dict) else []
            else:
                tools_data = []
        else:
            # Fallback to non-JSON-RPC response for backward compatibility
            tools_data = response_data.get("tools", [])
        
        logger.debug(f"Received {len(tools_data)} tools from server {name}")
        
        # Also register the base URL and token for each service to enable service-based lookups
        services_seen = set()
        for tool_data in tools_data:
            if isinstance(tool_data, dict) and "service" in tool_data:
                service_name = tool_data["service"]
                if service_name not in services_seen:
                    self._mcp_servers[service_name] = base_url
                    if token:
                        self._mcp_tokens[service_name] = token
                    services_seen.add(service_name)
                    logger.debug(f"Registered service '{service_name}' -> {base_url}")
        
        # Register each tool
        for idx, tool_data in enumerate(tools_data):
            logger.debug(f"Processing tool {idx}: {json.dumps(tool_data, indent=2)}")
            
            # Ensure tool_data is a dictionary
            if not isinstance(tool_data, dict):
                logger.error(f"Invalid tool data type: {type(tool_data)}. Expected dict, got {tool_data}")
                continue
                
            try:
                # Create MCPTool instance with proper dictionary unpacking
                tool = MCPTool(**tool_data)
                
                # Create the tool function (async-capable)
                tool_function = self._create_tool_function(tool)
                
                # Set the function after creation
                tool.function = tool_function
                
                # Register the tool with ToolClient
                self._tools[tool.name] = tool
                logger.debug(f"Successfully registered tool: {tool.name}")
            except Exception as e:
                logger.error(f"Failed to register tool: {str(e)}")
                logger.error(f"Tool data that caused the error: {json.dumps(tool_data, indent=2)}")