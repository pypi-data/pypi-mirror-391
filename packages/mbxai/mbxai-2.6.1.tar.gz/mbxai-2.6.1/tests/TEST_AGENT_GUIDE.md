# MCP Agent Integration Test Guide

## Overview

The `test_mcp_agent_integration.py` file demonstrates the **complete AI agent workflow** using MCP tools with OpenRouter.

## What This Test Does

```
┌─────────────────────────────────────────────────────────────┐
│ 1. User sends prompt: "Scrape https://google.de"            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. AI Agent (Claude/GPT) receives:                          │
│    - User prompt                                            │
│    - Available MCP tools (scrape_html, etc.)                │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. AI decides to use scrape_html tool                       │
│    - Generates tool call with correct parameters            │
│    - Arguments: {"input": {"url": "https://google.de"}}     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. MCP Client invokes tool via JSON-RPC 2.0                 │
│    - POST to https://api.mbxai.cloud/api/mcp                │
│    - Method: "tools/call"                                   │
│    - Authentication: Bearer token                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Tool executes and returns HTML content                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. AI processes result and returns structured output        │
│    - WebsiteContent model with url, html_preview, etc.      │
└─────────────────────────────────────────────────────────────┘
```

## Setup

### 1. Set Required Environment Variables

```bash
# MCP API Token (for MCP server authentication)
export MBXAI_API_TOKEN="ui-full-access-16b40d85eaf028624104a03c8b297536"

# OpenRouter API Key (for AI agent)
export OPENROUTER_API_KEY="your_openrouter_key_here"
```

Get your OpenRouter key from: https://openrouter.ai/keys

### 2. Install Dependencies

```bash
cd /Users/mikebertram/projects/mibexx/mbxai/packages
uv sync
```

## Running the Tests

### Run All Agent Tests

```bash
uv run pytest tests/test_mcp_agent_integration.py -v -s
```

### Run Individual Tests

```bash
# Test full AI agent with MCP tools
uv run pytest tests/test_mcp_agent_integration.py::test_mcp_agent_scrape_website -v -s

# Test tool registration
uv run pytest tests/test_mcp_agent_integration.py::test_mcp_tool_registration_details -v -s

# Test baseline (AI without tools)
uv run pytest tests/test_mcp_agent_integration.py::test_mcp_agent_without_tools -v -s
```

### Run as Standalone Script

```bash
cd tests
python test_mcp_agent_integration.py
```

## Test Breakdown

### Test 1: `test_mcp_agent_scrape_website` 🤖

**Full AI Agent Workflow**

This is the main test that demonstrates the complete integration:

```python
# 1. Register MCP server with tools
await mcp_client.register_mcp_server("mbxai-cloud", url, token=MCP_TOKEN)

# 2. Get tools for AI
tools = mcp_client.get_tools()

# 3. AI agent uses tools automatically
response = await openrouter.parse(
    messages=[{"role": "user", "content": "Scrape https://google.de"}],
    response_format=WebsiteContent,
    tools=tools,  # MCP tools available to AI
    tool_choice="auto"  # AI decides when to use tools
)

# 4. Get structured result
result = response.choices[0].message.parsed
```

**What Gets Tested:**
- ✅ MCP server registration with authentication
- ✅ Tool discovery and registration
- ✅ AI receiving available tools
- ✅ AI deciding to use the correct tool
- ✅ Tool invocation via JSON-RPC 2.0
- ✅ Result processing and structured output

### Test 2: `test_mcp_tool_registration_details` 🔍

**Validates Tool Schema**

Tests that MCP tools are properly converted to OpenAI function format:

```python
openai_function = scrape_tool.to_openai_function()
# Returns:
{
  "type": "function",
  "function": {
    "name": "scrape_html",
    "description": "Scrape HTML content from a URL...",
    "parameters": {...},
    "strict": true
  }
}
```

### Test 3: `test_mcp_agent_without_tools` ⚡

**Baseline Test**

Verifies the AI can still respond to simple queries without needing tools.

## Expected Output

### Successful Test Output

```
================================================================================
MCP Agent Integration Test - AI Using scrape_html Tool
================================================================================

=== Step 1: Registering MCP Server ===
✓ MCP server registered with 8 tools
✓ Available tools: ['analyze_html', 'scrape_html', 'generate_image', ...]
✓ Prepared 8 tools for AI agent

=== Step 2: Sending Prompt to AI Agent ===
Prompt: 'Please use the scrape_html tool to fetch HTML from https://google.de'

=== Step 3: AI Processing (with tool access) ===
✓ AI response received
✓ Response contains 1 choice(s)

=== Step 4: Analyzing AI Response ===
Message role: assistant
✓ AI made 1 tool call(s)
  Tool 1: scrape_html
    Arguments: {"input": {"url": "https://google.de"}}

=== Step 5: Structured Output ===
URL: https://google.de
HTML Preview: <!DOCTYPE html><html>...
Content Length: 15234
Has HTML: True

✅ MCP Agent Integration Test PASSED!
   - MCP server registered successfully
   - AI agent received and used scrape_html tool
   - Tool was invoked with correct parameters
   - Structured output returned successfully
```

## Key Features Demonstrated

### 1. Authentication 🔐
```python
await mcp_client.register_mcp_server(
    name="mbxai-cloud",
    base_url="https://api.mbxai.cloud/api",
    token="ui-full-access-16b40d85eaf028624104a03c8b297536"
)
```

### 2. Tool Discovery 🔍
```python
tools = mcp_client.get_tools()
# Returns list of OpenAI-formatted function definitions
```

### 3. AI Tool Usage 🤖
```python
response = await openrouter.parse(
    messages=messages,
    response_format=WebsiteContent,  # Structured output
    tools=tools,  # MCP tools
    tool_choice="auto"  # AI decides
)
```

### 4. Structured Output 📊
```python
class WebsiteContent(BaseModel):
    url: str
    html_preview: str
    content_length: int
    has_html: bool

# AI returns validated structured data
```

## Troubleshooting

### "OPENROUTER_API_KEY not set"

```bash
export OPENROUTER_API_KEY="sk-or-v1-..."
```

Get a key from: https://openrouter.ai/keys

### "Authorization token is required"

```bash
export MBXAI_API_TOKEN="ui-full-access-16b40d85eaf028624104a03c8b297536"
```

### "AI didn't use the tool"

Some AI models are better at tool usage than others. The test uses:
- Claude 3.5 Sonnet (recommended)
- GPT-4 (good alternative)

Make sure the prompt is clear about using the tool.

### "Test skipped"

If OpenRouter key is not set, the test will be skipped:
```
SKIPPED - OPENROUTER_API_KEY not set
```

## Integration with Your Application

### Example: Building an AI Agent with MCP Tools

```python
import os
from mbxai.mcp import AsyncMCPClient
from mbxai.openrouter import AsyncOpenRouterClient, OpenRouterModel
from pydantic import BaseModel

# Setup
mcp_token = os.getenv("MBXAI_API_TOKEN")
openrouter_token = os.getenv("OPENROUTER_API_KEY")

# Create clients
openrouter = AsyncOpenRouterClient(
    token=openrouter_token,
    model=OpenRouterModel.ANTHROPIC_CLAUDE_3_5_SONNET
)

async with AsyncMCPClient(openrouter) as mcp_client:
    # Register your MCP servers
    await mcp_client.register_mcp_server(
        "mbxai-cloud",
        "https://api.mbxai.cloud/api",
        token=mcp_token
    )
    
    # Get available tools
    tools = mcp_client.get_tools()
    
    # Create a conversation
    messages = [
        {"role": "system", "content": "You are a helpful assistant with access to tools."},
        {"role": "user", "content": "Scrape the HTML from https://example.com and summarize it"}
    ]
    
    # AI agent automatically uses tools as needed
    response = await openrouter.create(
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    
    # Process response
    assistant_message = response.choices[0].message
    print(assistant_message.content)
```

## Best Practices

1. **Always set environment variables** - Don't hardcode API keys
2. **Use structured output** - Leverage Pydantic models with `parse()`
3. **Let AI decide** - Use `tool_choice="auto"` for natural behavior
4. **Handle tool errors** - AI will see tool errors and can retry
5. **Monitor token usage** - Tool calls consume additional tokens

## Learn More

- **MCP Documentation**: `MCP_INTEGRATION_SUMMARY.md`
- **Tool Call Tests**: `test_mcp_tool_call.py`
- **Integration Tests**: `test_mcp_jsonrpc_integration.py`

---

**Questions?** Check the main MCP integration documentation or examine the test code for detailed examples.

