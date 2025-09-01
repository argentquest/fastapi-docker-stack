#!/usr/bin/env python3
"""
Frontend API Test Script
Test all frontend API client methods against running backend.
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from frontendclaude.utils.api_client import api_client

async def test_all_endpoints():
    """Test all API client methods."""
    print("Testing Frontend API Client Methods...")
    print("=" * 50)
    
    results = {}
    
    # Test health check
    print("1. Testing health check...")
    try:
        result = await api_client.health_check()
        if 'status' in result:
            results['health_check'] = 'SUCCESS'
            print(f"   SUCCESS: Health status: {result['status']}")
        else:
            results['health_check'] = 'FAILED'
            print(f"   FAILED: Unexpected response: {result}")
    except Exception as e:
        results['health_check'] = f'ERROR: {e}'
        print(f"   ERROR: Exception: {e}")
    
    # Test Google AI endpoints
    print("\n2. Testing Google AI...")
    try:
        result = await api_client.google_ai_test()
        if result.get('status') == 'success':
            results['google_ai_test'] = 'SUCCESS'
            print(f"   SUCCESS: Google AI test successful")
        else:
            results['google_ai_test'] = 'FAILED'
            print(f"   FAILED: Google AI test failed: {result.get('message', result)}")
    except Exception as e:
        results['google_ai_test'] = f'ERROR: {e}'
        print(f"   ERROR: Exception: {e}")
    
    # Test Google AI prompt
    print("\n3. Testing Google AI prompt...")
    try:
        result = await api_client.google_ai_prompt("Hello, this is a test!")
        if 'response' in result:
            results['google_ai_prompt'] = 'SUCCESS'
            print(f"   SUCCESS: Got response: {result['response'][:50]}...")
        else:
            results['google_ai_prompt'] = 'FAILED'
            print(f"   FAILED: No response: {result}")
    except Exception as e:
        results['google_ai_prompt'] = f'ERROR: {e}'
        print(f"   ERROR: Exception: {e}")
    
    # Test Google ADK endpoints
    print("\n4. Testing Google ADK...")
    try:
        result = await api_client.google_adk_test()
        if result.get('status') == 'success':
            results['google_adk_test'] = 'SUCCESS'
            print(f"   SUCCESS: Google ADK test successful")
        else:
            results['google_adk_test'] = 'FAILED'
            print(f"   FAILED: Google ADK test failed: {result.get('message', result)}")
    except Exception as e:
        results['google_adk_test'] = f'ERROR: {e}'
        print(f"   ERROR: Exception: {e}")
    
    # Test OpenRouter endpoints (expect failures)
    print("\n5. Testing OpenRouter simple...")
    try:
        result = await api_client.openrouter_simple("Hello, this is a test!")
        if 'response' in result:
            results['openrouter_simple'] = 'SUCCESS'
            print(f"   SUCCESS: Got response: {result['response'][:50]}...")
        else:
            results['openrouter_simple'] = 'FAILED'
            print(f"   FAILED: OpenRouter failed: {result}")
    except Exception as e:
        results['openrouter_simple'] = f'ERROR: {e}'
        print(f"   ERROR: Exception: {e}")
    
    # Test comprehensive AI test
    print("\n6. Testing comprehensive AI test...")
    try:
        result = await api_client.ai_test(
            system_prompt="You are a helpful assistant.", 
            user_context="Say hello!"
        )
        if 'ai_result' in result:
            results['ai_test'] = 'SUCCESS'
            print(f"   SUCCESS: AI test successful: {result['ai_result'][:50]}...")
        else:
            results['ai_test'] = 'FAILED'
            print(f"   FAILED: AI test failed: {result}")
    except Exception as e:
        results['ai_test'] = f'ERROR: {e}'
        print(f"   ERROR: Exception: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("FRONTEND API TEST SUMMARY")
    print("=" * 50)
    for endpoint, status in results.items():
        print(f"{endpoint:20}: {status}")
    
    # Count successes
    successes = sum(1 for status in results.values() if status.startswith('SUCCESS'))
    total = len(results)
    print(f"\nTotal: {successes}/{total} endpoints working")
    
    return results

if __name__ == "__main__":
    asyncio.run(test_all_endpoints())