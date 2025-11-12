"""Random word generator for creating default invalid examples."""

import random
from typing import List


# A curated list of common English words for generating random invalid examples
WORD_BANK = [
    "apple", "banana", "car", "dog", "elephant", "flower", "guitar", "house",
    "island", "jacket", "kite", "lamp", "mountain", "notebook", "ocean", "piano",
    "queen", "river", "sun", "tree", "umbrella", "violin", "window", "xylophone",
    "yellow", "zebra", "book", "chair", "door", "engine", "fork", "garden",
    "hammer", "ice", "jungle", "key", "lemon", "mirror", "nest", "orange",
    "pencil", "quilt", "rock", "shoe", "table", "unicorn", "vase", "wheel",
    "yard", "zoo", "bridge", "castle", "dragon", "eagle", "forest", "globe",
    "hill", "ink", "jewel", "kangaroo", "leaf", "moon", "night", "owl",
    "park", "question", "rainbow", "star", "tower", "universe", "valley", "water",
    "zipper", "boat", "cloud", "desert", "earth", "fire", "grass",
    "horizon", "iris", "joy", "kettle", "light", "mask", "net", "orbit",
    "pearl", "quiet", "rain", "snow", "time", "unity", "voice", "wind",
    "zone", "atom", "bell", "coin", "dream", "echo", "flame",
    "gift", "heart", "idea", "joke", "king", "luck", "magic", "north", "yarn",
]


class RandomWordGenerator:
    """Generator for creating random word combinations."""

    def __init__(self, seed: int = None):
        """Initialize the generator.

        Args:
            seed: Optional random seed for reproducibility
        """
        self._rng = random.Random(seed)

    def generate_invalid_examples(self, count: int = 3, words_per_example: int = 5) -> List[str]:
        """Generate random word combinations as invalid examples.

        Args:
            count: Number of invalid examples to generate
            words_per_example: Number of random words per example

        Returns:
            List of random word combinations
        """
        examples = []
        for _ in range(count):
            words = self._rng.sample(WORD_BANK, min(words_per_example, len(WORD_BANK)))
            examples.append(" ".join(words))
        return examples
