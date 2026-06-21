"""
Aspect Sentiment Classifier.
Analyzes sentiment for each detected aspect in feedback.
"""

from typing import List, Dict
import joblib
import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MultiLabelBinarizer
import numpy as np


class AspectSentimentClassifier:
    """Classify sentiment for individual aspects."""
    
    SENTIMENTS = ["positive", "neutral", "negative"]
    POSITIVE_PATTERNS = (
        r"\bexcellent\b", r"\bgood\b", r"\bgreat\b", r"\bhappy\b",
        r"\bhelpful\b", r"\bpolite\b", r"\bprofessional\b",
        r"\brecommend\b", r"\bresponsive\b", r"\bsatisfied\b",
        r"\bthank(?:s|ful)?\b", r"\bwell\b"
    )
    NEGATIVE_PATTERNS = (
        r"\barrogant\b", r"\bconfusing\b", r"\bdelay(?:ed)?\b",
        r"\bdirty\b", r"\bdisappointed\b", r"\berrors?\b",
        r"\bfail(?:ed|ure)?\b", r"\bfrustrated\b", r"\bharm(?:ful)?\b",
        r"\binaccurate\b", r"\bincorrect\b", r"\binattentive\b",
        r"\blate\b", r"\bmissing\b", r"\bpoor\b", r"\brude\b",
        r"\bserious\b", r"\bunacceptable\b", r"\bunhelpful\b",
        r"\bunsafe\b", r"\bwithout properly\b", r"\bwrong\b",
        r"\bnot (?:helpful|satisfied|professional|safe)\b"
    )
    
    def __init__(self, model_path: str = "models"):
        """
        Initialize the AspectSentimentClassifier.
        
        Args:
            model_path: Path to load/save models
        """
        self.model_path = model_path
        os.makedirs(model_path, exist_ok=True)
        
        # Dictionary to store models for each aspect
        self.models = {}
        self.is_trained = False
        
        self._load_models()
    
    def classify(self, text: str, aspect: str = None) -> str:
        """
        Classify sentiment for text, optionally focusing on an aspect.
        
        Args:
            text: Feedback text
            aspect: Optional aspect to focus on
            
        Returns:
            Sentiment label (positive, neutral, negative)
        """
        if not self.is_trained:
            return self._classify_rule_based(text)
        
        # Use overall sentiment model if aspect not specified
        model_key = aspect if aspect else "overall"
        
        if model_key not in self.models:
            return self._classify_rule_based(text)
        
        prediction = self.models[model_key].predict([text])[0]
        return prediction
    
    def classify_batch(self, texts: List[str], aspect: str = None) -> List[str]:
        """
        Classify sentiment for multiple texts.
        
        Args:
            texts: List of feedback texts
            aspect: Optional aspect to focus on
            
        Returns:
            List of sentiment labels
        """
        if not self.is_trained:
            return [self._classify_rule_based(text) for text in texts]
        
        model_key = aspect if aspect else "overall"
        
        if model_key not in self.models:
            return [self._classify_rule_based(text) for text in texts]
        
        predictions = self.models[model_key].predict(texts)
        return list(predictions)
    
    def classify_with_confidence(self, text: str, aspect: str = None) -> Dict[str, float]:
        """
        Classify sentiment with confidence scores.
        
        Args:
            text: Feedback text
            aspect: Optional aspect to focus on
            
        Returns:
            Dictionary with sentiments and confidence scores
        """
        if not self.is_trained:
            return {s: 1.0 / len(self.SENTIMENTS) for s in self.SENTIMENTS}
        
        model_key = aspect if aspect else "overall"
        
        if model_key not in self.models:
            return {s: 1.0 / len(self.SENTIMENTS) for s in self.SENTIMENTS}
        
        # Get probability scores
        try:
            probabilities = self.models[model_key].predict_proba([text])[0]
            classes = self.models[model_key].classes_
            
            result = {}
            for sentiment, prob in zip(classes, probabilities):
                result[sentiment] = float(prob)
            
            # Fill missing sentiments with 0
            for sentiment in self.SENTIMENTS:
                if sentiment not in result:
                    result[sentiment] = 0.0
            
            return result
        except:
            return {s: 1.0 / len(self.SENTIMENTS) for s in self.SENTIMENTS}
    
    def train(self, texts: List[str], labels: List[str], aspect: str = None):
        """
        Train a sentiment classifier for an aspect or overall.
        
        Args:
            texts: List of training texts
            labels: List of sentiment labels
            aspect: Optional aspect name (if None, trains overall sentiment)
        """
        model_key = aspect if aspect else "overall"
        
        # Create pipeline with TF-IDF and Logistic Regression
        model = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=1000, ngram_range=(1, 2))),
            ('classifier', LogisticRegression(max_iter=1000, random_state=42))
        ])
        
        # Train the model
        model.fit(texts, labels)
        
        # Store the model
        self.models[model_key] = model
        self.is_trained = True
        
        self._save_models()
    
    def train_all_aspects(self, texts_dict: Dict[str, List[str]], labels_dict: Dict[str, List[str]]):
        """
        Train sentiment classifiers for multiple aspects at once.
        
        Args:
            texts_dict: Dictionary with aspect names as keys and lists of texts as values
            labels_dict: Dictionary with aspect names as keys and lists of labels as values
        """
        for aspect in texts_dict.keys():
            texts = texts_dict[aspect]
            labels = labels_dict[aspect]
            if texts and labels:
                self.train(texts, labels, aspect=aspect)
    
    def _save_models(self):
        """Save trained models to disk."""
        for aspect, model in self.models.items():
            filename = f"aspect_sentiment_model_{aspect}.pkl"
            joblib.dump(model, os.path.join(self.model_path, filename))
    
    def _load_models(self):
        """Load trained models from disk if available."""
        for aspect in ["overall"] + [
            "wait_time", "politeness", "cleanliness", "billing", 
            "diagnostics", "discharge_process", "doctor_explanation", 
            "nursing_care", "lab_services"
        ]:
            model_path = os.path.join(self.model_path, f"aspect_sentiment_model_{aspect}.pkl")
            
            if os.path.exists(model_path):
                try:
                    self.models[aspect] = joblib.load(model_path)
                except Exception as e:
                    print(f"Could not load model for {aspect}: {e}")
        
        if self.models:
            self.is_trained = True

    def _classify_rule_based(self, text: str) -> str:
        """Classify sentiment when no trained model is available."""
        positive_score = sum(
            bool(re.search(pattern, text, flags=re.IGNORECASE))
            for pattern in self.POSITIVE_PATTERNS
        )
        negative_score = sum(
            bool(re.search(pattern, text, flags=re.IGNORECASE))
            for pattern in self.NEGATIVE_PATTERNS
        )

        if positive_score > negative_score:
            return "positive"
        if negative_score > positive_score:
            return "negative"
        return "neutral"
    
    def get_sentiments(self) -> List[str]:
        """Get list of all sentiment categories."""
        return self.SENTIMENTS
