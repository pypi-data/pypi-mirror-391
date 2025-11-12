"""
Example demonstrating the enhanced Agent Client with the new 6-step process.
"""

import os
from pydantic import BaseModel, Field
from mbxai import AgentClient, OpenRouterClient, ToolClient
from mbxai.agent.models import (
    DialogOption, HumanInLoopResponse, HumanInteractionType, 
    TaskStatus, AgentState
)


class ProjectPlan(BaseModel):
    """A project plan response."""
    project_name: str = Field(description="Name of the project")
    description: str = Field(description="Project description")
    technologies: list[str] = Field(description="Technologies to be used")
    phases: list[str] = Field(description="Project phases")
    estimated_duration: str = Field(description="Estimated project duration")
    deliverables: list[str] = Field(description="Key deliverables")
    risks: list[str] = Field(description="Potential risks and mitigation strategies")


class WeatherInfo(BaseModel):
    """Weather information response."""
    location: str = Field(description="The location")
    current_weather: str = Field(description="Current weather description")
    temperature: str = Field(description="Current temperature")
    recommendations: list[str] = Field(description="Recommendations based on weather")


def google_auth_dialog_option() -> str:
    """Simulate Google authentication."""
    print("🔐 Simulating Google Authentication...")
    return "Successfully authenticated with Google"


def slack_integration_dialog_option() -> str:
    """Simulate Slack integration setup."""
    print("💬 Simulating Slack integration setup...")
    return "Slack integration configured successfully"


def example_basic_agent():
    """Example of basic agent usage without human-in-the-loop."""
    print("=== Basic Agent Example ===")
    
    # Initialize client
    openrouter_client = OpenRouterClient(token=os.getenv("OPENROUTER_API_KEY", "demo-token"))
    agent = AgentClient(openrouter_client, human_in_loop=False)
    
    # Create a project plan
    prompt = "Create a project plan for building a simple weather app using React and Node.js"
    
    print(f"🚀 Starting agent with prompt: {prompt}")
    response = agent.agent(prompt, final_response_structure=ProjectPlan)
    
    print(f"📊 Agent state: {response.state}")
    
    if response.requirement_analysis:
        print(f"📋 Goal: {response.requirement_analysis.goal}")
        print(f"📋 Complexity: {response.requirement_analysis.complexity_estimate}/10")
    
    if response.todo_list:
        print(f"📝 Generated {len(response.todo_list.tasks)} tasks:")
        for task in response.todo_list.tasks:
            print(f"  - {task.title} (Status: {task.status.value})")
    
    if response.is_complete():
        plan = response.final_response
        print(f"\n✅ Project Plan Generated:")
        print(f"📦 Project: {plan.project_name}")
        print(f"📄 Description: {plan.description}")
        print(f"💻 Technologies: {', '.join(plan.technologies)}")
        print(f"⏱️ Duration: {plan.estimated_duration}")
        print(f"📋 Phases: {', '.join(plan.phases)}")
        
        # Print token usage
        if response.token_summary:
            print(f"\n📊 Token usage: {response.token_summary.total_tokens} total")
    
    return response.agent_id


def example_human_in_loop():
    """Example of agent with human-in-the-loop interactions."""
    print("\n=== Human-in-the-Loop Agent Example ===")
    
    # Initialize client with dialog options
    openrouter_client = OpenRouterClient(token=os.getenv("OPENROUTER_API_KEY", "demo-token"))
    
    dialog_options = [
        DialogOption(
            id="google_auth",
            title="Google Authentication",
            description="Authenticate with Google services",
            function=google_auth_dialog_option
        ),
        DialogOption(
            id="slack_integration",
            title="Slack Integration",
            description="Set up Slack integration",
            function=slack_integration_dialog_option
        )
    ]
    
    agent = AgentClient(
        openrouter_client, 
        human_in_loop=True, 
        dialog_options=dialog_options,
        max_task_iterations=5
    )
    
    # Start with a complex task
    prompt = "Set up a complete CI/CD pipeline for a web application with automated testing, deployment, and monitoring"
    
    print(f"🚀 Starting agent with human-in-loop: {prompt}")
    response = agent.agent(prompt, final_response_structure=ProjectPlan)
    
    print(f"📊 Agent state: {response.state}")
    
    # Simulate human interactions
    iteration = 0
    max_iterations = 3
    
    while not response.is_complete() and iteration < max_iterations:
        iteration += 1
        print(f"\n--- Iteration {iteration} ---")
        
        if response.needs_human_interaction():
            request = response.human_interaction_request
            print(f"👤 Human interaction needed: {request.interaction_type.value}")
            print(f"💬 Prompt: {request.prompt}")
            
            if request.interaction_type == HumanInteractionType.DECISION:
                print(f"📋 Options: {', '.join(request.options)}")
                # Simulate user choosing to proceed
                human_response = HumanInLoopResponse(
                    interaction_id=request.id,
                    response_type=HumanInteractionType.DECISION,
                    decision="proceed",
                    additional_context="User decided to proceed with the current approach"
                )
            elif request.interaction_type == HumanInteractionType.QUESTION:
                # Simulate user answering a question
                human_response = HumanInLoopResponse(
                    interaction_id=request.id,
                    response_type=HumanInteractionType.QUESTION,
                    answer="Use Docker for containerization and AWS for cloud services",
                    additional_context="User prefers cloud-native solutions"
                )
            elif request.interaction_type == HumanInteractionType.DIALOG_OPTION:
                # Simulate user selecting a dialog option
                print(f"🔧 Available dialog options:")
                for option in request.dialog_options:
                    print(f"  - {option.title}: {option.description}")
                
                selected_option = request.dialog_options[0] if request.dialog_options else None
                human_response = HumanInLoopResponse(
                    interaction_id=request.id,
                    response_type=HumanInteractionType.DIALOG_OPTION,
                    dialog_option_id=selected_option.id if selected_option else "none",
                    additional_context="User selected the first option"
                )
            else:
                # Default response
                human_response = HumanInLoopResponse(
                    interaction_id=request.id,
                    response_type=HumanInteractionType.QUESTION,
                    answer="Continue with default settings"
                )
            
            print(f"💭 Simulated user response: {human_response.answer or human_response.decision or 'dialog option selected'}")
            
            # Continue with human response
            response = agent.agent(
                prompt="Continue with user input", 
                final_response_structure=ProjectPlan, 
                agent_id=response.agent_id,
                human_response=human_response
            )
        
        elif response.state == AgentState.EXECUTING_TASKS:
            print(f"⚡ Agent is executing tasks...")
            if response.current_task:
                print(f"📋 Current task: {response.current_task.title}")
            
            # Continue execution
            response = agent.agent(
                prompt="Continue execution", 
                final_response_structure=ProjectPlan, 
                agent_id=response.agent_id
            )
        
        else:
            print(f"📊 Agent state: {response.state}")
            break
    
    if response.is_complete():
        plan = response.final_response
        print(f"\n✅ CI/CD Plan Generated:")
        print(f"📦 Project: {plan.project_name}")
        print(f"📄 Description: {plan.description}")
        print(f"💻 Technologies: {', '.join(plan.technologies)}")
        
        if response.goal_evaluation:
            print(f"\n🎯 Goal Achievement: {response.goal_evaluation.completion_percentage}%")
            print(f"💭 Feedback: {response.goal_evaluation.feedback}")
    
    return response.agent_id


def example_with_tools():
    """Example of agent with tools."""
    print("\n=== Agent with Tools Example ===")
    
    # Initialize tool client
    openrouter_client = OpenRouterClient(token=os.getenv("OPENROUTER_API_KEY", "demo-token"))
    tool_client = ToolClient(openrouter_client)
    
    # Register a weather tool
    def get_weather(location: str) -> str:
        """Get current weather for a location."""
        # This is a mock implementation
        return f"The weather in {location} is sunny and 72°F with light winds"
    
    def get_forecast(location: str, days: int = 5) -> str:
        """Get weather forecast for a location."""
        return f"5-day forecast for {location}: Mostly sunny with temperatures ranging from 68-75°F"
    
    agent = AgentClient(tool_client, human_in_loop=False)
    
    # Register tools
    agent.register_tool(
        name="get_weather",
        description="Get current weather information for a specific location",
        function=get_weather
    )
    
    agent.register_tool(
        name="get_forecast", 
        description="Get weather forecast for a location",
        function=get_forecast
    )
    
    # Ask for weather information
    prompt = "I'm planning a picnic in San Francisco this weekend. Can you help me understand the weather and give recommendations?"
    
    print(f"🚀 Starting agent with tools: {prompt}")
    response = agent.agent(prompt, final_response_structure=WeatherInfo)
    
    print(f"📊 Agent state: {response.state}")
    
    if response.tool_analysis:
        print(f"🔧 Relevant tools: {', '.join(response.tool_analysis.relevant_tools)}")
    
    if response.is_complete():
        weather = response.final_response
        print(f"\n🌤️ Weather Information:")
        print(f"📍 Location: {weather.location}")
        print(f"🌡️ Current: {weather.current_weather}")
        print(f"🌡️ Temperature: {weather.temperature}")
        print(f"💡 Recommendations:")
        for rec in weather.recommendations:
            print(f"  - {rec}")
    
    return response.agent_id


def example_session_management():
    """Example of session management and continuation."""
    print("\n=== Session Management Example ===")
    
    openrouter_client = OpenRouterClient(token=os.getenv("OPENROUTER_API_KEY", "demo-token"))
    agent = AgentClient(openrouter_client, human_in_loop=False)
    
    # Start first task
    prompt1 = "Create a basic project structure for a Python web API"
    response1 = agent.agent(prompt1, final_response_structure=ProjectPlan)
    agent_id = response1.agent_id
    
    print(f"📋 First task completed: {response1.is_complete()}")
    
    if response1.is_complete():
        plan1 = response1.final_response
        print(f"📦 First project: {plan1.project_name}")
        
        # Continue with related task
        prompt2 = "Now add authentication and user management to this API project"
        response2 = agent.agent(prompt2, final_response_structure=ProjectPlan, agent_id=agent_id)
        
        print(f"📋 Second task completed: {response2.is_complete()}")
        
        if response2.is_complete():
            plan2 = response2.final_response
            print(f"📦 Enhanced project: {plan2.project_name}")
            print(f"🔐 New features: {', '.join(plan2.technologies)}")
    
    # List sessions
    sessions = agent.list_sessions()
    print(f"📊 Active sessions: {len(sessions)}")
    
    # Get session info
    if agent_id in sessions:
        session_info = agent.get_session_info(agent_id)
        print(f"💬 Conversation length: {session_info.get('conversation_length', 0)} messages")
    
    # Clean up
    deleted = agent.delete_session(agent_id)
    print(f"🗑️ Session deleted: {deleted}")
    
    return agent_id


def main():
    """Run all examples."""
    print("🤖 Enhanced Agent Client Examples")
    print("=" * 50)
    
    try:
        # Basic agent without human interaction
        basic_id = example_basic_agent()
        
        # Agent with human-in-the-loop
        hitl_id = example_human_in_loop()
        
        # Agent with tools
        tools_id = example_with_tools()
        
        # Session management
        session_id = example_session_management()
        
        print(f"\n✅ All examples completed successfully!")
        print(f"📋 Generated agent IDs: {basic_id}, {hitl_id}, {tools_id}, {session_id}")
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
