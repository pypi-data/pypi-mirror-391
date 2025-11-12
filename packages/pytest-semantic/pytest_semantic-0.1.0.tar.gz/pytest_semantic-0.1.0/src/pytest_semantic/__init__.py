"""pytest-semantic: Semantic similarity matching for pytest."""

from pytest_semantic.matcher import SemanticMatcher
from pytest_semantic.embeddings import EmbeddingService
from pytest_semantic.exceptions import SemanticAssertionError
from pytest_semantic.config import SemanticConfig

__version__ = "0.1.0"

__all__ = [
    "SemanticMatcher",
    "EmbeddingService",
    "SemanticAssertionError",
    "SemanticConfig",
]
