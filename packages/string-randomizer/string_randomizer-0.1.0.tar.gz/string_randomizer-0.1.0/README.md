# String Randomizer

A simple Python package for randomizing letters in strings.

## Installation

You can install the package using pip:

```bash
pip install -e .
```

For development with testing tools:

```bash
pip install -e ".[dev]"
```

## Usage

The package provides two main functions:

### randomize_string

Randomizes all characters in a string:

```python
from string_randomizer import randomize_string

# Basic usage
result = randomize_string("hello world")
print(result)  # Example output: "owllorhd le"

# With seed for reproducible results
result = randomize_string("hello", seed=42)
print(result)  # Always produces the same output with seed=42
```

### randomize_words

Randomizes letters within each word while preserving word boundaries:

```python
from string_randomizer import randomize_words

# Basic usage
result = randomize_words("hello world")
print(result)  # Example output: "olehl dlrow"

# With seed for reproducible results
result = randomize_words("hello world", seed=42)
print(result)  # Always produces the same output with seed=42
```

## Running Tests

To run the tests, first install the package with dev dependencies:

```bash
pip install -e ".[dev]"
pytest
```

To run tests with coverage:

```bash
pytest --cov=string_randomizer --cov-report=html
```

## Building and Publishing

To build the package:

```bash
pip install build
python -m build
```

This will create distribution files in the `dist/` directory.

To publish to PyPI (requires PyPI account and credentials):

```bash
pip install twine
twine upload dist/*
```

## Project Structure

```
npi-dsw-example-eactions/
├── string_randomizer/       # Main package directory
│   ├── __init__.py         # Package initialization
│   └── randomizer.py       # Core functionality
├── tests/                  # Test directory
│   ├── __init__.py
│   └── test_randomizer.py  # Test cases
├── pyproject.toml          # Modern Python project configuration
├── setup.py                # Setup script for backward compatibility
├── MANIFEST.in             # Package manifest for distribution
├── README.md               # This file
└── LICENSE                 # License file
```

## License

See LICENSE file for details.
