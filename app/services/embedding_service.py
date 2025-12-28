# V2 BGE-Large Embedding Service (Mocked)
"""
This service is a MOCK implementation of the EmbeddingService.
The original dependency 'sentence-transformers' (and thus torch/nvidia libs)
has been removed to optimize for non-GPU environments.

It mocks the following:
- Loading the model (no-op).
- Generating embeddings (returns zero vectors).
"""

import logging
from typing import List, Optional
import asyncio

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    A MOCK service class for creating text embeddings.
    """

    def __init__(self):
        """Initializes the Mock EmbeddingService."""
        self.model = None
        self._model_name: str = "mock-bge-large-en-v1.5"
        self._dimensions: int = 1024

    async def _load_model(self):
        """
        Mock loading.
        """
        pass

    async def embed_text(self, text: str) -> List[float]:
        """
        Returns a mock vector embedding (zeros).

        Args:
            text: The input text to embed.

        Returns:
            A list of 1024 floats (all zeros).
        """
        text_length = len(text)
        logger.debug(f"Generating MOCK embedding for text with {text_length} characters...")
        
        # Simulate a slight delay to mimic async work if needed, or just return immediately.
        # await asyncio.sleep(0.01)

        embedding_list = [0.0] * self._dimensions
        logger.debug(f"Generated MOCK embedding of size {len(embedding_list)}")

        return embedding_list

    async def health_check(self) -> dict:
        """
        Performs a health check on the embedding service.

        Returns:
            A dictionary containing the health status.
        """
        return {
            "status": "mocked",
            "model": self._model_name,
            "dimensions": self._dimensions,
            "note": "Real embedding generation is disabled."
        }

# Create a single, global instance of the EmbeddingService.
embedding_service = EmbeddingService()
