"""Embedding service for semantic similarity calculations."""

from typing import Callable, List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """Service for generating and managing embeddings."""

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        custom_embed_fn: Optional[Callable[[str], List[float]]] = None,
    ):
        """Initialize the embedding service.

        Args:
            model_name: Name of the sentence-transformers model to use
            custom_embed_fn: Optional custom embedding function that takes text and returns embeddings
        """
        self._custom_embed_fn = custom_embed_fn
        self._model_name = model_name
        self._model: Optional[SentenceTransformer] = None

    def _ensure_model_loaded(self) -> None:
        """Lazy load the sentence-transformers model."""
        if self._model is None and self._custom_embed_fn is None:
            self._model = SentenceTransformer(self._model_name)

    def embed(self, text: str) -> np.ndarray:
        """Generate embeddings for the given text.

        Args:
            text: Text to embed

        Returns:
            Numpy array of embeddings
        """
        if self._custom_embed_fn:
            embeddings = self._custom_embed_fn(text)
            return np.array(embeddings)

        self._ensure_model_loaded()
        return self._model.encode(text, convert_to_numpy=True)

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            Numpy array of embeddings, shape (len(texts), embedding_dim)
        """
        if self._custom_embed_fn:
            embeddings = [self._custom_embed_fn(text) for text in texts]
            return np.array(embeddings)

        self._ensure_model_loaded()
        return self._model.encode(texts, convert_to_numpy=True)

    @staticmethod
    def cosine_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Cosine similarity score between -1 and 1
        """
        # Handle 1D and 2D arrays
        if embedding1.ndim == 1:
            embedding1 = embedding1.reshape(1, -1)
        if embedding2.ndim == 1:
            embedding2 = embedding2.reshape(1, -1)

        # Compute cosine similarity
        dot_product = np.dot(embedding1, embedding2.T)
        norm1 = np.linalg.norm(embedding1, axis=1, keepdims=True)
        norm2 = np.linalg.norm(embedding2, axis=1, keepdims=True)

        similarity = dot_product / (norm1 * norm2.T)
        return float(similarity[0, 0])

    @staticmethod
    def average_similarity(
        query_embedding: np.ndarray, candidate_embeddings: np.ndarray
    ) -> float:
        """Calculate average cosine similarity between query and multiple candidates.

        Args:
            query_embedding: Query embedding vector
            candidate_embeddings: Array of candidate embeddings, shape (n_candidates, embedding_dim)

        Returns:
            Average cosine similarity score
        """
        similarities = []
        for candidate_embedding in candidate_embeddings:
            sim = EmbeddingService.cosine_similarity(query_embedding, candidate_embedding)
            similarities.append(sim)

        return float(np.mean(similarities)) if similarities else 0.0
