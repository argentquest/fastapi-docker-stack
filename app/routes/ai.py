# AI Routes - All AI-related Endpoints
"""
This module contains all AI-related API endpoints.
Includes OpenRouter, Google AI, embeddings, and other AI service endpoints.
"""

import logging
import time
import re
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator

# Import core configuration
from app.core.config import settings

# Import all AI services
from app.services.openrouter_service import openrouter_service
from app.services.openrouter_langchain_service import openrouter_langchain_service
from app.services.openrouter_langgraph_service import openrouter_langgraph_service
from app.services.google_ai_service import google_ai_service
from app.services.google_adk_service import google_adk_service
from app.services.embedding_service import embedding_service
from app.services.storage_service import storage_service
from app.services.database_service import database_service
from app.services.cache_service import cache_service

logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(tags=["AI"])


# --- Pydantic Models ---
# Define the data structures for API requests and responses.

class AITestRequest(BaseModel):
    """Request model for the /ai-test endpoint."""
    system_prompt: str = Field(
        default="You are a helpful AI assistant. Provide clear and informative responses.",
        min_length=1,
        max_length=5000,
        description="System prompt to guide the AI's behavior."
    )
    user_context: str = Field(
        default="Explain what microservices are in one sentence.",
        min_length=1,
        max_length=10000,
        description="The user's query or context for the AI to process."
    )

    @validator('system_prompt', 'user_context')
    def sanitize_input(cls, v):
        """Sanitizes input to prevent basic injection attacks and removes leading/trailing whitespace."""
        if not v or v.isspace():
            raise ValueError("Input cannot be empty or only whitespace")
        # Basic sanitization - strip whitespace and limit consecutive special characters.
        v = v.strip()
        # Remove consecutive special characters
        v = re.sub(r'([<>"\]\[\]\t\n])\1+', r'\1', v)
        return v


class SimplePromptRequest(BaseModel):
    """Request model for simple prompt endpoints."""
    prompt: str = Field(
        default="Hello! How are you today?",
        min_length=1,
        max_length=10000,
        description="The prompt to send to the AI service."
    )

    @validator('prompt')
    def sanitize_prompt(cls, v):
        """Sanitizes prompt input."""
        if not v or v.isspace():
            raise ValueError("Prompt cannot be empty or only whitespace")
        return v.strip()


class SimplePromptResponse(BaseModel):
    """Response model for simple prompt endpoints."""
    response: str
    service_type: str
    model: str
    response_time_ms: int


class TopicRequest(BaseModel):
    """Request model for agentic blog generation endpoints."""
    topic: str = Field(
        default="The future of artificial intelligence",
        min_length=1,
        max_length=500,
        description="The topic for blog generation."
    )


class AITestResponse(BaseModel):
    """Response model for the /ai-test endpoint."""
    id: int
    ai_result: str
    embedding_similarity: Optional[float] = None
    file_url: Optional[str] = None
    response_time_ms: int
    containers_tested: dict
    created_at: str


# --- AI Test Endpoint ---

@router.post("/ai-test", response_model=AITestResponse)
async def ai_test_endpoint(request: AITestRequest):
    """
    This is the main endpoint for the Proof of Concept.

    It orchestrates a workflow that touches all 5 core backend services:
    1.  **OpenRouter:** Generates an AI response.
    2.  **Embedding Service:** Creates a vector embedding from the user context.
    3.  **MinIO:** Saves the AI response to S3-compatible storage.
    4.  **PostgreSQL:** Logs the entire transaction, including the vector embedding.
    5.  **Redis:** Caches the AI response.

    Returns a detailed response including the AI result, performance metrics,
    and a status of the containers tested.
    """
    start_time = time.time()
    containers_tested = {}

    logger.info(f"Starting AI test endpoint with system_prompt length: {len(request.system_prompt)}, user_context length: {len(request.user_context)}")

    try:
        # Step 1: Generate AI response via OpenRouter
        logger.info("Step 1: Generating AI response via OpenRouter...")
        ai_result = await openrouter_service.generate_response(
            system_prompt=request.system_prompt,
            user_context=request.user_context
        )
        containers_tested['openrouter'] = 'success'
        logger.info(f"Step 1 completed: AI response generated, length: {len(ai_result)}")

        # Step 2: Generate vector embedding for the user's context
        logger.info("Step 2: Generating vector embedding for user context...")
        embedding = await embedding_service.embed_text(request.user_context)
        containers_tested['embedding'] = 'success'
        logger.info(f"Step 2 completed: Embedding generated, dimensions: {len(embedding)}")

        # Step 3: Save the AI-generated text to a file in MinIO
        logger.info("Step 3: Saving AI response to MinIO storage...")
        filename = f"ai_result_{int(time.time())}.txt"
        file_url = await storage_service.save_text_file(
            content=ai_result,
            filename=filename
        )
        containers_tested['minio'] = 'success'
        logger.info(f"Step 3 completed: File saved to MinIO, URL: {file_url}")

        # Step 4: Log the transaction details to the PostgreSQL database
        logger.info("Step 4: Logging transaction to PostgreSQL database...")
        response_time_ms = int((time.time() - start_time) * 1000)
        log_entry = await database_service.create_ai_log(
            system_prompt=request.system_prompt,
            user_context=request.user_context,
            ai_result=ai_result,
            embedding=embedding,
            file_url=file_url,
            response_time_ms=response_time_ms
        )
        containers_tested['postgres'] = 'success'
        logger.info(f"Step 4 completed: Database log created with ID: {log_entry['id']}")

        # Step 5: Cache the result in Redis for future requests
        logger.info("Step 5: Caching AI response in Redis...")
        await cache_service.cache_ai_response(
            request.system_prompt,
            request.user_context,
            ai_result
        )
        containers_tested['redis'] = 'success'
        logger.info("Step 5 completed: Response cached in Redis")

        total_time_ms = int((time.time() - start_time) * 1000)
        logger.info(f"AI test endpoint completed successfully in {total_time_ms}ms")

        return AITestResponse(
            id=log_entry['id'],
            ai_result=ai_result,
            file_url=file_url,
            response_time_ms=total_time_ms,
            containers_tested=containers_tested,
            created_at=log_entry['created_at'].isoformat()
        )

    # --- Exception Handling ---
    except HTTPException:
        # Re-raise FastAPI's built-in exceptions directly.
        raise
    except ValueError as e:
        # Handle validation errors from Pydantic models or other checks.
        logger.warning(f"Validation error in AI test endpoint: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid input: {e}")
    except ConnectionError as e:
        # Handle network-related errors when connecting to other services.
        logger.error(f"Connection error in AI test endpoint: {e}")
        raise HTTPException(status_code=503, detail="A backend service is temporarily unavailable.")
    except Exception as e:
        # Catch-all for any other unexpected errors.
        logger.error(f"Unexpected error in AI test endpoint: {e}", exc_info=True)
        # Avoid exposing internal error details to the client.
        raise HTTPException(status_code=500, detail="An internal server error occurred.")


# --- Google AI Endpoints ---

@router.get("/google-ai/test", summary="Test Google AI connectivity and API key")
async def google_ai_test():
    """
    Tests Google AI service connectivity and API key validity.
    
    This endpoint performs a quick test to verify:
    - Google API key is configured
    - Can connect to Google AI services
    - Can generate a simple response
    
    Returns detailed status information about the Google AI service.
    """
    logger.info("Testing Google AI service connectivity...")
    
    try:
        # First check if service is available
        if not google_ai_service.is_available:
            return {
                'status': 'error',
                'message': 'Google AI service is not available. Please configure GOOGLE_API_KEY in your .env file.',
                'api_key_configured': False,
                'service': 'Google AI'
            }
        
        # Perform health check
        health_status = await google_ai_service.health_check()
        
        # If healthy, do a simple test generation
        if health_status.get('status') == 'healthy':
            test_response = await google_ai_service.generate_response(
                system_prompt="You are a test assistant.",
                user_context="Say 'Google AI is working!' in exactly 5 words.",
                max_tokens=50,
                temperature=0.1
            )
            
            return {
                'status': 'success',
                'message': 'Google AI service is working correctly!',
                'api_key_configured': True,
                'model': settings.GOOGLE_DEFAULT_MODEL,
                'test_response': test_response,
                'health_check': health_status,
                'service': 'Google AI'
            }
        else:
            return {
                'status': 'error',
                'message': 'Google AI service health check failed',
                'api_key_configured': True,
                'health_check': health_status,
                'service': 'Google AI'
            }
            
    except Exception as e:
        logger.error(f"Error testing Google AI service: {e}")
        return {
            'status': 'error',
            'message': f'Failed to test Google AI service: {str(e)}',
            'api_key_configured': bool(settings.GOOGLE_API_KEY),
            'service': 'Google AI'
        }


@router.post("/google-ai/gemini", response_model=SimplePromptResponse)
async def google_ai_gemini_endpoint(request: SimplePromptRequest):
    """
    Google AI endpoint using Gemini models.
    """
    start_time = time.time()
    default_system_prompt = "You are a helpful AI assistant powered by Google's Gemini. Provide accurate and informative responses."
    
    try:
        response = await google_ai_service.generate_response(
            system_prompt=default_system_prompt,
            user_context=request.prompt
        )
        
        response_time_ms = int((time.time() - start_time) * 1000)
        
        return SimplePromptResponse(
            response=response,
            service_type="Google AI Gemini",
            model=settings.GOOGLE_DEFAULT_MODEL,
            response_time_ms=response_time_ms
        )
    except Exception as e:
        logger.error(f"Error in Google AI Gemini endpoint: {e}")
        raise HTTPException(status_code=500, detail="Google AI Gemini service error")


# --- OpenRouter Endpoints ---

@router.post("/openrouter/simple", response_model=SimplePromptResponse)
async def openrouter_simple_endpoint(request: SimplePromptRequest):
    """
    Simple OpenRouter endpoint using the basic service.
    """
    start_time = time.time()
    default_system_prompt = "You are a helpful AI assistant. Provide clear and concise responses."
    
    try:
        response = await openrouter_service.generate_response(
            system_prompt=default_system_prompt,
            user_context=request.prompt
        )
        
        response_time_ms = int((time.time() - start_time) * 1000)
        
        return SimplePromptResponse(
            response=response,
            service_type="OpenRouter Basic",
            model=settings.OPENROUTER_DEFAULT_MODEL,
            response_time_ms=response_time_ms
        )
    except Exception as e:
        logger.error(f"Error in OpenRouter simple endpoint: {e}")
        raise HTTPException(status_code=500, detail="OpenRouter service error")


@router.post("/openrouter/langchain", response_model=SimplePromptResponse)
async def openrouter_langchain_endpoint(request: SimplePromptRequest):
    """
    OpenRouter endpoint using LangChain service.
    """
    start_time = time.time()
    default_system_prompt = "You are a helpful AI assistant powered by LangChain. Provide thoughtful and well-structured responses."
    
    try:
        response = await openrouter_langchain_service.generate_response_langchain(
            system_prompt=default_system_prompt,
            user_context=request.prompt
        )
        
        response_time_ms = int((time.time() - start_time) * 1000)
        
        return SimplePromptResponse(
            response=response,
            service_type="OpenRouter LangChain",
            model=settings.OPENROUTER_DEFAULT_MODEL,
            response_time_ms=response_time_ms
        )
    except Exception as e:
        logger.error(f"Error in OpenRouter LangChain endpoint: {e}")
        raise HTTPException(status_code=500, detail="OpenRouter LangChain service error")


@router.post("/openrouter/langgraph", response_model=SimplePromptResponse)
async def openrouter_langgraph_endpoint(request: SimplePromptRequest):
    """
    OpenRouter endpoint using LangGraph workflow service.
    """
    start_time = time.time()
    default_system_prompt = "You are an advanced AI assistant powered by LangGraph workflows. Provide comprehensive and well-reasoned responses."
    
    try:
        response = await openrouter_langgraph_service.generate_response_langgraph(
            system_prompt=default_system_prompt,
            user_context=request.prompt
        )
        
        response_time_ms = int((time.time() - start_time) * 1000)
        
        return SimplePromptResponse(
            response=response,
            service_type="OpenRouter LangGraph",
            model=settings.OPENROUTER_DEFAULT_MODEL,
            response_time_ms=response_time_ms
        )
    except Exception as e:
        logger.error(f"Error in OpenRouter LangGraph endpoint: {e}")
        raise HTTPException(status_code=500, detail="OpenRouter LangGraph service error")


# --- Google ADK Endpoints ---

@router.get("/google-adk/test", summary="Test Google ADK agent connectivity and configuration")
async def google_adk_test():
    """
    Tests Google ADK agent service connectivity and configuration.
    
    This endpoint performs a quick test to verify:
    - Google API key is configured
    - ADK agent is properly initialized
    - Can generate responses using the agent framework
    
    Returns detailed status information about the Google ADK service.
    """
    logger.info("Testing Google ADK agent service connectivity...")
    
    try:
        # First check if service is available
        if not google_adk_service.is_available:
            return {
                'status': 'error',
                'message': 'Google ADK service is not available. Please configure GOOGLE_API_KEY in your .env file.',
                'api_key_configured': False,
                'service': 'Google ADK'
            }
        
        # Get agent information
        agent_info = google_adk_service.get_agent_info()
        
        # Perform health check
        health_status = await google_adk_service.health_check()
        
        # If healthy, do a simple test generation
        if health_status.get('status') == 'healthy':
            test_response = await google_adk_service.generate_response(
                system_prompt="You are a test assistant using Google ADK.",
                user_context="Say 'Google ADK agent working!' in exactly 5 words.",
                max_tokens=50,
                temperature=0.1
            )
            
            return {
                'status': 'success',
                'message': 'Google ADK agent service is working correctly!',
                'api_key_configured': True,
                'agent_info': agent_info,
                'test_response': test_response,
                'health_check': health_status,
                'service': 'Google ADK'
            }
        else:
            return {
                'status': 'error',
                'message': 'Google ADK agent health check failed',
                'api_key_configured': True,
                'agent_info': agent_info,
                'health_check': health_status,
                'service': 'Google ADK'
            }
            
    except Exception as e:
        logger.error(f"Error testing Google ADK service: {e}")
        return {
            'status': 'error',
            'message': f'Failed to test Google ADK service: {str(e)}',
            'api_key_configured': bool(settings.GOOGLE_API_KEY),
            'service': 'Google ADK'
        }


@router.post("/google-adk/agent", response_model=SimplePromptResponse)
async def google_adk_agent_endpoint(request: SimplePromptRequest):
    """
    Google ADK endpoint using Agent Development Kit framework.
    
    This endpoint uses Google's ADK agent framework for enhanced AI capabilities
    including tool support, multi-agent workflows, and sophisticated orchestration.
    """
    start_time = time.time()
    default_system_prompt = "You are a sophisticated AI agent powered by Google's ADK framework. Provide thoughtful, well-structured responses using agent capabilities."
    
    try:
        response = await google_adk_service.generate_response(
            system_prompt=default_system_prompt,
            user_context=request.prompt
        )
        
        response_time_ms = int((time.time() - start_time) * 1000)
        
        return SimplePromptResponse(
            response=response,
            service_type="Google ADK Agent",
            model=settings.GOOGLE_DEFAULT_MODEL,
            response_time_ms=response_time_ms
        )
    except Exception as e:
        logger.error(f"Error in Google ADK agent endpoint: {e}")
        raise HTTPException(status_code=500, detail="Google ADK agent service error")