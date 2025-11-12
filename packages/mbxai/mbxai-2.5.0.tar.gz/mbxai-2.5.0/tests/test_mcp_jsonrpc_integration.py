"""Test MCP client integration with JSON-RPC 2.0 protocol."""

import pytest
import asyncio
import os
from mbxai.mcp import AsyncMCPClient
from mbxai.openrouter import AsyncOpenRouterClient

# Get authentication token
API_TOKEN = os.getenv("MBXAI_API_TOKEN", "ui-full-access-16b40d85eaf028624104a03c8b297536")


@pytest.mark.asyncio
async def test_mcp_server_jsonrpc_integration():
    """Test that the MCP client can read and parse JSON-RPC 2.0 responses from the server."""
    
    # Setup
    mcp_server_url = "https://api.mbxai.cloud/api"
    
    # Create a mock OpenRouter client (not needed for this test, but required by AsyncMCPClient)
    openrouter_client = AsyncOpenRouterClient(token="test-key")
    
    # Create MCP client and register the server
    async with AsyncMCPClient(openrouter_client) as mcp_client:
        # Register the MCP server with authentication (this will fetch and parse the tools)
        await mcp_client.register_mcp_server("mbxai-cloud", mcp_server_url, token=API_TOKEN)
        
        # Verify that tools were successfully registered
        assert len(mcp_client._tools) > 0, "No tools were registered from the server"
        
        # Expected tools from the server
        expected_tools = [
            "analyze_html",
            "analyze_variant_handling", 
            "generate_product_selectors",
            "scrape_html",
            "generate_image",
            "edit_image",
            "search_shopware_knowledge",
            "search_shopware_knowledge_by_category"
        ]
        
        # Verify all expected tools are present
        registered_tool_names = list(mcp_client._tools.keys())
        print(f"\nRegistered tools: {registered_tool_names}")
        
        for tool_name in expected_tools:
            assert tool_name in registered_tool_names, f"Tool '{tool_name}' was not registered"
        
        # Verify tool properties for one of the tools
        analyze_html_tool = mcp_client._tools["analyze_html"]
        
        assert analyze_html_tool.name == "analyze_html"
        assert analyze_html_tool.service == "html-structure-analyser"
        assert analyze_html_tool.strict is True
        assert "Analyze HTML content" in analyze_html_tool.description
        assert "inputSchema" in analyze_html_tool.model_dump()
        assert analyze_html_tool.internal_url == "http://html-structure-analyser.mbxai-mcp.svc.cluster.local:5000/tools/analyze_html/invoke"
        
        # Verify the inputSchema has the expected structure
        input_schema = analyze_html_tool.inputSchema
        assert "properties" in input_schema
        assert "input" in input_schema["properties"]
        assert "$defs" in input_schema
        assert "AnalyzeHtmlInput" in input_schema["$defs"]
        
        # Verify that the tool can be converted to OpenAI function format
        openai_function = analyze_html_tool.to_openai_function()
        assert openai_function["type"] == "function"
        assert openai_function["function"]["name"] == "analyze_html"
        assert openai_function["function"]["strict"] is True
        assert "parameters" in openai_function["function"]
        
        print(f"\n✓ Successfully registered {len(registered_tool_names)} tools from JSON-RPC 2.0 server")
        print(f"✓ Tool parsing and schema conversion working correctly")


def test_mcp_server_jsonrpc_integration_sync():
    """Synchronous wrapper for the async test."""
    asyncio.run(test_mcp_server_jsonrpc_integration())


if __name__ == "__main__":
    # Run the test directly
    print("Testing MCP JSON-RPC 2.0 integration...")
    test_mcp_server_jsonrpc_integration_sync()
    print("\n✅ All tests passed!")

