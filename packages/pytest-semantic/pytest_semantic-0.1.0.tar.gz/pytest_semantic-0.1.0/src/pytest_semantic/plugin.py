"""Pytest plugin for semantic matching."""

from typing import Callable, List, Optional
import pytest

from pytest_semantic.config import SemanticConfig
from pytest_semantic.embeddings import EmbeddingService
from pytest_semantic.matcher import SemanticMatcher


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add custom ini options for semantic matching.

    Args:
        parser: Pytest config parser
    """
    parser.addini(
        "semantic_threshold",
        help="Default threshold for semantic similarity difference (default: 0.15)",
        type="string",
        default="0.15",
    )
    parser.addini(
        "semantic_min_similarity",
        help="Default minimum absolute similarity (default: 0.5)",
        type="string",
        default="0.5",
    )
    parser.addini(
        "semantic_model",
        help="Default sentence-transformers model name (default: all-MiniLM-L6-v2)",
        type="string",
        default="all-MiniLM-L6-v2",
    )


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with semantic matcher settings.

    Args:
        config: Pytest configuration object
    """
    # Register custom markers
    config.addinivalue_line(
        "markers",
        "semantic: mark test to use semantic matching",
    )

    # Load and store semantic configuration
    semantic_config = SemanticConfig.from_pytest_config(config)
    config._semantic_config = semantic_config  # type: ignore


@pytest.fixture(scope="session")
def semantic_config(request: pytest.FixtureRequest) -> SemanticConfig:
    """Provide semantic configuration to tests.

    Args:
        request: Pytest fixture request

    Returns:
        SemanticConfig instance
    """
    return request.config._semantic_config  # type: ignore


@pytest.fixture(scope="session")
def semantic_embedding_service(semantic_config: SemanticConfig) -> EmbeddingService:
    """Provide a shared embedding service for the test session.

    Args:
        semantic_config: Semantic configuration

    Returns:
        EmbeddingService instance
    """
    return EmbeddingService(model_name=semantic_config.model_name)


@pytest.fixture
def semantic_matcher(
    semantic_config: SemanticConfig,
    semantic_embedding_service: EmbeddingService,
) -> Callable[..., SemanticMatcher]:
    """Provide a semantic matcher factory.

    Usage:
        def test_example(semantic_matcher):
            matcher = semantic_matcher(
                valid=["Hello!", "Hi!"],
                invalid=["Goodbye"],  # optional
                threshold=0.2,  # optional, overrides config
            )
            assert "Hey there!" == matcher

    Args:
        semantic_config: Semantic configuration
        semantic_embedding_service: Shared embedding service

    Returns:
        Function that creates SemanticMatcher instances
    """
    def create_matcher(
        valid: List[str],
        invalid: Optional[List[str]] = None,
        threshold: Optional[float] = None,
        min_similarity: Optional[float] = None,
        model_name: Optional[str] = None,
        custom_embed_fn: Optional[Callable[[str], List[float]]] = None,
    ) -> SemanticMatcher:
        """Create a semantic matcher.

        Args:
            valid: List of valid example responses
            invalid: Optional list of invalid examples
            threshold: Optional threshold override
            min_similarity: Optional minimum similarity override
            model_name: Optional model name override
            custom_embed_fn: Optional custom embedding function

        Returns:
            SemanticMatcher instance
        """
        # Use config defaults if not overridden
        threshold = threshold if threshold is not None else semantic_config.threshold
        min_similarity = (
            min_similarity if min_similarity is not None else semantic_config.min_similarity
        )

        # Use shared embedding service unless custom settings are provided
        embedding_service = None
        if model_name is None and custom_embed_fn is None:
            embedding_service = semantic_embedding_service

        return SemanticMatcher(
            valid=valid,
            invalid=invalid,
            threshold=threshold,
            min_similarity=min_similarity,
            embedding_service=embedding_service,
            model_name=model_name or semantic_config.model_name,
            custom_embed_fn=custom_embed_fn,
        )

    return create_matcher
