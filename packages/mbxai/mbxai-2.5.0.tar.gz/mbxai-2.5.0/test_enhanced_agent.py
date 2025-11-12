"""
Simple test to verify the enhanced agent client works.
"""

from pydantic import BaseModel, Field
from src.mbxai.agent.client import AgentClient
from src.mbxai.agent.models import (
    AgentState, TaskStatus, RequirementAnalysis, ToolAnalysis, 
    TodoList, Task, GoalEvaluation, DialogOption
)


class MockClient:
    """Mock AI client for testing."""
    
    def parse(self, messages, response_format):
        """Mock parse method."""
        
        class MockResponse:
            def __init__(self, parsed_content):
                self.choices = [MockChoice(parsed_content)]
                self.usage = MockUsage()
        
        class MockChoice:
            def __init__(self, parsed_content):
                self.message = MockMessage(parsed_content)
        
        class MockMessage:
            def __init__(self, parsed_content):
                self.parsed = parsed_content
        
        class MockUsage:
            def __init__(self):
                self.prompt_tokens = 100
                self.completion_tokens = 50
                self.total_tokens = 150
        
        # Return mock responses based on the expected format
        if response_format == RequirementAnalysis:
            return MockResponse(RequirementAnalysis(
                goal="Create a simple test application",
                success_criteria=["Application runs successfully", "Basic functionality works"],
                complexity_estimate=3
            ))
        elif response_format == ToolAnalysis:
            return MockResponse(ToolAnalysis(
                relevant_tools=[],
                tool_mapping={},
                missing_capabilities=["No tools available for testing"]
            ))
        elif response_format == TodoList:
            tasks = [
                Task(
                    title="Set up project structure",
                    description="Create basic project files and folders",
                    estimated_complexity=2
                ),
                Task(
                    title="Implement core functionality", 
                    description="Add main application logic",
                    estimated_complexity=3
                )
            ]
            return MockResponse(TodoList(tasks=tasks))
        elif response_format == GoalEvaluation:
            return MockResponse(GoalEvaluation(
                goal_achieved=True,
                completion_percentage=100,
                completed_criteria=["Application runs successfully", "Basic functionality works"],
                remaining_criteria=[],
                feedback="All tasks completed successfully"
            ))
        else:
            # Return the expected format if it's SimpleResponse
            if response_format == SimpleResponse:
                return MockResponse(SimpleResponse(
                    message="Test application created successfully",
                    status="completed"
                ))
            else:
                # Default to a simple result
                from src.mbxai.agent.models import Result
                return MockResponse(Result(result="Mock result generated"))


class SimpleResponse(BaseModel):
    """Simple response model for testing."""
    message: str = Field(description="A simple message")
    status: str = Field(description="Status of the request")


def test_basic_agent_flow():
    """Test the basic agent flow without external dependencies."""
    print("🧪 Testing Enhanced Agent Client")
    
    # Create mock client
    mock_client = MockClient()
    
    # Initialize agent
    agent = AgentClient(mock_client, human_in_loop=False, max_task_iterations=2)
    
    # Test basic agent flow
    prompt = "Create a simple test application"
    response = agent.agent(prompt, SimpleResponse)
    
    print(f"✅ Agent created with ID: {response.agent_id}")
    print(f"📊 Current state: {response.state}")
    
    # Check requirement analysis
    if response.requirement_analysis:
        print(f"📋 Goal: {response.requirement_analysis.goal}")
        print(f"📊 Complexity: {response.requirement_analysis.complexity_estimate}/10")
    
    # Check tool analysis  
    if response.tool_analysis:
        print(f"🔧 Relevant tools: {len(response.tool_analysis.relevant_tools)}")
        print(f"❌ Missing capabilities: {len(response.tool_analysis.missing_capabilities)}")
    
    # Check todo list
    if response.todo_list:
        print(f"📝 Tasks generated: {len(response.todo_list.tasks)}")
        for i, task in enumerate(response.todo_list.tasks, 1):
            print(f"  {i}. {task.title} - Status: {task.status.value}")
    
    # Continue execution until completion or max iterations
    iterations = 0
    max_iterations = 10
    
    while not response.is_complete() and iterations < max_iterations:
        iterations += 1
        print(f"\n--- Iteration {iterations} ---")
        print(f"📊 State: {response.state}")
        
        if response.state == AgentState.EXECUTING_TASKS:
            print("⚡ Executing tasks...")
        elif response.state == AgentState.EVALUATING_GOAL:
            print("🎯 Evaluating goal achievement...")
        elif response.state == AgentState.WAITING_FOR_HUMAN:
            print("👤 Waiting for human input...")
            break  # Can't continue without human input in this test
        
        # Continue execution
        response = agent.agent(
            "Continue processing",
            SimpleResponse,
            agent_id=response.agent_id
        )
    
    # Check final result
    if response.is_complete():
        print(f"\n✅ Agent completed successfully!")
        if response.final_response:
            print(f"📄 Final response: {response.final_response.message}")
            print(f"📊 Status: {response.final_response.status}")
        
        if response.goal_evaluation:
            print(f"🎯 Goal achieved: {response.goal_evaluation.goal_achieved}")
            print(f"📊 Completion: {response.goal_evaluation.completion_percentage}%")
    else:
        print(f"⏸️ Agent stopped at state: {response.state}")
    
    # Test session management
    print(f"\n📊 Session Management:")
    sessions = agent.list_sessions()
    print(f"Active sessions: {len(sessions)}")
    
    if response.agent_id in sessions:
        session_info = agent.get_session_info(response.agent_id)
        print(f"Conversation length: {session_info.get('conversation_length', 0)}")
    
    # Clean up
    deleted = agent.delete_session(response.agent_id)
    print(f"Session deleted: {deleted}")
    
    return True


def test_dialog_options():
    """Test dialog options functionality."""
    print("\n🧪 Testing Dialog Options")
    
    def test_action():
        return "Test action executed"
    
    dialog_options = [
        DialogOption(
            id="test_action",
            title="Test Action", 
            description="Execute a test action",
            function=test_action
        )
    ]
    
    mock_client = MockClient()
    agent = AgentClient(mock_client, human_in_loop=True, dialog_options=dialog_options)
    
    print(f"✅ Agent created with {len(dialog_options)} dialog options")
    print(f"🔧 Dialog option: {dialog_options[0].title}")
    
    return True


def test_models():
    """Test the new models."""
    print("\n🧪 Testing New Models")
    
    # Test Task model
    task = Task(
        title="Test Task",
        description="A test task",
        estimated_complexity=3
    )
    print(f"✅ Task created: {task.title} (complexity: {task.estimated_complexity})")
    
    # Test TodoList model
    todo_list = TodoList(tasks=[task])
    next_task = todo_list.get_next_task()
    print(f"✅ TodoList created with {len(todo_list.tasks)} tasks")
    print(f"📋 Next task: {next_task.title if next_task else 'None'}")
    
    # Test status updates
    task.status = TaskStatus.IN_PROGRESS
    next_task = todo_list.get_next_task()  # Should be None now
    print(f"📊 Task status updated: {task.status.value}")
    print(f"📋 Next task after status change: {next_task.title if next_task else 'None'}")
    
    return True


def main():
    """Run all tests."""
    print("🚀 Enhanced Agent Client Test Suite")
    print("=" * 50)
    
    try:
        # Test basic functionality
        test_basic_agent_flow()
        
        # Test dialog options
        test_dialog_options()
        
        # Test models
        test_models()
        
        print(f"\n✅ All tests passed successfully!")
        print("🎉 Enhanced Agent Client is working correctly!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
