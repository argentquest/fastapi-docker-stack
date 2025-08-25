# V2 BGE-Large Embedding Service
"""
This service handles the generation of vector embeddings using a Sentence Transformer model.

It is responsible for:
- Lazily loading the BAAI/bge-large-en-v1.5 model to avoid slow startup times.
- Generating embeddings for single texts or batches of texts.
- Running the model inference in a separate thread to avoid blocking the main asyncio event loop.
- Prepending a model-specific instruction to the text to improve embedding quality.
"""

import logging
from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import asyncio
import time

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    A service class for creating text embeddings using a Sentence Transformer model.

    Attributes:
        model: The loaded SentenceTransformer model instance.
        _model_name: The Hugging Face model identifier.
        _dimensions: The dimensionality of the embeddings produced by the model.
    """

    def __init__(self):
        """Initializes the EmbeddingService. The model is not loaded at this point."""
        self.model: Optional[SentenceTransformer] = None
        self._model_name: str = "BAAI/bge-large-en-v1.5"
        self._dimensions: int = 1024

    async def _load_model(self):
        """
        Loads the Sentence Transformer model on demand (lazy loading).

        This method is called automatically before any embedding operation.
        It runs the model loading in a separate thread to prevent blocking the
        asyncio event loop, which is crucial for a responsive application.
        """
        if self.model is None:
            logger.info(f"Lazily loading embedding model: {self._model_name} ({self._dimensions} dimensions)...")
            start_time = time.time()

            # The model loading is CPU/IO-bound, so we run it in a thread pool executor
            # to avoid blocking the main application event loop.
            loop = asyncio.get_event_loop()
            logger.debug("Loading model in background thread...")
            # Set local_files_only=True to skip checking for updates
            self.model = await loop.run_in_executor(
                None,  # Use the default executor
                lambda: SentenceTransformer(
                    self._model_name,
                    cache_folder=None,  # Use default cache
                    local_files_only=True  # Don't check for updates online
                )
            )

            load_time = time.time() - start_time
            logger.info(f"Embedding model '{self._model_name}' loaded successfully in {load_time:.2f}s")
        else:
            logger.debug("Model already loaded, skipping initialization")

    async def embed_text(self, text: str) -> List[float]:
        """
        Generates a vector embedding for a single piece of text.

        Args:
            text: The input text to embed.

        Returns:
            A list of floats representing the vector embedding (1024 dimensions).

        Raises:
            RuntimeError: If the embedding generation fails.
        """
        text_length = len(text)
        logger.debug(f"Starting embedding generation for text with {text_length} characters...")

        await self._load_model()  # Ensure the model is loaded before proceeding.

        try:
            start_time = time.time()

            # For BGE models, prepending an instruction can improve embedding quality for retrieval tasks.
            enhanced_text = f"Represent this document for retrieval: {text}"
            logger.debug(f"Enhanced text for BGE model (total length: {len(enhanced_text)} chars)")

            # Run the encoding process in a separate thread.
            logger.debug("Running model.encode in background thread...")
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None,
                lambda: self.model.encode(enhanced_text, normalize_embeddings=True)
            )

            embed_time = time.time() - start_time
            embedding_list = embedding.tolist()
            logger.info(f"Generated embedding with {len(embedding_list)} dimensions for {text_length} chars in {embed_time:.3f}s")
            logger.debug(f"Embedding stats: min={min(embedding_list):.4f}, max={max(embedding_list):.4f}, mean={sum(embedding_list)/len(embedding_list):.4f}")

            return embedding_list
        except Exception as e:
            logger.error(f"Error generating embedding for text of length {text_length}: {e}", exc_info=True)
            raise RuntimeError(f"Embedding generation failed: {e}")

    async def health_check(self) -> dict:
        """
        Performs a health check on the embedding service.

        This check verifies that the model can be loaded and can generate an embedding.

        Returns:
            A dictionary containing the health status and model information.
        """
        logger.debug("Starting embedding service health check...")
        try:
            # Test embedding generation for a simple text.
            test_text = "health check"
            logger.debug(f"Testing embedding generation with text: '{test_text}'")

            test_embedding = await self.embed_text(test_text)

            if not test_embedding or len(test_embedding) != self._dimensions:
                error_msg = f"Generated embedding has incorrect dimensions: expected {self._dimensions}, got {len(test_embedding) if test_embedding else 0}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            logger.info(f"Embedding service health check completed successfully (model: {self._model_name}, dimensions: {self._dimensions})")
            return {
                "status": "healthy",
                "model": self._model_name,
                "dimensions": self._dimensions
            }
        except Exception as e:
            logger.error(f"Embedding service health check failed: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}

# Create a single, global instance of the EmbeddingService.
# This instance will be imported and used by other parts of the application.


embedding_service = EmbeddingService()
