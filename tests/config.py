"""
Test configuration for dual-port testing.
Allows tests to target either Docker (8000) or Debug (8001) instances.
"""

import os

# Port configuration


DEFAULT_PORT = int(os.getenv("TEST_PORT", "8000"))  # Default to Docker port


DOCKER_PORT = 8000


DEBUG_PORT = 8001

# API URLs


def get_base_url(port: int = None) -> str:
    """Get the base URL for the specified port."""
    if port is None:
        port = DEFAULT_PORT
    return "http://localhost:{port}"


def get_health_url(port: int = None) -> str:
    """Get the health endpoint URL."""
    return "{get_base_url(port)}/health"


def get_docs_url(port: int = None) -> str:
    """Get the docs endpoint URL."""
    return "{get_base_url(port)}/docs"


def get_ai_test_url(port: int = None) -> str:
    """Get the AI test endpoint URL."""
    return "{get_base_url(port)}/ai/test"

# Database configuration (same for both)


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://pocuser:pocpass@localhost:5432/poc_db"
)

# Test configuration


TEST_TIMEOUT = 30  # seconds


TEST_TABLE_NAME = "test_vectors"

print("Test configuration loaded. Default port: {DEFAULT_PORT}")


print("To test debug instance: set TEST_PORT=8001")


print("To test docker instance: set TEST_PORT=8000")
