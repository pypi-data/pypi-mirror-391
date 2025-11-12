"""
Pydantic models for the agent client.
"""

from typing import Any, Optional, Union, Callable, Protocol, Dict
from pydantic import BaseModel, Field, field_validator
from enum import Enum
from abc import ABC, abstractmethod
import uuid
import re


class Question(BaseModel):
    """A question for the user to provide more information."""
    question: str = Field(description="The question to ask the user")
    key: str = Field(description="A unique and short technical key identifier using only alphanumeric characters and underscores (e.g., user_name, email_address, age)")
    required: bool = Field(default=True, description="Whether this question is required")
    
    @field_validator('key')
    @classmethod
    def validate_key(cls, v: str) -> str:
        """Ensure the key contains only alphanumeric characters and underscores."""
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', v):
            # Convert invalid key to valid format
            # Remove special characters and replace spaces with underscores
            cleaned = re.sub(r'[^a-zA-Z0-9_]', '_', v)
            # Ensure it starts with a letter
            if not cleaned or not cleaned[0].isalpha():
                cleaned = 'key_' + cleaned
            # Remove consecutive underscores
            cleaned = re.sub(r'_+', '_', cleaned)
            # Remove trailing underscores
            cleaned = cleaned.rstrip('_')
            # Ensure it's not empty
            if not cleaned:
                cleaned = 'key'
            return cleaned
        return v


class Result(BaseModel):
    """A simple result wrapper containing just text."""
    result: str = Field(description="The result text from the AI")




class QuestionList(BaseModel):
    """A list of questions to ask the user."""
    questions: list[Question] = Field(description="List of questions to ask the user")


class Answer(BaseModel):
    """An answer to a question."""
    key: str = Field(description="The key of the question being answered")
    answer: str = Field(description="The answer to the question")


class AnswerList(BaseModel):
    """A list of answers from the user."""
    answers: list[Answer] = Field(description="List of answers to questions")


class QualityCheck(BaseModel):
    """Result of quality checking the AI response."""
    is_good: bool = Field(description="Whether the result is good enough")
    feedback: str = Field(description="Feedback on what could be improved if not good")


class TokenUsage(BaseModel):
    """Token usage information for a single API call."""
    prompt_tokens: int = Field(default=0, description="Number of tokens in the prompt")
    completion_tokens: int = Field(default=0, description="Number of tokens in the completion")
    total_tokens: int = Field(default=0, description="Total number of tokens used")


class TokenSummary(BaseModel):
    """Summary of token usage across all API calls in an agent process."""
    requirement_analysis: TokenUsage = Field(default_factory=TokenUsage, description="Tokens used for requirement analysis")
    tool_analysis: TokenUsage = Field(default_factory=TokenUsage, description="Tokens used for tool analysis")
    todo_generation: TokenUsage = Field(default_factory=TokenUsage, description="Tokens used for todo list generation")
    task_execution: list[TokenUsage] = Field(default_factory=list, description="Tokens used for each task execution")
    dialog_interactions: list[TokenUsage] = Field(default_factory=list, description="Tokens used for human-in-the-loop interactions")
    goal_evaluation: TokenUsage = Field(default_factory=TokenUsage, description="Tokens used for goal evaluation")
    final_response: TokenUsage = Field(default_factory=TokenUsage, description="Tokens used for final response generation")
    
    @property
    def total_tokens(self) -> int:
        """Calculate total tokens used across all operations."""
        total = (
            self.requirement_analysis.total_tokens +
            self.tool_analysis.total_tokens +
            self.todo_generation.total_tokens +
            sum(usage.total_tokens for usage in self.task_execution) +
            sum(usage.total_tokens for usage in self.dialog_interactions) +
            self.goal_evaluation.total_tokens +
            self.final_response.total_tokens
        )
        return total
    
    @property
    def total_prompt_tokens(self) -> int:
        """Calculate total prompt tokens used across all operations."""
        total = (
            self.requirement_analysis.prompt_tokens +
            self.tool_analysis.prompt_tokens +
            self.todo_generation.prompt_tokens +
            sum(usage.prompt_tokens for usage in self.task_execution) +
            sum(usage.prompt_tokens for usage in self.dialog_interactions) +
            self.goal_evaluation.prompt_tokens +
            self.final_response.prompt_tokens
        )
        return total
    
    @property
    def total_completion_tokens(self) -> int:
        """Calculate total completion tokens used across all operations."""
        total = (
            self.requirement_analysis.completion_tokens +
            self.tool_analysis.completion_tokens +
            self.todo_generation.completion_tokens +
            sum(usage.completion_tokens for usage in self.task_execution) +
            sum(usage.completion_tokens for usage in self.dialog_interactions) +
            self.goal_evaluation.completion_tokens +
            self.final_response.completion_tokens
        )
        return total


# New models for the enhanced agent architecture

class TaskStatus(str, Enum):
    """Status of a task in the todo list."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class Task(BaseModel):
    """A task in the agent's todo list."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the task")
    title: str = Field(description="Short title of the task")
    description: str = Field(description="Detailed description of what needs to be done")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Current status of the task")
    dependencies: list[str] = Field(default_factory=list, description="List of task IDs that must be completed before this task")
    tools_needed: list[str] = Field(default_factory=list, description="List of tool names needed for this task")
    estimated_complexity: int = Field(default=1, ge=1, le=5, description="Complexity rating from 1-5")
    result: Optional[str] = Field(default=None, description="Result of the task execution")
    error_message: Optional[str] = Field(default=None, description="Error message if task failed")


class TodoList(BaseModel):
    """A list of tasks to complete the user's goal."""
    tasks: list[Task] = Field(description="List of tasks to complete")
    estimated_total_time: Optional[str] = Field(default=None, description="Estimated total time to complete all tasks")
    
    def get_next_task(self) -> Optional[Task]:
        """Get the next pending task that has all dependencies completed."""
        completed_task_ids = {task.id for task in self.tasks if task.status == TaskStatus.COMPLETED}
        
        for task in self.tasks:
            if task.status == TaskStatus.PENDING:
                # Check if all dependencies are completed
                if all(dep_id in completed_task_ids for dep_id in task.dependencies):
                    return task
        return None
    
    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Get a task by its ID."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None


class HumanInteractionType(str, Enum):
    """Type of human interaction needed."""
    DECISION = "decision"
    QUESTION = "question"
    DIALOG_OPTION = "dialog_option"


class DialogOption(BaseModel):
    """A dialog option for structured human-in-the-loop communication.
    
    Dialog options are UI-aware patterns that tell the frontend how to handle
    specific interactions (authentication, approvals, integrations, etc.).
    They are NOT functions executed by the agent - they're instructions for the UI.
    """
    id: str = Field(description="Unique identifier for the dialog option")
    title: str = Field(description="Short title of the dialog option")
    description: str = Field(description="Description of what this option does")
    function: Optional[Callable[..., Any]] = Field(default=None, description="Optional function for backwards compatibility - prefer UI handling")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Parameters to help the UI handle this dialog (URLs, scopes, etc.)")
    
    class Config:
        arbitrary_types_allowed = True


class HumanInLoopRequest(BaseModel):
    """A request for human interaction."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for this interaction")
    interaction_type: HumanInteractionType = Field(description="Type of interaction needed")
    prompt: str = Field(description="The prompt/question for the human")
    options: list[str] = Field(default_factory=list, description="Available options for decisions")
    dialog_options: list[DialogOption] = Field(default_factory=list, description="Available dialog options")
    context: str = Field(default="", description="Additional context for the interaction")
    required: bool = Field(default=True, description="Whether this interaction is required")


class HumanInLoopResponse(BaseModel):
    """Response from human interaction."""
    interaction_id: str = Field(description="ID of the interaction being responded to")
    response_type: HumanInteractionType = Field(description="Type of response")
    decision: Optional[str] = Field(default=None, description="Selected decision option")
    answer: Optional[str] = Field(default=None, description="Answer to a question")
    dialog_option_id: Optional[str] = Field(default=None, description="Selected dialog option ID")
    additional_context: str = Field(default="", description="Additional context from the user")


class HumanInLoopResponseBatch(BaseModel):
    """Batch of human responses for multiple interactions."""
    responses: list[HumanInLoopResponse] = Field(description="List of human responses")
    
    def get_response_by_id(self, interaction_id: str) -> Optional[HumanInLoopResponse]:
        """Get a response by interaction ID."""
        for response in self.responses:
            if response.interaction_id == interaction_id:
                return response
        return None


# Session Handler Interface
class SessionHandler(Protocol):
    """Protocol for custom session storage implementations."""
    
    def get_session(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a session by agent ID."""
        ...
    
    def set_session(self, agent_id: str, session_data: Dict[str, Any]) -> None:
        """Store session data for an agent ID."""
        ...
    
    def delete_session(self, agent_id: str) -> bool:
        """Delete a session by agent ID. Returns True if deleted, False if not found."""
        ...
    
    def list_sessions(self) -> list[str]:
        """List all active session IDs."""
        ...
    
    def session_exists(self, agent_id: str) -> bool:
        """Check if a session exists."""
        ...


class InMemorySessionHandler:
    """Default in-memory session handler implementation."""
    
    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}
    
    def get_session(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a session by agent ID."""
        return self._sessions.get(agent_id)
    
    def set_session(self, agent_id: str, session_data: Dict[str, Any]) -> None:
        """Store session data for an agent ID."""
        self._sessions[agent_id] = session_data
    
    def delete_session(self, agent_id: str) -> bool:
        """Delete a session by agent ID. Returns True if deleted, False if not found."""
        if agent_id in self._sessions:
            del self._sessions[agent_id]
            return True
        return False
    
    def list_sessions(self) -> list[str]:
        """List all active session IDs."""
        return list(self._sessions.keys())
    
    def session_exists(self, agent_id: str) -> bool:
        """Check if a session exists."""
        return agent_id in self._sessions


class RequirementAnalysis(BaseModel):
    """Analysis of the user's requirement/goal."""
    goal: str = Field(description="The main goal the user wants to achieve")
    sub_goals: list[str] = Field(default_factory=list, description="Sub-goals that contribute to the main goal")
    success_criteria: list[str] = Field(description="Criteria to determine if the goal is achieved")
    constraints: list[str] = Field(default_factory=list, description="Any constraints or limitations to consider")
    complexity_estimate: int = Field(ge=1, le=10, description="Complexity estimate from 1-10")


class ToolAnalysis(BaseModel):
    """Analysis of available tools and their relevance to the goal."""
    relevant_tools: list[str] = Field(description="List of tool names relevant to the goal")
    tool_mapping: dict[str, str] = Field(description="Mapping of tool names to their purpose for this goal")
    missing_capabilities: list[str] = Field(default_factory=list, description="Capabilities needed but not available in tools")


class GoalEvaluation(BaseModel):
    """Evaluation of whether the goal has been achieved."""
    goal_achieved: bool = Field(description="Whether the main goal has been achieved")
    completion_percentage: int = Field(ge=0, le=100, description="Percentage of goal completion")
    completed_criteria: list[str] = Field(description="Success criteria that have been met")
    remaining_criteria: list[str] = Field(description="Success criteria that still need to be met")
    feedback: str = Field(description="Detailed feedback on the goal achievement")
    next_steps: list[str] = Field(default_factory=list, description="Next steps if goal is not fully achieved")


class AgentState(str, Enum):
    """Current state of the agent."""
    ANALYZING_REQUIREMENT = "analyzing_requirement"
    ANALYZING_TOOLS = "analyzing_tools"
    GENERATING_TODO = "generating_todo"
    EXECUTING_TASKS = "executing_tasks"
    WAITING_FOR_HUMAN = "waiting_for_human"
    EVALUATING_GOAL = "evaluating_goal"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentResponse(BaseModel):
    """Response from the agent that can contain various states and information."""
    agent_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for this agent session")
    state: AgentState = Field(description="Current state of the agent")
    
    # Legacy support for existing questions-based flow
    questions: list[Question] = Field(default_factory=list, description="List of questions for the user (legacy)")
    
    # New architecture fields
    requirement_analysis: Optional[RequirementAnalysis] = Field(default=None, description="Analysis of the requirement")
    tool_analysis: Optional[ToolAnalysis] = Field(default=None, description="Analysis of available tools")
    todo_list: Optional[TodoList] = Field(default=None, description="Current todo list")
    current_task: Optional[Task] = Field(default=None, description="Currently executing task")
    human_interaction_request: Optional[HumanInLoopRequest] = Field(default=None, description="Request for human interaction")
    goal_evaluation: Optional[GoalEvaluation] = Field(default=None, description="Goal achievement evaluation")
    
    # Final response
    final_response: Optional[Any] = Field(default=None, description="The final response if processing is complete")
    
    # Token usage tracking
    token_summary: Optional[TokenSummary] = Field(default=None, description="Summary of token usage for this agent process")
    
    def has_questions(self) -> bool:
        """Check if this response has questions that need to be answered (legacy)."""
        return len(self.questions) > 0
    
    def needs_human_interaction(self) -> bool:
        """Check if this response needs human interaction."""
        return self.human_interaction_request is not None
    
    def is_complete(self) -> bool:
        """Check if this response contains a final result."""
        return self.state == AgentState.COMPLETED and self.final_response is not None
    
    def is_waiting_for_human(self) -> bool:
        """Check if the agent is waiting for human input."""
        return self.state == AgentState.WAITING_FOR_HUMAN
