# pytest-semantic

A pytest plugin for testing LLM outputs using semantic similarity matching instead of exact string comparison.

## Installation

```bash
pip install pytest-semantic
```

Or with uv:

```bash
uv pip install pytest-semantic
```

## Quick Start

```python
def test_llm_greeting(semantic_matcher):
    """Test that LLM generates appropriate greetings."""
    llm_response = my_llm("Say hello")

    matcher = semantic_matcher(
        valid=["Hello!", "Hi there!", "Greetings!"],
    )

    assert llm_response == matcher
```

## Features

- **Semantic Matching**: Compare text responses based on meaning, not exact strings
- **Flexible Configuration**: Configure thresholds globally or per-test
- **Custom Embeddings**: Use your own embedding models or functions
- **Offline-First**: Works locally with included sentence-transformers model
- **Clear Error Messages**: Detailed failure messages with similarity scores
- **Easy Integration**: Simple pytest fixture-based API

## Usage

### Basic Usage

Use the `semantic_matcher` fixture to create matchers with valid examples:

```python
def test_llm_response(semantic_matcher):
    response = generate_llm_response("What is the capital of France?")

    matcher = semantic_matcher(
        valid=["Paris", "The capital is Paris", "Paris is the capital"],
    )

    assert response == matcher
```

### With Invalid Examples

Provide invalid examples to strengthen the matching:

```python
def test_sentiment_classification(semantic_matcher):
    result = classify_sentiment("I love this product!")

    matcher = semantic_matcher(
        valid=["positive", "good", "happy"],
        invalid=["negative", "bad", "sad", "neutral"],
    )

    assert result == matcher
```

If you don't provide invalid examples, random word combinations are automatically generated as a baseline.

### Custom Thresholds

Adjust matching sensitivity per test:

```python
def test_with_custom_threshold(semantic_matcher):
    matcher = semantic_matcher(
        valid=["Python programming"],
        threshold=0.2,        # Difference between valid/invalid similarity
        min_similarity=0.6,   # Minimum absolute similarity to valid examples
    )

    assert "Python coding" == matcher
```

### Reusable Matchers

Create reusable matchers with fixtures:

```python
import pytest

@pytest.fixture
def greeting_matcher(semantic_matcher):
    return semantic_matcher(
        valid=["Hello!", "Hi there!", "Hey!"],
    )

@pytest.fixture
def farewell_matcher(semantic_matcher):
    return semantic_matcher(
        valid=["Goodbye!", "See you!", "Bye!"],
    )

def test_conversation(greeting_matcher, farewell_matcher):
    assert llm.greet() == greeting_matcher
    assert llm.say_goodbye() == farewell_matcher
```

### Custom Embedding Functions

Use your own embedding function:

```python
def test_with_custom_embeddings(semantic_matcher):
    def my_embed_function(text: str) -> list:
        # Your custom embedding logic
        return openai.embeddings.create(input=text, model="text-embedding-3-small")

    matcher = semantic_matcher(
        valid=["Hello"],
        custom_embed_fn=my_embed_function,
    )

    assert "Hi" == matcher
```

## Configuration

Configure default values in `pytest.ini`:

```ini
[pytest]
semantic_threshold = 0.15
semantic_min_similarity = 0.5
semantic_model = all-MiniLM-L6-v2
```

Or in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
semantic_threshold = 0.15
semantic_min_similarity = 0.5
semantic_model = "all-MiniLM-L6-v2"
```

### Configuration Options

- **`semantic_threshold`** (default: `0.15`): Minimum difference between similarity to valid examples vs invalid examples
- **`semantic_min_similarity`** (default: `0.5`): Minimum absolute similarity score to valid examples (0-1 range)
- **`semantic_model`** (default: `"all-MiniLM-L6-v2"`): Sentence-transformers model name

## How It Works

1. **Embeddings**: Text is converted to vector embeddings using sentence-transformers
2. **Similarity Calculation**: Cosine similarity is computed between response and examples
3. **Dual Criteria**:
   - Response must be at least `min_similarity` similar to valid examples
   - Response must be at least `threshold` more similar to valid vs invalid examples

This dual-criteria approach prevents false positives while ensuring meaningful matches.

## Error Messages

When a test fails, you get detailed information:

```
AssertionError: Semantic similarity check failed
  Response: "Bonjour"
  Similarity to valid examples: 0.342
  Similarity to invalid examples: 0.156
  Difference: 0.186 (threshold: 0.150)
  Failure reason: Response similarity (0.342) is below minimum threshold (0.500)
  Closest valid example: 'Hello!' (similarity: 0.389)
  Valid examples:
    - 'Hello!'
    - 'Hi there!'
    - 'Greetings!'
```

## API Reference

### `semantic_matcher(valid, invalid=None, threshold=None, min_similarity=None, model_name=None, custom_embed_fn=None)`

Creates a semantic matcher for comparing text responses.

**Parameters:**
- `valid` (List[str]): List of valid example responses (required)
- `invalid` (List[str], optional): List of invalid examples (random words if not provided)
- `threshold` (float, optional): Override default threshold (0-1 range)
- `min_similarity` (float, optional): Override default minimum similarity (0-1 range)
- `model_name` (str, optional): Override default sentence-transformers model
- `custom_embed_fn` (Callable, optional): Custom embedding function `(str) -> List[float]`

**Returns:** `SemanticMatcher` instance that can be used with `==` operator

### `SemanticMatcher.check(response: str) -> bool`

Explicitly check if a response matches. Raises `SemanticAssertionError` on failure.

## Examples

### Testing LLM Text Generation

```python
def test_story_generation(semantic_matcher):
    """Test that LLM generates creative stories."""
    story = llm.generate_story(prompt="A robot learning to paint")

    matcher = semantic_matcher(
        valid=[
            "A robot discovers art and creativity",
            "An AI learns to express itself through painting",
            "A mechanical being explores artistic expression",
        ],
        threshold=0.1,  # Allow more variation for creative content
    )

    assert story == matcher
```

### Testing Classification

```python
def test_intent_classification(semantic_matcher):
    """Test intent classification accuracy."""
    intent = classify_intent("I want to cancel my subscription")

    matcher = semantic_matcher(
        valid=["cancel", "cancellation", "unsubscribe"],
        invalid=["help", "question", "purchase", "upgrade"],
    )

    assert intent == matcher
```

### Testing Summarization

```python
def test_summarization(semantic_matcher):
    """Test that summaries capture key points."""
    long_text = "..." # Long article
    summary = llm.summarize(long_text)

    matcher = semantic_matcher(
        valid=[
            "Article discusses climate change impacts",
            "The text is about environmental challenges",
        ],
        min_similarity=0.4,  # Lower threshold for summaries
    )

    assert summary == matcher
```

## Development

### Setup

```bash
git clone https://github.com/tombedor/pytest-semantic.git
cd pytest-semantic
uv sync
```

### Running Tests

```bash
uv run pytest tests/
```

### Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Credits

Built with:
- [sentence-transformers](https://www.sbert.net/) for embeddings
- [pytest](https://pytest.org/) testing framework
