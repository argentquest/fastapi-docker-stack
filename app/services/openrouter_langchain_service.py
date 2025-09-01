# V2 OpenRouter LangChain Service
"""
This service provides LangChain-based integration with OpenRouter.ai API.

It uses LangChain's ChatOpenAI interface for more advanced conversational AI capabilities
including memory, chains, and advanced prompt management.
"""

import logging
from typing import Optional, List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenRouterLangChainService:
    """
    A LangChain-based service for interacting with OpenRouter API.
    
    Provides advanced conversational AI capabilities with memory,
    prompt templates, and chain-based interactions.
    """

    def __init__(self):
        """Initializes the OpenRouterLangChainService."""
        self.llm = self._create_langchain_client()

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

        logger.info(f"Initializing LangChain OpenRouter client with base URL: {settings.OPENROUTER_BASE_URL}")

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

        logger.info("LangChain OpenRouter client initialized successfully")
        return llm

    async def generate_response_langchain(
        self, 
        system_prompt: str, 
        user_context: str, 
        model: Optional[str] = None,
        temperature: float = 0.7, 
        max_tokens: int = 2000,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generates a chat completion response using LangChain with OpenRouter.

        Args:
            system_prompt: The instruction or persona for the AI.
            user_context: The user's query or input.
            model: The specific model to use. Defaults to settings.DEFAULT_MODEL.
            temperature: Controls the creativity of the response (0.0 to 2.0).
            max_tokens: The maximum number of tokens in the generated response.
            conversation_history: Optional list of previous messages for context.

        Returns:
            The content of the AI's response as a string.

        Raises:
            RuntimeError: If the API call fails or returns an empty response.
        """
        target_model = model or settings.DEFAULT_MODEL
        logger.info(f"Generating LangChain AI response using model: {target_model}, temperature: {temperature}, max_tokens: {max_tokens}")
        logger.debug(f"System prompt length: {len(system_prompt)} chars, User context length: {len(user_context)} chars")

        try:
            # Update model parameters if different from default
            if target_model != settings.DEFAULT_MODEL or temperature != 0.7 or max_tokens != 2000:
                llm = self.llm.bind(
                    model=target_model,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            else:
                llm = self.llm

            # Build message list
            messages: List[BaseMessage] = []
            
            # Add system message
            messages.append(SystemMessage(content=system_prompt))
            
            # Add conversation history if provided
            if conversation_history:
                for msg in conversation_history:
                    if msg.get("role") == "user":
                        messages.append(HumanMessage(content=msg["content"]))
                    elif msg.get("role") == "assistant":
                        messages.append(SystemMessage(content=msg["content"]))  # Use SystemMessage for assistant responses
            
            # Add current user message
            messages.append(HumanMessage(content=user_context))

            logger.debug(f"Sending {len(messages)} messages to LangChain...")
            
            # Generate response using LangChain
            response = await llm.ainvoke(messages)
            
            if not response or not response.content:
                logger.warning("Received an empty response from LangChain OpenRouter")
                raise ValueError("No content in response from LangChain OpenRouter")

            content = response.content
            logger.info(f"Successfully generated LangChain AI response of {len(content)} characters using {target_model}")
            
            return content.strip()

        except Exception as e:
            logger.error(f"Error generating LangChain OpenRouter response with model {target_model}: {e}", exc_info=True)
            raise RuntimeError(f"LangChain OpenRouter API call failed: {e}")

    async def generate_with_template(
        self,
        template: str,
        template_variables: Dict[str, Any],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Generates a response using a LangChain prompt template.

        Args:
            template: The prompt template with variable placeholders.
            template_variables: Dictionary of variables to fill in the template.
            model: The specific model to use.
            temperature: Controls the creativity of the response.
            max_tokens: The maximum number of tokens in the generated response.

        Returns:
            The content of the AI's response as a string.
        """
        target_model = model or settings.DEFAULT_MODEL
        logger.info(f"Generating response using LangChain template with model: {target_model}")
        
        try:
            # Create prompt template
            prompt = ChatPromptTemplate.from_template(template)
            
            # Update model parameters if needed
            if target_model != settings.DEFAULT_MODEL or temperature != 0.7 or max_tokens != 2000:
                llm = self.llm.bind(
                    model=target_model,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            else:
                llm = self.llm
            
            # Create chain
            chain = prompt | llm
            
            # Generate response
            response = await chain.ainvoke(template_variables)
            
            if not response or not response.content:
                logger.warning("Received an empty response from LangChain template")
                raise ValueError("No content in response from LangChain template")

            content = response.content
            logger.info(f"Successfully generated templated response of {len(content)} characters")
            
            return content.strip()

        except Exception as e:
            logger.error(f"Error generating LangChain template response: {e}", exc_info=True)
            raise RuntimeError(f"LangChain template call failed: {e}")

    async def health_check_langchain(self) -> dict:
        """
        Performs a health check using LangChain.

        Returns:
            A dictionary containing the health status.
        """
        logger.debug("Starting LangChain OpenRouter health check...")
        try:
            response = await self.generate_response_langchain(
                system_prompt="You are a health check assistant.",
                user_context="Reply with a single word: ok",
                max_tokens=20
            )

            logger.info(f"LangChain OpenRouter health check completed successfully, response: '{response}'")
            return {
                "status": "healthy",
                "details": "LangChain API integration is working properly.",
                "model": settings.DEFAULT_MODEL,
                "framework": "LangChain"
            }
        except Exception as e:
            logger.error(f"LangChain OpenRouter health check failed: {e}", exc_info=True)
            return {"status": "error", "error": str(e), "framework": "LangChain"}


# Create a single, global instance of the OpenRouterLangChainService
openrouter_langchain_service = OpenRouterLangChainService()