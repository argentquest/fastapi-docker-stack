# V2 Google AI Service
"""
This service acts as a client for the Google AI Gemini API.

It uses the `google-genai` Python library for accessing Google's Gemini models.
Key features include:
- A configured client that uses Google AI API key authentication.
- A method for generating chat-based AI responses using Gemini models.
- A health check to verify connectivity and API key validity.
"""

import logging
from typing import Optional, List, Dict
from google import genai
from app.core.config import settings

logger = logging.getLogger(__name__)


class GoogleAIService:
    """
    A service class for interacting with the Google AI Gemini API.

    Attributes:
        client: A `google.genai.Client` instance configured for Google AI.
    """

    def __init__(self):
        """Initializes the GoogleAIService and its API client."""
        self.client = None
        self.is_available = False
        try:
            self.client = self._create_client()
            self.is_available = True
        except ValueError as e:
            logger.warning(f"Google AI service initialization failed: {e}")
            self.is_available = False

    def _create_client(self) -> genai.Client:
        """
        Creates and configures the Google AI client.

        Raises:
            ValueError: If the Google API key is not set in the environment.

        Returns:
            An instance of `google.genai.Client`.
        """
        if not settings.GOOGLE_API_KEY:
            logger.warning("Google API key is not configured. Service will not be available.")
            raise ValueError("GOOGLE_API_KEY is not set in the environment.")

        logger.info("Initializing Google AI client")

        try:
            client = genai.Client(api_key=settings.GOOGLE_API_KEY)
            logger.info("Google AI client initialized successfully")
            return client
        except Exception as e:
            logger.error(f"Failed to initialize Google AI client: {e}")
            raise ValueError(f"Failed to create Google AI client: {e}")

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
        Generates a chat completion response from a Google AI Gemini model.

        Args:
            system_prompt: The instruction or persona for the AI.
            user_context: The user's query or input.
            model: The specific Gemini model to use (e.g., 'gemini-1.5-flash').
                   Defaults to the one in settings.
            temperature: Controls the creativity of the response (0.0 to 2.0).
            max_tokens: The maximum number of tokens in the generated response.
            conversation_history: Optional list of previous messages for context.

        Returns:
            The content of the AI's response as a string.

        Raises:
            RuntimeError: If the API call fails or returns an empty response.
        """
        if not self.is_available or not self.client:
            raise RuntimeError("Google AI service is not available. Please configure GOOGLE_API_KEY.")
            
        # Use provided model or fall back to gemini-2.5-flash-image-preview
        # This model supports both text and image generation
        target_model = model or "gemini-2.5-flash-image-preview"
        logger.info(f"Generating Google AI response using model: {target_model}, temperature: {temperature}, max_tokens: {max_tokens}")
        logger.debug(f"System prompt length: {len(system_prompt)} chars, User context length: {len(user_context)} chars")

        try:
            # Build message list with system prompt and conversation history
            messages = []
            
            # Add conversation history if provided
            if conversation_history:
                for msg in conversation_history:
                    if msg.get("role") == "user":
                        messages.append({"role": "user", "parts": [{"text": msg["content"]}]})
                    elif msg.get("role") == "assistant":
                        messages.append({"role": "model", "parts": [{"text": msg["content"]}]})
            
            # Combine system prompt with user context for Gemini
            combined_prompt = f"{system_prompt}\n\nUser: {user_context}"
            messages.append({"role": "user", "parts": [{"text": combined_prompt}]})

            logger.debug("Sending request to Google AI API...")
            
            # Configure generation parameters
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }

            response = await self.client.aio.models.generate_content(
                model=target_model,
                contents=messages,
                config=generation_config
            )

            if not response or not response.text:
                logger.warning("Received an empty response from Google AI")
                raise ValueError("No content in response from Google AI")

            content = response.text

            # Log token usage if available
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                usage = response.usage_metadata
                logger.info(f"Token usage - Prompt: {usage.prompt_token_count}, Candidates: {usage.candidates_token_count}, Total: {usage.total_token_count}")

            logger.info(f"Successfully generated Google AI response of {len(content)} characters using {target_model}")
            return content.strip()

        except Exception as e:
            logger.error(f"Error generating Google AI response with model {target_model}: {e}", exc_info=True)
            raise RuntimeError(f"Google AI API call failed: {e}")

    async def health_check(self) -> dict:
        """
        Performs a health check on the Google AI service.

        This check verifies that the API key is valid and that a model can be reached.

        Returns:
            A dictionary containing the health status.
        """
        logger.debug("Starting Google AI health check...")
        
        if not self.is_available or not self.client:
            return {
                "status": "unavailable",
                "error": "Google API key not configured",
                "service": "Google AI"
            }
        
        try:
            # A simple, low-token request to verify connectivity and authentication.
            logger.debug(f"Testing API connectivity with model: gemini-2.5-flash-image-preview")

            response = await self.generate_response(
                system_prompt="You are a health check assistant.",
                user_context="Reply with a single word: ok",
                max_tokens=20
            )

            logger.info(f"Google AI health check completed successfully, response: '{response}'")
            return {
                "status": "healthy",
                "details": "API key is valid and service is reachable.",
                "model": "gemini-2.5-flash-image-preview",
                "service": "Google AI"
            }
        except Exception as e:
            logger.error(f"Google AI health check failed: {e}", exc_info=True)
            return {"status": "error", "error": str(e), "service": "Google AI"}


# Create a single, global instance of the GoogleAIService
google_ai_service = GoogleAIService()