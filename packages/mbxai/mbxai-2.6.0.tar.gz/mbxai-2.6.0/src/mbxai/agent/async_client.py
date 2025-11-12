"""
Async Enhanced Agent client implementation for MBX AI with human-in-the-loop capabilities.
"""

from typing import Any, Union, Type, Callable, Optional
import logging
import json
from pydantic import BaseModel

from ..openrouter.async_client import AsyncOpenRouterClient
from ..tools.async_client import AsyncToolClient
from ..mcp.async_client import AsyncMCPClient
from .models import (
    AgentResponse, AgentState, RequirementAnalysis, ToolAnalysis, TodoList, Task, TaskStatus,
    HumanInLoopRequest, HumanInLoopResponse, HumanInLoopResponseBatch, HumanInteractionType, DialogOption,
    GoalEvaluation, TokenUsage, TokenSummary, Result, SessionHandler, InMemorySessionHandler
)

logger = logging.getLogger(__name__)


class AsyncTaskManager:
    """Manages task generation and execution for the agent (async version)."""
    
    def __init__(self, ai_client):
        self.ai_client = ai_client
    
    async def generate_todo_list(
        self,
        requirement_analysis: RequirementAnalysis,
        tool_analysis: ToolAnalysis,
        conversation_history: list[dict[str, Any]] = None
    ) -> tuple[TodoList, TokenUsage]:
        """Generate a todo list based on requirement and tool analysis (async)."""
        if conversation_history is None:
            conversation_history = []
            
        # Format available tools
        tools_text = ""
        if tool_analysis.relevant_tools:
            tools_text = "\n\nAvailable Tools:\n"
            for tool_name in tool_analysis.relevant_tools:
                purpose = tool_analysis.tool_mapping.get(tool_name, "No description available")
                tools_text += f"- {tool_name}: {purpose}\n"
        
        # Format missing capabilities
        missing_text = ""
        if tool_analysis.missing_capabilities:
            missing_text = "\n\nMissing Capabilities (to be handled manually):\n"
            for capability in tool_analysis.missing_capabilities:
                missing_text += f"- {capability}\n"
        
        prompt = f"""
Based on this requirement analysis:
Goal: {requirement_analysis.goal}
Sub-goals: {', '.join(requirement_analysis.sub_goals)}
Success Criteria: {', '.join(requirement_analysis.success_criteria)}
Constraints: {', '.join(requirement_analysis.constraints)}
Complexity: {requirement_analysis.complexity_estimate}/10
{tools_text}{missing_text}

Create a detailed todo list with specific, actionable tasks to achieve the goal.
Each task should be concrete and measurable. Consider dependencies between tasks.
Assign the appropriate tools to tasks that need them.
Estimate complexity for each task (1-5 scale).
Provide an estimated total time to complete all tasks.

Break down complex goals into smaller, manageable tasks that can be executed step by step.
"""
        
        messages = [{"role": "user", "content": prompt}]
        
        try:
            response = await self.ai_client.parse(conversation_history + messages, TodoList)
            todo_list = self._extract_parsed_content(response, TodoList)
            token_usage = self._extract_token_usage(response)
            
            # Validate and fix todo list
            self._validate_todo_list(todo_list)
            
            logger.info(f"Generated todo list with {len(todo_list.tasks)} tasks")
            return todo_list, token_usage
            
        except Exception as e:
            logger.error(f"Failed to generate todo list: {e}")
            # Return a basic todo list
            basic_task = Task(
                title="Complete the requirement",
                description=requirement_analysis.goal,
                estimated_complexity=requirement_analysis.complexity_estimate
            )
            return TodoList(tasks=[basic_task], estimated_total_time="Unknown"), TokenUsage()
    
    def _validate_todo_list(self, todo_list: TodoList):
        """Validate and fix the todo list."""
        # Ensure all tasks have valid IDs
        task_ids = set()
        for task in todo_list.tasks:
            if not task.id or task.id in task_ids:
                task.id = str(__import__("uuid").uuid4())
            task_ids.add(task.id)
        
        # Validate dependencies exist
        for task in todo_list.tasks:
            valid_deps = [dep for dep in task.dependencies if dep in task_ids]
            task.dependencies = valid_deps
    
    def _extract_parsed_content(self, response: Any, response_format: Type[BaseModel]) -> BaseModel:
        """Extract the parsed content from the AI response."""
        if hasattr(response, 'choices') and len(response.choices) > 0:
            choice = response.choices[0]
            if hasattr(choice.message, 'parsed') and choice.message.parsed:
                return choice.message.parsed
            elif hasattr(choice.message, 'content'):
                try:
                    content_dict = json.loads(choice.message.content)
                    return response_format(**content_dict)
                except (json.JSONDecodeError, TypeError):
                    if response_format == TodoList:
                        return TodoList(tasks=[])
                    else:
                        return response_format()
        
        # Fallback
        if response_format == TodoList:
            return TodoList(tasks=[])
        else:
            return response_format()
    
    def _extract_token_usage(self, response: Any) -> TokenUsage:
        """Extract token usage information from an AI response."""
        try:
            if hasattr(response, 'usage') and response.usage:
                usage = response.usage
                return TokenUsage(
                    prompt_tokens=getattr(usage, 'prompt_tokens', 0),
                    completion_tokens=getattr(usage, 'completion_tokens', 0),
                    total_tokens=getattr(usage, 'total_tokens', 0)
                )
        except (AttributeError, TypeError) as e:
            logger.debug(f"Could not extract token usage: {e}")
        
        return TokenUsage()


class AsyncDialogHandler:
    """Handles human-in-the-loop interactions (async version)."""
    
    def __init__(self, ai_client):
        self.ai_client = ai_client
    
    def create_human_interaction_request(
        self,
        interaction_type: HumanInteractionType,
        context: str,
        task: Optional[Task] = None,
        available_dialog_options: list[DialogOption] = None
    ) -> HumanInLoopRequest:
        """Create a human interaction request based on the context."""
        if available_dialog_options is None:
            available_dialog_options = []
            
        if interaction_type == HumanInteractionType.DECISION:
            return self._create_decision_request(context, task)
        elif interaction_type == HumanInteractionType.QUESTION:
            return self._create_question_request(context, task)
        elif interaction_type == HumanInteractionType.DIALOG_OPTION:
            return self._create_dialog_option_request(context, task, available_dialog_options)
        else:
            # Default question request
            return HumanInLoopRequest(
                interaction_type=HumanInteractionType.QUESTION,
                prompt=f"I need your input for: {context}",
                context=context
            )
    
    def _create_decision_request(self, context: str, task: Optional[Task]) -> HumanInLoopRequest:
        """Create a decision request."""
        task_info = f" for task '{task.title}'" if task else ""
        return HumanInLoopRequest(
            interaction_type=HumanInteractionType.DECISION,
            prompt=f"I need you to make a decision{task_info}: {context}",
            options=["proceed", "skip", "modify", "abort"],
            context=context
        )
    
    def _create_question_request(self, context: str, task: Optional[Task]) -> HumanInLoopRequest:
        """Create a question request."""
        task_info = f" while working on '{task.title}'" if task else ""
        return HumanInLoopRequest(
            interaction_type=HumanInteractionType.QUESTION,
            prompt=f"I have a question{task_info}: {context}",
            context=context
        )
    
    def _create_dialog_option_request(
        self,
        context: str,
        task: Optional[Task],
        available_dialog_options: list[DialogOption]
    ) -> HumanInLoopRequest:
        """Create a dialog option request."""
        task_info = f" for task '{task.title}'" if task else ""
        return HumanInLoopRequest(
            interaction_type=HumanInteractionType.DIALOG_OPTION,
            prompt=f"Please select an action{task_info}: {context}",
            dialog_options=available_dialog_options,
            context=context
        )


class AsyncAgentClient:
    """
    Async Enhanced Agent client that follows a structured 6-step process:
    1. Understand the requirement - What is the expected goal
    2. Which tools do I have to help me reaching that goal
    3. Think about a todo list - What is required to reach the goal
    4. Work step by step on the todo list
    5. When human in the loop is active, have a dialog to the user
    6. Last step - Is the goal reached? If no, create a new todo-list, If yes return the answer
    
    The agent supports:
    - A prompt/requirement/task
    - A list of tools
    - A list of dialog-options
    - Human in the loop - yes or no
    - Possible question types for human in the loop (decision, question, dialog_option)
    - Pydantic model for last response
    """

    def __init__(
        self,
        ai_client: Union[AsyncOpenRouterClient, AsyncToolClient, AsyncMCPClient],
        human_in_loop: bool = False,
        dialog_options: list[DialogOption] = None,
        max_task_iterations: int = 10,
        session_handler: SessionHandler = None
    ) -> None:
        """
        Initialize the AsyncAgentClient.

        Args:
            ai_client: The underlying async AI client (AsyncOpenRouterClient, AsyncToolClient, or AsyncMCPClient)
            human_in_loop: Whether to enable human-in-the-loop interactions
            dialog_options: Available dialog options for human interactions
            max_task_iterations: Maximum number of task execution iterations
            session_handler: Custom session storage handler (defaults to InMemorySessionHandler)
            
        Raises:
            ValueError: If the client doesn't support structured responses (no parse method)
        """
        if not hasattr(ai_client, 'parse'):
            raise ValueError(
                f"AsyncAgentClient requires a client with structured response support (parse method). "
                f"The provided client {type(ai_client).__name__} does not have a parse method."
            )
        
        if max_task_iterations < 1:
            raise ValueError("max_task_iterations must be positive")
        
        self._ai_client = ai_client
        self._human_in_loop = human_in_loop
        self._dialog_options = dialog_options or []
        self._max_task_iterations = max_task_iterations
        
        # Initialize session handler (default to in-memory if none provided)
        self._session_handler = session_handler or InMemorySessionHandler()
        
        # Create helper components
        self._task_manager = AsyncTaskManager(ai_client)
        self._dialog_handler = AsyncDialogHandler(ai_client)

    def register_tool(
        self,
        name: str,
        description: str,
        function: Callable[..., Any],
        schema: dict[str, Any] | None = None,
    ) -> None:
        """
        Register a new tool with the underlying AI client.
        
        Args:
            name: The name of the tool
            description: A description of what the tool does
            function: The function to call when the tool is used
            schema: The JSON schema for the tool's parameters
            
        Raises:
            AttributeError: If the underlying client doesn't support tool registration
        """
        if hasattr(self._ai_client, 'register_tool'):
            self._ai_client.register_tool(name, description, function, schema)
            logger.debug(f"Registered tool '{name}' with {type(self._ai_client).__name__}")
        else:
            raise AttributeError(
                f"Tool registration is not supported by {type(self._ai_client).__name__}. "
                f"Use AsyncToolClient or AsyncMCPClient to register tools."
            )

    async def register_mcp_server(self, name: str, base_url: str) -> None:
        """
        Register an MCP server and load its tools.
        
        Args:
            name: The name of the MCP server
            base_url: The base URL of the MCP server
            
        Raises:
            AttributeError: If the underlying client doesn't support MCP server registration
        """
        if hasattr(self._ai_client, 'register_mcp_server'):
            await self._ai_client.register_mcp_server(name, base_url)
            logger.debug(f"Registered MCP server '{name}' at {base_url}")
        else:
            raise AttributeError(
                f"MCP server registration is not supported by {type(self._ai_client).__name__}. "
                f"Use AsyncMCPClient to register MCP servers."
            )

    async def agent(
        self,
        prompt: str,
        final_response_structure: Type[BaseModel],
        tools: list[str] = None,
        dialog_options: list[DialogOption] = None,
        human_in_loop: bool = None,
        agent_id: str = None,
        human_response: Union[HumanInLoopResponse, HumanInLoopResponseBatch, list[HumanInLoopResponse]] = None
    ) -> AgentResponse:
        """
        Process a prompt through the enhanced 6-step agent process (async version).

        Args:
            prompt: The user's prompt/requirement/task
            final_response_structure: Pydantic model defining the expected final response format
            tools: List of tool names to use (if None, uses all available tools)
            dialog_options: Available dialog options for this session
            human_in_loop: Whether to enable human-in-the-loop (overrides default)
            agent_id: Optional agent session ID to continue an existing conversation
            human_response: Response(s) from human for continuing interaction - can be single response, batch, or list

        Returns:
            AgentResponse containing the current state and any required interactions
        """
        # Setup session
        is_existing_session = agent_id is not None and self._session_handler.session_exists(agent_id)
        if not is_existing_session:
            if agent_id is None:
                agent_id = str(__import__("uuid").uuid4())
            logger.info(f"🚀 Starting new async agent process (ID: {agent_id})")
        else:
            logger.info(f"🔄 Continuing async agent process (ID: {agent_id})")
        
        # Initialize or get session data
        session = self._session_handler.get_session(agent_id) or {
            "original_prompt": prompt,
            "final_response_structure": final_response_structure,
            "human_in_loop": human_in_loop if human_in_loop is not None else self._human_in_loop,
            "dialog_options": dialog_options or self._dialog_options,
            "conversation_history": [],
            "token_summary": TokenSummary(),
            "state": AgentState.ANALYZING_REQUIREMENT,
            "requirement_analysis": None,
            "tool_analysis": None,
            "todo_list": None,
            "current_task_index": 0,
            "iteration_count": 0
        }
        
        # Handle human response(s) if provided
        if human_response:
            session = self._handle_human_responses(session, human_response)
        
        # Store session
        self._session_handler.set_session(agent_id, session)
        
        # Process based on current state
        return await self._process_agent_state(agent_id, session)

    async def _process_agent_state(self, agent_id: str, session: dict[str, Any]) -> AgentResponse:
        """Process the agent based on its current state (async version)."""
        state = session["state"]
        token_summary = session["token_summary"]
        
        try:
            if state == AgentState.ANALYZING_REQUIREMENT:
                return await self._step1_analyze_requirement(agent_id, session)
            elif state == AgentState.ANALYZING_TOOLS:
                return await self._step2_analyze_tools(agent_id, session)
            elif state == AgentState.GENERATING_TODO:
                return await self._step3_generate_todo(agent_id, session)
            elif state == AgentState.EXECUTING_TASKS:
                return await self._step4_execute_tasks(agent_id, session)
            elif state == AgentState.WAITING_FOR_HUMAN:
                return await self._step5_handle_human_interaction(agent_id, session)
            elif state == AgentState.EVALUATING_GOAL:
                return await self._step6_evaluate_goal(agent_id, session)
            elif state == AgentState.COMPLETED:
                return AgentResponse(
                    agent_id=agent_id,
                    state=AgentState.COMPLETED,
                    final_response=session.get("final_response"),
                    token_summary=token_summary
                )
            else:
                # Unknown state, reset to beginning
                session["state"] = AgentState.ANALYZING_REQUIREMENT
                return await self._step1_analyze_requirement(agent_id, session)
                
        except Exception as e:
            logger.error(f"Error in async agent state {state}: {e}")
            session["state"] = AgentState.FAILED
            return AgentResponse(
                agent_id=agent_id,
                state=AgentState.FAILED,
                final_response=f"Agent failed with error: {str(e)}",
                token_summary=token_summary
            )

    async def _step1_analyze_requirement(self, agent_id: str, session: dict[str, Any]) -> AgentResponse:
        """Step 1: Understand the requirement - What is the expected goal (async version)."""
        logger.info(f"📋 Agent {agent_id}: Step 1 - Analyzing requirement (async)")
        
        prompt = session["original_prompt"]
        conversation_history = session["conversation_history"]
        
        analysis_prompt = f"""
Analyze this user requirement and understand what they want to achieve:
==========
{prompt}
==========

Break down the requirement into:
1. The main goal the user wants to achieve
2. Sub-goals that contribute to the main goal
3. Success criteria to determine if the goal is achieved
4. Any constraints or limitations to consider
5. Complexity estimate (1-10 scale, where 1 is trivial and 10 is extremely complex)

Provide a comprehensive analysis of what the user wants to accomplish.
"""
        
        messages = [{"role": "user", "content": analysis_prompt}]
        
        try:
            response = await self._ai_client.parse(conversation_history + messages, RequirementAnalysis)
            requirement_analysis = self._extract_parsed_content(response, RequirementAnalysis)
            token_usage = self._extract_token_usage(response)
            
            # Update session
            session["requirement_analysis"] = requirement_analysis
            session["token_summary"].requirement_analysis = token_usage
            session["state"] = AgentState.ANALYZING_TOOLS
            
            logger.info(f"📋 Agent {agent_id}: Requirement analysis completed - Goal: {requirement_analysis.goal}")
            
            # Continue to next step
            return await self._step2_analyze_tools(agent_id, session)
            
        except Exception as e:
            logger.error(f"Failed to analyze requirement: {e}")
            session["state"] = AgentState.FAILED
            return AgentResponse(
                agent_id=agent_id,
                state=AgentState.FAILED,
                final_response=f"Failed to analyze requirement: {str(e)}",
                token_summary=session["token_summary"]
            )

    async def _step2_analyze_tools(self, agent_id: str, session: dict[str, Any]) -> AgentResponse:
        """Step 2: Which tools do I have to help me reach that goal (async version)."""
        logger.info(f"🔧 Agent {agent_id}: Step 2 - Analyzing available tools (async)")
        
        requirement_analysis = session["requirement_analysis"]
        conversation_history = session["conversation_history"]
        
        # Get available tools
        available_tools = self._get_available_tools()
        
        tools_text = "Available Tools:\n"
        if available_tools:
            for tool_name, tool_desc in available_tools.items():
                tools_text += f"- {tool_name}: {tool_desc}\n"
        else:
            tools_text += "No tools are currently available.\n"
        
        analysis_prompt = f"""
Given this goal analysis:
Goal: {requirement_analysis.goal}
Sub-goals: {', '.join(requirement_analysis.sub_goals)}
Success Criteria: {', '.join(requirement_analysis.success_criteria)}

And these available tools:
{tools_text}

Analyze which tools are relevant for achieving this goal:
1. List the relevant tools and explain how each helps achieve the goal
2. Map each tool to its specific purpose for this goal
3. Identify any missing capabilities that aren't covered by available tools

Provide a comprehensive tool analysis.
"""
        
        messages = [{"role": "user", "content": analysis_prompt}]
        
        try:
            response = await self._ai_client.parse(conversation_history + messages, ToolAnalysis)
            tool_analysis = self._extract_parsed_content(response, ToolAnalysis)
            token_usage = self._extract_token_usage(response)
            
            # Update session
            session["tool_analysis"] = tool_analysis
            session["token_summary"].tool_analysis = token_usage
            session["state"] = AgentState.GENERATING_TODO
            
            logger.info(f"🔧 Agent {agent_id}: Tool analysis completed - {len(tool_analysis.relevant_tools)} relevant tools")
            
            # Continue to next step
            return await self._step3_generate_todo(agent_id, session)
            
        except Exception as e:
            logger.error(f"Failed to analyze tools: {e}")
            session["state"] = AgentState.FAILED
            return AgentResponse(
                agent_id=agent_id,
                state=AgentState.FAILED,
                final_response=f"Failed to analyze tools: {str(e)}",
                token_summary=session["token_summary"]
            )

    async def _step3_generate_todo(self, agent_id: str, session: dict[str, Any]) -> AgentResponse:
        """Step 3: Think about a todo list - What is required to reach the goal (async version)."""
        logger.info(f"📝 Agent {agent_id}: Step 3 - Generating todo list (async)")
        
        requirement_analysis = session["requirement_analysis"]
        tool_analysis = session["tool_analysis"]
        conversation_history = session["conversation_history"]
        
        try:
            todo_list, token_usage = await self._task_manager.generate_todo_list(
                requirement_analysis,
                tool_analysis,
                conversation_history
            )
            
            # Update session
            session["todo_list"] = todo_list
            session["token_summary"].todo_generation = token_usage
            session["current_task_index"] = 0
            session["state"] = AgentState.EXECUTING_TASKS
            
            logger.info(f"📝 Agent {agent_id}: Todo list generated with {len(todo_list.tasks)} tasks")
            
            # Return current state for visibility
            return AgentResponse(
                agent_id=agent_id,
                state=AgentState.EXECUTING_TASKS,
                requirement_analysis=requirement_analysis,
                tool_analysis=tool_analysis,
                todo_list=todo_list,
                token_summary=session["token_summary"]
            )
            
        except Exception as e:
            logger.error(f"Failed to generate todo list: {e}")
            session["state"] = AgentState.FAILED
            return AgentResponse(
                agent_id=agent_id,
                state=AgentState.FAILED,
                final_response=f"Failed to generate todo list: {str(e)}",
                token_summary=session["token_summary"]
            )

    async def _step4_execute_tasks(self, agent_id: str, session: dict[str, Any]) -> AgentResponse:
        """Step 4: Work step by step on the todo list (async version)."""
        logger.info(f"⚡ Agent {agent_id}: Step 4 - Executing tasks (async)")
        
        todo_list = session["todo_list"]
        conversation_history = session["conversation_history"]
        
        # Check if we've exceeded iteration limit
        session["iteration_count"] = session.get("iteration_count", 0) + 1
        if session["iteration_count"] > self._max_task_iterations:
            logger.warning(f"Agent {agent_id}: Reached max task iterations, moving to goal evaluation")
            session["state"] = AgentState.EVALUATING_GOAL
            return await self._step6_evaluate_goal(agent_id, session)
        
        # Get next task to execute
        next_task = todo_list.get_next_task()
        
        if not next_task:
            # No more tasks, move to goal evaluation
            logger.info(f"⚡ Agent {agent_id}: All tasks completed, moving to goal evaluation")
            session["state"] = AgentState.EVALUATING_GOAL
            return await self._step6_evaluate_goal(agent_id, session)
        
        # Mark task as in progress
        next_task.status = TaskStatus.IN_PROGRESS
        session["current_task"] = next_task
        
        logger.info(f"⚡ Agent {agent_id}: Executing task '{next_task.title}'")
        
        # Check if human interaction is needed for this task
        if session["human_in_loop"] and self._should_request_human_interaction(next_task, session):
            session["state"] = AgentState.WAITING_FOR_HUMAN
            return await self._step5_handle_human_interaction(agent_id, session)
        
        # Execute the task
        try:
            result, token_usage = await self._execute_task(next_task, session, conversation_history)
            
            # Update task status
            next_task.status = TaskStatus.COMPLETED
            next_task.result = result
            
            # Track token usage
            session["token_summary"].task_execution.append(token_usage)
            
            logger.info(f"⚡ Agent {agent_id}: Task '{next_task.title}' completed")
            
            # Continue with next task
            return await self._step4_execute_tasks(agent_id, session)
            
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            next_task.status = TaskStatus.FAILED
            next_task.error_message = str(e)
            
            # Continue with next task (skip failed one)
            return await self._step4_execute_tasks(agent_id, session)

    async def _step5_handle_human_interaction(self, agent_id: str, session: dict[str, Any]) -> AgentResponse:
        """Step 5: When human in the loop is active, have a dialog to the user (async version)."""
        logger.info(f"👤 Agent {agent_id}: Step 5 - Handling human interaction (async)")
        
        current_task = session.get("current_task")
        dialog_options = session.get("dialog_options", [])
        
        # Create human interaction request
        context = f"I need your input for the task: {current_task.title if current_task else 'General question'}"
        if current_task:
            context += f"\nTask description: {current_task.description}"
        
        # Determine interaction type based on task and context
        interaction_type = self._determine_interaction_type(current_task, session)
        
        human_request = self._dialog_handler.create_human_interaction_request(
            interaction_type=interaction_type,
            context=context,
            task=current_task,
            available_dialog_options=dialog_options
        )
        
        session["pending_human_request"] = human_request
        
        return AgentResponse(
            agent_id=agent_id,
            state=AgentState.WAITING_FOR_HUMAN,
            current_task=current_task,
            human_interaction_request=human_request,
            todo_list=session["todo_list"],
            token_summary=session["token_summary"]
        )

    async def _step6_evaluate_goal(self, agent_id: str, session: dict[str, Any]) -> AgentResponse:
        """Step 6: Is the goal reached? If no, create a new todo-list, If yes return the answer (async version)."""
        logger.info(f"🎯 Agent {agent_id}: Step 6 - Evaluating goal achievement (async)")
        
        requirement_analysis = session["requirement_analysis"]
        todo_list = session["todo_list"]
        conversation_history = session["conversation_history"]
        
        # Prepare task results summary
        completed_tasks = [task for task in todo_list.tasks if task.status == TaskStatus.COMPLETED]
        failed_tasks = [task for task in todo_list.tasks if task.status == TaskStatus.FAILED]
        
        tasks_summary = "Completed Tasks:\n"
        for task in completed_tasks:
            tasks_summary += f"- {task.title}: {task.result or 'Completed'}\n"
        
        if failed_tasks:
            tasks_summary += "\nFailed Tasks:\n"
            for task in failed_tasks:
                tasks_summary += f"- {task.title}: {task.error_message or 'Failed'}\n"
        
        evaluation_prompt = f"""
Evaluate whether the original goal has been achieved based on the work completed:

Original Goal: {requirement_analysis.goal}
Success Criteria: {', '.join(requirement_analysis.success_criteria)}

{tasks_summary}

Determine:
1. Whether the main goal has been achieved (true/false)
2. Percentage of goal completion (0-100)
3. Which success criteria have been met
4. Which success criteria still need to be met
5. Detailed feedback on the goal achievement
6. Next steps if the goal is not fully achieved

Provide a comprehensive evaluation of goal achievement.
"""
        
        messages = [{"role": "user", "content": evaluation_prompt}]
        
        try:
            response = await self._ai_client.parse(conversation_history + messages, GoalEvaluation)
            goal_evaluation = self._extract_parsed_content(response, GoalEvaluation)
            token_usage = self._extract_token_usage(response)
            
            # Update session
            session["goal_evaluation"] = goal_evaluation
            session["token_summary"].goal_evaluation = token_usage
            
            if goal_evaluation.goal_achieved:
                # Goal achieved, generate final response
                logger.info(f"🎯 Agent {agent_id}: Goal achieved! Generating final response")
                return await self._generate_final_response(agent_id, session)
            else:
                # Goal not achieved, complete with partial success for now
                logger.info(f"🎯 Agent {agent_id}: Goal not fully achieved ({goal_evaluation.completion_percentage}%), completing with current progress")
                return await self._generate_final_response(agent_id, session)
            
        except Exception as e:
            logger.error(f"Failed to evaluate goal: {e}")
            session["state"] = AgentState.FAILED
            return AgentResponse(
                agent_id=agent_id,
                state=AgentState.FAILED,
                final_response=f"Failed to evaluate goal: {str(e)}",
                token_summary=session["token_summary"]
            )

    async def _generate_final_response(self, agent_id: str, session: dict[str, Any]) -> AgentResponse:
        """Generate the final response in the requested format (async version)."""
        logger.info(f"📝 Agent {agent_id}: Generating final structured response (async)")
        
        requirement_analysis = session["requirement_analysis"]
        goal_evaluation = session.get("goal_evaluation")
        todo_list = session["todo_list"]
        final_response_structure = session["final_response_structure"]
        conversation_history = session["conversation_history"]
        
        # Prepare summary of work done
        completed_tasks = [task for task in todo_list.tasks if task.status == TaskStatus.COMPLETED]
        work_summary = "Work completed:\n"
        for task in completed_tasks:
            work_summary += f"- {task.title}: {task.result or 'Completed'}\n"
        
        evaluation_text = ""
        if goal_evaluation:
            evaluation_text = f"\nGoal Achievement: {goal_evaluation.completion_percentage}% complete\nFeedback: {goal_evaluation.feedback}"
        
        final_prompt = f"""
Based on the work completed for this goal:
Goal: {requirement_analysis.goal}

{work_summary}{evaluation_text}

Generate the final response in the exact format requested. Summarize the results and provide a comprehensive answer that addresses the original requirement.
"""
        
        messages = [{"role": "user", "content": final_prompt}]
        
        try:
            response = await self._ai_client.parse(conversation_history + messages, final_response_structure)
            final_response = self._extract_parsed_content(response, final_response_structure)
            token_usage = self._extract_token_usage(response)
            
            # Update session
            session["token_summary"].final_response = token_usage
            session["final_response"] = final_response
            session["state"] = AgentState.COMPLETED
            
            logger.info(f"📝 Agent {agent_id}: Final response generated successfully")
            
            return AgentResponse(
                agent_id=agent_id,
                state=AgentState.COMPLETED,
                final_response=final_response,
                goal_evaluation=goal_evaluation,
                token_summary=session["token_summary"]
            )
            
        except Exception as e:
            logger.error(f"Failed to generate final response: {e}")
            # Fallback response
            try:
                fallback_response = self._create_fallback_response(final_response_structure, str(e))
                session["final_response"] = fallback_response
                session["state"] = AgentState.COMPLETED
                
                return AgentResponse(
                    agent_id=agent_id,
                    state=AgentState.COMPLETED,
                    final_response=fallback_response,
                    token_summary=session["token_summary"]
                )
            except Exception as fallback_error:
                logger.error(f"Fallback response creation failed: {fallback_error}")
                session["state"] = AgentState.FAILED
                return AgentResponse(
                    agent_id=agent_id,
                    state=AgentState.FAILED,
                    final_response=f"Failed to generate response: {str(e)}",
                    token_summary=session["token_summary"]
                )

    # Essential helper methods
    def _handle_human_responses(self, session: dict[str, Any], human_response: Union[HumanInLoopResponse, HumanInLoopResponseBatch, list[HumanInLoopResponse]]) -> dict[str, Any]:
        """Handle human response(s) - supports single response, batch, or list."""
        # Normalize input to a list of responses
        responses = []
        
        if isinstance(human_response, HumanInLoopResponse):
            responses = [human_response]
        elif isinstance(human_response, HumanInLoopResponseBatch):
            responses = human_response.responses
        elif isinstance(human_response, list):
            responses = human_response
        else:
            logger.warning(f"Unknown human response type: {type(human_response)}")
            return session
        
        # Process each response
        for response in responses:
            session = self._handle_human_response(session, response)
        
        return session

    def _handle_human_response(self, session: dict[str, Any], human_response: HumanInLoopResponse) -> dict[str, Any]:
        """Handle human response and update session accordingly."""
        pending_request = session.get("pending_human_request")
        if not pending_request or pending_request.id != human_response.interaction_id:
            logger.warning("Received human response for unknown or expired interaction")
            return session
        
        # For now, just continue with execution
        session["state"] = AgentState.EXECUTING_TASKS
        session.pop("pending_human_request", None)
        
        # Store human input for context
        if human_response.answer:
            session["human_context"] = session.get("human_context", "") + f"\nUser: {human_response.answer}"
        if human_response.additional_context:
            session["human_context"] = session.get("human_context", "") + f"\nContext: {human_response.additional_context}"
        
        return session

    def _should_request_human_interaction(self, task: Task, session: dict[str, Any]) -> bool:
        """Determine if human interaction is needed for a task."""
        # Request human interaction for high complexity tasks
        if task.estimated_complexity >= 4:
            return True
        
        # Check if task requires capabilities we don't have
        tool_analysis = session.get("tool_analysis")
        if tool_analysis and tool_analysis.missing_capabilities:
            for capability in tool_analysis.missing_capabilities:
                if capability.lower() in task.description.lower():
                    return True
        
        return False

    def _determine_interaction_type(self, task: Optional[Task], session: dict[str, Any]) -> HumanInteractionType:
        """Determine the appropriate interaction type for a task."""
        if not task:
            return HumanInteractionType.QUESTION
        
        # If we have dialog options available, prefer those
        dialog_options = session.get("dialog_options", [])
        if dialog_options:
            return HumanInteractionType.DIALOG_OPTION
        
        # For high complexity tasks, use decision
        if task.estimated_complexity >= 4:
            return HumanInteractionType.DECISION
        
        # Default to question
        return HumanInteractionType.QUESTION

    async def _execute_task(self, task: Task, session: dict[str, Any], conversation_history: list[dict[str, Any]]) -> tuple[str, TokenUsage]:
        """Execute a task and return the result (async version)."""
        # Prepare context
        requirement = session["requirement_analysis"]
        human_context = session.get("human_context", "")
        
        execution_prompt = f"""
Execute this task to help achieve the goal:
Goal: {requirement.goal}
Task: {task.title}
Description: {task.description}
Tools needed: {', '.join(task.tools_needed) if task.tools_needed else 'None'}

{human_context}

Use any available tools to complete this task. Provide a detailed result of what was accomplished.
If the task cannot be completed with available tools, explain what was attempted and what is missing.
"""
        
        messages = [{"role": "user", "content": execution_prompt}]
        
        try:
            response = await self._ai_client.parse(conversation_history + messages, Result)
            result_obj = self._extract_parsed_content(response, Result)
            token_usage = self._extract_token_usage(response)
            
            return result_obj.result, token_usage
            
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            return f"Task execution failed: {str(e)}", TokenUsage()

    def _get_available_tools(self) -> dict[str, str]:
        """Get available tools from the AI client."""
        tools = {}
        
        # Try to get tools from different client types
        if hasattr(self._ai_client, 'tools') and self._ai_client.tools:
            for tool in self._ai_client.tools:
                tools[tool.name] = tool.description
        elif hasattr(self._ai_client, '_tools') and self._ai_client._tools:
            for tool in self._ai_client._tools:
                tools[tool.name] = tool.description
        
        return tools

    def _extract_parsed_content(self, response: Any, response_format: Type[BaseModel]) -> BaseModel:
        """Extract the parsed content from the AI response."""
        if hasattr(response, 'choices') and len(response.choices) > 0:
            choice = response.choices[0]
            if hasattr(choice.message, 'parsed') and choice.message.parsed:
                return choice.message.parsed
            elif hasattr(choice.message, 'content'):
                try:
                    content_dict = json.loads(choice.message.content)
                    return response_format(**content_dict)
                except (json.JSONDecodeError, TypeError):
                    # Create default response based on type
                    return self._create_fallback_response(response_format)
        
        return self._create_fallback_response(response_format)

    def _create_fallback_response(self, response_format: Type[BaseModel], error_msg: str = "") -> BaseModel:
        """Create a fallback response when parsing fails."""
        try:
            if response_format == RequirementAnalysis:
                return RequirementAnalysis(
                    goal="Goal analysis failed",
                    success_criteria=["Unable to determine criteria"],
                    complexity_estimate=5
                )
            elif response_format == ToolAnalysis:
                return ToolAnalysis(
                    relevant_tools=[],
                    tool_mapping={},
                    missing_capabilities=["Analysis failed"]
                )
            elif response_format == TodoList:
                return TodoList(tasks=[])
            elif response_format == GoalEvaluation:
                return GoalEvaluation(
                    goal_achieved=False,
                    completion_percentage=0,
                    completed_criteria=[],
                    remaining_criteria=["Evaluation failed"],
                    feedback=f"Goal evaluation failed: {error_msg}"
                )
            elif response_format == Result:
                return Result(result=f"Result generation failed: {error_msg}")
            else:
                # Try to create with default values
                return response_format()
        except Exception:
            # Last resort - return basic result
            return Result(result=f"Failed to create response: {error_msg}")

    def _extract_token_usage(self, response: Any) -> TokenUsage:
        """Extract token usage information from an AI response."""
        try:
            if hasattr(response, 'usage') and response.usage:
                usage = response.usage
                return TokenUsage(
                    prompt_tokens=getattr(usage, 'prompt_tokens', 0),
                    completion_tokens=getattr(usage, 'completion_tokens', 0),
                    total_tokens=getattr(usage, 'total_tokens', 0)
                )
        except (AttributeError, TypeError) as e:
            logger.debug(f"Could not extract token usage: {e}")
        
        return TokenUsage()

    # Session management methods (kept for compatibility)
    def get_session_info(self, agent_id: str) -> dict[str, Any]:
        """Get information about an agent session."""
        session = self._session_handler.get_session(agent_id)
        if not session:
            raise ValueError(f"Agent session {agent_id} not found")
        
        session = session.copy()
        session["conversation_length"] = len(session.get("conversation_history", []))
        return session

    def delete_session(self, agent_id: str) -> bool:
        """Delete an agent session."""
        deleted = self._session_handler.delete_session(agent_id)
        if deleted:
            logger.info(f"🗑️ Deleted agent session {agent_id}")
        return deleted

    def list_sessions(self) -> list[str]:
        """List all active agent session IDs."""
        return self._session_handler.list_sessions()
