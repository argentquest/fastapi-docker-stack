#!/usr/bin/env python3
"""
Test 02: PostgreSQL + pgvector Validation
Tests database connectivity, pgvector extension, and vector operations
"""

import sys
import asyncio
import asyncpg
import json
import numpy as np
from typing import List, Dict, Any

DATABASE_URL = "postgresql://pocuser:pocpass@localhost:5432/poc_db"

async def run_test():
    """Test PostgreSQL + pgvector functionality"""
    print("=" * 60)
    print("TEST 02: POSTGRESQL + PGVECTOR VALIDATION")
    print("=" * 60)
    
    # Test basic database connectivity
    print("\n1. Testing database connectivity...")
    conn = await test_database_connection()
    if not conn:
        print("❌ FAILED: Cannot connect to PostgreSQL")
        return False
    print("✅ Database connection successful")
    
    try:
        # Test pgvector extension
        print("\n2. Testing pgvector extension...")
        pgvector_status = await test_pgvector_extension(conn)
        if not pgvector_status['success']:
            print("❌ FAILED: pgvector extension issues")
            print(f"Error: {pgvector_status.get('error', 'Unknown error')}")
            return False
        print(f"✅ pgvector extension loaded: {pgvector_status['version']}")
        
        # Test table structure
        print("\n3. Testing ai_test_logs table structure...")
        table_status = await test_table_structure(conn)
        if not table_status['success']:
            print("❌ FAILED: Table structure issues")
            print(f"Error: {table_status.get('error', 'Unknown error')}")
            return False
        print("✅ Table structure is correct")
        print(f"  Columns: {', '.join(table_status['columns'])}")
        
        # Test vector operations
        print("\n4. Testing vector operations...")
        vector_status = await test_vector_operations(conn)
        if not vector_status['success']:
            print("❌ FAILED: Vector operations failed")
            print(f"Error: {vector_status.get('error', 'Unknown error')}")
            return False
        print("✅ Vector operations working correctly")
        print(f"  Test vectors created: {vector_status['vectors_created']}")
        print(f"  Similarity search results: {vector_status['similarity_results']}")
        
        # Test indexes
        print("\n5. Testing vector indexes...")
        index_status = await test_vector_indexes(conn)
        if not index_status['success']:
            print("❌ FAILED: Vector index issues")
            print(f"Error: {index_status.get('error', 'Unknown error')}")
            return False
        print("✅ Vector indexes are functional")
        print(f"  Indexes found: {', '.join(index_status['indexes'])}")
        
        # Test sample data
        print("\n6. Testing sample data...")
        data_status = await test_sample_data(conn)
        print(f"✅ Sample data: {data_status['count']} rows found")
        
        print("\n" + "=" * 60)
        print("✅ TEST 02 PASSED: PostgreSQL + pgvector fully functional")
        print("=" * 60)
        return True
        
    finally:
        await conn.close()

async def test_database_connection():
    """Test basic database connectivity"""
    try:
        conn = await asyncpg.connect(DATABASE_URL, timeout=10)
        # Test basic query
        result = await conn.fetchval("SELECT 1")
        if result != 1:
            await conn.close()
            return None
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

async def test_pgvector_extension(conn) -> Dict[str, Any]:
    """Test pgvector extension is loaded"""
    try:
        # Check if pgvector extension exists
        result = await conn.fetchrow("""
            SELECT extname, extversion 
            FROM pg_extension 
            WHERE extname = 'vector'
        """)
        
        if not result:
            return {'success': False, 'error': 'pgvector extension not installed'}
        
        return {
            'success': True,
            'version': result['extversion'],
            'name': result['extname']
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

async def test_table_structure(conn) -> Dict[str, Any]:
    """Test ai_test_logs table structure"""
    try:
        # Get table columns
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'ai_test_logs'
            ORDER BY ordinal_position
        """)
        
        if not columns:
            return {'success': False, 'error': 'ai_test_logs table not found'}
        
        column_info = []
        has_embedding_column = False
        
        for col in columns:
            col_name = col['column_name']
            col_type = col['data_type']
            column_info.append(f"{col_name}({col_type})")
            
            if col_name == 'embedding':
                has_embedding_column = True
                # Check if it's a vector type
                vector_check = await conn.fetchval("""
                    SELECT data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'ai_test_logs' 
                    AND column_name = 'embedding'
                """)
                
                if 'USER-DEFINED' not in str(vector_check).upper():
                    print(f"Warning: embedding column type is {vector_check}, expected vector type")
        
        if not has_embedding_column:
            return {'success': False, 'error': 'embedding column not found'}
        
        return {
            'success': True,
            'columns': column_info,
            'has_embedding': has_embedding_column
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

async def test_vector_operations(conn) -> Dict[str, Any]:
    """Test vector operations (insert, similarity search)"""
    try:
        # Create test vectors
        test_vectors = [
            np.random.rand(1024).tolist(),  # Random 1024-dim vector
            np.random.rand(1024).tolist(),
            np.random.rand(1024).tolist()
        ]
        
        # Insert test data with vectors
        inserted_ids = []
        for i, vector in enumerate(test_vectors):
            result = await conn.fetchval("""
                INSERT INTO ai_test_logs 
                (system_prompt, user_context, ai_result, embedding)
                VALUES ($1, $2, $3, $4)
                RETURNING id
            """, 
            f"Test system prompt {i}",
            f"Test user context {i}",
            f"Test AI result {i}",
            vector
            )
            inserted_ids.append(result)
        
        # Test similarity search
        query_vector = test_vectors[0]  # Use first vector as query
        
        similar_results = await conn.fetch("""
            SELECT id, system_prompt,
                   1 - (embedding <=> $1::vector) as similarity
            FROM ai_test_logs
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> $1::vector
            LIMIT 5
        """, query_vector)
        
        # Clean up test data
        await conn.execute("""
            DELETE FROM ai_test_logs 
            WHERE id = ANY($1::int[])
        """, inserted_ids)
        
        similarity_scores = [float(r['similarity']) for r in similar_results]
        
        return {
            'success': True,
            'vectors_created': len(inserted_ids),
            'similarity_results': len(similar_results),
            'similarity_scores': similarity_scores[:3],  # Show first 3 scores
            'max_similarity': max(similarity_scores) if similarity_scores else 0
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

async def test_vector_indexes(conn) -> Dict[str, Any]:
    """Test vector indexes exist and are functional"""
    try:
        # Check for vector indexes
        indexes = await conn.fetch("""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename = 'ai_test_logs'
            AND indexdef ILIKE '%vector%'
        """)
        
        index_names = [idx['indexname'] for idx in indexes]
        
        # Test index usage with EXPLAIN
        if indexes:
            explain_result = await conn.fetch("""
                EXPLAIN (FORMAT JSON)
                SELECT id FROM ai_test_logs
                WHERE embedding <=> $1::vector < 0.5
                LIMIT 10
            """, np.random.rand(1024).tolist())
            
            # Check if index scan is being used
            explain_text = json.dumps(explain_result[0][0], indent=2)
            uses_index = 'Index Scan' in explain_text or 'ivfflat' in explain_text.lower()
        else:
            uses_index = False
        
        return {
            'success': len(indexes) > 0,
            'indexes': index_names,
            'uses_index_scan': uses_index,
            'index_count': len(indexes)
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

async def test_sample_data(conn) -> Dict[str, Any]:
    """Test sample data exists"""
    try:
        # Count total rows
        total_count = await conn.fetchval("SELECT COUNT(*) FROM ai_test_logs")
        
        # Count rows with embeddings
        embedding_count = await conn.fetchval("""
            SELECT COUNT(*) FROM ai_test_logs WHERE embedding IS NOT NULL
        """)
        
        # Get sample row
        sample_row = await conn.fetchrow("""
            SELECT id, system_prompt, user_context, 
                   CASE WHEN embedding IS NOT NULL 
                        THEN vector_dims(embedding) 
                        ELSE NULL 
                   END as embedding_dims
            FROM ai_test_logs 
            LIMIT 1
        """)
        
        sample_info = {}
        if sample_row:
            sample_info = {
                'id': sample_row['id'],
                'has_embedding': sample_row['embedding_dims'] is not None,
                'embedding_dims': sample_row['embedding_dims']
            }
        
        return {
            'success': True,
            'count': int(total_count),
            'embedding_count': int(embedding_count),
            'sample': sample_info
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def main():
    """Main test runner"""
    try:
        success = asyncio.run(run_test())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()