"""Test MCP server tool invocation with JSON-RPC 2.0 protocol."""

import pytest
import asyncio
import httpx
import json
import os
from mbxai.mcp import AsyncMCPClient
from mbxai.openrouter import AsyncOpenRouterClient

# Get authentication token from environment variable or use default
# Set this in your environment: export MBXAI_API_TOKEN="your_token_here"
# Or use the provided default token for testing
API_TOKEN = os.getenv("MBXAI_API_TOKEN", "ui-full-access-16b40d85eaf028624104a03c8b297536")


@pytest.mark.asyncio
async def test_direct_jsonrpc_tool_call():
    """Test direct JSON-RPC 2.0 call to MCP server without using the client."""
    
    # Use the unified MCP endpoint for all JSON-RPC methods
    mcp_url = "https://api.mbxai.cloud/api/mcp"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Step 1: Get tools list using JSON-RPC 2.0
        print("\n=== Step 1: Fetching tools list ===")
        tools_request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 1
        }
        
        # Prepare headers with authentication if token is available
        headers = {"Content-Type": "application/json"}
        if API_TOKEN:
            headers["Authorization"] = f"Bearer {API_TOKEN}"
            print("Using authentication token")
        else:
            print("⚠️  No API token found - set MBXAI_API_TOKEN environment variable")
        
        response = await client.post(mcp_url, json=tools_request, headers=headers)
        assert response.status_code == 200, f"Failed to fetch tools: {response.status_code}"
        
        tools_data = response.json()
        print(f"Tools response: {json.dumps(tools_data, indent=2)[:500]}...")
        
        # Verify JSON-RPC 2.0 format
        assert tools_data.get("jsonrpc") == "2.0", "Response is not JSON-RPC 2.0 format"
        assert "result" in tools_data, "Response missing result field"
        assert "tools" in tools_data["result"], "Result missing tools field"
        
        # Find the scrape_html tool
        tools_list = tools_data["result"]["tools"]
        scrape_html_tool = next((t for t in tools_list if t["name"] == "scrape_html"), None)
        assert scrape_html_tool is not None, "scrape_html tool not found"
        
        print(f"\n=== scrape_html tool found ===")
        print(f"Description: {scrape_html_tool['description'][:100]}...")
        print(f"Service: {scrape_html_tool['service']}")
        print(f"Internal URL: {scrape_html_tool['internal_url']}")
        
        # Step 2: Call the scrape_html tool using JSON-RPC 2.0
        print("\n=== Step 2: Calling scrape_html tool with google.de ===")
        tool_call_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "scrape_html",
                "arguments": {
                    "input": {
                        "url": "https://google.de"
                    }
                }
            },
            "id": 2
        }
        
        print(f"Request: {json.dumps(tool_call_request, indent=2)}")
        
        # Use the same headers with authentication
        response = await client.post(mcp_url, json=tool_call_request, headers=headers)
        print(f"Response status: {response.status_code}")
        
        assert response.status_code == 200, f"Tool call failed: {response.status_code}"
        
        result_data = response.json()
        print(f"Response structure: {json.dumps({k: type(v).__name__ for k, v in result_data.items()}, indent=2)}")
        
        # Verify JSON-RPC 2.0 response format
        assert result_data.get("jsonrpc") == "2.0", "Response is not JSON-RPC 2.0 format"
        
        if "error" in result_data:
            error = result_data["error"]
            print(f"Error received: {json.dumps(error, indent=2)}")
            pytest.fail(f"Tool call returned error: {error.get('message')}")
        
        assert "result" in result_data, "Response missing result field"
        
        # Verify the result contains HTML content
        html_content = result_data["result"]
        print(f"\n=== Step 3: Verifying HTML content ===")
        print(f"HTML content length: {len(str(html_content))} characters")
        print(f"HTML preview: {str(html_content)[:200]}...")
        
        # Verify it's HTML content
        html_str = str(html_content)
        assert len(html_str) > 100, "HTML content seems too short"
        assert "html" in html_str.lower() or "doctype" in html_str.lower() or "<" in html_str, \
            "Result doesn't appear to contain HTML"
        
        print("\n✓ Direct JSON-RPC 2.0 tool call successful!")


@pytest.mark.asyncio
async def test_mcp_client_tool_call():
    """Test MCP client tool invocation using the AsyncMCPClient."""
    
    print("\n=== Testing MCP Client Integration ===")
    
    # Setup
    mcp_server_url = "https://api.mbxai.cloud/api"
    
    # Create OpenRouter client (needed for MCP client initialization)
    openrouter_client = AsyncOpenRouterClient(token="test-key")
    
    # Create MCP client and register the server
    async with AsyncMCPClient(openrouter_client) as mcp_client:
        # Register the MCP server with optional authentication
        print("\n=== Step 1: Registering MCP server ===")
        if API_TOKEN:
            print("Using authentication token")
            await mcp_client.register_mcp_server("mbxai-cloud", mcp_server_url, token=API_TOKEN)
        else:
            print("⚠️  No API token found - set MBXAI_API_TOKEN environment variable")
            await mcp_client.register_mcp_server("mbxai-cloud", mcp_server_url)
        
        # Verify scrape_html tool is registered
        assert "scrape_html" in mcp_client._tools, "scrape_html tool not registered"
        scrape_html_tool = mcp_client._tools["scrape_html"]
        
        print(f"Tool registered: {scrape_html_tool.name}")
        print(f"Service: {scrape_html_tool.service}")
        print(f"Description: {scrape_html_tool.description[:100]}...")
        
        # Call the tool
        print("\n=== Step 2: Calling scrape_html tool with google.de ===")
        
        # The tool function is already bound to the tool object
        result = await scrape_html_tool.function(input={"url": "https://google.de"})
        
        print(f"\n=== Step 3: Verifying result ===")
        print(f"Result type: {type(result)}")
        print(f"Result length: {len(str(result))} characters")
        print(f"Result preview: {str(result)[:200]}...")
        
        # Verify the result contains HTML content
        html_str = str(result)
        assert len(html_str) > 100, "HTML content seems too short"
        assert "html" in html_str.lower() or "doctype" in html_str.lower() or "<" in html_str, \
            "Result doesn't appear to contain HTML"
        
        print("\n✓ MCP client tool call successful!")


def test_direct_jsonrpc_tool_call_sync():
    """Synchronous wrapper for the direct JSON-RPC test."""
    asyncio.run(test_direct_jsonrpc_tool_call())


def test_mcp_client_tool_call_sync():
    """Synchronous wrapper for the MCP client test."""
    asyncio.run(test_mcp_client_tool_call())


if __name__ == "__main__":
    print("=" * 80)
    print("Testing MCP Server Tool Call with JSON-RPC 2.0")
    print("=" * 80)
    
    print("\n" + "=" * 80)
    print("TEST 1: Direct JSON-RPC 2.0 Call")
    print("=" * 80)
    test_direct_jsonrpc_tool_call_sync()
    
    print("\n" + "=" * 80)
    print("TEST 2: MCP Client Integration")
    print("=" * 80)
    test_mcp_client_tool_call_sync()
    
    print("\n" + "=" * 80)
    print("✅ All tests passed!")
    print("=" * 80)

