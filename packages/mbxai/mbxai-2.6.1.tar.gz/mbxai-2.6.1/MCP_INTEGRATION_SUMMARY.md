# MCP Integration Summary

## Overview

The MCP clients (`AsyncMCPClient` and `MCPClient`) have been updated to fully comply with your MCP server's JSON-RPC 2.0 protocol implementation as documented.

---

## Changes Made

### 1. Unified Endpoint Structure ✅

**Before:** Clients attempted to use multiple endpoints (`/api/tools`, `/api/tools/call`)

**After:** All requests now go to the single unified MCP endpoint: `/api/mcp`

The `method` field in the JSON-RPC request determines the action:
- `tools/list` - List all available tools
- `tools/call` - Invoke a specific tool

This matches your documentation:
> **ONE** JSON-RPC 2.0 compliant endpoint: `/api/mcp`

---

### 2. Authentication Support 🔐

**Added Bearer Token Support:**

```python
# When registering an MCP server
await mcp_client.register_mcp_server(
    name="mbxai-cloud",
    base_url="https://api.mbxai.cloud/api",
    token="your_bearer_token_here"  # ✅ New parameter
)
```

**Implementation Details:**
- Tokens are stored per server/service in `_mcp_tokens` dictionary
- Automatically included in `Authorization: Bearer {token}` header
- Supports granular namespace:service permissions as per your documentation
- Token is propagated to all services discovered from that server

**Headers Sent:**
```python
{
    "Content-Type": "application/json",
    "Authorization": "Bearer YOUR_TOKEN"  # When token provided
}
```

---

### 3. JSON-RPC 2.0 Protocol Compliance

#### Tools List Request

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {}
}
```

**Endpoint:** `POST https://api.mbxai.cloud/api/mcp`

#### Tool Call Request

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "scrape_html",
    "arguments": {
      "input": {
        "url": "https://example.com"
      }
    }
  }
}
```

**Endpoint:** `POST https://api.mbxai.cloud/api/mcp` (same endpoint!)

---

### 4. Response Handling

**Success Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [...]
  }
}
```

**Error Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32603,
    "message": "Tool execution error",
    "data": "Detailed error information"
  }
}
```

The clients properly extract:
- `result` field for successful responses
- `error.code`, `error.message`, and `error.data` for errors
- Handle JSON-RPC 2.0 error codes as per specification

---

### 5. Service Resolution

When you register a server like `mbxai-cloud`, the client automatically maps all discovered services to that server's base URL:

```python
# Register once
await mcp_client.register_mcp_server("mbxai-cloud", "https://api.mbxai.cloud/api", token=token)

# All services get registered:
# - html-structure-analyser → https://api.mbxai.cloud/api
# - image-generator → https://api.mbxai.cloud/api
# - shopware-knowledge → https://api.mbxai.cloud/api

# Each service inherits the authentication token
```

This enables tools from different services to work seamlessly through the same MCP endpoint.

---

## Updated Method Signatures

### AsyncMCPClient

```python
async def register_mcp_server(
    self, 
    name: str, 
    base_url: str, 
    token: str | None = None  # ✅ New optional parameter
) -> None:
    """Register an MCP server and load its tools.
    
    Args:
        name: A friendly name for the server
        base_url: The base URL of the MCP server (e.g., "https://api.mbxai.cloud/api")
        token: Optional Bearer token for authentication
    """
```

### MCPClient (Synchronous)

```python
def register_mcp_server(
    self, 
    name: str, 
    base_url: str, 
    token: str | None = None  # ✅ New optional parameter
) -> None:
    """Register an MCP server and load its tools.
    
    Args:
        name: A friendly name for the server
        base_url: The base URL of the MCP server
        token: Optional Bearer token for authentication
    """

async def aregister_mcp_server(
    self, 
    name: str, 
    base_url: str, 
    token: str | None = None  # ✅ New optional parameter
) -> None:
    """Async version."""
```

---

## Usage Examples

### Basic Usage (No Authentication)

```python
from mbxai.mcp import AsyncMCPClient
from mbxai.openrouter import AsyncOpenRouterClient

openrouter = AsyncOpenRouterClient(token="your_openrouter_token")

async with AsyncMCPClient(openrouter) as mcp_client:
    # Register server (will work if server allows unauthenticated access)
    await mcp_client.register_mcp_server(
        "mbxai-cloud", 
        "https://api.mbxai.cloud/api"
    )
    
    # Use tools
    result = await mcp_client.invoke_tool("scrape_html", input={"url": "https://example.com"})
```

### With Authentication (Recommended)

```python
import os
from mbxai.mcp import AsyncMCPClient
from mbxai.openrouter import AsyncOpenRouterClient

# Get your MCP API token
MCP_TOKEN = os.getenv("MBXAI_API_TOKEN")

openrouter = AsyncOpenRouterClient(token="your_openrouter_token")

async with AsyncMCPClient(openrouter) as mcp_client:
    # Register server with authentication
    await mcp_client.register_mcp_server(
        name="mbxai-cloud",
        base_url="https://api.mbxai.cloud/api",
        token=MCP_TOKEN  # ✅ Bearer token for authentication
    )
    
    # Now you can call tools based on your token permissions
    # Tools you don't have access to won't be visible
    
    available_tools = list(mcp_client._tools.keys())
    print(f"Available tools: {available_tools}")
    
    # Call a tool (requires appropriate permissions)
    result = await mcp_client.invoke_tool(
        "scrape_html",
        input={"url": "https://google.de"}
    )
```

### Token Permissions

According to your documentation, tokens can have different permission levels:

```python
# Full access token (admin)
token = "admin_token_xyz"  # Permissions: ["*:*"]

# Namespace-specific token
token = "mcp_token_abc"  # Permissions: ["mbxai-mcp:*"]

# Service-specific token
token = "scraper_token"  # Permissions: ["mbxai-mcp:html-structure-analyser"]

# Multi-service token
token = "multi_token"  # Permissions: [
#     "mbxai-mcp:html-structure-analyser",
#     "mbxai-mcp:image-generator"
# ]
```

The client will only see and be able to call tools that your token has permissions for.

---

## Testing

### Environment Setup

```bash
# Set your API token
export MBXAI_API_TOKEN="your_token_here"

# Run tests
uv run pytest tests/test_mcp_tool_call.py -v -s
```

### Test Coverage

1. **test_direct_jsonrpc_tool_call** - Tests direct JSON-RPC 2.0 calls to `/api/mcp`
   - Fetches tools list using `tools/list` method
   - Calls `scrape_html` tool using `tools/call` method
   - Verifies JSON-RPC 2.0 response format

2. **test_mcp_client_tool_call** - Tests AsyncMCPClient integration
   - Registers MCP server with authentication
   - Loads and verifies tools
   - Invokes tools through the client

Both tests support optional authentication via the `MBXAI_API_TOKEN` environment variable.

---

## Backward Compatibility

✅ **Maintained:** The client still supports:
- Non-JSON-RPC responses (fallback mode)
- Registration without authentication (if server allows)
- Internal URLs as fallback

⚠️ **Breaking Changes:** None! The `token` parameter is optional.

---

## Architecture Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     Your Application                         │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
            ┌───────────────────────────────┐
            │   AsyncMCPClient / MCPClient   │
            │                               │
            │  - Stores tokens              │
            │  - Manages service mapping    │
            │  - Handles JSON-RPC 2.0       │
            └───────────────┬───────────────┘
                            │
                            │ All requests via /api/mcp
                            ▼
            ┌───────────────────────────────┐
            │   https://api.mbxai.cloud      │
            │         /api/mcp               │
            │                               │
            │  Method routing:              │
            │  - tools/list → List tools    │
            │  - tools/call → Invoke tool   │
            └───────────────┬───────────────┘
                            │
                            │ Routes to services
                            ▼
    ┌───────────────────────────────────────────────┐
    │              MCP Services                     │
    ├───────────────────────────────────────────────┤
    │  - html-structure-analyser                    │
    │  - image-generator                            │
    │  - shopware-knowledge                         │
    │  ...                                          │
    └───────────────────────────────────────────────┘
```

---

## Error Handling

The clients properly handle all error scenarios from your documentation:

| Status | Error Type | Client Behavior |
|--------|-----------|-----------------|
| 401 | Authentication Required | Raises ValueError with "Authorization token is required" |
| 403 | Permission Denied | Raises ValueError with "Token does not have access..." |
| 404 | Tool Not Found | Raises ValueError with "Tool 'name' not found" |
| -32602 | Invalid Params | Raises ValueError with parameter error details |
| -32603 | Tool Execution Error | Raises ValueError with tool error details |

---

## Best Practices

Based on your documentation, here are recommended practices:

1. **Always use authentication in production:**
   ```python
   token = os.getenv("MBXAI_API_TOKEN")
   await mcp_client.register_mcp_server("server", url, token=token)
   ```

2. **Use specific tokens with minimum necessary permissions:**
   ```python
   # Good: Service-specific token
   token = "scraper_token"  # Only html-structure-analyser access
   
   # Avoid: Admin token when not needed
   token = "admin_token"  # Full *:* access
   ```

3. **Handle authentication errors gracefully:**
   ```python
   try:
       await mcp_client.register_mcp_server(name, url, token=token)
   except ValueError as e:
       if "Authorization" in str(e) or "Forbidden" in str(e):
           logger.error("Authentication failed - check token permissions")
       raise
   ```

4. **Cache tool list to avoid repeated discovery:**
   ```python
   # Register once
   await mcp_client.register_mcp_server("mbxai", url, token=token)
   
   # Tools are cached in mcp_client._tools
   # No need to re-fetch for each operation
   ```

---

## Compliance Checklist

✅ **Single endpoint** - All requests go to `/api/mcp`  
✅ **JSON-RPC 2.0** - Proper `jsonrpc`, `method`, `params`, `id` fields  
✅ **Authentication** - Bearer token support in headers  
✅ **Method routing** - `tools/list` and `tools/call` methods  
✅ **Error handling** - Proper JSON-RPC error code extraction  
✅ **Response parsing** - Extract `result` for success, `error` for failures  
✅ **Service mapping** - Automatic service-to-URL resolution  
✅ **Token propagation** - Tokens shared across services from same server  

---

## Future Enhancements

Potential additions to align with your roadmap:

- [ ] Support for `resources/list` method
- [ ] Support for `prompts/list` method
- [ ] Rate limiting awareness
- [ ] Streaming response support
- [ ] Batch tool calls
- [ ] Progress tracking for long-running tools
- [ ] Webhook support

---

## Support

For questions about the MCP integration:
- See test examples in `tests/test_mcp_tool_call.py`
- Review this documentation
- Check your MCP server documentation at your API endpoint

---

**Status:** ✅ Fully Compliant with MCP Documentation  
**Last Updated:** 2025-11-12  
**Version:** 2.6.1+

