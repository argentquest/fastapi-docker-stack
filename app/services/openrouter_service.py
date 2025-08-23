# V2 OpenRouter Service (Adapted from RAG)
import logging
from typing import Optional
import openai
from app.core.config import settings

logger = logging.getLogger(__name__)

class OpenRouterService:
    """OpenRouter AI client service for V2 POC"""
    
    def __init__(self):
        self.client = self._create_client()
    
    def _create_client(self) -> openai.AsyncOpenAI:
        """Create OpenRouter client."""
        if not settings.OPENROUTER_API_KEY:
            raise ValueError("OpenRouter API key is not configured")
            
        logger.debug("Creating OpenRouter client for V2 POC")
        
        # Build default headers for OpenRouter
        default_headers = {}
        if settings.OPENROUTER_SITE_URL:
            default_headers["HTTP-Referer"] = settings.OPENROUTER_SITE_URL
        if settings.OPENROUTER_APP_NAME:
            default_headers["X-Title"] = settings.OPENROUTER_APP_NAME
            
        return openai.AsyncOpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL,
            default_headers=default_headers if default_headers else None
        )
    
    async def generate_response(
        self,
        system_prompt: str,
        user_context: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Generate AI response using OpenRouter.
        
        Args:
            system_prompt: System instruction for the AI
            user_context: User's input/context
            model: Model to use (defaults to settings.DEFAULT_MODEL)
            temperature: Response creativity (0.0 to 2.0)
            max_tokens: Maximum response length
            
        Returns:
            Generated AI response text
        """
        if not model:
            model = settings.DEFAULT_MODEL
            
        try:
            logger.info(f"Generating response with model: {model}")
            
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_context}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            if not response.choices:
                raise ValueError("No response generated from OpenRouter")
                
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response content from OpenRouter")
                
            logger.info(f"Successfully generated response ({len(content)} chars)")
            return content.strip()
            
        except Exception as e:
            logger.error(f"Error generating OpenRouter response: {e}")
            raise RuntimeError(f"OpenRouter generation failed: {e}")
    
    async def health_check(self) -> dict:
        """Check if OpenRouter service is accessible."""
        try:
            # Simple test request
            response = await self.generate_response(
                system_prompt="You are a test assistant.",
                user_context="Say 'OK' if you can respond.",
                max_tokens=10
            )
            return {"status": "healthy", "test_response": response}
            
        except Exception as e:
            return {"status": "error", "error": str(e)}

# Global service instance
openrouter_service = OpenRouterService()