"""Setup script for string_randomizer package."""

from setuptools import setup, find_packages

# Read the contents of README file
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="string-randomizer",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A simple Python package for randomizing letters in strings",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/adimus11/npi-dsw-example-eactions",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
)
