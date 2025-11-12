"""Custom exceptions for pytest-semantic."""

from typing import List, Optional


class SemanticAssertionError(AssertionError):
    """Custom assertion error with detailed semantic similarity information."""

    def __init__(
        self,
        response: str,
        valid_similarity: float,
        invalid_similarity: float,
        difference: float,
        threshold: float,
        min_similarity: float,
        closest_valid_example: Optional[str] = None,
        closest_valid_similarity: Optional[float] = None,
        valid_examples: Optional[List[str]] = None,
    ):
        """Initialize the semantic assertion error.

        Args:
            response: The actual response that failed the check
            valid_similarity: Average similarity to valid examples
            invalid_similarity: Average similarity to invalid examples
            difference: Difference between valid and invalid similarities
            threshold: Required threshold for the difference
            min_similarity: Minimum absolute similarity required
            closest_valid_example: The closest valid example
            closest_valid_similarity: Similarity to the closest valid example
            valid_examples: List of valid examples for reference
        """
        self.response = response
        self.valid_similarity = valid_similarity
        self.invalid_similarity = invalid_similarity
        self.difference = difference
        self.threshold = threshold
        self.min_similarity = min_similarity
        self.closest_valid_example = closest_valid_example
        self.closest_valid_similarity = closest_valid_similarity
        self.valid_examples = valid_examples

        # Build detailed error message
        message_parts = [
            "Semantic similarity check failed",
            f"  Response: {repr(response)}",
            f"  Similarity to valid examples: {valid_similarity:.3f}",
            f"  Similarity to invalid examples: {invalid_similarity:.3f}",
            f"  Difference: {difference:.3f} (threshold: {threshold:.3f})",
        ]

        # Add failure reason
        if valid_similarity < min_similarity:
            message_parts.append(
                f"  Failure reason: Response similarity ({valid_similarity:.3f}) "
                f"is below minimum threshold ({min_similarity:.3f})"
            )
        else:
            message_parts.append(
                f"  Failure reason: Difference ({difference:.3f}) "
                f"is below required threshold ({threshold:.3f})"
            )

        # Add closest match info
        if closest_valid_example and closest_valid_similarity is not None:
            message_parts.append(
                f"  Closest valid example: {repr(closest_valid_example)} "
                f"(similarity: {closest_valid_similarity:.3f})"
            )

        # Add valid examples for context
        if valid_examples:
            message_parts.append("  Valid examples:")
            for example in valid_examples[:3]:  # Show max 3 examples
                message_parts.append(f"    - {repr(example)}")
            if len(valid_examples) > 3:
                message_parts.append(f"    ... and {len(valid_examples) - 3} more")

        super().__init__("\n".join(message_parts))
