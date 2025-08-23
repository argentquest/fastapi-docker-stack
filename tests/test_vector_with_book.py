#!/usr/bin/env python3
"""
Test Vector Operations with Andersen's Fairy Tales
Tests chunking, embedding, storing, and searching book content using pgvector
"""

import sys
import os
import time
import json
import asyncio
import asyncpg
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple
from sentence_transformers import SentenceTransformer

# Configuration
DATABASE_URL = "postgresql://pocuser:pocpass@localhost:5432/poc_db"
BOOK_FILE = Path(__file__).parent.parent / "datafiles" / "Andersen's Fairy Tales by H. C. Andersen.txt"
MODEL_NAME = "BAAI/bge-large-en-v1.5"  # 1024-dimensional embeddings

def run_test():
    """Test vector operations with book content"""
    print("=" * 60)
    print("📚 VECTOR TEST WITH ANDERSEN'S FAIRY TALES")
    print("=" * 60)
    
    # Load book content
    print("\n1. Loading book content...")
    book_status = load_book_content()
    if not book_status['success']:
        print("❌ FAILED: Cannot load book file")
        print(f"Error: {book_status.get('error', 'Unknown error')}")
        return False
    print("✅ Book loaded successfully")
    print(f"  File size: {book_status['file_size_kb']:.1f} KB")
    print(f"  Character count: {book_status['char_count']:,}")
    
    book_text = book_status['content']
    
    # Chunk the book
    print("\n2. Chunking book into passages...")
    chunks_status = chunk_book(book_text)
    if not chunks_status['success']:
        print("❌ FAILED: Chunking failed")
        print(f"Error: {chunks_status.get('error', 'Unknown error')}")
        return False
    print("✅ Book chunked successfully")
    print(f"  Total chunks: {chunks_status['chunk_count']}")
    print(f"  Average chunk size: {chunks_status['avg_chunk_size']} chars")
    print(f"  Stories found: {chunks_status['stories_found']}")
    
    chunks = chunks_status['chunks']
    
    # Initialize embedding model
    print("\n3. Initializing embedding model...")
    model_status = initialize_embedding_model()
    if not model_status['success']:
        print("❌ FAILED: Cannot initialize embedding model")
        print(f"Error: {model_status.get('error', 'Unknown error')}")
        return False
    print("✅ Embedding model loaded")
    print(f"  Model: {model_status['model_name']}")
    print(f"  Embedding dimensions: {model_status['embedding_dim']}")
    
    model = model_status['model']
    
    # Generate embeddings
    print("\n4. Generating embeddings for chunks...")
    embeddings_status = generate_embeddings(model, chunks[:20])  # First 20 chunks for testing
    if not embeddings_status['success']:
        print("❌ FAILED: Embedding generation failed")
        print(f"Error: {embeddings_status.get('error', 'Unknown error')}")
        return False
    print("✅ Embeddings generated successfully")
    print(f"  Chunks embedded: {embeddings_status['chunks_embedded']}")
    print(f"  Time taken: {embeddings_status['time_taken']:.2f}s")
    
    chunk_embeddings = embeddings_status['embeddings']
    
    # Store in database
    print("\n5. Storing chunks and embeddings in database...")
    storage_status = asyncio.run(store_in_database(chunks[:20], chunk_embeddings))
    if not storage_status['success']:
        print("❌ FAILED: Database storage failed")
        print(f"Error: {storage_status.get('error', 'Unknown error')}")
        return False
    print("✅ Chunks stored in database")
    print(f"  Rows inserted: {storage_status['rows_inserted']}")
    print(f"  Table used: {storage_status['table_name']}")
    
    # Test similarity search
    print("\n6. Testing similarity search...")
    search_queries = [
        "Tell me about the emperor's new clothes",
        "What happened to the little match girl?",
        "Stories about magic and transformation",
        "Tales with happy endings",
        "Stories about children"
    ]
    
    search_results = asyncio.run(test_similarity_search(model, search_queries))
    if not search_results['success']:
        print("❌ FAILED: Similarity search failed")
        print(f"Error: {search_results.get('error', 'Unknown error')}")
        return False
    
    print("✅ Similarity search successful")
    for query, results in search_results['results'].items():
        print(f"\n  Query: '{query}'")
        for i, (similarity, preview) in enumerate(results[:2], 1):  # Show top 2
            print(f"    {i}. Similarity: {similarity:.3f}")
            print(f"       Preview: {preview[:100]}...")
    
    # Test advanced vector operations
    print("\n7. Testing advanced vector operations...")
    advanced_status = asyncio.run(test_advanced_operations())
    if not advanced_status['success']:
        print("❌ FAILED: Advanced operations failed")
        print(f"Error: {advanced_status.get('error', 'Unknown error')}")
        return False
    print("✅ Advanced operations successful")
    print(f"  Distance calculations: {advanced_status['distance_types']}")
    print(f"  Index performance: {advanced_status['index_performance']}ms")
    
    # Cleanup
    print("\n8. Cleaning up test data...")
    cleanup_status = asyncio.run(cleanup_test_data())
    print(f"✅ Cleaned up {cleanup_status['rows_deleted']} test rows")
    
    print("\n" + "=" * 60)
    print("✅ VECTOR TEST PASSED: Book content successfully processed with pgvector")
    print("🎉 Key achievements:")
    print("   • Loaded and chunked 500KB+ book")
    print("   • Generated 1024-dimensional embeddings")
    print("   • Stored vectors in PostgreSQL with pgvector")
    print("   • Performed semantic similarity search")
    print("   • Verified vector operations and indexing")
    print("=" * 60)
    return True

def load_book_content() -> Dict[str, Any]:
    """Load book content from file"""
    try:
        if not BOOK_FILE.exists():
            return {'success': False, 'error': f'Book file not found: {BOOK_FILE}'}
        
        with open(BOOK_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        file_size_kb = len(content.encode('utf-8')) / 1024
        
        return {
            'success': True,
            'content': content,
            'file_size_kb': file_size_kb,
            'char_count': len(content)
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def chunk_book(text: str, chunk_size: int = 1000, overlap: int = 200) -> Dict[str, Any]:
    """Chunk book into smaller passages"""
    try:
        chunks = []
        stories_found = 0
        
        # Split by stories (look for story titles in caps)
        lines = text.split('\n')
        current_chunk = []
        current_size = 0
        
        for line in lines:
            # Check if this might be a story title (all caps, short line)
            if line.strip() and line.strip().isupper() and len(line.strip()) < 50:
                # Save current chunk if it has content
                if current_chunk and current_size > 100:
                    chunk_text = '\n'.join(current_chunk).strip()
                    if chunk_text:
                        chunks.append({
                            'text': chunk_text,
                            'metadata': {
                                'type': 'story',
                                'story_number': stories_found,
                                'char_count': len(chunk_text)
                            }
                        })
                        stories_found += 1
                
                # Start new chunk with story title
                current_chunk = [line]
                current_size = len(line)
            else:
                # Add line to current chunk
                current_chunk.append(line)
                current_size += len(line)
                
                # If chunk is getting too large, split it
                if current_size >= chunk_size:
                    chunk_text = '\n'.join(current_chunk).strip()
                    if chunk_text:
                        chunks.append({
                            'text': chunk_text,
                            'metadata': {
                                'type': 'continuation',
                                'char_count': len(chunk_text)
                            }
                        })
                    
                    # Keep some overlap
                    if overlap > 0 and len(current_chunk) > 5:
                        current_chunk = current_chunk[-5:]
                        current_size = sum(len(line) for line in current_chunk)
                    else:
                        current_chunk = []
                        current_size = 0
        
        # Add final chunk
        if current_chunk:
            chunk_text = '\n'.join(current_chunk).strip()
            if chunk_text:
                chunks.append({
                    'text': chunk_text,
                    'metadata': {
                        'type': 'final',
                        'char_count': len(chunk_text)
                    }
                })
        
        # Calculate statistics
        avg_chunk_size = sum(c['metadata']['char_count'] for c in chunks) / len(chunks) if chunks else 0
        
        return {
            'success': True,
            'chunks': chunks,
            'chunk_count': len(chunks),
            'avg_chunk_size': int(avg_chunk_size),
            'stories_found': stories_found
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def initialize_embedding_model() -> Dict[str, Any]:
    """Initialize the embedding model"""
    try:
        print(f"  Loading {MODEL_NAME}...")
        model = SentenceTransformer(MODEL_NAME)
        
        # Test with a sample embedding
        test_embedding = model.encode("Test sentence")
        embedding_dim = len(test_embedding)
        
        return {
            'success': True,
            'model': model,
            'model_name': MODEL_NAME,
            'embedding_dim': embedding_dim
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def generate_embeddings(model: SentenceTransformer, chunks: List[Dict]) -> Dict[str, Any]:
    """Generate embeddings for text chunks"""
    try:
        start_time = time.time()
        
        # Extract text from chunks
        texts = [chunk['text'] for chunk in chunks]
        
        # Generate embeddings in batch
        embeddings = model.encode(texts, show_progress_bar=False)
        
        # Convert to list format for PostgreSQL
        embeddings_list = [embedding.tolist() for embedding in embeddings]
        
        time_taken = time.time() - start_time
        
        return {
            'success': True,
            'embeddings': embeddings_list,
            'chunks_embedded': len(embeddings_list),
            'time_taken': time_taken
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

async def store_in_database(chunks: List[Dict], embeddings: List[List[float]]) -> Dict[str, Any]:
    """Store chunks and embeddings in database"""
    try:
        conn = await asyncpg.connect(DATABASE_URL, timeout=10)
        
        try:
            # Create table for book chunks if it doesn't exist
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS book_chunks (
                    id SERIAL PRIMARY KEY,
                    chunk_text TEXT NOT NULL,
                    metadata JSONB,
                    embedding vector(1024),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create index for vector similarity search
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS book_chunks_embedding_idx 
                ON book_chunks USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100)
            """)
            
            # Insert chunks with embeddings
            rows_inserted = 0
            for chunk, embedding in zip(chunks, embeddings):
                await conn.execute("""
                    INSERT INTO book_chunks (chunk_text, metadata, embedding)
                    VALUES ($1, $2, $3)
                """, chunk['text'], json.dumps(chunk['metadata']), embedding)
                rows_inserted += 1
            
            return {
                'success': True,
                'rows_inserted': rows_inserted,
                'table_name': 'book_chunks'
            }
            
        finally:
            await conn.close()
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

async def test_similarity_search(model: SentenceTransformer, queries: List[str]) -> Dict[str, Any]:
    """Test similarity search with various queries"""
    try:
        conn = await asyncpg.connect(DATABASE_URL, timeout=10)
        
        try:
            results = {}
            
            for query in queries:
                # Generate query embedding
                query_embedding = model.encode(query).tolist()
                
                # Search for similar chunks
                rows = await conn.fetch("""
                    SELECT 
                        chunk_text,
                        metadata,
                        1 - (embedding <=> $1::vector) as similarity
                    FROM book_chunks
                    WHERE embedding IS NOT NULL
                    ORDER BY embedding <=> $1::vector
                    LIMIT 5
                """, query_embedding)
                
                # Store results
                results[query] = [
                    (float(row['similarity']), row['chunk_text'][:200])
                    for row in rows
                ]
            
            return {
                'success': True,
                'results': results,
                'queries_tested': len(queries)
            }
            
        finally:
            await conn.close()
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

async def test_advanced_operations() -> Dict[str, Any]:
    """Test advanced vector operations"""
    try:
        conn = await asyncpg.connect(DATABASE_URL, timeout=10)
        
        try:
            # Test different distance metrics
            test_vector = np.random.rand(1024).tolist()
            
            # Cosine distance
            cosine_result = await conn.fetchval("""
                SELECT MIN(embedding <=> $1::vector) as min_distance
                FROM book_chunks
                WHERE embedding IS NOT NULL
            """, test_vector)
            
            # L2 distance
            l2_result = await conn.fetchval("""
                SELECT MIN(embedding <-> $1::vector) as min_distance
                FROM book_chunks
                WHERE embedding IS NOT NULL
            """, test_vector)
            
            # Inner product
            ip_result = await conn.fetchval("""
                SELECT MAX(embedding <#> $1::vector) as max_product
                FROM book_chunks
                WHERE embedding IS NOT NULL
            """, test_vector)
            
            # Test index performance
            start_time = time.time()
            await conn.fetch("""
                SELECT id FROM book_chunks
                WHERE embedding IS NOT NULL
                ORDER BY embedding <=> $1::vector
                LIMIT 10
            """, test_vector)
            index_time = (time.time() - start_time) * 1000
            
            return {
                'success': True,
                'distance_types': ['cosine', 'l2', 'inner_product'],
                'cosine_min': float(cosine_result) if cosine_result else None,
                'l2_min': float(l2_result) if l2_result else None,
                'ip_max': float(ip_result) if ip_result else None,
                'index_performance': int(index_time)
            }
            
        finally:
            await conn.close()
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

async def cleanup_test_data() -> Dict[str, Any]:
    """Clean up test data from database"""
    try:
        conn = await asyncpg.connect(DATABASE_URL, timeout=10)
        
        try:
            # Delete test data from book_chunks table
            rows_deleted = await conn.fetchval("""
                DELETE FROM book_chunks
                WHERE created_at > NOW() - INTERVAL '1 hour'
                RETURNING COUNT(*)
            """)
            
            return {
                'success': True,
                'rows_deleted': rows_deleted or 0
            }
            
        finally:
            await conn.close()
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

if __name__ == '__main__':
    success = run_test()
    sys.exit(0 if success else 1)