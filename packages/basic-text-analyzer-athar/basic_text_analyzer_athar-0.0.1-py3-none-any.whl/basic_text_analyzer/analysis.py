"""
Core text analysis functions for the library.
"""

import string
from .stopwords import BASIC_STOPWORDS

def word_count(text: str) -> int:
    """
    Counts the number of words in a text string.
    Words are separated by whitespace.
    """
    if not isinstance(text, str):
        return 0
    return len(text.split())

def char_count(text: str) -> int:
    """
    Counts the total number of characters in a text string.
    """
    if not isinstance(text, str):
        return 0
    return len(text)

def remove_stopwords(text: str, stopwords: set[str] = BASIC_STOPWORDS) -> str:
    """
    Removes punctuation and common stop words from a text string.
    
    1. Converts text to lowercase.
    2. Removes all punctuation.
    3. Splits text into words.
    4. Removes words that are in the stopword set.
    5. Joins the remaining words back into a string.
    """
    if not isinstance(text, str):
        return ""

    # 1. Convert to lowercase
    text_low = text.lower()
    
    # 2. Remove punctuation
    # string.punctuation is a string of all punctuation: '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
    # We create a translation table that maps each punctuation char to None
    translator = str.maketrans('', '', string.punctuation)
    text_no_punct = text_low.translate(translator)
    
    # 3. Split into words
    words = text_no_punct.split()
    
    # 4. Remove stopwords
    filtered_words = [word for word in words if word not in stopwords]
    
    # 5. Join back into a string
    return " ".join(filtered_words)