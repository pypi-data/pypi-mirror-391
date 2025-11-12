# pytest-semantic PRD

## Overview
This package is a pytest plugin which allows users to test LLM outputs against expected responses using semantic similarity matching rather than exact string comparison.

## Core Features

### 1. Semantic Matcher API
Users create matchers with valid example responses and optionally invalid examples:

```python
def test_greeting(semantic_matcher):
    response = my_llm("say hello")
    assert response == semantic_matcher(
        valid=["Hello!", "Hi there!", "Greetings!"],
        invalid=["Goodbye", "Random text"]  # optional
    )
```

Reusable matchers via fixtures:
```python
@pytest.fixture
def greeting_matcher(semantic_matcher):
    return semantic_matcher(
        valid=["Hello!", "Hi there!"],
        threshold=0.15  # optional override
    )

def test_greeting(greeting_matcher):
    assert my_llm("say hello") == greeting_matcher
```

### 2. Embeddings Model
- **Default**: Ship with `sentence-transformers` using `all-MiniLM-L6-v2` model (~80MB)
- **Offline-first**: Works locally without network after initial model download
- **Custom embeddings**: Users can provide custom embedding function: `def embed(text: str) -> List[float]`

### 3. Similarity Threshold Logic
Use a relative comparison approach:
- Calculate: `avg_similarity_to_valid - avg_similarity_to_invalid >= threshold`
- Also require: `avg_similarity_to_valid >= min_absolute_similarity` (default: 0.5)
- **Default threshold**: 0.15-0.20 (valid responses should be 15-20% more similar than invalid)

This prevents false positives when everything has low similarity.

### 4. Invalid Examples
- **Optional**: If not provided, generate random word combinations as default invalid examples
- **Purpose**: Provides baseline for "completely wrong" responses

### 5. Error Messages
When a semantic test fails, display:
```
AssertionError: Semantic similarity check failed
  Response: "What's up?"
  Similarity to valid examples: 0.45
  Similarity to invalid examples: 0.12
  Difference: 0.33 (threshold: 0.15)
  Closest valid example: "Hello!" (similarity: 0.48)
```

### 6. Configuration
Support pytest.ini and pyproject.toml configuration:
```toml
[tool.pytest.ini_options]
semantic_threshold = 0.15
semantic_min_similarity = 0.5
semantic_model = "all-MiniLM-L6-v2"
```

### 7. Scope
- **Text-to-text matching only**: Single response comparison (not multi-turn conversations)
- **General semantic comparison**: Works for any text comparison, not just LLM outputs

## Technical Details

### Package Name
- PyPI: `pytest-semantic`
- Import: `pytest_semantic`

### Dependencies
- `sentence-transformers`: Embedding model support
- `numpy`: Vector similarity calculations
- `pytest`: Testing framework (peer dependency)

### Publishing
Follow PACKAGE_SETUP.md for PyPI publishing process.

## Implementation Plan

1. Core semantic matcher with embedding model integration
2. pytest plugin fixtures and assertion integration
3. Configuration support via pytest.ini/pyproject.toml
4. Clear error formatting with similarity metrics
5. Random word generator for default invalid examples
6. Comprehensive test suite
7. Documentation with usage examples
8. Package setup for PyPI distribution
