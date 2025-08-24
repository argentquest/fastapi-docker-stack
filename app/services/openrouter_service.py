# V2 OpenRouter Service
"""
This service acts as a client for the OpenRouter.ai API.

It uses the `openai` Python library, which is compatible with OpenRouter's API structure.
Key features include:
- A configured client that sends appropriate headers for OpenRouter.
- A method for generating chat-based AI responses.
- A health check to verify connectivity and API key validity.
"""

import logging
from typing import Optional
import openai
from app.core.config import settings

logger = logging.getLogger(__name__)

class OpenRouterService:
    """
    A service class for interacting with the OpenRouter API.

    Attributes:
        client: An `openai.AsyncOpenAI` client instance configured for OpenRouter.
    """

    def __init__(self):
        """Initializes the OpenRouterService and its API client."""
        self.client = self._create_client()

    def _create_client(self) -> openai.AsyncOpenAI:
        """
        Creates and configures the asynchronous OpenAI client for OpenRouter.

        Raises:
            ValueError: If the OpenRouter API key is not set in the environment.

        Returns:
            An instance of `openai.AsyncOpenAI`.
        """
        if not settings.OPENROUTER_API_KEY:
            logger.critical("OpenRouter API key is not configured. Service cannot start.")
            raise ValueError("OPENROUTER_API_KEY is not set in the environment.")
        
        # OpenRouter allows identifying your app with specific headers.
        default_headers = {
            "HTTP-Referer": settings.OPENROUTER_SITE_URL, 
            "X-Title": settings.OPENROUTER_APP_NAME
        }
        
        logger.debug("Creating OpenRouter client.")
        return openai.AsyncOpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL,
            default_headers={k: v for k, v in default_headers.items() if v} # Remove empty headers
        )

    async def generate_response(
        self, system_prompt: str, user_context: str, model: Optional[str] = None,
        temperature: float = 0.7, max_tokens: int = 2000
    ) -> str:
        """
        Generates a chat completion response from an AI model via OpenRouter.

        Args:
            system_prompt: The instruction or persona for the AI.
            user_context: The user's query or input.
            model: The specific model to use (e.g., 'deepseek/deepseek-r1'). 
                   Defaults to the one in settings.
            temperature: Controls the creativity of the response (0.0 to 2.0).
            max_tokens: The maximum number of tokens in the generated response.

        Returns:
            The content of the AI's response as a string.

        Raises:
            RuntimeError: If the API call fails or returns an empty response.
        """
        target_model = model or settings.DEFAULT_MODEL
        logger.info(f"Generating AI response using model: {target_model}")
        
        try:
            response = await self.client.chat.completions.create(
                model=target_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_context}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            if not response.choices or not response.choices[0].message.content:
                logger.warning("Received an empty response from OpenRouter.")
                raise ValueError("No content in response from OpenRouter.")
                
            content = response.choices[0].message.content
            logger.info(f"Successfully generated AI response of {len(content)} characters.")
            return content.strip()
            
        except Exception as e:
            logger.error(f"Error generating OpenRouter response: {e}", exc_info=True)
            raise RuntimeError(f"OpenRouter API call failed: {e}")

    async def health_check(self) -> dict:
        """
        Performs a health check on the OpenRouter service.

        This check verifies that the API key is valid and that a model can be reached.

        Returns:
            A dictionary containing the health status.
        """
        try:
            # A simple, low-token request to verify connectivity and authentication.
            await self.generate_response(
                system_prompt="You are a health check assistant.",
                user_context="Reply with a single word: ok",
                max_tokens=5
            )
            return {"status": "healthy", "details": "API key is valid and service is reachable."}
        except Exception as e:
            logger.error(f"OpenRouter health check failed: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}

# Create a single, global instance of the OpenRouterService.
# This instance will be imported and used by other parts of the application.
openrouter_service = OpenRouterService()
