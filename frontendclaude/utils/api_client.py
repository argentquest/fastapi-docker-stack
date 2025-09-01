# API Client for FastAPI Backend
"""
HTTP client for making requests to the FastAPI backend.
Handles all communication between NiceGUI frontend and FastAPI endpoints.
"""

import httpx
import json
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class APIClient:
    """Client for communicating with FastAPI backend."""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url.rstrip('/')
        self.timeout = 60.0  # Increased to 60 seconds for AI operations
    
    async def get(self, endpoint: str) -> Dict[str, Any]:
        """Make GET request to endpoint."""
        url = f"{self.base_url}{endpoint}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} for {url}: {e.response.text}")
            return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            logger.error(f"Request error for {url}: {e}")
            return {"error": str(e)}
    
    async def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make POST request to endpoint with JSON data."""
        url = f"{self.base_url}{endpoint}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=data)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} for {url}: {e.response.text}")
            try:
                error_detail = e.response.json().get('detail', e.response.text)
            except:
                error_detail = e.response.text
            return {"error": f"HTTP {e.response.status_code}: {error_detail}"}
        except Exception as e:
            logger.error(f"Request error for {url}: {e}")
            return {"error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all services."""
        return await self.get("/health")
    
    async def ai_test(self, system_prompt: str, user_context: str) -> Dict[str, Any]:
        """Run comprehensive AI test."""
        data = {
            "system_prompt": system_prompt,
            "user_context": user_context
        }
        return await self.post("/ai-test", data)
    
    async def google_ai_test(self) -> Dict[str, Any]:
        """Test Google AI connectivity."""
        return await self.get("/google-ai/test")
    
    async def google_ai_prompt(self, prompt: str) -> Dict[str, Any]:
        """Send prompt to Google AI."""
        data = {"prompt": prompt}
        return await self.post("/google-ai/gemini", data)
    
    async def openrouter_simple(self, prompt: str) -> Dict[str, Any]:
        """Send prompt to OpenRouter simple endpoint."""
        data = {"prompt": prompt}
        return await self.post("/openrouter/simple", data)
    
    async def openrouter_langchain(self, prompt: str) -> Dict[str, Any]:
        """Send prompt to OpenRouter LangChain endpoint."""
        data = {"prompt": prompt}
        return await self.post("/openrouter/langchain", data)
    
    async def openrouter_langgraph(self, prompt: str) -> Dict[str, Any]:
        """Send prompt to OpenRouter LangGraph endpoint."""
        data = {"prompt": prompt}
        return await self.post("/openrouter/langgraph", data)


# Global API client instance
api_client = APIClient()