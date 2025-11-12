"""Configuration management for pytest-semantic."""

from typing import Any, Optional
import pytest


class SemanticConfig:
    """Configuration holder for semantic matcher settings."""

    def __init__(
        self,
        threshold: float = 0.15,
        min_similarity: float = 0.5,
        model_name: str = "all-MiniLM-L6-v2",
    ):
        """Initialize configuration with default values.

        Args:
            threshold: Default threshold for similarity difference
            min_similarity: Default minimum absolute similarity
            model_name: Default sentence-transformers model name
        """
        self.threshold = threshold
        self.min_similarity = min_similarity
        self.model_name = model_name

    @classmethod
    def from_pytest_config(cls, config: pytest.Config) -> "SemanticConfig":
        """Load configuration from pytest config.

        Args:
            config: Pytest configuration object

        Returns:
            SemanticConfig instance with values from pytest config
        """
        threshold = cls._get_config_value(
            config, "semantic_threshold", default=0.15, value_type=float
        )
        min_similarity = cls._get_config_value(
            config, "semantic_min_similarity", default=0.5, value_type=float
        )
        model_name = cls._get_config_value(
            config, "semantic_model", default="all-MiniLM-L6-v2", value_type=str
        )

        return cls(
            threshold=threshold,
            min_similarity=min_similarity,
            model_name=model_name,
        )

    @staticmethod
    def _get_config_value(
        config: pytest.Config,
        key: str,
        default: Any,
        value_type: type,
    ) -> Any:
        """Get a configuration value from pytest config.

        Args:
            config: Pytest configuration object
            key: Configuration key to look up
            default: Default value if key is not found
            value_type: Expected type of the value

        Returns:
            Configuration value cast to the appropriate type
        """
        value = config.getini(key)

        # If value is not set or is empty, return default
        if not value:
            return default

        # Convert value to appropriate type
        try:
            if value_type == float:
                return float(value)
            elif value_type == int:
                return int(value)
            elif value_type == bool:
                return str(value).lower() in ("true", "1", "yes", "on")
            else:
                return str(value)
        except (ValueError, TypeError):
            return default

    def __repr__(self) -> str:
        """Return string representation of the configuration."""
        return (
            f"SemanticConfig(threshold={self.threshold}, "
            f"min_similarity={self.min_similarity}, "
            f"model_name={self.model_name!r})"
        )
