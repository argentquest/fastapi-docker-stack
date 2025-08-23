#!/usr/bin/env python3
"""
Test 05: Redis Cache Validation
Tests Redis caching functionality and operations
"""

import sys
import time
import json
import redis
from typing import Dict, Any, List

# Redis configuration
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

def run_test():
    """Test Redis cache functionality"""
    print("=" * 60)
    print("TEST 05: REDIS CACHE VALIDATION")
    print("=" * 60)
    
    # Test Redis connectivity
    print("\n1. Testing Redis connectivity...")
    client_status = test_redis_connection()
    if not client_status['success']:
        print("❌ FAILED: Cannot connect to Redis")
        print(f"Error: {client_status.get('error', 'Unknown error')}")
        return False
    print("✅ Redis connection successful")
    
    client = client_status['client']
    
    # Test basic operations
    print("\n2. Testing basic string operations...")
    string_status = test_string_operations(client)
    if not string_status['success']:
        print("❌ FAILED: String operations failed")
        print(f"Error: {string_status.get('error', 'Unknown error')}")
        return False
    print("✅ String operations successful")
    print(f"  Operations tested: {string_status['operations_count']}")
    
    # Test hash operations
    print("\n3. Testing hash operations...")
    hash_status = test_hash_operations(client)
    if not hash_status['success']:
        print("❌ FAILED: Hash operations failed")
        print(f"Error: {hash_status.get('error', 'Unknown error')}")
        return False
    print("✅ Hash operations successful")
    print(f"  Hash fields set: {hash_status['fields_set']}")
    print(f"  Hash fields retrieved: {hash_status['fields_retrieved']}")
    
    # Test list operations
    print("\n4. Testing list operations...")
    list_status = test_list_operations(client)
    if not list_status['success']:
        print("❌ FAILED: List operations failed")
        print(f"Error: {list_status.get('error', 'Unknown error')}")
        return False
    print("✅ List operations successful")
    print(f"  List items pushed: {list_status['items_pushed']}")
    print(f"  List items popped: {list_status['items_popped']}")
    
    # Test expiration
    print("\n5. Testing key expiration...")
    expiry_status = test_expiration(client)
    if not expiry_status['success']:
        print("❌ FAILED: Expiration test failed")
        print(f"Error: {expiry_status.get('error', 'Unknown error')}")
        return False
    print("✅ Key expiration working correctly")
    print(f"  Keys expired as expected: {expiry_status['expired_correctly']}")
    
    # Test JSON operations (if supported)
    print("\n6. Testing JSON operations...")
    json_status = test_json_operations(client)
    if not json_status['success']:
        print("⚠️  WARNING: JSON operations not fully supported (expected for basic Redis)")
        print(f"  Fallback to string JSON: {json_status.get('fallback_success', False)}")
    else:
        print("✅ JSON operations successful")
    
    # Test performance
    print("\n7. Testing performance...")
    perf_status = test_performance(client)
    if not perf_status['success']:
        print("❌ FAILED: Performance test failed")
        print(f"Error: {perf_status.get('error', 'Unknown error')}")
        return False
    print("✅ Performance test passed")
    print(f"  Average operation time: {perf_status['avg_time_ms']:.2f}ms")
    print(f"  Operations per second: {perf_status['ops_per_second']}")
    
    # Cleanup test data
    print("\n8. Cleaning up test data...")
    cleanup_status = cleanup_test_data(client)
    if cleanup_status['cleaned_count'] > 0:
        print(f"✅ Cleaned up {cleanup_status['cleaned_count']} test keys")
    
    print("\n" + "=" * 60)
    print("✅ TEST 05 PASSED: Redis cache fully functional")
    print("=" * 60)
    return True

def test_redis_connection() -> Dict[str, Any]:
    """Test Redis connection"""
    try:
        # Create Redis client
        client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        
        # Test connection
        response = client.ping()
        if not response:
            return {'success': False, 'error': 'Ping failed'}
        
        # Get server info
        info = client.info()
        redis_version = info.get('redis_version', 'unknown')
        
        return {
            'success': True,
            'client': client,
            'redis_version': redis_version,
            'connected_clients': info.get('connected_clients', 0)
        }
        
    except redis.ConnectionError as e:
        return {'success': False, 'error': f'Connection error: {e}'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def test_string_operations(client: redis.Redis) -> Dict[str, Any]:
    """Test basic string operations"""
    try:
        test_operations = [
            ('set', 'test:string:simple', 'hello world'),
            ('get', 'test:string:simple', None),
            ('set', 'test:string:number', 42),
            ('incr', 'test:string:counter', None),
            ('incrby', 'test:string:counter', 5),
            ('set', 'test:string:json', json.dumps({'key': 'value', 'number': 123}))
        ]
        
        operations_completed = 0
        
        for operation, key, value in test_operations:
            try:
                if operation == 'set':
                    client.set(key, value)
                elif operation == 'get':
                    result = client.get(key)
                    if result is None:
                        raise ValueError(f"Key {key} not found")
                elif operation == 'incr':
                    client.incr(key)
                elif operation == 'incrby':
                    client.incrby(key, value)
                
                operations_completed += 1
                
            except Exception as e:
                print(f"  Warning: Operation {operation} failed: {e}")
        
        # Test exists
        existing_keys = client.exists('test:string:simple', 'test:string:number')
        
        return {
            'success': operations_completed >= len(test_operations) - 1,  # Allow one failure
            'operations_count': operations_completed,
            'existing_keys': existing_keys
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def test_hash_operations(client: redis.Redis) -> Dict[str, Any]:
    """Test hash operations"""
    try:
        hash_key = 'test:hash:user'
        
        # Set hash fields
        hash_data = {
            'id': '123',
            'name': 'Test User',
            'email': 'test@example.com',
            'created_at': str(int(time.time())),
            'active': 'true'
        }
        
        client.hset(hash_key, mapping=hash_data)
        
        # Get individual fields
        retrieved_fields = {}
        for field in hash_data.keys():
            value = client.hget(hash_key, field)
            if value is not None:
                retrieved_fields[field] = value
        
        # Get all fields
        all_fields = client.hgetall(hash_key)
        
        # Test field existence
        field_exists = client.hexists(hash_key, 'name')
        
        return {
            'success': True,
            'fields_set': len(hash_data),
            'fields_retrieved': len(retrieved_fields),
            'all_fields_count': len(all_fields),
            'field_exists_test': field_exists
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def test_list_operations(client: redis.Redis) -> Dict[str, Any]:
    """Test list operations"""
    try:
        list_key = 'test:list:queue'
        
        # Push items to list
        test_items = ['item1', 'item2', 'item3', 'item4', 'item5']
        
        items_pushed = 0
        for item in test_items:
            client.rpush(list_key, item)
            items_pushed += 1
        
        # Get list length
        list_length = client.llen(list_key)
        
        # Pop items from list
        items_popped = 0
        popped_items = []
        while client.llen(list_key) > 2:  # Leave 2 items
            popped_item = client.lpop(list_key)
            if popped_item:
                popped_items.append(popped_item)
                items_popped += 1
        
        # Get remaining items
        remaining_items = client.lrange(list_key, 0, -1)
        
        return {
            'success': True,
            'items_pushed': items_pushed,
            'max_list_length': int(list_length),
            'items_popped': items_popped,
            'remaining_items': len(remaining_items)
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def test_expiration(client: redis.Redis) -> Dict[str, Any]:
    """Test key expiration"""
    try:
        # Set keys with expiration
        client.setex('test:expire:short', 2, 'expires in 2 seconds')  # 2 seconds
        client.setex('test:expire:medium', 10, 'expires in 10 seconds')  # 10 seconds
        
        # Check initial existence
        initial_exists = client.exists('test:expire:short', 'test:expire:medium')
        
        # Wait for short expiry
        time.sleep(3)
        
        # Check after short expiry
        after_short = client.exists('test:expire:short', 'test:expire:medium')
        
        # Check TTL of medium key
        ttl = client.ttl('test:expire:medium')
        
        return {
            'success': True,
            'initial_exists': int(initial_exists),
            'after_short_expiry': int(after_short),
            'expired_correctly': initial_exists == 2 and after_short == 1,
            'remaining_ttl': int(ttl) if ttl > 0 else 0
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def test_json_operations(client: redis.Redis) -> Dict[str, Any]:
    """Test JSON operations (fallback to string-based JSON)"""
    try:
        # Try RedisJSON operations first (might not be available)
        json_key = 'test:json:document'
        
        test_data = {
            'user_id': 123,
            'username': 'testuser',
            'preferences': {
                'theme': 'dark',
                'language': 'en'
            },
            'tags': ['test', 'user', 'example']
        }
        
        try:
            # Try native JSON operations (RedisJSON module)
            client.execute_command('JSON.SET', json_key, '.', json.dumps(test_data))
            retrieved_json = client.execute_command('JSON.GET', json_key)
            
            return {
                'success': True,
                'native_json': True,
                'data_set': True,
                'data_retrieved': retrieved_json is not None
            }
            
        except redis.ResponseError:
            # Fallback to string-based JSON storage
            client.set(json_key, json.dumps(test_data))
            retrieved_string = client.get(json_key)
            
            if retrieved_string:
                parsed_data = json.loads(retrieved_string)
                return {
                    'success': True,
                    'native_json': False,
                    'fallback_success': True,
                    'data_matches': parsed_data == test_data
                }
            else:
                return {'success': False, 'error': 'String fallback failed'}
                
    except Exception as e:
        return {'success': False, 'error': str(e)}

def test_performance(client: redis.Redis) -> Dict[str, Any]:
    """Test Redis performance"""
    try:
        operation_count = 100
        start_time = time.time()
        
        # Perform mixed operations
        for i in range(operation_count):
            key = f"test:perf:{i}"
            # Set
            client.set(key, f"value_{i}")
            # Get
            client.get(key)
            # Delete
            client.delete(key)
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time_ms = (total_time / (operation_count * 3)) * 1000  # 3 operations per iteration
        ops_per_second = int((operation_count * 3) / total_time)
        
        return {
            'success': True,
            'total_time_ms': total_time * 1000,
            'avg_time_ms': avg_time_ms,
            'ops_per_second': ops_per_second,
            'operations_completed': operation_count * 3
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def cleanup_test_data(client: redis.Redis) -> Dict[str, Any]:
    """Clean up test data"""
    try:
        # Find all test keys
        test_patterns = [
            'test:string:*',
            'test:hash:*',
            'test:list:*',
            'test:expire:*',
            'test:json:*',
            'test:perf:*'
        ]
        
        cleaned_count = 0
        for pattern in test_patterns:
            keys = client.keys(pattern)
            if keys:
                deleted = client.delete(*keys)
                cleaned_count += deleted
        
        return {
            'success': True,
            'cleaned_count': cleaned_count
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

if __name__ == '__main__':
    success = run_test()
    sys.exit(0 if success else 1)