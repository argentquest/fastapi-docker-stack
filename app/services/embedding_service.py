# V2 BGE-Large Embedding Service
import logging
from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import asyncio
import time

logger = logging.getLogger(__name__)

class EmbeddingService:
    """BGE-large embedding service for V2 POC"""
    
    def __init__(self):
        self.model = None
        self._model_name = "BAAI/bge-large-en-v1.5"
        self._dimensions = 1024
    
    async def _load_model(self):
        """Load the embedding model (lazy loading)"""
        if self.model is None:
            logger.info(f"Loading embedding model: {self._model_name}")
            start_time = time.time()
            
            # Load in thread to avoid blocking async loop
            loop = asyncio.get_event_loop()
            self.model = await loop.run_in_executor(
                None, 
                lambda: SentenceTransformer(self._model_name)
            )
            
            load_time = time.time() - start_time
            logger.info(f"Model loaded successfully in {load_time:.2f}s")
    
    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of float values representing the embedding (1024 dimensions)
        """
        await self._load_model()
        
        try:
            start_time = time.time()
            
            # Add retrieval instruction for better quality (BGE-specific)
            enhanced_text = f"Represent this text for retrieval: {text}"
            
            # Generate embedding in thread to avoid blocking
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None,
                lambda: self.model.encode(enhanced_text, normalize_embeddings=True)
            )
            
            embed_time = time.time() - start_time
            logger.debug(f"Generated embedding in {embed_time:.3f}s for {len(text)} chars")
            
            # Convert to list of floats
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise RuntimeError(f"Embedding generation failed: {e}")
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (more efficient).
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings (each with 1024 dimensions)
        """
        await self._load_model()
        
        try:
            start_time = time.time()
            
            # Add retrieval instruction to all texts
            enhanced_texts = [f"Represent this text for retrieval: {text}" for text in texts]
            
            # Generate embeddings in batch
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None,
                lambda: self.model.encode(enhanced_texts, normalize_embeddings=True)
            )
            
            embed_time = time.time() - start_time
            logger.info(f"Generated {len(texts)} embeddings in {embed_time:.3f}s")
            
            # Convert to list of lists
            return [embedding.tolist() for embedding in embeddings]
            
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise RuntimeError(f"Batch embedding generation failed: {e}")
    
    async def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Compute cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score (0.0 to 1.0, higher = more similar)
        """
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Compute cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
                
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error computing similarity: {e}")
            return 0.0
    
    @property
    def dimensions(self) -> int:
        """Get the embedding dimensions"""
        return self._dimensions
    
    @property
    def model_name(self) -> str:
        """Get the model name"""
        return self._model_name
    
    async def health_check(self) -> dict:
        """Check if embedding service is working"""
        try:
            # Test embedding generation
            test_embedding = await self.embed_text("This is a test.")
            
            return {
                "status": "healthy",
                "model": self._model_name,
                "dimensions": len(test_embedding),
                "test_embedding_length": len(test_embedding)
            }
            
        except Exception as e:
            return {
                "status": "error", 
                "error": str(e)
            }

# Global service instance
embedding_service = EmbeddingService()