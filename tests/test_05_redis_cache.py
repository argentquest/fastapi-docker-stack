#!/usr/bin/env python3
"""
Test 05: Redis Cache Validation

This script tests the functionality of the Redis caching service.

It verifies:
- Client connectivity to the Redis server.
- Basic SET/GET/DELETE operations.
- Key expiration (TTL).
- A cleanup routine to remove test keys.
"""

import sys
import time
import redis
from typing import Dict, Any

# Configuration for connecting to the local Redis container.
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
TEST_KEY_PREFIX = "test-suite:"

def main_test_logic():
    """Main function to run all Redis tests."""
    print("=" * 60)
    print("TEST 05: REDIS CACHE VALIDATION")
    print("=" * 60)
    
    client = None
    try:
        # --- Test 1: Client Connection ---
        print("\n1. Attempting to connect to Redis server...")
        client = test_redis_connection()
        if not client:
            raise ConnectionError("Could not create a Redis client.")
        print(f"✅ Redis connection successful (Version: {client.info()['redis_version']}).")

        # --- Test 2: Basic Operations ---
        print("\n2. Verifying basic SET, GET, and DELETE operations...")
        if not test_basic_operations(client):
            raise RuntimeError("Basic operations test failed.")
        print("✅ Basic SET, GET, and DELETE operations are working correctly.")

        # --- Test 3: Key Expiration ---
        print("\n3. Verifying key expiration (TTL)...")
        if not test_expiration(client):
            raise RuntimeError("Key expiration test failed.")
        print("✅ Key expiration is working correctly.")

    except Exception as e:
        print(f"\n❌ FAILED: An error occurred: {e}")
        return False
    finally:
        # --- Cleanup ---
        if client:
            print("\n4. Cleaning up test keys...")
            cleaned_count = cleanup_test_data(client)
            print(f"✅ Cleaned up {cleaned_count} test key(s).")

    print("\n" + "=" * 60)
    print("✅ TEST 05 PASSED: Redis cache is fully functional.")
    print("=" * 60)
    return True

def test_redis_connection() -> redis.Redis:
    """Tests connectivity to the Redis server by creating a client and sending a PING command."""
    client = redis.Redis(
        host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB,
        decode_responses=True, socket_connect_timeout=5, socket_timeout=5
    )
    # The PING command is the standard way to check if a server is alive and responsive.
    client.ping()
    return client

def test_basic_operations(client: redis.Redis) -> bool:
    """Tests a full cycle of SET, GET, and DELETE operations."""
    test_key = f"{TEST_KEY_PREFIX}basic-op"
    test_value = f"hello-redis-{time.time()}"

    # 1. SET the value.
    client.set(test_key, test_value)
    print(f"   -> SET '{test_key}'.")

    # 2. GET the value and verify it matches.
    retrieved_value = client.get(test_key)
    if retrieved_value != test_value:
        raise ValueError(f"Value mismatch: Expected '{test_value}', got '{retrieved_value}'.")
    print(f"   -> GET '{test_key}' and verified content.")

    # 3. DELETE the key.
    delete_count = client.delete(test_key)
    if delete_count != 1:
        raise ValueError(f"Expected to delete 1 key, but deleted {delete_count}.")
    print(f"   -> DELETE '{test_key}'.")

    # 4. Verify the key no longer exists.
    if client.exists(test_key):
        raise ValueError(f"Key '{test_key}' still exists after deletion.")
    print(f"   -> Verified key no longer exists.")
    return True

def test_expiration(client: redis.Redis) -> bool:
    """Tests the functionality of key expiration (Time To Live)."""
    test_key = f"{TEST_KEY_PREFIX}ttl-test"
    test_value = "this key will expire"
    expire_time_seconds = 2

    # Set a key with a 2-second expiration.
    client.setex(test_key, expire_time_seconds, test_value)
    print(f"   -> SET '{test_key}' with a {expire_time_seconds}s TTL.")

    # Verify the key exists immediately after setting.
    if not client.exists(test_key):
        raise ValueError("Key does not exist immediately after setting with EX.")
    
    # Wait for a duration longer than the expiration time.
    time.sleep(expire_time_seconds + 1)

    # Verify the key no longer exists.
    if client.exists(test_key):
        raise ValueError("Key still exists after it should have expired.")
    print(f"   -> Verified key no longer exists after {expire_time_seconds+1}s.")
    return True

def cleanup_test_data(client: redis.Redis) -> int:
    """Removes all keys created during the test run using a pattern match."""
    # Use the SCAN command to find all keys with the test prefix.
    # This is safer for production than using the KEYS command.
    test_keys = []
    cursor = '0'
    while cursor != 0:
        cursor, keys = client.scan(cursor=cursor, match=f"{TEST_KEY_PREFIX}*", count=100)
        test_keys.extend(keys)
    
    if not test_keys:
        return 0

    # Delete all found keys.
    return client.delete(*test_keys)

if __name__ == '__main__':
    try:
        if main_test_logic():
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        sys.exit(1)
