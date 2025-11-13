# MBX AI

A comprehensive Python library for building intelligent AI applications with Large Language Models (LLMs), structured responses, tool integration, and agent-based thinking.

## 🚀 Features

- **🔗 Multiple AI Client Types**: OpenRouter integration with tool-enabled and MCP-enabled variants
- **🤖 Enhanced Agent System**: 6-step intelligent process with human-in-the-loop, task management, and goal evaluation
- **💾 Pluggable Session Storage**: Custom session handlers (Redis, Database, File System) for scalable, distributed sessions
- **🛠️ Tool Integration**: Easy function registration with automatic schema generation
- **🔌 MCP Support**: Full Model Context Protocol (MCP) client and server implementation
- **📋 Structured Responses**: Type-safe responses using Pydantic models
- **🔄 Quality Iteration**: Built-in response improvement through AI-powered quality checks
- **💬 Conversation Memory**: Persistent dialog sessions with history management
- **⚡ Automatic Retry**: Built-in retry logic with exponential backoff for robust connections

## 📦 Installation

```bash
pip install mbxai
```

## 🏗️ Architecture Overview

MBX AI provides five main client types, each building upon the previous, available in both sync and async versions:

1. **OpenRouterClient / AsyncOpenRouterClient** - Basic LLM interactions with structured responses
2. **ToolClient / AsyncToolClient** - Adds function calling capabilities
3. **MCPClient / AsyncMCPClient** - Adds Model Context Protocol server integration
4. **AgentClient / AsyncAgentClient** - Adds intelligent dialog-based thinking (wraps any of the above)
5. **AsyncImageClient** - Specialized image generation and editing capabilities

| Client | Structured Responses | Function Calling | MCP Integration | Agent Thinking | Image Operations | Async Support |
|--------|---------------------|------------------|-----------------|----------------|------------------|---------------|
| OpenRouterClient | ✅ | ❌ | ❌ | ❌ | ❌ | Sync + Async |
| ToolClient | ✅ | ✅ | ❌ | ❌ | ❌ | Sync + Async |
| MCPClient | ✅ | ✅ | ✅ | ❌ | ❌ | Sync + Async |
| AgentClient | ✅ | ✅* | ✅* | ✅ | ❌ | Sync + Async |
| AsyncImageClient | ❌ | ❌ | ❌ | ❌ | ✅ | Async Only |

*AgentClient capabilities depend on the wrapped client

## 🚀 Quick Start

### Basic OpenRouter Client

```python
import os
from mbxai import OpenRouterClient
from pydantic import BaseModel, Field

# Initialize client
client = OpenRouterClient(token=os.getenv("OPENROUTER_API_KEY"))

# Simple chat
response = client.create([
    {"role": "user", "content": "What is the capital of France?"}
])
print(response.choices[0].message.content)

# Structured response
class CityInfo(BaseModel):
    name: str = Field(description="City name")
    population: int = Field(description="Population count")
    country: str = Field(description="Country name")

response = client.parse(
    messages=[{"role": "user", "content": "Tell me about Paris"}],
    response_format=CityInfo
)
city = response.choices[0].message.parsed
print(f"{city.name}, {city.country} - Population: {city.population:,}")
```

### Tool Client with Automatic Schema Generation

```python
import os
from mbxai import ToolClient, OpenRouterClient

# Initialize clients
openrouter_client = OpenRouterClient(token=os.getenv("OPENROUTER_API_KEY"))
tool_client = ToolClient(openrouter_client)

# Define a function - schema is auto-generated!
def get_weather(location: str, unit: str = "celsius") -> dict:
    """Get weather information for a location.
    
    Args:
        location: The city or location name
        unit: Temperature unit (celsius or fahrenheit)
    """
    return {
        "location": location,
        "temperature": 22,
        "unit": unit,
        "condition": "Sunny"
    }

# Register tool (schema automatically generated from function signature)
tool_client.register_tool(
    name="get_weather",
    description="Get current weather for a location",
    function=get_weather
    # No schema needed - automatically generated!
)

# Use the tool
response = tool_client.chat([
    {"role": "user", "content": "What's the weather like in Tokyo?"}
])
print(response.choices[0].message.content)
```

### MCP Client for Server Integration

```python
import os
from mbxai import MCPClient, OpenRouterClient

# Initialize MCP client
openrouter_client = OpenRouterClient(token=os.getenv("OPENROUTER_API_KEY"))
mcp_client = MCPClient(openrouter_client)

# Register MCP server (automatically loads all tools)
mcp_client.register_mcp_server("data-analysis", "http://localhost:8000")

# Chat with MCP tools available
response = mcp_client.chat([
    {"role": "user", "content": "Analyze the sales data from the server"}
])
print(response.choices[0].message.content)
```

### Async Image Client for Generation and Editing

```python
import os
import asyncio
from mbxai import AsyncImageClient

async def main():
    # Initialize image client
    image_client = AsyncImageClient(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Generate an image
    response = await image_client.generate(
        prompt="A futuristic cityscape with flying cars at sunset",
        size="1024x1024",
        quality="hd",
        model="gpt-image-1"
    )
    
    if response.success:
        print(f"Generated image: {response.image_url}")
    else:
        print(f"Generation failed: {response.error}")
    
    # Edit an image with a mask
    edit_response = await image_client.edit(
        prompt="Add a rainbow in the sky",
        images=["https://example.com/cityscape.jpg"],  # URL or base64
        mask="",  # Optional mask for selective editing
        size="1024x1024",
        model="gpt-image-1"
    )
    
    if edit_response.success:
        print(f"Edited image: {edit_response.image_url}")
    else:
        print(f"Edit failed: {edit_response.error}")

asyncio.run(main())
```

### Enhanced Agent Client - 6-Step Intelligent Process

The AgentClient provides a structured 6-step process: requirement analysis, tool analysis, todo generation, task execution, human-in-the-loop interactions, and goal evaluation.

```python
import os
from mbxai import AgentClient, OpenRouterClient
from mbxai.agent.models import DialogOption, HumanInLoopResponse, HumanInteractionType
from pydantic import BaseModel, Field

class ProjectPlan(BaseModel):
    project_name: str = Field(description="Name of the project")
    technologies: list[str] = Field(description="Technologies to be used")
    phases: list[str] = Field(description="Project phases")
    estimated_duration: str = Field(description="Estimated duration")

# Basic usage without human-in-the-loop
openrouter_client = OpenRouterClient(token=os.getenv("OPENROUTER_API_KEY"))
agent = AgentClient(openrouter_client, human_in_loop=False)

response = agent.agent(
    "Create a project plan for a React web application",
    final_response_structure=ProjectPlan
)

print(f"Agent State: {response.state}")
if response.requirement_analysis:
    print(f"Goal: {response.requirement_analysis.goal}")
    print(f"Complexity: {response.requirement_analysis.complexity_estimate}/10")

if response.todo_list:
    print(f"Generated {len(response.todo_list.tasks)} tasks:")
    for task in response.todo_list.tasks:
        print(f"  - {task.title} (Status: {task.status.value})")

if response.is_complete():
    plan = response.final_response
    print(f"Project: {plan.project_name}")
    print(f"Technologies: {', '.join(plan.technologies)}")
```

### Human-in-the-Loop Agent

```python
# Define dialog options for UI-aware authentication flows
# These don't execute functions directly - they provide structured 
# communication patterns that the UI can handle

dialog_options = [
    DialogOption(
        id="jira_auth",
        title="Jira Authentication", 
        description="Authenticate with Atlassian Jira",
        # No function - this is handled by the UI
        parameters={"jira_url": "https://company.atlassian.net"}
    ),
    DialogOption(
        id="github_auth",
        title="GitHub Authentication",
        description="Authenticate with GitHub",
        parameters={"scopes": ["repo", "user"]}
    ),
    DialogOption(
        id="approval_request",
        title="Deployment Approval",
        description="Request approval for production deployment",
        parameters={"environment": "production", "risk_level": "medium"}
    )
]

# Initialize agent with human-in-the-loop
agent = AgentClient(
    openrouter_client,
    human_in_loop=True,
    dialog_options=dialog_options,
    max_task_iterations=10
)

# Start task that requires authentication
response = agent.agent(
    "Create a summary of the Jira story PROJ-123 from https://company.atlassian.net",
    final_response_structure=ProjectPlan
)

# Handle human interactions
while not response.is_complete():
    if response.needs_human_interaction():
        request = response.human_interaction_request
        print(f"Human input needed: {request.prompt}")
        
        if request.interaction_type == HumanInteractionType.DECISION:
            # Present options and get user choice
            print(f"Options: {', '.join(request.options)}")
            user_choice = "proceed"  # Simulate user input
            
            human_response = HumanInLoopResponse(
                interaction_id=request.id,
                response_type=HumanInteractionType.DECISION,
                decision=user_choice
            )
            
        elif request.interaction_type == HumanInteractionType.QUESTION:
            # Get user answer
            user_answer = "Use AWS for deployment"  # Simulate user input
            
            human_response = HumanInLoopResponse(
                interaction_id=request.id,
                response_type=HumanInteractionType.QUESTION,
                answer=user_answer
            )
            
        elif request.interaction_type == HumanInteractionType.DIALOG_OPTION:
            # UI presents structured authentication dialog
            # User sees "Login to Atlassian" button, completes OAuth flow
            # UI receives auth token and sends it back to agent
            
            # Simulate UI completing authentication
            auth_token = "oauth_token_abc123"  # Retrieved by UI from OAuth flow
            
            human_response = HumanInLoopResponse(
                interaction_id=request.id,
                response_type=HumanInteractionType.DIALOG_OPTION,
                dialog_option_id="jira_auth",
                additional_context=f"auth_token:{auth_token}"
            )
        
        # Continue with human response
        response = agent.agent(
            "Continue with user input",
            final_response_structure=ProjectPlan,
            agent_id=response.agent_id,
            human_response=human_response
        )
else:
        # Continue execution
        response = agent.agent(
            "Continue processing",
            final_response_structure=ProjectPlan,
            agent_id=response.agent_id
        )

# Final result
if response.is_complete():
    plan = response.final_response
    print(f"✅ Project completed: {plan.project_name}")
    
    if response.goal_evaluation:
        print(f"Goal Achievement: {response.goal_evaluation.completion_percentage}%")
        print(f"Feedback: {response.goal_evaluation.feedback}")
```

### Agent with Tool Integration

```python
from mbxai import AgentClient, ToolClient, OpenRouterClient

# Setup tool-enabled agent
openrouter_client = OpenRouterClient(token=os.getenv("OPENROUTER_API_KEY"))
tool_client = ToolClient(openrouter_client)
agent = AgentClient(tool_client)

# Register tools via agent (proxy method)
def search_flights(origin: str, destination: str, date: str) -> dict:
    """Search for flights between cities."""
    return {
        "flights": [
            {"airline": "Example Air", "price": "$450", "duration": "3h 15m"}
        ]
    }

agent.register_tool(
    name="search_flights",
    description="Search for flights between cities",
    function=search_flights
)

# Agent automatically uses tools when needed
class FlightInfo(BaseModel):
    flights: list[dict] = Field(description="Available flights")
    recommendation: str = Field(description="Flight recommendation")

response = agent.agent(
    prompt="Find flights from New York to Los Angeles for tomorrow",
    final_response_structure=FlightInfo,
    ask_questions=False
)

flight_info = response.final_response
print(f"Found {len(flight_info.flights)} flights")
print(f"Recommendation: {flight_info.recommendation}")
```

### New Models and Types

The enhanced agent client introduces several new models and types:

```python
# Import new agent models
from mbxai.agent.models import (
    Task, TodoList, TaskStatus,           # Task management
    DialogOption, HumanInLoopRequest,     # Human interactions  
    HumanInLoopResponse, HumanInteractionType,
    RequirementAnalysis, ToolAnalysis,    # Analysis models
    GoalEvaluation, AgentState,           # State management
    SessionHandler, InMemorySessionHandler, # Session storage
    TokenSummary, TokenUsage              # Token tracking
)

# Or import from main package
from mbxai import (
    Task, TodoList, DialogOption, HumanInLoopRequest,
    AgentState, TaskStatus, HumanInteractionType,
    SessionHandler, InMemorySessionHandler
)
```

## 📚 Detailed Documentation

### OpenRouterClient

The base client for OpenRouter API integration with structured response support.

#### Key Features:
- **Multiple Models**: Support for GPT-4, Claude, Llama, and other models via OpenRouter
- **Structured Responses**: Type-safe responses using Pydantic models
- **Retry Logic**: Automatic retry with exponential backoff
- **Error Handling**: Comprehensive error handling with detailed logging

#### Methods:
- `create()` - Basic chat completion
- `parse()` - Chat completion with structured response
- `acreate()` - Async basic chat completion
- `aparse()` - Async chat completion with structured response
- `chat()` - Alias for create method
- `achat()` - Async alias for acreate method

#### Configuration:
```python
client = OpenRouterClient(
    token="your-api-key",
    model="openai/gpt-4-turbo",  # or use OpenRouterModel enum
    max_retries=3,
    retry_initial_delay=1.0,
    retry_max_delay=10.0
)
```

### ToolClient

Extends OpenRouterClient with function calling capabilities.

#### Key Features:
- **Automatic Schema Generation**: Generate JSON schemas from Python function signatures
- **Tool Registration**: Simple function registration
- **Tool Execution**: Automatic tool calling and response handling
- **Error Recovery**: Graceful handling of tool execution errors

#### Methods:
- `chat()` - Chat completion with tool calling
- `parse()` - Parse completion with tool calling
- `achat()` - Async chat completion with tool calling
- `aparse()` - Async parse completion with tool calling
- `acreate()` - Async alias for achat method

#### Usage:
```python
tool_client = ToolClient(openrouter_client)

# Register with automatic schema
tool_client.register_tool("function_name", "description", function)

# Register with custom schema
tool_client.register_tool("function_name", "description", function, custom_schema)

# Async usage
response = await tool_client.achat([
    {"role": "user", "content": "What's the weather like in Tokyo?"}
])
```

### MCPClient

Extends ToolClient with Model Context Protocol (MCP) server integration.

#### Key Features:
- **MCP Server Integration**: Connect to MCP servers and load their tools
- **Tool Discovery**: Automatically discover and register tools from MCP servers
- **HTTP Client Management**: Built-in HTTP client for MCP communication
- **Schema Conversion**: Convert MCP schemas to OpenAI function format

#### Methods:
- Inherits all ToolClient methods (chat, parse, achat, aparse, acreate)
- `register_mcp_server()` - Register MCP server and load tools
- `aregister_mcp_server()` - Async register MCP server and load tools

#### Usage:
```python
mcp_client = MCPClient(openrouter_client)
mcp_client.register_mcp_server("server-name", "http://localhost:8000")

# Async server registration
await mcp_client.aregister_mcp_server("server-name", "http://localhost:8000")

# Async context manager
async with mcp_client:
    response = await mcp_client.achat([
        {"role": "user", "content": "Analyze the sales data from the server"}
    ])
```

### AsyncImageClient

Specialized async client for image generation and editing operations using OpenAI's image models.

#### Key Features:
- **Image Generation**: Create images from text prompts with support for reference images
- **Image Editing**: Edit existing images with optional masks for selective modifications
- **Multiple Models**: Support for gpt-image-1 (default) and dall-e-3
- **Flexible Input**: Accept both URLs and base64-encoded images
- **Quality Control**: Configurable image size and quality settings
- **Async-Only**: Optimized for non-blocking operations

#### Methods:
- `generate()` - Generate images from text prompts
- `edit()` - Edit existing images with prompts and optional masks

#### Usage:
```python
from mbxai import AsyncImageClient
import asyncio

async def main():
    image_client = AsyncImageClient(api_key="your-openai-api-key")
    
    # Generate an image
    response = await image_client.generate(
        prompt="A futuristic robot in a cyberpunk city",
        size="1024x1024",
        quality="hd",
        model="gpt-image-1"
    )
    
    if response.success:
        print(f"Generated: {response.image_url}")
    
    # Edit an image
    edit_response = await image_client.edit(
        prompt="Add neon lights and rain",
        images=["https://example.com/robot.jpg"],
        size="1024x1024"
    )
    
    if edit_response.success:
        print(f"Edited: {edit_response.image_url}")

asyncio.run(main())
```

### Enhanced AgentClient

Wraps any client with a structured 6-step intelligent process and human-in-the-loop capabilities.

#### Key Features:
- **6-Step Process**: Requirement analysis → Tool analysis → Todo generation → Task execution → Human interaction → Goal evaluation
- **Human-in-the-Loop**: Support for decisions, questions, and custom dialog options
- **Task Management**: Intelligent todo list generation with dependencies and complexity assessment
- **Goal Evaluation**: Automatic assessment of goal achievement with feedback
- **Conversation Memory**: Maintains full conversation history and context
- **Tool Integration**: Seamlessly works with any underlying client (OpenRouter, Tool, MCP)
- **Async Support**: Full async/await support for non-blocking operation

#### Configuration Options:
```python
from mbxai import AgentClient, InMemorySessionHandler

agent = AgentClient(
    ai_client=any_supported_client,
    human_in_loop=False,              # Enable human-in-the-loop
    dialog_options=[],                # Custom dialog options
    max_task_iterations=10,           # Max task execution cycles
    session_handler=InMemorySessionHandler()  # Session storage (optional)
)
```

**Session Storage Options:**
- **InMemorySessionHandler** (default): Single-instance memory storage
- **Custom handlers**: Redis, Database, File System for distributed/persistent sessions

#### The 6-Step Process:
1. **Requirement Analysis**: Understand goals, success criteria, constraints, and complexity
2. **Tool Analysis**: Map available tools to goals, identify missing capabilities
3. **Todo Generation**: Create specific, actionable tasks with dependencies
4. **Task Execution**: Execute tasks step-by-step with status tracking
5. **Human Interaction**: Dialog for decisions, questions, or custom actions (if enabled)
6. **Goal Evaluation**: Assess achievement, provide feedback, generate new todos if needed

#### Human Interaction Types:
- **DECISION**: Multiple choice with predefined options
- **QUESTION**: Free-text input for clarification  
- **DIALOG_OPTION**: Structured UI-aware communication patterns (authentication, integrations, etc.)

#### Tools vs Dialog Options:
- **Tools**: Functions the agent executes directly (fetch data, generate documents, setup systems)
- **Dialog Options**: Structured human-in-the-loop patterns that the UI can handle (authentication flows, approvals, integrations)

#### New Response Properties:
```python
response = agent.agent("Create a web app", ProjectPlan)

# Enhanced state information
response.state                    # Current agent state
response.requirement_analysis     # Goal breakdown
response.tool_analysis           # Tool mapping
response.todo_list               # Generated tasks
response.current_task            # Currently executing task
response.human_interaction_request # Human input needed
response.goal_evaluation         # Achievement assessment

# Check states
response.is_complete()           # Final response ready
response.needs_human_interaction() # Human input required
response.is_waiting_for_human()  # Waiting for human response
```

#### Session Management:
```python
# List active sessions
sessions = agent.list_sessions()

# Get session info
info = agent.get_session_info(agent_id)

# Delete session
agent.delete_session(agent_id)
```

## ⚡ Async/Await Support

All clients are available in both synchronous and asynchronous versions for non-blocking execution. The async clients are separate classes with the same method names but async-only implementations:

### Async OpenRouter Client

```python
import asyncio
from mbxai import AsyncOpenRouterClient
from pydantic import BaseModel, Field

async def main():
    client = AsyncOpenRouterClient(token=os.getenv("OPENROUTER_API_KEY"))
    
    # Async chat completion
    response = await client.create([
        {"role": "user", "content": "What is the capital of France?"}
    ])
    print(response.choices[0].message.content)
    
    # Async structured response
    class CityInfo(BaseModel):
        name: str = Field(description="City name")
        population: int = Field(description="Population count")
        country: str = Field(description="Country name")

    response = await client.parse(
        messages=[{"role": "user", "content": "Tell me about Paris"}],
        response_format=CityInfo
    )
    city = response.choices[0].message.parsed
    print(f"{city.name}, {city.country} - Population: {city.population:,}")

asyncio.run(main())
```

### Async Tool Client

```python
import asyncio
from mbxai import AsyncToolClient, AsyncOpenRouterClient

async def get_weather_async(location: str, unit: str = "celsius") -> dict:
    """Async weather function."""
    # Simulate async API call
    await asyncio.sleep(0.1)
    return {
        "location": location,
        "temperature": 22,
        "unit": unit,
        "condition": "Sunny"
    }

async def main():
    openrouter_client = AsyncOpenRouterClient(token=os.getenv("OPENROUTER_API_KEY"))
    tool_client = AsyncToolClient(openrouter_client)
    
    # Register async tool
    tool_client.register_tool(
        name="get_weather_async",
        description="Get current weather for a location (async)",
        function=get_weather_async
    )
    
    # Async chat with tools
    response = await tool_client.chat([
        {"role": "user", "content": "What's the weather like in Tokyo?"}
    ])
    print(response.choices[0].message.content)

asyncio.run(main())
```

### Async MCP Client

```python
import asyncio
from mbxai import AsyncMCPClient, AsyncOpenRouterClient

async def main():
    openrouter_client = AsyncOpenRouterClient(token=os.getenv("OPENROUTER_API_KEY"))
    
    async with AsyncMCPClient(openrouter_client) as mcp_client:
        # Async MCP server registration
        await mcp_client.register_mcp_server("data-analysis", "http://localhost:8000")
        
        # Async chat with MCP tools
        response = await mcp_client.chat([
            {"role": "user", "content": "Analyze the sales data from the server"}
        ])
        print(response.choices[0].message.content)

asyncio.run(main())
```

### Async Agent Client

```python
import asyncio
from mbxai import AsyncAgentClient, AsyncOpenRouterClient
from pydantic import BaseModel, Field

class ProjectPlan(BaseModel):
    project_name: str = Field(description="Name of the project")
    technologies: list[str] = Field(description="Technologies to be used")
    phases: list[str] = Field(description="Project phases")
    estimated_duration: str = Field(description="Estimated duration")

async def main():
    openrouter_client = AsyncOpenRouterClient(token=os.getenv("OPENROUTER_API_KEY"))
    agent = AsyncAgentClient(openrouter_client, human_in_loop=False)
    
    # Async agent processing
    response = await agent.agent(
        "Create a project plan for a React web application",
        final_response_structure=ProjectPlan
    )
    
    print(f"Agent State: {response.state}")
    if response.is_complete():
        plan = response.final_response
        print(f"Project: {plan.project_name}")
        print(f"Technologies: {', '.join(plan.technologies)}")

asyncio.run(main())
```

### Async Human-in-the-Loop Agent

```python
import asyncio
from mbxai import AsyncAgentClient, AsyncOpenRouterClient
from mbxai.agent.models import HumanInLoopResponse, HumanInteractionType

async def handle_human_interaction(agent, response, project_plan_class):
    """Handle human interactions asynchronously."""
    while not response.is_complete():
        if response.needs_human_interaction():
            request = response.human_interaction_request
            print(f"Human input needed: {request.prompt}")
            
            # Simulate user input (in real app, this would come from UI)
            if request.interaction_type == HumanInteractionType.DECISION:
                user_choice = "proceed"  # Simulate user decision
                human_response = HumanInLoopResponse(
                    interaction_id=request.id,
                    response_type=HumanInteractionType.DECISION,
                    decision=user_choice
                )
            elif request.interaction_type == HumanInteractionType.QUESTION:
                user_answer = "Use AWS for deployment"  # Simulate user answer
                human_response = HumanInLoopResponse(
                    interaction_id=request.id,
                    response_type=HumanInteractionType.QUESTION,
                    answer=user_answer
                )
            
            # Continue with human response (async)
            response = await agent.agent(
                "Continue with user input",
                final_response_structure=project_plan_class,
                agent_id=response.agent_id,
                human_response=human_response
            )
        else:
            # Continue execution (async)
            response = await agent.agent(
                "Continue processing",
                final_response_structure=project_plan_class,
                agent_id=response.agent_id
            )
    
    return response

async def main():
    openrouter_client = AsyncOpenRouterClient(token=os.getenv("OPENROUTER_API_KEY"))
    agent = AsyncAgentClient(openrouter_client, human_in_loop=True)
    
    # Start async agent process
    response = await agent.agent(
        "Create a deployment plan for a microservices application",
        final_response_structure=ProjectPlan
    )
    
    # Handle interactions asynchronously
    final_response = await handle_human_interaction(agent, response, ProjectPlan)
    
    if final_response.is_complete():
        plan = final_response.final_response
        print(f"✅ Project completed: {plan.project_name}")

asyncio.run(main())
```

### Performance Benefits of Async

Async operations provide significant performance benefits, especially when:

- **Multiple concurrent requests**: Process multiple agent sessions simultaneously
- **I/O-bound operations**: Non-blocking HTTP calls to MCP servers, APIs, databases
- **Tool execution**: Async tools can run concurrently without blocking
- **Human interactions**: Handle multiple user sessions without blocking server threads
- **Scalability**: Support thousands of concurrent operations with minimal resources

```python
import asyncio
from mbxai import AsyncAgentClient, AsyncOpenRouterClient

async def process_user_request(user_id: str, prompt: str):
    """Process individual user request asynchronously."""
    openrouter_client = AsyncOpenRouterClient(token=os.getenv("OPENROUTER_API_KEY"))
    agent = AsyncAgentClient(openrouter_client)
    
    response = await agent.agent(prompt, ProjectPlan)
    return f"User {user_id}: {response.final_response.project_name}"

async def main():
    # Process 100 concurrent user requests
    tasks = [
        process_user_request(f"user_{i}", f"Create project plan {i}")
        for i in range(100)
    ]
    
    # All requests run concurrently
    results = await asyncio.gather(*tasks)
    
    for result in results:
        print(result)

asyncio.run(main())
```

## 🏃‍♂️ Advanced Examples

### Custom Model Registration

```python
from mbxai import OpenRouterClient, OpenRouterModel

# Register custom model
OpenRouterClient.register_model("CUSTOM_MODEL", "provider/model-name")

# Use custom model
client = OpenRouterClient(token="your-key", model="CUSTOM_MODEL")
```

### Enhanced Agent Session Continuation

```python
# Start a complex project
response1 = agent.agent(
    "Create a microservices architecture for an e-commerce platform", 
    final_response_structure=ProjectPlan
)
agent_id = response1.agent_id

# Continue with additional requirements
response2 = agent.agent(
    "Add authentication and payment processing to the architecture",
    final_response_structure=ProjectPlan,
    agent_id=agent_id  # Continues previous session
)

# The agent remembers the full context and builds upon previous work
print(f"Updated project: {response2.final_response.project_name}")
print(f"Goal achievement: {response2.goal_evaluation.completion_percentage}%")
```

### Complete Example: Jira Integration with Authentication

```python
from mbxai import AgentClient, ToolClient, OpenRouterClient
from mbxai.agent.models import DialogOption, HumanInLoopResponse, HumanInteractionType
from pydantic import BaseModel, Field

class JiraSummary(BaseModel):
    story_id: str = Field(description="Jira story ID")
    title: str = Field(description="Story title")
    description: str = Field(description="Story description")
    status: str = Field(description="Current status")
    assignee: str = Field(description="Assigned person")
    summary: str = Field(description="AI-generated summary")

# Tool for fetching Jira data (agent executes this)
def fetch_jira_story(story_id: str, jira_url: str, auth_token: str) -> dict:
    """Fetch a Jira story using the API."""
    # Your Jira API integration logic here
    return {
        "id": story_id,
        "title": "Implement user authentication",
        "description": "Add OAuth2 authentication to the application",
        "status": "In Progress",
        "assignee": "john.doe@company.com"
    }

# Dialog option for authentication (UI handles this)
dialog_options = [
    DialogOption(
        id="jira_auth",
        title="Jira Authentication",
        description="Authenticate with Atlassian Jira",
        # No function - this tells the UI to handle authentication
        parameters={
            "jira_url": "https://company.atlassian.net",
            "scopes": ["read:jira-work", "read:jira-user"]
        }
    )
]

# Setup agent with both tools and dialog options
openrouter_client = OpenRouterClient(token=os.getenv("OPENROUTER_API_KEY"))
tool_client = ToolClient(openrouter_client)
agent = AgentClient(
    tool_client,
    human_in_loop=True,
    dialog_options=dialog_options
)

# Register the Jira tool
agent.register_tool(
    name="fetch_jira_story",
    description="Fetch Jira story details using API",
    function=fetch_jira_story
)

# Agent process
response = agent.agent(
    "Create a summary of Jira story PROJ-123 from https://company.atlassian.net",
    final_response_structure=JiraSummary
)

# Handle authentication dialog
if response.needs_human_interaction():
    request = response.human_interaction_request
    
    if request.interaction_type == HumanInteractionType.DIALOG_OPTION:
        # UI shows "Login to Atlassian" button
        # User completes OAuth flow
        # UI receives auth token and sends it back
        
        auth_token = "oauth_token_from_ui"  # Provided by UI after OAuth
        
        human_response = HumanInLoopResponse(
            interaction_id=request.id,
            response_type=HumanInteractionType.DIALOG_OPTION,
            dialog_option_id="jira_auth",
            additional_context=f"auth_token:{auth_token}"
        )
        
        # Continue with authentication
        response = agent.agent(
            "Continue with Jira authentication",
            final_response_structure=JiraSummary,
            agent_id=response.agent_id,
            human_response=human_response
        )

# Now agent can use the auth token with the fetch_jira_story tool
if response.is_complete():
    summary = response.final_response
    print(f"Story: {summary.story_id} - {summary.title}")
    print(f"Status: {summary.status}")
    print(f"Summary: {summary.summary}")
```

### Key Distinction: Tools vs Dialog Options

This example demonstrates the important difference:

**Tools** (Agent-Executed Functions):
- Functions that the agent calls directly to perform tasks
- Examples: `fetch_jira_story`, `generate_document`, `setup_database`
- Executed server-side by the agent
- Used for data processing, API calls, system operations

**Dialog Options** (UI-Handled Patterns):
- Structured communication patterns that the UI can understand and handle
- Examples: `jira_auth`, `github_oauth`, `approval_request`
- NOT executed by the agent - they're instructions for the UI
- Used for authentication flows, user approvals, secure interactions
- Parameters help the UI know how to handle the interaction
- Responses provide the agent with the results (tokens, approvals, etc.)

**Benefits**:
- **Security**: No sensitive data (auth tokens) passed as plain text
- **User Experience**: UI can provide proper authentication flows, not just text input
- **Structured**: Both agent and UI know exactly what type of interaction is needed
- **Flexible**: UI can handle complex flows (OAuth, 2FA, file uploads) appropriately

### Multiple Human Interactions

For complex workflows requiring multiple human interactions, you can provide responses as a list:

```python
from mbxai.agent.models import HumanInLoopResponseBatch, HumanInLoopResponse, HumanInteractionType

# Multiple individual responses
responses = [
    HumanInLoopResponse(
        interaction_id="auth_req_1",
        response_type=HumanInteractionType.DIALOG_OPTION,
        dialog_option_id="github_auth",
        additional_context="auth_token:github_oauth_token_123"
    ),
    HumanInLoopResponse(
        interaction_id="approval_req_1", 
        response_type=HumanInteractionType.DECISION,
        decision="approve",
        additional_context="approved_by:john.doe@company.com"
    )
]

# Send multiple responses at once
response = agent.agent(
    prompt="Continue with multiple inputs",
    final_response_structure=ProjectPlan,
    agent_id=agent_id,
    human_response=responses  # List of responses
)

# Or use the batch model
response_batch = HumanInLoopResponseBatch(responses=responses)
response = agent.agent(
    prompt="Continue with batch input",
    final_response_structure=ProjectPlan,
    agent_id=agent_id,
    human_response=response_batch  # Batch object
)
```

This is particularly useful when:
- The agent requests multiple approvals simultaneously
- Complex workflows need multiple authentication steps
- Batch processing user decisions for efficiency

### Custom Session Handlers

The `AgentClient` supports pluggable session storage through the `SessionHandler` protocol. This enables distributed, persistent, and scalable session management.

#### Built-in Session Handlers

**InMemorySessionHandler (Default):**
```python
from mbxai import AgentClient, InMemorySessionHandler

# Default in-memory storage (single instance)
agent = AgentClient(ai_client, session_handler=InMemorySessionHandler())
```

**Custom Redis Session Handler:**
```python
import redis
from mbxai import AgentClient, SessionHandler
from typing import Dict, Any, Optional

class RedisSessionHandler:
    def __init__(self, redis_client: redis.Redis = None, ttl_seconds: int = 86400):
        self.redis_client = redis_client or redis.Redis()
        self.ttl_seconds = ttl_seconds
    
    def get_session(self, agent_id: str) -> Optional[Dict[str, Any]]:
        session_json = self.redis_client.get(f"agent:{agent_id}")
        return json.loads(session_json) if session_json else None
    
    def set_session(self, agent_id: str, session_data: Dict[str, Any]) -> None:
        session_json = json.dumps(session_data, default=str)
        self.redis_client.setex(f"agent:{agent_id}", self.ttl_seconds, session_json)
    
    def delete_session(self, agent_id: str) -> bool:
        return self.redis_client.delete(f"agent:{agent_id}") > 0
    
    def list_sessions(self) -> list[str]:
        keys = self.redis_client.keys("agent:*")
        return [key.decode().replace("agent:", "") for key in keys]
    
    def session_exists(self, agent_id: str) -> bool:
        return self.redis_client.exists(f"agent:{agent_id}") > 0

# Use Redis for distributed session storage
redis_handler = RedisSessionHandler(ttl_seconds=3600)  # 1 hour TTL
agent = AgentClient(ai_client, session_handler=redis_handler)
```

#### Benefits of Custom Session Handlers

- **Distributed**: Share sessions across multiple application instances
- **Persistent**: Sessions survive application restarts
- **Scalable**: Handle thousands of concurrent sessions
- **Flexible**: Database, file system, cloud storage integration
- **TTL Support**: Automatic session cleanup
- **High Availability**: Redis Sentinel/Cluster support

#### Production Setup Example

```python
from mbxai import AgentClient
import redis.sentinel

# Redis Sentinel for high availability
sentinels = [('sentinel1', 26379), ('sentinel2', 26379)]
sentinel = redis.sentinel.Sentinel(sentinels)
redis_client = sentinel.master_for('mymaster', decode_responses=True)

class ProductionRedisHandler:
    def __init__(self):
        self.redis_client = redis_client
        self.ttl_seconds = 24 * 60 * 60  # 24 hours
    
    # ... implement SessionHandler methods

# Production agent with Redis clustering
agent = AgentClient(
    ai_client=ai_client,
    session_handler=ProductionRedisHandler()
)
```

### Real-World Example: Separate UI and Agent Systems

This example shows how the UI and Agent run as separate services with their own endpoints:

**UI Service (FastAPI - Container 1):**
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
from typing import Optional

app = FastAPI()

# Models for UI service
class ChatMessage(BaseModel):
    message: str
    user_id: str

class AgentRequest(BaseModel):
    prompt: str
    final_response_structure: str = "OrderInfo"
    agent_id: Optional[str] = None
    human_response: Optional[dict] = None

class CredentialsForm(BaseModel):
    username: str
    password: str
    shop_url: str

# In-memory session storage (use Redis in production)
active_sessions = {}

@app.post("/chat")
async def chat_endpoint(message: ChatMessage):
    """Main chat endpoint for the UI"""
    
    # Send user message to Agent service
    agent_request = AgentRequest(
        prompt=message.message,
        final_response_structure="OrderInfo"
    )
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://agent-service:8001/agent",
            json=agent_request.dict()
        )
        agent_response = response.json()
    
    # Check if agent needs human interaction
    if agent_response.get("needs_human_interaction"):
        request = agent_response["human_interaction_request"]
        
        if request["interaction_type"] == "dialog_option" and request.get("dialog_option_id") == "shop_credentials":
            # Store session and ask user for credentials
            session_id = agent_response["agent_id"]
            active_sessions[session_id] = {
                "interaction_id": request["id"],
                "shop_url": request["parameters"]["shop_url"]
            }
            
            return {
                "type": "credentials_form",
                "message": "Please provide your shop credentials",
                "shop_url": request["parameters"]["shop_url"],
                "session_id": session_id
            }
    
    # Return final result if available
    if agent_response.get("is_complete"):
        order = agent_response["final_response"]
        return {
            "type": "order_result",
            "message": f"Your last order: #{order['order_number']} from {order['date']} (ID: {order['id']})"
        }
    
    return {"type": "message", "message": "Processing your request..."}

@app.post("/submit_credentials")
async def submit_credentials(credentials: CredentialsForm, session_id: str):
    """Handle user credentials submission"""
    
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    
    # Send credentials back to agent
    human_response = {
        "interaction_id": session["interaction_id"],
        "response_type": "dialog_option",
        "dialog_option_id": "shop_credentials",
        "additional_context": f"username:{credentials.username},password:{credentials.password}"
    }
    
    agent_request = AgentRequest(
        prompt="Continue with shop credentials",
        final_response_structure="OrderInfo",
        agent_id=session_id,
        human_response=human_response
    )
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://agent-service:8001/agent",
            json=agent_request.dict()
        )
        agent_response = response.json()
    
    # Clean up session
    del active_sessions[session_id]
    
    if agent_response.get("is_complete"):
        order = agent_response["final_response"]
        return {
            "type": "order_result",
            "message": f"Your last order: #{order['order_number']} from {order['date']} (ID: {order['id']})"
        }
    
    return {"type": "message", "message": "Processing your order request..."}
```

**Agent Service (FastAPI - Container 2):**
```python
from fastapi import FastAPI
from pydantic import BaseModel, Field
from mbxai import AgentClient, ToolClient, OpenRouterClient
from mbxai.agent.models import DialogOption, HumanInLoopResponse, HumanInteractionType
import os
from typing import Optional

app = FastAPI()

# Models for Agent service
class OrderInfo(BaseModel):
    id: str = Field(description="Order ID")
    order_number: str = Field(description="Order number")
    date: str = Field(description="Order date")

class AgentRequest(BaseModel):
    prompt: str
    final_response_structure: str
    agent_id: Optional[str] = None
    human_response: Optional[dict] = None

# Shop integration tool (agent executes this)
def list_orders_from_shop(username: str, password: str, shop_url: str) -> list:
    """Fetch orders from shop using credentials."""
    # Mock shop API call
    if username == "demo" and password == "demo123":
        return [
            {"id": "ord_001", "order_number": "ORD-2024-001", "date": "2024-01-15"},
            {"id": "ord_002", "order_number": "ORD-2024-002", "date": "2024-01-20"},
            {"id": "ord_003", "order_number": "ORD-2024-003", "date": "2024-01-25"}
        ]
    else:
        return []

# Dialog option for shop credentials (UI handles this)
dialog_options = [
    DialogOption(
        id="shop_credentials",
        title="Shop Credentials",
        description="Provide shop login credentials",
        parameters={"shop_url": "https://shop.example.com"}
    )
]

# Initialize agent
openrouter_client = OpenRouterClient(token=os.getenv("OPENROUTER_API_KEY"))
tool_client = ToolClient(openrouter_client)
agent = AgentClient(
    tool_client,
    human_in_loop=True,
    dialog_options=dialog_options
)

# Register the shop tool
agent.register_tool(
    name="list_orders_from_shop",
    description="List orders from online shop using user credentials",
    function=list_orders_from_shop
)

@app.post("/agent")
async def agent_endpoint(request: AgentRequest):
    """Main agent processing endpoint"""
    
    # Process human response if provided
    human_response = None
    if request.human_response:
        human_response = HumanInLoopResponse(
            interaction_id=request.human_response["interaction_id"],
            response_type=HumanInteractionType(request.human_response["response_type"]),
            dialog_option_id=request.human_response.get("dialog_option_id"),
            additional_context=request.human_response.get("additional_context", "")
        )
    
    # Call agent
    response = agent.agent(
        prompt=request.prompt,
        final_response_structure=OrderInfo,
        agent_id=request.agent_id,
        human_response=human_response
    )
    
    # Convert response to JSON-serializable format
    result = {
        "agent_id": response.agent_id,
        "state": response.state.value,
        "is_complete": response.is_complete(),
        "needs_human_interaction": response.needs_human_interaction()
    }
    
    if response.needs_human_interaction():
        request = response.human_interaction_request
        result["human_interaction_request"] = {
            "id": request.id,
            "interaction_type": request.interaction_type.value,
            "prompt": request.prompt,
            "dialog_option_id": "shop_credentials" if request.dialog_options else None,
            "parameters": {"shop_url": "https://shop.example.com"}
        }
    
    if response.is_complete():
        # Get the last order (most recent)
        order_data = response.final_response
        result["final_response"] = {
            "id": order_data.id,
            "order_number": order_data.order_number,
            "date": order_data.date
        }
    
    return result

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

**Flow Explanation:**

1. **User**: "Give me my last order from this online shop"
2. **UI**: Sends message to Agent service `/agent` endpoint
3. **Agent**: Analyzes request, realizes it needs shop credentials
4. **Agent**: Returns `needs_human_interaction=True` with `shop_credentials` dialog option
5. **UI**: Recognizes dialog option, shows credentials form to user
6. **User**: Enters username/password in UI form
7. **UI**: Sends credentials to Agent via `/agent` endpoint with `human_response`
8. **Agent**: Uses `list_orders_from_shop` tool with provided credentials
9. **Agent**: Returns last order information
10. **UI**: Displays order to user

**Key Points:**
- **Separation**: UI handles user interaction, Agent handles business logic
- **Security**: Credentials flow through structured dialog, not plain text
- **Scalability**: Services can be scaled independently
- **Flexibility**: UI can customize credential forms, Agent focuses on order processing

### Error Handling and Logging

```python
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

try:
    response = client.create(messages)
except OpenRouterAPIError as e:
    print(f"API Error: {e}")
except OpenRouterConnectionError as e:
    print(f"Connection Error: {e}")
except Exception as e:
    print(f"Unexpected Error: {e}")
```

### Streaming Responses

```python
# Streaming with OpenRouterClient
response = client.create(messages, stream=True)
for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")

# Streaming with ToolClient (tools execute before streaming)
response = tool_client.chat(messages, stream=True)
for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

## 🧪 Testing

Run the test suite:

```bash
# Install development dependencies using uv
uv sync

# Run tests with uv
uv run pytest tests/

# Run with coverage
uv run pytest tests/ --cov=mbxai --cov-report=html

# Test enhanced agent examples
uv run python src/mbxai/examples/enhanced_agent_example.py

# Test Redis session handler (requires Redis)
uv run python src/mbxai/examples/redis_session_handler_example.py
```

## 🔧 Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mbxai.git
cd mbxai/packages
```

2. Install using uv (recommended):
```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies and create virtual environment
uv sync

# Activate virtual environment (optional, uv run handles this automatically)
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Alternatively, use pip:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

4. Set up environment variables:
```bash
export OPENROUTER_API_KEY="your-api-key"
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🔗 Links

- **Homepage**: [https://www.mibexx.de](https://www.mibexx.de)
- **Documentation**: [https://www.mibexx.de](https://www.mibexx.de)
- **Repository**: [https://github.com/yourusername/mbxai](https://github.com/yourusername/mbxai)

## 📊 Version Information

Current version: **2.6.1**

### What's New in 2.6.1:
- **⚡ Async Client Architecture**: Complete async versions of all clients with separate classes
- **🖼️ AsyncImageClient**: New specialized client for image generation and editing with gpt-image-1 support
- **🔄 Dual API Support**: Both sync and async versions available for all major clients
- **🚀 Performance Optimized**: True async/await patterns for non-blocking operations
- **📦 Clean Separation**: Async clients are separate classes maintaining API consistency

### What's New in 2.6.1:
- **🎯 Enhanced Agent Client**: Complete rewrite with 6-step intelligent process
- **💾 Pluggable Session Storage**: Custom session handlers for Redis, Database, File System
- **👤 Human-in-the-Loop**: Interactive decision making, questions, and custom dialog options
- **📋 Task Management**: Intelligent todo list generation with dependencies and status tracking
- **🎯 Goal Evaluation**: Automatic assessment of goal achievement with iterative improvement
- **🔧 Dialog Options**: Custom functions for authentication, integrations, and workflows
- **📊 Enhanced State Management**: Full visibility into agent process and progress
- **🧠 Requirement Analysis**: Intelligent goal breakdown and complexity assessment
- **🛠️ Tool Analysis**: Smart mapping of available tools to goals
- **🌐 Distributed Sessions**: Scale across multiple instances with persistent session storage

### Requirements:
- Python 3.12+ required
- Built with modern async/await patterns
- Type-safe with Pydantic v2
- Compatible with OpenAI SDK v1.77+
- Recommended: Use `uv` for dependency management