"""
Text cleaning and preprocessing module.
Handles lowercase conversion, punctuation removal, stop word removal, etc.
"""

import re
import string
from typing import List


class TextCleaner:
    """Clean and preprocess text data."""
    
    # Common stop words
    STOP_WORDS = {
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
        'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'or', 'that',
        'the', 'to', 'was', 'will', 'with', 'i', 'me', 'my', 'we', 'you',
        'he', 'she', 'it', 'this', 'that', 'what', 'which', 'who', 'when',
        'where', 'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more',
        'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
        'same', 'so', 'than', 'too', 'very', 'can', 'just', 'should', 'now'
    }
    
    def __init__(self, remove_stopwords=True, lowercase=True):
        """
        Initialize the TextCleaner.
        
        Args:
            remove_stopwords: Whether to remove stop words
            lowercase: Whether to convert to lowercase
        """
        self.remove_stopwords = remove_stopwords
        self.lowercase = lowercase
    
    def clean(self, text: str) -> str:
        """
        Clean a single text string.
        
        Args:
            text: Input text to clean
            
        Returns:
            Cleaned text
        """
        if not isinstance(text, str):
            return ""
        
        # Lowercase
        if self.lowercase:
            text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove special characters and digits while preserving spaces
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def clean_and_tokenize(self, text: str) -> List[str]:
        """
        Clean text and return tokens.
        
        Args:
            text: Input text
            
        Returns:
            List of tokens
        """
        cleaned = self.clean(text)
        tokens = cleaned.split()
        
        if self.remove_stopwords:
            tokens = [t for t in tokens if t.lower() not in self.STOP_WORDS]
        
        return tokens
    
    def clean_batch(self, texts: List[str]) -> List[str]:
        """
        Clean a batch of texts.
        
        Args:
            texts: List of texts to clean
            
        Returns:
            List of cleaned texts
        """
        return [self.clean(text) for text in texts]
    
    @staticmethod
    def remove_punctuation(text: str) -> str:
        """Remove punctuation from text."""
        return text.translate(str.maketrans('', '', string.punctuation))
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Normalize whitespace."""
        return ' '.join(text.split())
    
    @staticmethod
    def expand_contractions(text: str) -> str:
        """Expand common contractions."""
        contractions_dict = {
            "ain't": "am not",
            "aren't": "are not",
            "can't": "cannot",
            "can't've": "cannot have",
            "could've": "could have",
            "couldn't": "could not",
            "didn't": "did not",
            "doesn't": "does not",
            "don't": "do not",
            "hadn't": "had not",
            "hasn't": "has not",
            "haven't": "have not",
            "he'd": "he would",
            "he'll": "he will",
            "he's": "he is",
            "how'd": "how did",
            "how'll": "how will",
            "how's": "how is",
            "i'd": "i would",
            "i'll": "i will",
            "i'm": "i am",
            "i've": "i have",
            "isn't": "is not",
            "it'd": "it would",
            "it'll": "it will",
            "it's": "it is",
            "let's": "let us",
            "shouldn't": "should not",
            "that's": "that is",
            "there's": "there is",
            "they'd": "they would",
            "they'll": "they will",
            "they're": "they are",
            "they've": "they have",
            "wasn't": "was not",
            "we'd": "we would",
            "we'll": "we will",
            "we're": "we are",
            "we've": "we have",
            "weren't": "were not",
            "what's": "what is",
            "won't": "will not",
            "wouldn't": "would not",
            "you'd": "you would",
            "you'll": "you will",
            "you're": "you are",
            "you've": "you have",
            "yours": "yours"
        }
        
        text_lower = text.lower()
        for contraction, expansion in contractions_dict.items():
            text_lower = re.sub(r'\b' + contraction + r'\b', expansion, text_lower)
        
        return text_lower
