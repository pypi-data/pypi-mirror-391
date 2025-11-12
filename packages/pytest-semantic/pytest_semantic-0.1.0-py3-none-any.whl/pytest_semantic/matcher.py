"""Core semantic matcher for comparing text responses."""

from typing import Callable, List, Optional
import numpy as np

from pytest_semantic.embeddings import EmbeddingService
from pytest_semantic.exceptions import SemanticAssertionError
from pytest_semantic.generator import RandomWordGenerator


class SemanticMatcher:
    """Matcher for comparing responses to valid/invalid examples using semantic similarity."""

    def __init__(
        self,
        valid: List[str],
        invalid: Optional[List[str]] = None,
        threshold: float = 0.15,
        min_similarity: float = 0.5,
        embedding_service: Optional[EmbeddingService] = None,
        model_name: str = "all-MiniLM-L6-v2",
        custom_embed_fn: Optional[Callable[[str], List[float]]] = None,
    ):
        """Initialize the semantic matcher.

        Args:
            valid: List of valid example responses
            invalid: Optional list of invalid example responses (random words if not provided)
            threshold: Minimum difference between valid and invalid similarity (default: 0.15)
            min_similarity: Minimum absolute similarity to valid examples (default: 0.5)
            embedding_service: Optional pre-configured embedding service
            model_name: Name of the sentence-transformers model (default: all-MiniLM-L6-v2)
            custom_embed_fn: Optional custom embedding function
        """
        if not valid:
            raise ValueError("At least one valid example must be provided")

        self.valid = valid
        self.threshold = threshold
        self.min_similarity = min_similarity

        # Generate default invalid examples if not provided
        if invalid is None:
            generator = RandomWordGenerator()
            self.invalid = generator.generate_invalid_examples(count=3)
        else:
            self.invalid = invalid

        # Set up embedding service
        if embedding_service:
            self.embedding_service = embedding_service
        else:
            self.embedding_service = EmbeddingService(
                model_name=model_name,
                custom_embed_fn=custom_embed_fn,
            )

        # Pre-compute embeddings for valid and invalid examples
        self._valid_embeddings = self.embedding_service.embed_batch(self.valid)
        self._invalid_embeddings = self.embedding_service.embed_batch(self.invalid)

    def check(self, response: str) -> bool:
        """Check if the response matches the valid examples.

        Args:
            response: The response to check

        Returns:
            True if the response passes the semantic similarity check

        Raises:
            SemanticAssertionError: If the response fails the check
        """
        # Compute embedding for the response
        response_embedding = self.embedding_service.embed(response)

        # Calculate similarities
        valid_similarity = self.embedding_service.average_similarity(
            response_embedding, self._valid_embeddings
        )
        invalid_similarity = self.embedding_service.average_similarity(
            response_embedding, self._invalid_embeddings
        )
        difference = valid_similarity - invalid_similarity

        # Find closest valid example
        closest_valid_idx = self._find_closest_example(
            response_embedding, self._valid_embeddings
        )
        closest_valid_example = self.valid[closest_valid_idx]
        closest_valid_similarity = self.embedding_service.cosine_similarity(
            response_embedding, self._valid_embeddings[closest_valid_idx]
        )

        # Check if response passes
        passes = (
            valid_similarity >= self.min_similarity
            and difference >= self.threshold
        )

        if not passes:
            raise SemanticAssertionError(
                response=response,
                valid_similarity=valid_similarity,
                invalid_similarity=invalid_similarity,
                difference=difference,
                threshold=self.threshold,
                min_similarity=self.min_similarity,
                closest_valid_example=closest_valid_example,
                closest_valid_similarity=closest_valid_similarity,
                valid_examples=self.valid,
            )

        return True

    def _find_closest_example(
        self, query_embedding: np.ndarray, candidate_embeddings: np.ndarray
    ) -> int:
        """Find the index of the closest candidate to the query.

        Args:
            query_embedding: Query embedding vector
            candidate_embeddings: Array of candidate embeddings

        Returns:
            Index of the closest candidate
        """
        similarities = []
        for candidate_embedding in candidate_embeddings:
            sim = self.embedding_service.cosine_similarity(
                query_embedding, candidate_embedding
            )
            similarities.append(sim)

        return int(np.argmax(similarities))

    def __eq__(self, other: str) -> bool:
        """Enable using the matcher with == operator in assertions.

        Args:
            other: The response string to check

        Returns:
            True if the response passes the semantic check
        """
        if not isinstance(other, str):
            return NotImplemented
        return self.check(other)

    def __repr__(self) -> str:
        """Return a string representation of the matcher."""
        return (
            f"SemanticMatcher(valid={len(self.valid)} examples, "
            f"invalid={len(self.invalid)} examples, "
            f"threshold={self.threshold}, "
            f"min_similarity={self.min_similarity})"
        )
