"""
Tests for string_randomizer package.
"""

import random
import pytest
from string_randomizer import randomize_string, randomize_words


class TestRandomizeString:
    """Tests for randomize_string function."""

    def test_randomize_string_basic(self):
        """Test basic string randomization."""
        text = "hello"
        result = randomize_string(text)
        # Check that result has same length
        assert len(result) == len(text)
        # Check that result has same characters (just reordered)
        assert sorted(result) == sorted(text)

    def test_randomize_string_with_seed(self):
        """Test that seed produces reproducible results."""
        text = "hello"
        result1 = randomize_string(text, seed=42)
        result2 = randomize_string(text, seed=42)
        assert result1 == result2

    def test_randomize_string_empty(self):
        """Test randomizing empty string."""
        assert randomize_string("") == ""

    def test_randomize_string_single_char(self):
        """Test randomizing single character."""
        assert randomize_string("a") == "a"

    def test_randomize_string_with_spaces(self):
        """Test that spaces are also randomized."""
        text = "a b c"
        result = randomize_string(text)
        assert len(result) == len(text)
        assert sorted(result) == sorted(text)

    def test_randomize_string_with_numbers(self):
        """Test randomizing string with numbers."""
        text = "abc123"
        result = randomize_string(text)
        assert len(result) == len(text)
        assert sorted(result) == sorted(text)

    def test_randomize_string_with_special_chars(self):
        """Test randomizing string with special characters."""
        text = "hello!@#"
        result = randomize_string(text)
        assert len(result) == len(text)
        assert sorted(result) == sorted(text)

    def test_randomize_string_unicode(self):
        """Test randomizing Unicode characters."""
        text = "héllo wörld"
        result = randomize_string(text)
        assert len(result) == len(text)
        assert sorted(result) == sorted(text)

    def test_randomize_string_is_random(self):
        """Test that randomization actually changes the string (probabilistically)."""
        text = "abcdefghijklmnopqrstuvwxyz"
        # With high probability, at least one shuffle should differ
        results = [randomize_string(text) for _ in range(10)]
        # At least one result should be different from original
        assert any(r != text for r in results)


class TestRandomizeWords:
    """Tests for randomize_words function."""

    def test_randomize_words_basic(self):
        """Test basic word randomization."""
        text = "hello world"
        result = randomize_words(text)
        words = result.split()
        # Check we still have 2 words
        assert len(words) == 2
        # Check each word has same characters as original
        assert sorted(words[0]) == sorted("hello")
        assert sorted(words[1]) == sorted("world")

    def test_randomize_words_with_seed(self):
        """Test that seed produces reproducible results."""
        text = "hello world"
        result1 = randomize_words(text, seed=42)
        result2 = randomize_words(text, seed=42)
        assert result1 == result2

    def test_randomize_words_empty(self):
        """Test randomizing empty string."""
        assert randomize_words("") == ""

    def test_randomize_words_single_word(self):
        """Test randomizing single word."""
        text = "hello"
        result = randomize_words(text)
        assert sorted(result) == sorted(text)

    def test_randomize_words_single_char_words(self):
        """Test randomizing single character words."""
        text = "a b c"
        result = randomize_words(text)
        # Single char words should remain the same
        assert result == "a b c"

    def test_randomize_words_multiple_spaces(self):
        """Test handling of multiple spaces (splits on any whitespace)."""
        text = "hello  world"
        result = randomize_words(text)
        # split() handles multiple spaces
        words = result.split()
        assert len(words) == 2

    def test_randomize_words_preserves_word_count(self):
        """Test that word count is preserved."""
        text = "the quick brown fox jumps"
        result = randomize_words(text)
        assert len(result.split()) == len(text.split())

    def test_randomize_words_each_word_randomized(self):
        """Test that each word is independently randomized."""
        text = "abc def ghi"
        result = randomize_words(text)
        result_words = result.split()
        original_words = text.split()

        for i, (orig, rand) in enumerate(zip(original_words, result_words)):
            assert sorted(orig) == sorted(rand), f"Word {i} doesn't have same chars"
