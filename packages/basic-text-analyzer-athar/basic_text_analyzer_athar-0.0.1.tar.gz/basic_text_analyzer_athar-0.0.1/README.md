Basic Text Analyzer
A simple Python library for basic Natural Language Processing (NLP) tasks. This is a starter-kit to demonstrate how to publish a package to PyPI.

Installation
You can install this package from PyPI (once it's published):

pip install basic_text_analyzer_athar

Usage
Here's how to use the functions in your Python code:

import basic_text_analyzer as bta

text = "This is a simple example sentence to demonstrate the library."

Count words
count = bta.word_count(text) print(f"Word Count: {count}")

Output: Word Count: 11
Count characters
char_count = bta.char_count(text) print(f"Character Count: {char_count}")

Output: Character Count: 60
Remove stop words
cleaned_text = bta.remove_stopwords(text) print(f"Cleaned Text: {cleaned_text}")

Output: Cleaned Text: simple example sentence demonstrate library.