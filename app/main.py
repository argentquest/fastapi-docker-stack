# V2 POC FastAPI Application
"""
Main application file for the V2 Proof of Concept.

This file initializes the FastAPI application, manages the application
lifecycle (startup/shutdown), and integrates all route modules.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

# NiceGUI import
from nicegui import ui

# Frontend integrations
from frontendclaude.main import setup_claude_frontend

# Placeholder for Gemini frontend
def setup_gemini_frontend(fastapi_app: FastAPI, prefix: str = "/gemini", register_only: bool = False):
    """
    Placeholder for Gemini frontend setup.
    This will be replaced when frontendgemini is implemented.
    """
    @ui.page(f'{prefix}/')
    def gemini_placeholder():
        ui.label('Frontend Gemini').classes('text-h4')
        ui.label('Coming soon! This will be the Gemini-based frontend.').classes('text-subtitle1')
        ui.link('← Back to Claude Frontend', '/claude/').classes('text-primary')
        ui.link('← Back to API Docs', '/docs').classes('text-primary q-ml-md')

# V2 Services - Import required for lifecycle management
from app.core.config import settings
from app.services.database_service import database_service
from app.services.cache_service import cache_service

# Import route modules
from app.routes import general, ai

# Configure logging based on settings from config.py
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


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

    # Print startup banner
    print("\n" + "="*75)
    print("🚀 InkAndQuill V2 POC - Multi-Service AI Architecture")
    print("="*75)
    print("📋 Objective: Demonstrate scalable microservices with AI integration")
    print("🔧 Services: PostgreSQL, Redis, MinIO, MongoDB, AI (OpenRouter/Google)")
    print("")
    print("🎯 Frontend Experiments - Two UI Approaches:")
    print("   💙 Frontend Claude:  http://localhost:8001/claude/")
    print("   💚 Frontend Gemini:  http://localhost:8001/gemini/")
    print("")
    print("📚 API Documentation: http://localhost:8001/docs")
    print("🌐 Live Demo:         https://pocmaster.argentquest.com")
    print("💻 GitHub Repository: https://github.com/argentquest/fastapi-docker-stack")
    print("")
    print("✅ Server is running and ready to accept requests!")
    print("="*75 + "\n")

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

# --- Include Routers ---

# Include general routes (health, root, etc.)
app.include_router(general.router)

# Include AI routes with prefix for organization
app.include_router(ai.router)

# Setup frontends - Register pages only (don't call ui.run_with yet)
setup_claude_frontend(app, prefix="/claude", register_only=True)
setup_gemini_frontend(app, prefix="/gemini", register_only=True)

# Initialize NiceGUI with FastAPI (single call for all frontends)
ui.run_with(app, storage_secret='v2-poc-frontends-2025')


# --- Main Execution Block ---

if __name__ == "__main__":
    # This block allows running the application directly with uvicorn for local development.
    # The --reload flag enables hot-reloading when code changes are detected.
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)