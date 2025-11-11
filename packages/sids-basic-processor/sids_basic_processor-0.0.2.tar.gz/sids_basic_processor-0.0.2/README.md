# sids-basic-processor

A simple, basic utility package for common natural language text preprocessing tasks. It is designed to quickly clean raw text for analysis.

## Features

The `TextProcessor` class performs the following sequential steps:

1.  **Lowercasing**: Converts all text to lowercase.
2.  **Punctuation Removal**: Removes all common punctuation marks.
3.  **Tokenization**: Splits the cleaned text into a list of words.
4.  **Stop Word Removal**: Filters out a predefined set of common English stop words (like "the", "is", "a", etc.).

## Installation

You can install the package using Python's package manager, `pip`:

```bash
pip install sids-basic-processor