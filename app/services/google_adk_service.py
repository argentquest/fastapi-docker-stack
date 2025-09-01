# V2 Google ADK Service
"""
This service uses Google's Agent Development Kit (ADK) for AI agent functionality.

The Google ADK provides a more sophisticated agent framework compared to direct API calls,
supporting tools, multi-agent workflows, and enhanced orchestration capabilities.
Key features include:
- Agent-based architecture with tool support
- Enhanced model orchestration via ADK framework
- Built-in agent evaluation and monitoring
- Multi-agent composition and delegation
"""

import logging
from typing import Optional, List, Dict, Any
from google.adk import Agent, Runner
from app.core.config import settings

logger = logging.getLogger(__name__)


class GoogleADKService:
    """
    A service class for interacting with Google AI using the Agent Development Kit (ADK).
    
    This provides a more advanced agent-based approach compared to direct API calls,
    supporting sophisticated workflows, tools, and multi-agent orchestration.
    
    Attributes:
        agent: A configured ADK Agent instance
        runner: A configured ADK Runner instance
        is_available: Boolean indicating if the service is ready for use
    """

    def __init__(self):
        """Initializes the GoogleADKService and creates the base agent."""
        self.agent = None
        self.runner = None
        self.is_available = False
        
        # Check API key first
        if not settings.GOOGLE_API_KEY:
            logger.warning("Google API key is not configured. ADK service will not be available.")
            self.is_available = False
            return
            
        try:
            self.agent = self._create_agent()
            # Create Runner with required parameters
            self.runner = Runner(
                app_name="v2_poc_adk",
                agent=self.agent,
                session_service=None  # Use default session service
            )
            self.is_available = True
            logger.info("Google ADK service initialized successfully")
        except ImportError as e:
            logger.warning(f"Google ADK import failed: {e}. Service will not be available.")
            self.is_available = False
        except Exception as e:
            logger.warning(f"Google ADK service initialization failed: {e}")
            self.is_available = False

    def _create_agent(self) -> Agent:
        """
        Creates and configures the ADK Agent.

        Raises:
            ValueError: If the Google API key is not set in the environment.

        Returns:
            An instance of `google.adk.Agent`.
        """
        if not settings.GOOGLE_API_KEY:
            logger.warning("Google API key is not configured. ADK service will not be available.")
            raise ValueError("GOOGLE_API_KEY is not set in the environment.")

        logger.info("Initializing Google ADK Agent")

        try:
            # Create a general-purpose ADK agent similar to google_ai_service functionality
            agent = Agent(
                name="v2_poc_agent",
                model="gemini-2.5-flash-image-preview",  # Match the model from google_ai_service
                description="V2 POC agent for general AI assistance and response generation",
                instruction="""You are a helpful AI assistant for the V2 POC application. 
                Provide accurate, helpful responses based on the user's context and system prompts.
                Always be concise and professional in your responses."""
            )
            
            logger.info("Google ADK Agent initialized successfully")
            return agent
            
        except Exception as e:
            logger.error(f"Failed to initialize Google ADK Agent: {e}")
            raise ValueError(f"Failed to create ADK Agent: {e}")

    async def generate_response(
        self, 
        system_prompt: str, 
        user_context: str, 
        model: Optional[str] = None,
        temperature: float = 0.7, 
        max_tokens: int = 2000,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generates a response using the ADK Agent framework.

        Args:
            system_prompt: The instruction or persona for the AI.
            user_context: The user's query or input.
            model: The specific Gemini model to use (defaults to agent's configured model).
            temperature: Controls the creativity of the response (0.0 to 2.0).
            max_tokens: The maximum number of tokens in the generated response.
            conversation_history: Optional list of previous messages for context.

        Returns:
            The content of the AI's response as a string.

        Raises:
            RuntimeError: If the ADK agent is not available or the request fails.
        """
        if not self.is_available or not self.agent:
            raise RuntimeError("Google ADK service is not available. Please configure GOOGLE_API_KEY.")
            
        logger.info(f"Generating ADK response with model: {model or 'agent default'}, temperature: {temperature}, max_tokens: {max_tokens}")
        logger.debug(f"System prompt length: {len(system_prompt)} chars, User context length: {len(user_context)} chars")

        try:
            # Combine system prompt and user context for the agent
            # ADK agents work with direct prompts rather than separate system/user messages
            full_prompt = f"{system_prompt}\n\nUser: {user_context}"
            
            # Add conversation history if provided
            if conversation_history:
                history_text = "\n\nConversation History:\n"
                for msg in conversation_history:
                    role = msg.get("role", "unknown")
                    content = msg.get("content", "")
                    history_text += f"{role.title()}: {content}\n"
                full_prompt = history_text + "\n" + full_prompt

            logger.debug("Sending request to ADK Agent...")
            
            # Use the ADK Runner to execute the agent
            # ADK uses Runner.run_async for programmatic execution
            if not self.runner:
                raise RuntimeError("ADK Runner not initialized")
            
            response = await self.runner.run_async(
                agent=self.agent,
                prompt=full_prompt
            )
            
            if not response:
                logger.warning("Received an empty response from ADK Agent")
                raise ValueError("No content in response from ADK Agent")

            # Extract response content (ADK response structure may vary)
            content = str(response) if not hasattr(response, 'content') else response.content
            
            logger.info(f"Successfully generated ADK response of {len(content)} characters")
            return content.strip()

        except Exception as e:
            logger.error(f"Error generating ADK response: {e}", exc_info=True)
            raise RuntimeError(f"Google ADK agent call failed: {e}")

    async def health_check(self) -> dict:
        """
        Performs a health check on the Google ADK service.

        This check verifies that the ADK agent is properly configured and can generate responses.

        Returns:
            A dictionary containing the health status.
        """
        logger.debug("Starting Google ADK health check...")
        
        if not self.is_available or not self.agent:
            return {
                "status": "unavailable",
                "error": "Google API key not configured or ADK agent not initialized",
                "service": "Google ADK"
            }
        
        try:
            # Simple health check with minimal token usage
            logger.debug("Testing ADK agent connectivity...")

            response = await self.generate_response(
                system_prompt="You are a health check assistant.",
                user_context="Reply with exactly: 'ADK OK'",
                max_tokens=20
            )

            logger.info(f"Google ADK health check completed successfully, response: '{response}'")
            return {
                "status": "healthy",
                "details": "ADK agent is properly configured and responsive.",
                "model": "gemini-2.5-flash-image-preview",
                "framework": "Google ADK",
                "service": "Google ADK"
            }
        except Exception as e:
            logger.error(f"Google ADK health check failed: {e}", exc_info=True)
            return {"status": "error", "error": str(e), "service": "Google ADK"}

    def get_agent_info(self) -> dict:
        """
        Returns information about the configured ADK agent.
        
        Returns:
            Dictionary with agent configuration details.
        """
        if not self.is_available or not self.agent:
            return {"error": "ADK agent not available"}
            
        return {
            "name": getattr(self.agent, 'name', 'unknown'),
            "model": getattr(self.agent, 'model', 'unknown'),
            "description": getattr(self.agent, 'description', 'No description'),
            "tools_count": len(getattr(self.agent, 'tools', [])),
            "framework": "Google ADK",
            "status": "initialized"
        }


# Create a single, global instance of the GoogleADKService
google_adk_service = GoogleADKService()