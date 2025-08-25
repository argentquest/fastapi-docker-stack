# V2 POC FastAPI Application
"""
Main application file for the V2 Proof of Concept.

This file initializes the FastAPI application, defines the API endpoints,
manages the application lifecycle (startup/shutdown), and integrates all the
backend services.
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
import uvicorn
import re

# V2 Services - Import all required microservices
from app.core.config import settings
from app.services.openrouter_service import openrouter_service
from app.services.embedding_service import embedding_service
from app.services.storage_service import storage_service
from app.services.database_service import database_service
from app.services.cache_service import cache_service

# Configure logging based on settings from config.py
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# --- Pydantic Models ---
# Define the data structures for API requests and responses.


class AITestRequest(BaseModel):
    """Request model for the /ai-test endpoint."""
    system_prompt: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="System prompt to guide the AI's behavior."
    )
    user_context: str = Field(
        ...,
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


class AITestResponse(BaseModel):
    """Response model for the /ai-test endpoint."""
    id: int
    ai_result: str
    embedding_similarity: Optional[float] = None
    file_url: Optional[str] = None
    response_time_ms: int
    containers_tested: dict
    created_at: str

# --- Application Lifecycle ---


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application startup and shutdown events.
    This context manager ensures that services like database connections are
    properly initialized before the application starts serving requests and
    gracefully closed when the application shuts down.
    """
    # Startup sequence
    logger.info("Starting V2 POC Application...")
    try:
        await database_service.initialize()
        logger.info("Database service initialized successfully.")
        # Note: Redis and other services use connection pools that connect on-demand,
        # so they don't require an explicit initialization step here.
    except Exception as e:
        logger.critical(f"Failed to start application due to: {e}", exc_info=True)
        raise

    yield

    # Shutdown sequence
    logger.info("Shutting down V2 POC Application...")
    try:
        await database_service.close()
        await cache_service.close()
        logger.info("Application shutdown complete.")
    except Exception as e:
        logger.error(f"Error during application shutdown: {e}", exc_info=True)

# --- FastAPI App Initialization ---

app = FastAPI(
    title="InkAndQuill V2 POC",
    description="Proof of Concept for a Docker-based microservices architecture.",
    version="1.0.0",
    lifespan=lifespan
)

# --- API Endpoints ---


@app.post("/ai-test", response_model=AITestResponse)
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


@app.get("/health", summary="Perform a health check on all backend services")
async def health_check():
    """
    Checks the status of all critical backend services.

    This endpoint iterates through each service and calls its health_check method.
    It aggregates the results to provide a single, comprehensive status report
    for the entire application stack.

    Returns a status of 'healthy' if all services are responsive, and 'degraded' otherwise.
    """
    logger.info("Starting health check for all services...")

    containers = {
        'openrouter': await openrouter_service.health_check(),
        'postgres': await database_service.health_check(),
        'redis': await cache_service.health_check(),
        'minio': await storage_service.health_check(),
        'embedding': await embedding_service.health_check()
    }

    all_healthy = all(c.get('status') == 'healthy' for c in containers.values())
    status = 'healthy' if all_healthy else 'degraded'

    logger.info(f"Health check completed - Status: {status}, Services: {list(containers.keys())}")

    return {
        'status': status,
        'containers': containers
    }


@app.get("/", summary="Root endpoint providing basic application info")
async def root():
    """Provides basic information about the application, including its name and version."""
    return {
        "message": "InkAndQuill V2 POC",
        "version": "1.0.0",
        "description": "This is a Proof of Concept for a Docker-based microservices architecture.",
        "documentation": "/docs"
    }

# --- Main Execution Block ---

if __name__ == "__main__":
    # This block allows running the application directly with uvicorn for local development.
    # The --reload flag enables hot-reloading when code changes are detected.
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
