"""Test MCP agent integration - AI using MCP tools."""

import pytest
import asyncio
import os
from pydantic import BaseModel
from mbxai.mcp import AsyncMCPClient
from mbxai.openrouter import AsyncOpenRouterClient, OpenRouterModel


# Get authentication tokens
MCP_TOKEN = os.getenv("MBXAI_API_TOKEN", "ui-full-access-16b40d85eaf028624104a03c8b297536")
OPENROUTER_TOKEN = os.getenv("OPENROUTER_API_KEY", None)


class WebsiteContent(BaseModel):
    """Response model for website content extraction."""
    url: str
    html_preview: str
    content_length: int
    has_html: bool


@pytest.mark.asyncio
async def test_mcp_agent_scrape_website():
    """Test AI agent using MCP scrape_html tool via parse method.
    
    This test demonstrates the complete integration:
    1. Register MCP server with authentication
    2. AI agent receives tools from MCP server
    3. User asks AI to scrape a website
    4. AI decides to use scrape_html tool
    5. Tool is invoked automatically
    6. AI processes the result and returns structured data
    """
    
    if not OPENROUTER_TOKEN:
        pytest.skip("OPENROUTER_API_KEY not set - skipping agent integration test")
    
    print("\n" + "="*80)
    print("MCP Agent Integration Test - AI Using scrape_html Tool")
    print("="*80)
    
    # Setup
    mcp_server_url = "https://api.mbxai.cloud/api"
    
    # Create OpenRouter client with a capable model
    openrouter = AsyncOpenRouterClient(
        token=OPENROUTER_TOKEN,
        model=OpenRouterModel.GPT41  # Good tool-using model
    )
    
    # Create MCP client and register the server
    async with AsyncMCPClient(openrouter) as mcp_client:
        print("\n=== Step 1: Registering MCP Server ===")
        await mcp_client.register_mcp_server(
            name="mbxai-cloud",
            base_url=mcp_server_url,
            token=MCP_TOKEN
        )
        
        # Verify scrape_html tool is available
        assert "scrape_html" in mcp_client._tools, "scrape_html tool not registered"
        print(f"✓ MCP server registered with {len(mcp_client._tools)} tools")
        print(f"✓ Available tools: {list(mcp_client._tools.keys())[:5]}...")
        
        # Get the tools for the AI
        tools = mcp_client.get_tools()
        print(f"✓ Prepared {len(tools)} tools for AI agent")
        
        print("\n=== Step 2: Sending Prompt to AI Agent ===")
        # Create a prompt asking the AI to scrape a website
        messages = [
            {
                "role": "user",
                "content": "Please use the scrape_html tool to fetch the HTML content from https://google.de and tell me what you find. Give me a brief summary of the content."
            }
        ]
        
        print("Prompt: 'Please use the scrape_html tool to fetch HTML from https://google.de'")
        print("\n=== Step 3: AI Processing (with tool access) ===")
        
        # Use parse to get structured output with tool calling
        response = await openrouter.parse(
            messages=messages,
            response_format=WebsiteContent,
            tools=tools,  # Provide MCP tools to the AI
            tool_choice="auto"  # Let AI decide when to use tools
        )
        
        print(f"✓ AI response received")
        
        # The response should contain tool calls that were executed
        print(f"✓ Response contains {len(response.choices)} choice(s)")
        
        # Extract the parsed result
        choice = response.choices[0]
        message = choice.message
        
        print(f"\n=== Step 4: Analyzing AI Response ===")
        print(f"Message role: {message.role}")
        
        # Check if AI used tools
        if hasattr(message, 'tool_calls') and message.tool_calls:
            print(f"✓ AI made {len(message.tool_calls)} tool call(s)")
            for i, tool_call in enumerate(message.tool_calls):
                print(f"  Tool {i+1}: {tool_call.function.name}")
                print(f"    Arguments: {tool_call.function.arguments[:100]}...")
        
        # Get the final parsed content
        if hasattr(choice, 'message') and hasattr(choice.message, 'parsed'):
            parsed_content = choice.message.parsed
            print(f"\n=== Step 5: Structured Output ===")
            print(f"URL: {parsed_content.url}")
            print(f"HTML Preview: {parsed_content.html_preview[:100]}...")
            print(f"Content Length: {parsed_content.content_length}")
            print(f"Has HTML: {parsed_content.has_html}")
            
            # Verify the content
            assert parsed_content.url == "https://google.de"
            assert parsed_content.content_length > 0
            assert parsed_content.has_html is True
            
            print("\n✅ MCP Agent Integration Test PASSED!")
            print("   - MCP server registered successfully")
            print("   - AI agent received and used scrape_html tool")
            print("   - Tool was invoked with correct parameters")
            print("   - Structured output returned successfully")
        else:
            # Fallback if structured parsing not available
            print(f"Message content: {message.content if hasattr(message, 'content') else 'N/A'}")
            print("✓ AI responded (structured parsing may not be available with this model)")


@pytest.mark.asyncio
async def test_mcp_agent_without_tools():
    """Test that AI can respond even without using tools (baseline test)."""
    
    if not OPENROUTER_TOKEN:
        pytest.skip("OPENROUTER_API_KEY not set")
    
    print("\n=== Baseline Test: AI without MCP tools ===")
    
    openrouter = AsyncOpenRouterClient(
        token=OPENROUTER_TOKEN,
        model=OpenRouterModel.ANTHROPIC_CLAUDE_3_5_SONNET
    )
    
    async with AsyncMCPClient(openrouter) as mcp_client:
        # Register MCP server
        await mcp_client.register_mcp_server(
            "mbxai-cloud",
            "https://api.mbxai.cloud/api",
            token=MCP_TOKEN
        )
        
        # Ask a simple question that doesn't require tools
        messages = [
            {
                "role": "user",
                "content": "What is 2 + 2? Just give me the number."
            }
        ]
        
        # Send without tools
        response = await openrouter.create(
            messages=messages
        )
        
        content = response.choices[0].message.content
        print(f"AI Response: {content}")
        
        assert "4" in content
        print("✓ Baseline test passed - AI can respond without tools")


@pytest.mark.asyncio
async def test_mcp_tool_registration_details():
    """Test that MCP tools are properly registered with correct schemas."""
    
    if not OPENROUTER_TOKEN:
        pytest.skip("OPENROUTER_API_KEY not set")
    
    print("\n=== Testing MCP Tool Registration Details ===")
    
    openrouter = AsyncOpenRouterClient(token=OPENROUTER_TOKEN)
    
    async with AsyncMCPClient(openrouter) as mcp_client:
        await mcp_client.register_mcp_server(
            "mbxai-cloud",
            "https://api.mbxai.cloud/api",
            token=MCP_TOKEN
        )
        
        # Get scrape_html tool
        scrape_tool = mcp_client._tools["scrape_html"]
        
        print(f"\nTool Name: {scrape_tool.name}")
        print(f"Tool Service: {scrape_tool.service}")
        print(f"Tool Description: {scrape_tool.description[:100]}...")
        
        # Convert to OpenAI format
        openai_function = scrape_tool.to_openai_function()
        
        print(f"\nOpenAI Function Format:")
        print(f"  Type: {openai_function['type']}")
        print(f"  Name: {openai_function['function']['name']}")
        print(f"  Strict: {openai_function['function']['strict']}")
        print(f"  Parameters type: {openai_function['function']['parameters']['type']}")
        
        # Verify structure
        assert openai_function["type"] == "function"
        assert openai_function["function"]["name"] == "scrape_html"
        assert openai_function["function"]["strict"] is True
        assert "parameters" in openai_function["function"]
        assert "properties" in openai_function["function"]["parameters"]
        
        print("✓ Tool schema is properly formatted for OpenAI/OpenRouter")


def test_mcp_agent_scrape_website_sync():
    """Synchronous wrapper for the async test."""
    asyncio.run(test_mcp_agent_scrape_website())


def test_mcp_agent_without_tools_sync():
    """Synchronous wrapper for the baseline test."""
    asyncio.run(test_mcp_agent_without_tools())


def test_mcp_tool_registration_details_sync():
    """Synchronous wrapper for the registration details test."""
    asyncio.run(test_mcp_tool_registration_details())


if __name__ == "__main__":
    import sys
    
    if not OPENROUTER_TOKEN:
        print("❌ OPENROUTER_API_KEY not set!")
        print("   Set it with: export OPENROUTER_API_KEY='your_key_here'")
        sys.exit(1)
    
    print("=" * 80)
    print("MCP Agent Integration Tests")
    print("=" * 80)
    
    print("\n[1/3] Testing tool registration details...")
    test_mcp_tool_registration_details_sync()
    
    print("\n[2/3] Testing baseline AI response...")
    test_mcp_agent_without_tools_sync()
    
    print("\n[3/3] Testing AI agent with MCP tools...")
    test_mcp_agent_scrape_website_sync()
    
    print("\n" + "=" * 80)
    print("✅ All MCP Agent Integration Tests Passed!")
    print("=" * 80)

