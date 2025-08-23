#!/usr/bin/env python3
"""
Test 03: OpenRouter Integration Validation
Tests OpenRouter API connectivity and AI response generation
"""

import sys
import os
import time
import requests
import json
from typing import Dict, Any

# Test configuration
TEST_API_URL = "http://localhost:8000"
HEALTH_URL = "http://localhost/health"

def run_test():
    """Test OpenRouter integration"""
    print("=" * 60)
    print("TEST 03: OPENROUTER INTEGRATION VALIDATION")
    print("=" * 60)
    
    # Check environment variables
    print("\n1. Checking environment configuration...")
    env_status = check_environment()
    if not env_status['success']:
        print("❌ FAILED: Environment configuration issues")
        print(f"Issues: {env_status['issues']}")
        return False
    print("✅ Environment configuration is valid")
    
    # Test OpenRouter service health via app
    print("\n2. Testing OpenRouter service health...")
    service_health = test_openrouter_service_health()
    if not service_health['success']:
        print("❌ FAILED: OpenRouter service not healthy")
        print(f"Error: {service_health.get('error', 'Unknown error')}")
        return False
    print("✅ OpenRouter service reports healthy")
    
    # Test simple AI generation
    print("\n3. Testing simple AI generation...")
    simple_test = test_simple_ai_generation()
    if not simple_test['success']:
        print("❌ FAILED: Simple AI generation failed")
        print(f"Error: {simple_test.get('error', 'Unknown error')}")
        return False
    print("✅ Simple AI generation successful")
    print(f"  Response length: {simple_test['response_length']} characters")
    print(f"  Response time: {simple_test['response_time_ms']}ms")
    
    # Test different prompt types
    print("\n4. Testing different prompt types...")
    prompt_tests = test_different_prompt_types()
    failed_prompts = [name for name, result in prompt_tests.items() if not result['success']]
    
    if failed_prompts:
        print(f"❌ FAILED: Some prompt types failed: {failed_prompts}")
        return False
    
    print("✅ All prompt types successful")
    for prompt_type, result in prompt_tests.items():
        print(f"  {prompt_type}: {result['response_length']} chars, {result['response_time_ms']}ms")
    
    # Test error handling
    print("\n5. Testing error handling...")
    error_test = test_error_handling()
    if not error_test['success']:
        print("❌ FAILED: Error handling not working properly")
        return False
    print("✅ Error handling works correctly")
    
    # Performance test
    print("\n6. Testing performance with multiple requests...")
    perf_test = test_performance()
    if not perf_test['success']:
        print("❌ FAILED: Performance test failed")
        print(f"Issues: {perf_test.get('issues', [])}")
        return False
    print("✅ Performance test passed")
    print(f"  Average response time: {perf_test['avg_response_time']}ms")
    print(f"  Success rate: {perf_test['success_rate']}%")
    
    print("\n" + "=" * 60)
    print("✅ TEST 03 PASSED: OpenRouter integration fully functional")
    print("=" * 60)
    return True

def check_environment() -> Dict[str, Any]:
    """Check environment variables and configuration"""
    issues = []
    
    # Check if OPENROUTER_API_KEY is set
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key or api_key == 'your_openrouter_api_key_here':
        issues.append("OPENROUTER_API_KEY not set or using placeholder value")
    
    # Try to read from .env file if environment variable not set
    if not api_key:
        try:
            with open('.env', 'r') as f:
                for line in f:
                    if line.startswith('OPENROUTER_API_KEY='):
                        api_key = line.split('=', 1)[1].strip()
                        if api_key and api_key != 'your_openrouter_api_key_here':
                            print("  Found API key in .env file")
                            break
        except FileNotFoundError:
            issues.append(".env file not found")
    
    if not api_key or api_key == 'your_openrouter_api_key_here':
        issues.append("Valid OpenRouter API key not found")
    else:
        print(f"  API key found: {api_key[:10]}...{api_key[-4:]}")
    
    return {
        'success': len(issues) == 0,
        'issues': issues,
        'has_api_key': bool(api_key and api_key != 'your_openrouter_api_key_here')
    }

def test_openrouter_service_health() -> Dict[str, Any]:
    """Test OpenRouter service health via application health endpoint"""
    try:
        response = requests.get(HEALTH_URL, timeout=10)
        
        if response.status_code != 200:
            return {'success': False, 'error': f'Health endpoint returned {response.status_code}'}
        
        health_data = response.json()
        containers = health_data.get('containers', {})
        openrouter_health = containers.get('openrouter', {})
        
        if isinstance(openrouter_health, dict):
            status = openrouter_health.get('status', 'unknown')
            return {
                'success': status == 'healthy',
                'status': status,
                'details': openrouter_health
            }
        else:
            return {'success': False, 'error': 'OpenRouter health data not found'}
        
    except requests.exceptions.RequestException as e:
        return {'success': False, 'error': f'Request failed: {e}'}

def test_simple_ai_generation() -> Dict[str, Any]:
    """Test simple AI generation via the ai-test endpoint"""
    test_data = {
        "system_prompt": "You are a helpful assistant. Respond concisely.",
        "user_context": "Say hello and confirm you are working properly."
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{TEST_API_URL}/ai-test",
            json=test_data,
            timeout=30
        )
        response_time_ms = int((time.time() - start_time) * 1000)
        
        if response.status_code != 200:
            return {
                'success': False,
                'error': f'HTTP {response.status_code}: {response.text[:200]}'
            }
        
        result = response.json()
        ai_result = result.get('ai_result', '')
        
        # Basic validation
        if not ai_result or len(ai_result.strip()) < 10:
            return {
                'success': False,
                'error': f'AI response too short or empty: "{ai_result}"'
            }
        
        # Check if OpenRouter was actually used
        containers_tested = result.get('containers_tested', {})
        if containers_tested.get('openrouter') != 'success':
            return {
                'success': False,
                'error': f'OpenRouter not successful: {containers_tested.get("openrouter", "not tested")}'
            }
        
        return {
            'success': True,
            'ai_result': ai_result,
            'response_length': len(ai_result),
            'response_time_ms': response_time_ms,
            'containers_tested': containers_tested
        }
        
    except requests.exceptions.RequestException as e:
        return {'success': False, 'error': f'Request failed: {e}'}
    except json.JSONDecodeError as e:
        return {'success': False, 'error': f'JSON decode error: {e}'}

def test_different_prompt_types() -> Dict[str, Dict[str, Any]]:
    """Test different types of prompts"""
    test_prompts = {
        'creative': {
            'system_prompt': 'You are a creative storyteller.',
            'user_context': 'Write a one-sentence story about a robot.'
        },
        'factual': {
            'system_prompt': 'You are a factual assistant.',
            'user_context': 'What is 2+2?'
        },
        'conversational': {
            'system_prompt': 'You are a friendly chatbot.',
            'user_context': 'How are you today?'
        },
        'technical': {
            'system_prompt': 'You are a technical expert.',
            'user_context': 'Briefly explain what an API is.'
        }
    }
    
    results = {}
    
    for prompt_type, prompt_data in test_prompts.items():
        try:
            start_time = time.time()
            response = requests.post(
                f"{TEST_API_URL}/ai-test",
                json=prompt_data,
                timeout=25
            )
            response_time_ms = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                result = response.json()
                ai_result = result.get('ai_result', '')
                
                results[prompt_type] = {
                    'success': len(ai_result.strip()) > 5,
                    'response_length': len(ai_result),
                    'response_time_ms': response_time_ms,
                    'preview': ai_result[:100] + '...' if len(ai_result) > 100 else ai_result
                }
            else:
                results[prompt_type] = {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'response_time_ms': response_time_ms
                }
                
        except Exception as e:
            results[prompt_type] = {
                'success': False,
                'error': str(e),
                'response_time_ms': 0
            }
    
    return results

def test_error_handling() -> Dict[str, Any]:
    """Test error handling with invalid requests"""
    try:
        # Test with missing fields
        response = requests.post(
            f"{TEST_API_URL}/ai-test",
            json={"system_prompt": "Test"},  # Missing user_context
            timeout=10
        )
        
        # Should return 422 (validation error)
        if response.status_code != 422:
            return {
                'success': False,
                'error': f'Expected 422 for validation error, got {response.status_code}'
            }
        
        # Test with empty strings
        response = requests.post(
            f"{TEST_API_URL}/ai-test",
            json={"system_prompt": "", "user_context": ""},
            timeout=10
        )
        
        # Should handle gracefully (either 422 or 500 with proper error message)
        if response.status_code not in [422, 500]:
            return {
                'success': False,
                'error': f'Unexpected status code for empty prompts: {response.status_code}'
            }
        
        return {'success': True}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def test_performance() -> Dict[str, Any]:
    """Test performance with multiple concurrent requests"""
    import concurrent.futures
    import threading
    
    def make_request():
        try:
            start_time = time.time()
            response = requests.post(
                f"{TEST_API_URL}/ai-test",
                json={
                    "system_prompt": "You are a helpful assistant.",
                    "user_context": f"Test request at {time.time()}"
                },
                timeout=30
            )
            response_time = (time.time() - start_time) * 1000
            
            return {
                'success': response.status_code == 200,
                'response_time': response_time,
                'status_code': response.status_code
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response_time': 30000  # Timeout
            }
    
    # Run 3 concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(make_request) for _ in range(3)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    successful_requests = [r for r in results if r['success']]
    response_times = [r['response_time'] for r in results if 'response_time' in r]
    
    success_rate = (len(successful_requests) / len(results)) * 100
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    issues = []
    if success_rate < 100:
        issues.append(f"Success rate too low: {success_rate}%")
    if avg_response_time > 10000:  # 10 seconds
        issues.append(f"Average response time too high: {avg_response_time}ms")
    
    return {
        'success': len(issues) == 0,
        'success_rate': success_rate,
        'avg_response_time': int(avg_response_time),
        'total_requests': len(results),
        'successful_requests': len(successful_requests),
        'issues': issues
    }

if __name__ == '__main__':
    success = run_test()
    sys.exit(0 if success else 1)