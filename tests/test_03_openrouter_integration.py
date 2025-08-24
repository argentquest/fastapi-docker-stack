#!/usr/bin/env python3
"""
Test 03: OpenRouter Integration Validation

This script tests the application's ability to connect to and receive valid
responses from the OpenRouter AI service.

It verifies:
- The presence of a valid OpenRouter API key.
- The health status of the OpenRouter service via the app's health check.
- Basic AI response generation.
- The application's error handling for invalid requests.
"""

import sys
import os
import time
import requests
import json
from typing import Dict, Any

# The base URL for the FastAPI application being tested.
TEST_API_URL = "http://localhost:8000"
HEALTH_URL = "http://localhost/health"

def main_test_logic():
    """Main function to run all OpenRouter integration tests."""
    print("=" * 60)
    print("TEST 03: OPENROUTER INTEGRATION VALIDATION")
    print("=" * 60)

    # --- Test 1: Environment Configuration ---
    print("\n1. Checking for OpenRouter API key...")
    if not check_environment():
        print("❌ FAILED: OPENROUTER_API_KEY is not set or is invalid.")
        print("   Please add a valid key to your .env file or environment variables.")
        return False
    print("✅ OpenRouter API key is configured.")

    # --- Test 2: Service Health ---
    print("\n2. Checking OpenRouter service health via the application...")
    if not test_openrouter_service_health():
        print("❌ FAILED: The application reports that the OpenRouter service is not healthy.")
        return False
    print("✅ Application reports a healthy connection to OpenRouter.")

    # --- Test 3: AI Response Generation ---
    print("\n3. Testing basic AI response generation...")
    if not test_simple_ai_generation():
        print("❌ FAILED: Could not generate a valid AI response.")
        return False
    print("✅ AI response generated successfully.")

    # --- Test 4: Error Handling ---
    print("\n4. Testing server error handling for invalid requests...")
    if not test_error_handling():
        print("❌ FAILED: The server did not handle invalid requests correctly.")
        return False
    print("✅ Server correctly handles invalid requests with a 422 error.")

    print("\n" + "=" * 60)
    print("✅ TEST 03 PASSED: OpenRouter integration is fully functional.")
    print("=" * 60)
    return True

def check_environment() -> bool:
    """Checks if the OPENROUTER_API_KEY is set in the environment."""
    api_key = os.getenv('OPENROUTER_API_KEY')
    return api_key is not None and api_key != 'your_openrouter_api_key_here'

def test_openrouter_service_health() -> bool:
    """Queries the app's health endpoint to check the OpenRouter service status."""
    try:
        response = requests.get(HEALTH_URL, timeout=10)
        response.raise_for_status()
        health_data = response.json()
        openrouter_health = health_data.get('containers', {}).get('openrouter', {})
        return openrouter_health.get('status') == 'healthy'
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        print(f"   -> Error checking health: {e}")
        return False

def test_simple_ai_generation() -> bool:
    """Sends a valid request to the /ai-test endpoint and validates the response."""
    test_data = {
        "system_prompt": "You are a test assistant.",
        "user_context": "Please reply with the single word: success"
    }
    try:
        response = requests.post(f"{TEST_API_URL}/ai-test", json=test_data, timeout=30)
        response.raise_for_status()
        result = response.json()
        # Check that we got a non-empty string back in the ai_result field.
        return 'ai_result' in result and isinstance(result['ai_result'], str) and len(result['ai_result']) > 0
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        print(f"   -> Error during AI generation test: {e}")
        return False

def test_error_handling() -> bool:
    """Tests if the server correctly returns a 422 Unprocessable Entity error for invalid requests."""
    try:
        # Send a request with a missing `user_context` field.
        response = requests.post(f"{TEST_API_URL}/ai-test", json={"system_prompt": "test"}, timeout=10)
        # A 422 status code is expected because the request fails Pydantic validation.
        return response.status_code == 422
    except requests.exceptions.RequestException as e:
        print(f"   -> Error during error handling test: {e}")
        return False

if __name__ == '__main__':
    try:
        if main_test_logic():
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        sys.exit(1)
