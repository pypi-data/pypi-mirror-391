"""
Basic Text Analyzer
A simple NLP package.
"""

# This file makes 'src/basic_text_analyzer' a Python package.
# It also controls what functions are exposed to the user.

__version__ = "0.0.1"

# Import functions from our modules to make them available
# at the top level (e.g., `import basic_text_analyzer as bta; bta.word_count()`)
from .analysis import word_count, char_count, remove_stopwords
from .stopwords import BASIC_STOPWORDS

# This controls what `from basic_text_analyzer import *` imports
__all__ = [
    'word_count',
    'char_count',
    'remove_stopwords',
    'BASIC_STOPWORDS'
]