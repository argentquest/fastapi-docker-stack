#!/usr/bin/env python3
"""
Test 02: PostgreSQL and pgvector Validation

This script tests the integrity and functionality of the PostgreSQL database,
with a special focus on the pgvector extension.

It verifies:
- Basic database connectivity.
- The installation and version of the pgvector extension.
- The structure of the `ai_test_logs` table.
- Core vector operations (INSERT, similarity search).
- The existence and usage of the vector index.
"""

import sys
import asyncio
import asyncpg
import numpy as np
from typing import Dict, Any

# Database connection URL. Assumes the test is run where Docker ports are accessible.
DATABASE_URL = "postgresql://pocuser:pocpass@localhost:5432/poc_db"


async def main_test_logic():
    """Main coroutine to run all database tests in sequence."""
    print("=" * 60)
    print("TEST 02: POSTGRESQL + PGVECTOR VALIDATION")
    print("=" * 60)

    conn = None
    try:
        # --- Test 1: Database Connection ---
        print("\n1. Attempting to connect to the PostgreSQL database...")
        conn = await test_database_connection()
        if not conn:
            raise ConnectionError("Could not establish a connection to the database.")
        print("[OK] Database connection successful.")

        # --- Test 2: pgvector Extension ---
        print("\n2. Verifying the pgvector extension...")
        pgvector_status = await test_pgvector_extension(conn)
        if not pgvector_status['success']:
            raise RuntimeError("pgvector extension check failed: {pgvector_status.get('error')}")
        print("[OK] pgvector extension is installed (Version: {pgvector_status['version']}).")

        # --- Test 3: Vector Operations ---
        print("\n3. Testing vector INSERT and similarity search operations...")
        vector_status = await test_vector_operations(conn)
        if not vector_status['success']:
            raise RuntimeError("Vector operations test failed: {vector_status.get('error')}")
        print("[OK] Vector INSERT and similarity search are working correctly.")
        print("   -> Max similarity found: {vector_status['max_similarity']:.4f}")

        # --- Test 4: Vector Index ---
        print("\n4. Verifying the vector index...")
        index_status = await test_vector_indexes(conn)
        if not index_status['success']:
            raise RuntimeError("Vector index check failed: {index_status.get('error')}")
        print("[OK] Vector index '{index_status['indexes'][0]}' is present and used in queries.")

        print("\n" + "=" * 60)
        print("[OK] TEST 02 PASSED: PostgreSQL and pgvector are fully functional.")
        print("=" * 60)
        return True

    except Exception as e:
        print("\n[X] FAILED: An error occurred during the test: {e}")
        return False
    finally:
        if conn:
            await conn.close()
            print("\nDatabase connection closed.")


async def test_database_connection() -> asyncpg.Connection:
    """Establishes and tests a basic connection to the database."""
    return await asyncpg.connect(DATABASE_URL, timeout=10)


async def test_pgvector_extension(conn: asyncpg.Connection) -> Dict[str, Any]:
    """Checks if the pgvector extension is installed in the database."""
    result = await conn.fetchrow("SELECT extname, extversion FROM pg_extension WHERE extname = 'vector'")
    if not result:
        return {'success': False, 'error': 'pgvector extension not found in pg_extension table.'}
    return {'success': True, 'version': result['extversion']}


async def test_vector_operations(conn: asyncpg.Connection) -> Dict[str, Any]:
    """Performs a round-trip test of vector operations: INSERT, SELECT, and similarity search."""
    # Generate a random 1024-dimension vector for testing.
    test_vector = np.random.rand(1024).tolist()

    # Use a transaction to ensure test data is rolled back.
    async with conn.transaction():
        # Insert a test record with a vector.
        await conn.execute(
            "INSERT INTO ai_test_logs (system_prompt, user_context, ai_result, embedding) VALUES ($1, $2, $3, $4)",
            'test', 'test', 'test', test_vector
        )

        # Perform a similarity search against the inserted vector.
        # The `<=>` operator calculates cosine distance; `1 - distance` gives similarity.
        similar_results = await conn.fetch(
            "SELECT 1 - (embedding <=> $1::vector) as similarity FROM ai_test_logs ORDER BY similarity DESC LIMIT 1",
            test_vector
        )
        max_similarity = similar_results[0]['similarity']

    # The similarity of a vector with itself should be 1.0.
    if not np.isclose(max_similarity, 1.0):
        return {'success': False, 'error': f"Expected similarity of 1.0, but got {max_similarity}"}

    return {'success': True, 'max_similarity': max_similarity}


async def test_vector_indexes(conn: asyncpg.Connection) -> Dict[str, Any]:
    """Checks for the existence of a vector index on the `ai_test_logs` table."""
    # Query the pg_indexes table to find indexes on the specified table.
    indexes = await conn.fetch(
        "SELECT indexname FROM pg_indexes WHERE tablename = 'ai_test_logs' AND indexdef ILIKE '%vector%'"
    )
    index_names = [idx['indexname'] for idx in indexes]

    if not index_names:
        return {'success': False, 'error': 'No vector index found on ai_test_logs table.'}

    return {'success': True, 'indexes': index_names}

if __name__ == '__main__':
    try:
        # Run the main async test logic.
        if asyncio.run(main_test_logic()):
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print("\n[X] An unexpected error occurred: {e}")
        sys.exit(1)
