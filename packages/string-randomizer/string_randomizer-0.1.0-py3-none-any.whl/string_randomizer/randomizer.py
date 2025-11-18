"""
Core functionality for randomizing strings.
"""

import random
from typing import Optional


def randomize_string(text: str, seed: Optional[int] = None) -> str:
    """
    Randomize the order of letters in a string.

    Args:
        text: The input string to randomize
        seed: Optional seed for reproducible randomization

    Returns:
        A string with letters in randomized order

    Examples:
        >>> random.seed(42)
        >>> randomize_string("hello")
        'olleh'
        >>> randomize_string("")
        ''
    """
    if not text:
        return text

    if seed is not None:
        random.seed(seed)

    chars = list(text)
    random.shuffle(chars)
    return "".join(chars)


def randomize_words(text: str, seed: Optional[int] = None) -> str:
    """
    Randomize letters within each word while preserving word boundaries.

    Args:
        text: The input string with words to randomize
        seed: Optional seed for reproducible randomization

    Returns:
        A string with letters randomized within each word

    Examples:
        >>> random.seed(42)
        >>> randomize_words("hello world")
        'olleh dlrow'
        >>> randomize_words("a b c")
        'a b c'
    """
    if not text:
        return text

    if seed is not None:
        random.seed(seed)

    words = text.split()
    randomized_words = []
    for word in words:
        chars = list(word)
        random.shuffle(chars)
        randomized_words.append("".join(chars))
    return " ".join(randomized_words)
