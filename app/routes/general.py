# General Routes - Non-AI Endpoints
"""
This module contains general API endpoints that are not AI-related.
Includes health checks, root endpoint, and other utility endpoints.
"""

import logging
from fastapi import APIRouter

# Import services for health checks
from app.services.openrouter_service import openrouter_service
from app.services.google_ai_service import google_ai_service
from app.services.embedding_service import embedding_service
from app.services.storage_service import storage_service
from app.services.database_service import database_service
from app.services.cache_service import cache_service

logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(tags=["General"])


@router.get("/", summary="Root endpoint providing basic application info")
async def root():
    """Provides basic information about the application, including its name and version."""
    return {
        "message": "InkAndQuill V2 POC",
        "version": "1.0.0",
        "description": "This is a Proof of Concept for a Docker-based microservices architecture.",
        "documentation": "/docs"
    }


@router.get("/health", summary="Perform a health check on all backend services")
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
        'embedding': await embedding_service.health_check(),
        'google_ai': await google_ai_service.health_check()
    }

    all_healthy = all(c.get('status') == 'healthy' for c in containers.values())
    status = 'healthy' if all_healthy else 'degraded'

    logger.info(f"Health check completed - Status: {status}, Services: {list(containers.keys())}")

    return {
        'status': status,
        'containers': containers
    }