# V2 OpenRouter LangGraph Service
"""
This service provides LangGraph-based integration with OpenRouter.ai API.

It uses LangGraph's StateGraph for complex workflow management and state-based
AI interactions, allowing for multi-step reasoning and complex decision trees.
"""

import logging
from typing import Optional, List, Dict, Any, TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from app.core.config import settings

logger = logging.getLogger(__name__)


class WorkflowState(TypedDict):
    """State structure for LangGraph workflows."""
    messages: List[BaseMessage]
    system_prompt: str
    user_context: str
    model: str
    temperature: float
    max_tokens: int
    current_step: str
    response: str
    metadata: Dict[str, Any]


class OpenRouterLangGraphService:
    """
    A LangGraph-based service for workflow-driven interactions with OpenRouter API.
    
    Provides advanced state management, multi-step reasoning, and complex
    decision-making capabilities through graph-based workflows.
    """

    def __init__(self):
        """Initializes the OpenRouterLangGraphService."""
        self.llm = self._create_langchain_client()
        self.memory = MemorySaver()
        self.workflow = self._create_workflow()

    def _create_langchain_client(self) -> ChatOpenAI:
        """
        Creates and configures the LangChain ChatOpenAI client for OpenRouter.

        Returns:
            An instance of ChatOpenAI configured for OpenRouter.
            
        Raises:
            ValueError: If the OpenRouter API key is not set.
        """
        if not settings.OPENROUTER_API_KEY:
            logger.critical("OpenRouter API key is not configured. Service cannot start.")
            raise ValueError("OPENROUTER_API_KEY is not set in the environment.")

        logger.info(f"Initializing LangGraph OpenRouter client with base URL: {settings.OPENROUTER_BASE_URL}")

        # Configure LangChain ChatOpenAI for OpenRouter
        llm = ChatOpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL,
            model=settings.DEFAULT_MODEL,
            temperature=0.7,
            max_tokens=2000,
            default_headers={
                "HTTP-Referer": settings.OPENROUTER_SITE_URL,
                "X-Title": settings.OPENROUTER_APP_NAME
            }
        )

        logger.info("LangGraph OpenRouter client initialized successfully")
        return llm

    def _create_workflow(self) -> StateGraph:
        """
        Creates the LangGraph workflow for complex AI interactions.
        
        Returns:
            A configured StateGraph workflow.
        """
        workflow = StateGraph(WorkflowState)
        
        # Define workflow nodes
        workflow.add_node("prepare_messages", self._prepare_messages)
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("validate_response", self._validate_response)
        workflow.add_node("finalize_response", self._finalize_response)
        
        # Define workflow edges
        workflow.set_entry_point("prepare_messages")
        workflow.add_edge("prepare_messages", "generate_response")
        workflow.add_edge("generate_response", "validate_response")
        workflow.add_conditional_edges(
            "validate_response",
            self._should_regenerate,
            {
                "regenerate": "generate_response",
                "finalize": "finalize_response"
            }
        )
        workflow.add_edge("finalize_response", END)
        
        return workflow.compile(checkpointer=self.memory)

    async def _prepare_messages(self, state: WorkflowState) -> WorkflowState:
        """Prepares the message list for the AI model."""
        logger.debug("Preparing messages for AI generation")
        
        messages: List[BaseMessage] = []
        
        # Add system message
        if state["system_prompt"]:
            messages.append(SystemMessage(content=state["system_prompt"]))
        
        # Add user message
        if state["user_context"]:
            messages.append(HumanMessage(content=state["user_context"]))
        
        state["messages"] = messages
        state["current_step"] = "prepare_messages"
        
        logger.debug(f"Prepared {len(messages)} messages for processing")
        return state

    async def _generate_response(self, state: WorkflowState) -> WorkflowState:
        """Generates AI response using the configured model."""
        logger.debug(f"Generating response using model: {state['model']}")
        
        try:
            # Configure model with current parameters
            llm = self.llm.bind(
                model=state["model"],
                temperature=state["temperature"],
                max_tokens=state["max_tokens"]
            )
            
            # Generate response
            response = await llm.ainvoke(state["messages"])
            
            if response and response.content:
                state["response"] = response.content.strip()
                state["current_step"] = "generate_response"
                logger.debug(f"Generated response of {len(state['response'])} characters")
            else:
                state["response"] = ""
                logger.warning("Received empty response from AI model")
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            state["response"] = ""
            state["metadata"]["error"] = str(e)
        
        return state

    async def _validate_response(self, state: WorkflowState) -> WorkflowState:
        """Validates the generated response for quality and completeness."""
        logger.debug("Validating generated response")
        
        response = state["response"]
        metadata = state.get("metadata", {})
        
        # Basic validation checks
        validation_passed = True
        validation_errors = []
        
        if not response:
            validation_passed = False
            validation_errors.append("Empty response")
        
        if len(response) < 10:
            validation_passed = False
            validation_errors.append("Response too short")
        
        # Store validation results
        metadata["validation_passed"] = validation_passed
        metadata["validation_errors"] = validation_errors
        metadata["retry_count"] = metadata.get("retry_count", 0)
        
        state["metadata"] = metadata
        state["current_step"] = "validate_response"
        
        logger.debug(f"Validation result: {'passed' if validation_passed else 'failed'}")
        return state

    def _should_regenerate(self, state: WorkflowState) -> str:
        """Determines whether to regenerate the response or finalize it."""
        metadata = state.get("metadata", {})
        validation_passed = metadata.get("validation_passed", True)
        retry_count = metadata.get("retry_count", 0)
        
        # Regenerate if validation failed and we haven't retried too many times
        if not validation_passed and retry_count < 2:
            metadata["retry_count"] = retry_count + 1
            state["metadata"] = metadata
            logger.debug(f"Regenerating response (attempt {retry_count + 1})")
            return "regenerate"
        
        logger.debug("Finalizing response")
        return "finalize"

    async def _finalize_response(self, state: WorkflowState) -> WorkflowState:
        """Finalizes the response and prepares the final output."""
        logger.debug("Finalizing response")
        
        state["current_step"] = "finalize_response"
        
        # Log final statistics
        metadata = state.get("metadata", {})
        retry_count = metadata.get("retry_count", 0)
        validation_passed = metadata.get("validation_passed", True)
        
        logger.info(f"Response finalized - Length: {len(state['response'])}, "
                   f"Retries: {retry_count}, Validation: {'passed' if validation_passed else 'failed'}")
        
        return state

    async def generate_response_langgraph(
        self, 
        system_prompt: str, 
        user_context: str, 
        model: Optional[str] = None,
        temperature: float = 0.7, 
        max_tokens: int = 2000,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        thread_id: Optional[str] = None
    ) -> str:
        """
        Generates a chat completion response using LangGraph workflow with OpenRouter.

        Args:
            system_prompt: The instruction or persona for the AI.
            user_context: The user's query or input.
            model: The specific model to use. Defaults to settings.DEFAULT_MODEL.
            temperature: Controls the creativity of the response (0.0 to 2.0).
            max_tokens: The maximum number of tokens in the generated response.
            conversation_history: Optional list of previous messages for context.
            thread_id: Optional thread ID for conversation continuity.

        Returns:
            The content of the AI's response as a string.

        Raises:
            RuntimeError: If the workflow execution fails.
        """
        target_model = model or settings.DEFAULT_MODEL
        logger.info(f"Generating LangGraph AI response using model: {target_model}, "
                   f"temperature: {temperature}, max_tokens: {max_tokens}")
        
        try:
            # Initialize workflow state
            initial_state: WorkflowState = {
                "messages": [],
                "system_prompt": system_prompt,
                "user_context": user_context,
                "model": target_model,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "current_step": "init",
                "response": "",
                "metadata": {
                    "conversation_history": conversation_history or [],
                    "thread_id": thread_id,
                    "retry_count": 0
                }
            }
            
            # Execute the workflow
            config = {"configurable": {"thread_id": thread_id or "default"}}
            final_state = await self.workflow.ainvoke(initial_state, config=config)
            
            response_content = final_state.get("response", "")
            if not response_content:
                logger.warning("Workflow completed but produced empty response")
                raise ValueError("No content generated by LangGraph workflow")
            
            logger.info(f"Successfully generated LangGraph AI response of {len(response_content)} characters")
            return response_content
            
        except Exception as e:
            logger.error(f"Error in LangGraph workflow with model {target_model}: {e}", exc_info=True)
            raise RuntimeError(f"LangGraph workflow failed: {e}")

    async def generate_with_workflow(
        self,
        workflow_type: str,
        context: Dict[str, Any],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        thread_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates a response using a specific workflow type.

        Args:
            workflow_type: The type of workflow to execute ('simple', 'complex', 'creative').
            context: Dictionary containing workflow-specific context.
            model: The specific model to use.
            temperature: Controls the creativity of the response.
            max_tokens: The maximum number of tokens in the generated response.
            thread_id: Optional thread ID for conversation continuity.

        Returns:
            Dictionary containing the response and workflow metadata.
        """
        target_model = model or settings.DEFAULT_MODEL
        logger.info(f"Executing {workflow_type} workflow with model: {target_model}")
        
        # Prepare workflow-specific prompts
        workflow_prompts = {
            "simple": "You are a helpful assistant. Provide clear, concise answers.",
            "complex": "You are an expert analyst. Provide detailed, well-reasoned responses with multiple perspectives.",
            "creative": "You are a creative storytelling assistant. Generate imaginative, engaging content."
        }
        
        system_prompt = workflow_prompts.get(workflow_type, workflow_prompts["simple"])
        user_context = context.get("query", "")
        
        try:
            response = await self.generate_response_langgraph(
                system_prompt=system_prompt,
                user_context=user_context,
                model=target_model,
                temperature=temperature,
                max_tokens=max_tokens,
                thread_id=thread_id
            )
            
            return {
                "response": response,
                "workflow_type": workflow_type,
                "model": target_model,
                "metadata": {
                    "thread_id": thread_id,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
            }
            
        except Exception as e:
            logger.error(f"Error in {workflow_type} workflow: {e}")
            raise RuntimeError(f"Workflow execution failed: {e}")

    async def health_check_langgraph(self) -> dict:
        """
        Performs a health check using LangGraph workflow.

        Returns:
            A dictionary containing the health status and workflow information.
        """
        logger.debug("Starting LangGraph OpenRouter health check...")
        try:
            response = await self.generate_response_langgraph(
                system_prompt="You are a health check assistant.",
                user_context="Reply with a single word: ok",
                max_tokens=20,
                thread_id="health_check"
            )

            logger.info(f"LangGraph OpenRouter health check completed successfully, response: '{response}'")
            return {
                "status": "healthy",
                "details": "LangGraph workflow integration is working properly.",
                "model": settings.DEFAULT_MODEL,
                "framework": "LangGraph",
                "workflow_enabled": True
            }
        except Exception as e:
            logger.error(f"LangGraph OpenRouter health check failed: {e}", exc_info=True)
            return {
                "status": "error", 
                "error": str(e), 
                "framework": "LangGraph",
                "workflow_enabled": False
            }

    async def get_workflow_state(self, thread_id: str) -> Dict[str, Any]:
        """
        Retrieves the current state of a workflow thread.
        
        Args:
            thread_id: The thread ID to get state for.
            
        Returns:
            Dictionary containing the current workflow state.
        """
        try:
            config = {"configurable": {"thread_id": thread_id}}
            state = await self.workflow.aget_state(config)
            
            return {
                "thread_id": thread_id,
                "current_step": state.values.get("current_step", "unknown") if state.values else "unknown",
                "messages_count": len(state.values.get("messages", [])) if state.values else 0,
                "has_response": bool(state.values.get("response")) if state.values else False
            }
        except Exception as e:
            logger.error(f"Error retrieving workflow state for thread {thread_id}: {e}")
            return {"error": str(e), "thread_id": thread_id}


# Create a single, global instance of the OpenRouterLangGraphService
openrouter_langgraph_service = OpenRouterLangGraphService()