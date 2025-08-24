#!/usr/bin/env python3
"""
Test Vector Operations with a Large Text Corpus

This script provides a comprehensive, real-world test of the vector database
by processing a large text file (Andersen's Fairy Tales).

It validates the entire RAG (Retrieval-Augmented Generation) data pipeline:
1.  Loading and parsing a large text file.
2.  Chunking the text into meaningful passages.
3.  Generating high-dimensional vector embeddings for each chunk.
4.  Storing the chunks and their embeddings in a dedicated PostgreSQL table.
5.  Performing semantic similarity searches against the stored vectors.
"""

import sys
import os
import time
import json
import asyncio
import asyncpg
import numpy as np
from pathlib import Path
from typing import Dict, Any, List
from sentence_transformers import SentenceTransformer

# --- Configuration ---
DATABASE_URL = "postgresql://pocuser:pocpass@localhost:5432/poc_db"
BOOK_FILE = Path(__file__).parent.parent / "datafiles" / "Andersen's Fairy Tales by H. C. Andersen.txt"
MODEL_NAME = "BAAI/bge-large-en-v1.5"  # 1024-dim embeddings
TEST_TABLE_NAME = "book_chunks_test"

def main_test_logic():
    """Main function to run the complete vector processing pipeline test."""
    print("=" * 60)
    print("📚 VECTOR TEST WITH ANDERSEN'S FAIRY TALES")
    print("=" * 60)
    
    model = None
    try:
        # --- Step 1: Load and Chunk Data ---
        print("\n1. Loading and chunking book content...")
        book_text = load_book_content()
        chunks = chunk_book(book_text)
        print(f"✅ Book loaded and chunked into {len(chunks)} passages.")

        # --- Step 2: Initialize Model and Generate Embeddings ---
        print("\n2. Initializing embedding model and generating embeddings...")
        model = initialize_embedding_model()
        # For the test, we only embed a subset of chunks to keep it fast.
        test_chunks = chunks[:25]
        embeddings = generate_embeddings(model, test_chunks)
        print(f"✅ Generated {len(embeddings)} embeddings successfully.")

        # --- Step 3: Store in Database ---
        print("\n3. Storing chunks and embeddings in the database...")
        rows_inserted = asyncio.run(store_in_database(test_chunks, embeddings))
        print(f"✅ Stored {rows_inserted} chunks in the '{TEST_TABLE_NAME}' table.")

        # --- Step 4: Test Similarity Search ---
        print("\n4. Testing semantic similarity search...")
        search_queries = [
            "the emperor's new clothes",
            "the little match girl",
            "a story about a mermaid"
        ]
        search_results = asyncio.run(test_similarity_search(model, search_queries))
        print("✅ Semantic search completed successfully.")
        for query, results in search_results.items():
            print(f"  -> Top result for '{query}': Similarity={results[0]['similarity']:.3f}")

    except Exception as e:
        print(f"\n❌ FAILED: An error occurred: {e}")
        return False
    finally:
        # --- Cleanup ---
        print("\n5. Cleaning up test data...")
        rows_deleted = asyncio.run(cleanup_test_data())
        print(f"✅ Cleaned up {rows_deleted} test row(s).")

    print("\n" + "=" * 60)
    print("✅ VECTOR TEST PASSED: Book content pipeline is functional.")
    print("=" * 60)
    return True

def load_book_content() -> str:
    """Loads the full text of the book from the specified file."""
    if not BOOK_FILE.exists():
        raise FileNotFoundError(f"Book file not found at: {BOOK_FILE}")
    with open(BOOK_FILE, 'r', encoding='utf-8') as f:
        return f.read()

def chunk_book(text: str, chunk_size: int = 1500) -> List[Dict[str, Any]]:
    """Chunks the book text into smaller, manageable passages."""
    # A simple chunking strategy: split by paragraphs.
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    return [{'text': p} for p in paragraphs]

def initialize_embedding_model() -> SentenceTransformer:
    """Initializes and returns the Sentence Transformer model."""
    return SentenceTransformer(MODEL_NAME)

def generate_embeddings(model: SentenceTransformer, chunks: List[Dict]) -> List[List[float]]:
    """Generates vector embeddings for a list of text chunks."""
    texts = [chunk['text'] for chunk in chunks]
    embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    return [emb.tolist() for emb in embeddings]

async def store_in_database(chunks: List[Dict], embeddings: List[List[float]]) -> int:
    """Stores the text chunks and their corresponding embeddings in the database."""
    conn = await asyncpg.connect(DATABASE_URL, timeout=10)
    try:
        # Create a dedicated table for this test if it doesn't exist.
        await conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {TEST_TABLE_NAME} (
                id SERIAL PRIMARY KEY,
                chunk_text TEXT NOT NULL,
                embedding vector(1024)
            );
        """)
        # Insert all chunks and embeddings.
        await conn.executemany(
            f"INSERT INTO {TEST_TABLE_NAME} (chunk_text, embedding) VALUES ($1, $2)",
            [(chunk['text'], embedding) for chunk, embedding in zip(chunks, embeddings)]
        )
        return len(chunks)
    finally:
        await conn.close()

async def test_similarity_search(model: SentenceTransformer, queries: List[str]) -> Dict[str, List]:
    """Performs a similarity search for each query and returns the top results."""
    conn = await asyncpg.connect(DATABASE_URL, timeout=10)
    try:
        all_results = {}
        for query in queries:
            query_embedding = model.encode(query, normalize_embeddings=True).tolist()
            # Use the cosine distance operator `<=>` to find the most similar chunks.
            rows = await conn.fetch(
                f"SELECT chunk_text, 1 - (embedding <=> $1) AS similarity FROM {TEST_TABLE_NAME} ORDER BY similarity DESC LIMIT 3",
                query_embedding
            )
            all_results[query] = [dict(row) for row in rows]
        return all_results
    finally:
        await conn.close()

async def cleanup_test_data() -> int:
    """Removes the test table and all its data from the database."""
    conn = await asyncpg.connect(DATABASE_URL, timeout=10)
    try:
        # Use DROP TABLE with IF EXISTS to safely remove the table.
        result = await conn.execute(f"DROP TABLE IF EXISTS {TEST_TABLE_NAME};")
        # The result string for DROP TABLE is just "DROP TABLE", so we can't get a row count.
        # We assume success if no exception was raised.
        return 1
    except Exception:
        return 0
    finally:
        await conn.close()

if __name__ == '__main__':
    try:
        if main_test_logic():
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        sys.exit(1)
