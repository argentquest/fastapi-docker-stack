import httpx
import logging

logger = logging.getLogger(__name__)

async def run_ai_test_api(system_prompt: str, user_context: str):
    """Calls the /ai-test endpoint."""
    API_URL = "http://localhost:8001/ai-test"
    async with httpx.AsyncClient(timeout=300.0) as client:
        request_data = {"system_prompt": system_prompt, "user_context": user_context}
        logger.info(f"Sending request to {API_URL}")
        response = await client.post(API_URL, json=request_data)
        response.raise_for_status()
        return response.json()

async def run_health_check_api():
    """Calls the /health endpoint."""
    API_URL = "http://localhost:8001/health"
    async with httpx.AsyncClient() as client:
        logger.info(f"Sending request to {API_URL}")
        response = await client.get(API_URL)
        response.raise_for_status()
        return response.json()

async def run_simple_prompt_api(prompt: str, model_path: str):
    """Calls a simple prompt endpoint."""
    API_URL = f"http://localhost:8001{model_path}"
    async with httpx.AsyncClient(timeout=300.0) as client:
        request_data = {"prompt": prompt}
        logger.info(f"Sending request to {API_URL}")
        response = await client.post(API_URL, json=request_data)
        response.raise_for_status()
        return response.json()
