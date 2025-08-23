#!/usr/bin/env python3
"""
Test 06: End-to-End Integration Test
Comprehensive test that validates all 5 containers working together
"""

import sys
import time
import json
import requests
import asyncio
import asyncpg
import redis
from minio import Minio
from typing import Dict, Any
import numpy as np

# Configuration
API_URL = "http://localhost:8000"
HEALTH_URL = "http://localhost/health"
DATABASE_URL = "postgresql://pocuser:pocpass@localhost:5432/poc_db"

def run_test():
    """Run comprehensive end-to-end test"""
    print("=" * 60)
    print("TEST 06: END-TO-END INTEGRATION TEST")
    print("=" * 60)
    
    # Test 1: Full system health
    print("\n1. Validating system health...")
    health_status = test_system_health()
    if not health_status['success']:
        print("❌ FAILED: System health check failed")
        return False
    print("✅ All systems healthy")
    
    # Test 2: Complete AI workflow
    print("\n2. Testing complete AI workflow...")
    workflow_status = test_complete_ai_workflow()
    if not workflow_status['success']:
        print("❌ FAILED: AI workflow failed")
        print(f"Error: {workflow_status.get('error', 'Unknown error')}")
        return False
    print("✅ Complete AI workflow successful")
    print(f"  Response generated: {workflow_status['ai_response_length']} chars")
    print(f"  Database logged: {workflow_status['database_stored']}")
    print(f"  Vector search: {workflow_status['vector_similarity_found']}")
    
    # Test 3: Storage and retrieval workflow
    print("\n3. Testing storage and retrieval workflow...")
    storage_status = test_storage_retrieval_workflow()
    if not storage_status['success']:
        print("❌ FAILED: Storage workflow failed")
        print(f"Error: {storage_status.get('error', 'Unknown error')}")
        return False
    print("✅ Storage and retrieval workflow successful")
    print(f"  Files stored: {storage_status['files_stored']}")
    print(f"  Cache operations: {storage_status['cache_operations']}")
    
    # Test 4: Concurrent operations
    print("\n4. Testing concurrent operations...")
    concurrent_status = test_concurrent_operations()
    if not concurrent_status['success']:
        print("❌ FAILED: Concurrent operations failed")
        print(f"Error: {concurrent_status.get('error', 'Unknown error')}")
        return False
    print("✅ Concurrent operations successful")
    print(f"  Concurrent requests: {concurrent_status['concurrent_requests']}")
    print(f"  Success rate: {concurrent_status['success_rate']}%")
    
    # Test 5: Data consistency
    print("\n5. Testing data consistency...")
    consistency_status = test_data_consistency()
    if not consistency_status['success']:
        print("❌ FAILED: Data consistency issues")
        print(f"Error: {consistency_status.get('error', 'Unknown error')}")
        return False
    print("✅ Data consistency verified")
    print(f"  Consistency checks passed: {consistency_status['checks_passed']}")
    
    # Test 6: Error handling and recovery
    print("\n6. Testing error handling and recovery...")
    error_handling_status = test_error_handling()
    if not error_handling_status['success']:
        print("❌ FAILED: Error handling issues")
        print(f"Error: {error_handling_status.get('error', 'Unknown error')}")
        return False
    print("✅ Error handling working correctly")
    
    # Test 7: Performance under load
    print("\n7. Testing performance under load...")
    performance_status = test_performance_load()
    if not performance_status['success']:
        print("❌ FAILED: Performance test failed")
        print(f"Issues: {performance_status.get('issues', [])}")
        return False
    print("✅ Performance test passed")
    print(f"  Average response time: {performance_status['avg_response_time']}ms")
    print(f"  Throughput: {performance_status['requests_per_second']} req/s")
    
    print("\n" + "=" * 60)
    print("✅ TEST 06 PASSED: Complete end-to-end integration successful")
    print("🎉 ALL 5 CONTAINERS WORKING TOGETHER PERFECTLY!")
    print("=" * 60)
    return True

def test_system_health() -> Dict[str, Any]:
    """Test overall system health"""
    try:
        response = requests.get(HEALTH_URL, timeout=15)
        if response.status_code != 200:
            return {'success': False, 'error': f'Health endpoint returned {response.status_code}'}
        
        health_data = response.json()
        overall_status = health_data.get('status', 'unknown')
        
        if overall_status != 'healthy':
            return {'success': False, 'error': f'System status is {overall_status}'}
        
        # Check individual services
        containers = health_data.get('containers', {})
        unhealthy_services = []
        
        for service, details in containers.items():
            service_status = details.get('status', 'unknown') if isinstance(details, dict) else 'unknown'
            if service_status != 'healthy':
                unhealthy_services.append(service)
        
        if unhealthy_services:
            return {'success': False, 'error': f'Unhealthy services: {unhealthy_services}'}
        
        return {'success': True, 'services_healthy': len(containers)}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def test_complete_ai_workflow() -> Dict[str, Any]:
    """Test complete AI workflow with all services"""
    try:
        # Step 1: Send AI request
        ai_request = {
            "system_prompt": "You are a creative writing assistant. Be descriptive and engaging.",
            "user_context": "Write a short story about a robot discovering emotions for the first time. Include themes of curiosity and wonder."
        }
        
        start_time = time.time()
        response = requests.post(f"{API_URL}/ai-test", json=ai_request, timeout=45)
        response_time = time.time() - start_time
        
        if response.status_code != 200:
            return {'success': False, 'error': f'AI request failed: {response.status_code}'}
        
        result = response.json()
        ai_result = result.get('ai_result', '')
        containers_tested = result.get('containers_tested', {})
        
        if not ai_result or len(ai_result) < 50:
            return {'success': False, 'error': 'AI response too short'}
        
        # Step 2: Verify database storage
        async def check_database():
            conn = await asyncpg.connect(DATABASE_URL, timeout=10)
            try:
                # Find the most recent entry
                row = await conn.fetchrow("""
                    SELECT id, system_prompt, user_context, ai_result, embedding, created_at
                    FROM ai_test_logs 
                    ORDER BY created_at DESC 
                    LIMIT 1
                """)
                
                if not row:
                    return {'stored': False}
                
                # Check if embedding exists and has correct dimensions
                has_embedding = row['embedding'] is not None
                embedding_dims = 0
                
                if has_embedding:
                    embedding_dims = await conn.fetchval(
                        "SELECT vector_dims(embedding) FROM ai_test_logs WHERE id = $1", 
                        row['id']
                    )
                
                return {
                    'stored': True,
                    'has_embedding': has_embedding,
                    'embedding_dims': embedding_dims,
                    'content_matches': ai_result in row['ai_result']
                }
            finally:
                await conn.close()
        
        db_status = asyncio.run(check_database())
        
        # Step 3: Test vector similarity search
        similarity_found = False
        if db_status.get('has_embedding'):
            async def test_similarity():
                conn = await asyncpg.connect(DATABASE_URL, timeout=10)
                try:
                    # Find similar entries
                    similar = await conn.fetch("""
                        SELECT id, 1 - (embedding <=> (
                            SELECT embedding FROM ai_test_logs ORDER BY created_at DESC LIMIT 1
                        )) as similarity
                        FROM ai_test_logs 
                        WHERE embedding IS NOT NULL
                        ORDER BY similarity DESC
                        LIMIT 5
                    """)
                    return len(similar) > 0
                finally:
                    await conn.close()
            
            similarity_found = asyncio.run(test_similarity())
        
        return {
            'success': True,
            'ai_response_length': len(ai_result),
            'response_time': response_time,
            'database_stored': db_status.get('stored', False),
            'has_embedding': db_status.get('has_embedding', False),
            'embedding_dims': db_status.get('embedding_dims', 0),
            'vector_similarity_found': similarity_found,
            'containers_tested': containers_tested
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def test_storage_retrieval_workflow() -> Dict[str, Any]:
    """Test storage and retrieval across MinIO and Redis"""
    try:
        # Test MinIO storage
        minio_client = Minio(
            "localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin123",
            secure=False
        )
        
        # Test Redis cache
        redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
        
        # Store test data
        test_data = {
            'workflow_test': True,
            'timestamp': time.time(),
            'test_content': 'This is end-to-end test data'
        }
        
        # Store in MinIO
        import io
        json_data = json.dumps(test_data)
        minio_client.put_object(
            "poc-bucket",
            "test/e2e-workflow.json",
            io.BytesIO(json_data.encode()),
            length=len(json_data)
        )
        
        # Store in Redis cache
        redis_client.setex("e2e:test:data", 300, json_data)  # 5 minutes TTL
        
        # Retrieve and verify
        # From MinIO
        minio_response = minio_client.get_object("poc-bucket", "test/e2e-workflow.json")
        minio_data = json.loads(minio_response.read().decode())
        minio_response.close()
        minio_response.release_conn()
        
        # From Redis
        redis_data = json.loads(redis_client.get("e2e:test:data"))
        
        # Verify data consistency
        data_matches = (minio_data == test_data == redis_data)
        
        # Cleanup
        minio_client.remove_object("poc-bucket", "test/e2e-workflow.json")
        redis_client.delete("e2e:test:data")
        
        return {
            'success': data_matches,
            'files_stored': 2,  # MinIO + Redis
            'cache_operations': 3,  # set, get, delete
            'data_consistent': data_matches
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def test_concurrent_operations() -> Dict[str, Any]:
    """Test concurrent operations across all services"""
    import concurrent.futures
    import threading
    
    def make_ai_request(request_id):
        try:
            response = requests.post(
                f"{API_URL}/ai-test",
                json={
                    "system_prompt": "You are a helpful assistant.",
                    "user_context": f"Concurrent test request #{request_id}. Respond with a unique identifier."
                },
                timeout=30
            )
            return {
                'success': response.status_code == 200,
                'request_id': request_id,
                'response_time': response.elapsed.total_seconds() * 1000
            }
        except Exception as e:
            return {'success': False, 'request_id': request_id, 'error': str(e)}
    
    try:
        # Run 5 concurrent requests
        concurrent_requests = 5
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            futures = [executor.submit(make_ai_request, i) for i in range(concurrent_requests)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        successful_requests = [r for r in results if r.get('success', False)]
        success_rate = (len(successful_requests) / len(results)) * 100
        
        return {
            'success': success_rate >= 80,  # Allow 20% failure rate
            'concurrent_requests': concurrent_requests,
            'successful_requests': len(successful_requests),
            'success_rate': success_rate,
            'avg_response_time': sum(r.get('response_time', 0) for r in successful_requests) / len(successful_requests) if successful_requests else 0
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def test_data_consistency() -> Dict[str, Any]:
    """Test data consistency across services"""
    try:
        checks_passed = 0
        total_checks = 3
        
        # Check 1: Database consistency
        async def check_db_consistency():
            conn = await asyncpg.connect(DATABASE_URL, timeout=10)
            try:
                # Check if recent entries have proper structure
                recent_count = await conn.fetchval("""
                    SELECT COUNT(*) FROM ai_test_logs 
                    WHERE created_at > NOW() - INTERVAL '1 hour'
                    AND system_prompt IS NOT NULL 
                    AND user_context IS NOT NULL 
                    AND ai_result IS NOT NULL
                """)
                return recent_count > 0
            finally:
                await conn.close()
        
        db_consistent = asyncio.run(check_db_consistency())
        if db_consistent:
            checks_passed += 1
        
        # Check 2: Redis consistency
        redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
        test_key = "consistency:test"
        test_value = f"test_value_{int(time.time())}"
        
        redis_client.set(test_key, test_value)
        retrieved_value = redis_client.get(test_key)
        redis_client.delete(test_key)
        
        redis_consistent = retrieved_value == test_value
        if redis_consistent:
            checks_passed += 1
        
        # Check 3: MinIO consistency
        minio_client = Minio(
            "localhost:9000",
            access_key="minioadmin", 
            secret_key="minioadmin123",
            secure=False
        )
        
        import io
        test_content = f"consistency_test_{int(time.time())}"
        object_name = "test/consistency-check.txt"
        
        minio_client.put_object(
            "poc-bucket",
            object_name,
            io.BytesIO(test_content.encode()),
            length=len(test_content)
        )
        
        response = minio_client.get_object("poc-bucket", object_name)
        retrieved_content = response.read().decode()
        response.close()
        response.release_conn()
        
        minio_client.remove_object("poc-bucket", object_name)
        
        minio_consistent = retrieved_content == test_content
        if minio_consistent:
            checks_passed += 1
        
        return {
            'success': checks_passed == total_checks,
            'checks_passed': checks_passed,
            'total_checks': total_checks,
            'db_consistent': db_consistent,
            'redis_consistent': redis_consistent,
            'minio_consistent': minio_consistent
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def test_error_handling() -> Dict[str, Any]:
    """Test error handling across services"""
    try:
        # Test invalid AI request
        invalid_response = requests.post(
            f"{API_URL}/ai-test",
            json={"system_prompt": ""},  # Missing user_context
            timeout=10
        )
        
        handles_validation_error = invalid_response.status_code == 422
        
        # Test non-existent endpoint
        not_found_response = requests.get(f"{API_URL}/non-existent-endpoint", timeout=10)
        handles_not_found = not_found_response.status_code == 404
        
        return {
            'success': handles_validation_error and handles_not_found,
            'handles_validation_error': handles_validation_error,
            'handles_not_found': handles_not_found
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def test_performance_load() -> Dict[str, Any]:
    """Test performance under load"""
    import concurrent.futures
    
    def make_request():
        start_time = time.time()
        try:
            response = requests.post(
                f"{API_URL}/ai-test",
                json={
                    "system_prompt": "You are a helpful assistant.",
                    "user_context": "Simple performance test request."
                },
                timeout=25
            )
            response_time = (time.time() - start_time) * 1000
            return {
                'success': response.status_code == 200,
                'response_time': response_time
            }
        except Exception:
            return {'success': False, 'response_time': 25000}  # Timeout
    
    try:
        # Run 10 requests with some concurrency
        total_requests = 10
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(make_request) for _ in range(total_requests)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        total_time = time.time() - start_time
        
        successful_results = [r for r in results if r['success']]
        success_rate = (len(successful_results) / len(results)) * 100
        
        if successful_results:
            avg_response_time = sum(r['response_time'] for r in successful_results) / len(successful_results)
        else:
            avg_response_time = 0
        
        requests_per_second = total_requests / total_time
        
        issues = []
        if success_rate < 90:
            issues.append(f"Low success rate: {success_rate}%")
        if avg_response_time > 15000:  # 15 seconds
            issues.append(f"High response time: {avg_response_time}ms")
        if requests_per_second < 0.5:
            issues.append(f"Low throughput: {requests_per_second} req/s")
        
        return {
            'success': len(issues) == 0,
            'success_rate': success_rate,
            'avg_response_time': int(avg_response_time),
            'requests_per_second': round(requests_per_second, 2),
            'total_requests': total_requests,
            'issues': issues
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

if __name__ == '__main__':
    success = run_test()
    sys.exit(0 if success else 1)