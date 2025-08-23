# V2 POC FastAPI Application
import logging
import time
from contextlib import asynccontextmanager
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# V2 Services
from app.core.config import settings
from app.services.openrouter_service import openrouter_service
from app.services.embedding_service import embedding_service
from app.services.storage_service import storage_service
from app.services.database_service import database_service
from app.services.cache_service import cache_service

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Pydantic Models with validation
from pydantic import Field, validator
import re

class AITestRequest(BaseModel):
    system_prompt: str = Field(
        ..., 
        min_length=1, 
        max_length=5000,
        description="System prompt for AI generation"
    )
    user_context: str = Field(
        ..., 
        min_length=1, 
        max_length=10000,
        description="User context/query for AI generation"
    )
    
    @validator('system_prompt', 'user_context')
    def sanitize_input(cls, v):
        """Sanitize input to prevent injection attacks"""
        # Remove any potential harmful characters while preserving normal text
        if not v or v.isspace():
            raise ValueError("Input cannot be empty or only whitespace")
        # Basic sanitization - preserve normal text but remove potential injection vectors
        v = v.strip()
        # Limit consecutive special characters
        v = re.sub(r'([<>\'";])\1+', r'\1', v)
        return v

class AITestResponse(BaseModel):
    id: int
    ai_result: str
    embedding_similarity: Optional[float] = None
    file_url: Optional[str] = None
    response_time_ms: int
    containers_tested: dict
    created_at: str

# Application Lifespan Management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown"""
    # Startup
    logger.info("Starting V2 POC Application...")
    
    try:
        # Initialize database connection pool
        await database_service.initialize()
        logger.info("Database service initialized")
        
        logger.info("V2 POC Application started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down V2 POC Application...")
    try:
        await database_service.close()
        await cache_service.close()
        logger.info("V2 POC Application shut down successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

# Create FastAPI application
app = FastAPI(
    title="InkAndQuill V2 POC",
    description="Proof of Concept for V2 Docker-based Architecture", 
    version="1.0.0",
    lifespan=lifespan
)

# Main POC Endpoint
@app.post("/ai-test", response_model=AITestResponse)
async def ai_test_endpoint(request: AITestRequest):
    """Main POC endpoint that tests all 5 core containers"""
    start_time = time.time()
    containers_tested = {}
    
    try:
        # Step 1: Generate AI response with OpenRouter
        ai_result = await openrouter_service.generate_response(
            system_prompt=request.system_prompt,
            user_context=request.user_context
        )
        containers_tested['openrouter'] = 'success'
        
        # Step 2: Generate embedding
        embedding = await embedding_service.embed_text(request.user_context)
        containers_tested['embedding'] = 'success'
        
        # Step 3: Save result file to MinIO
        filename = f"ai_result_{int(time.time())}.txt"
        file_url = await storage_service.save_text_file(
            content=ai_result,
            filename=filename
        )
        containers_tested['minio'] = 'success'
        
        # Step 4: Store in PostgreSQL + pgvector
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
        
        # Step 5: Cache result
        await cache_service.cache_ai_response(
            request.system_prompt,
            request.user_context, 
            ai_result
        )
        containers_tested['redis'] = 'success'
        
        total_time_ms = int((time.time() - start_time) * 1000)
        
        return AITestResponse(
            id=log_entry['id'],
            ai_result=ai_result,
            file_url=file_url,
            response_time_ms=total_time_ms,
            containers_tested=containers_tested,
            created_at=log_entry['created_at'].isoformat()
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValueError as e:
        logger.warning(f"Validation error in AI test endpoint: {e}")
        raise HTTPException(
            status_code=400, 
            detail="Invalid input parameters"
        )
    except ConnectionError as e:
        logger.error(f"Connection error in AI test endpoint: {e}")
        raise HTTPException(
            status_code=503, 
            detail="Service temporarily unavailable"
        )
    except Exception as e:
        logger.error(f"Unexpected error in AI test endpoint: {e}", exc_info=True)
        # Don't expose internal errors to clients
        raise HTTPException(
            status_code=500, 
            detail="An internal error occurred. Please try again later."
        )

# Health Check
@app.get("/health")
async def health_check():
    """Health check for all containers"""
    containers = {
        'openrouter': await openrouter_service.health_check(),
        'postgres': await database_service.health_check(),
        'redis': await cache_service.health_check(),
        'minio': await storage_service.health_check(),
        'embedding': await embedding_service.health_check()
    }
    
    all_healthy = all(c.get('status') == 'healthy' for c in containers.values())
    
    return {
        'status': 'healthy' if all_healthy else 'degraded',
        'containers': containers
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "InkAndQuill V2 POC",
        "version": "1.0.0",
        "containers": ["FastAPI", "PostgreSQL+pgvector", "Redis", "MinIO", "Nginx"]
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)