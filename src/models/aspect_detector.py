"""
Aspect detection module.
Detects aspects mentioned in patient feedback using rule-based and ML approaches.
"""

from typing import List, Dict, Set
import joblib
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multioutput import MultiOutputClassifier
from sklearn.linear_model import LogisticRegression
import numpy as np


class AspectDetector:
    """Detect aspects in patient feedback."""
    
    # Keyword mappings for rule-based detection
    ASPECT_KEYWORDS = {
        "wait_time": ["wait", "delay", "queue", "late", "long time", "took hours", "waiting", "delayed"],
        "politeness": ["rude", "arrogant", "shouted", "polite", "courteous", "respectful", "rude", "disrespectful"],
        "cleanliness": ["dirty", "smell", "unclean", "clean", "hygiene", "facilities", "messy", "untidy"],
        "billing": ["bill", "insurance", "charges", "payment", "expensive", "affordable", "cost", "fee"],
        "diagnostics": ["report", "result", "scan", "lab", "test", "x-ray", "blood", "pathology"],
        "discharge_process": ["discharge", "summary", "clearance", "checkout", "release"],
        "doctor_explanation": ["explain", "understand", "told", "informed", "communication", "discussed"],
        "nursing_care": ["nurse", "care", "attentive", "responsive", "support", "helpful"],
        "lab_services": ["lab", "test", "blood", "sample", "results", "lab report"]
    }
    
    def __init__(self, use_ml=True, model_path: str = "models"):
        """
        Initialize the AspectDetector.
        
        Args:
            use_ml: Whether to use ML model (if trained) for detection
            model_path: Path to load/save models
        """
        self.use_ml = use_ml
        self.model_path = model_path
        os.makedirs(model_path, exist_ok=True)
        
        self.vectorizer = None
        self.model = None
        self.aspect_names = list(self.ASPECT_KEYWORDS.keys())
        self.is_trained = False
        
        self._load_model()
    
    def detect_rule_based(self, text: str) -> List[str]:
        """
        Detect aspects using rule-based keyword matching.
        
        Args:
            text: Input feedback text
            
        Returns:
            List of detected aspects
        """
        text_lower = text.lower()
        detected_aspects = []
        
        for aspect, keywords in self.ASPECT_KEYWORDS.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_aspects.append(aspect)
        
        # Ensure at least one aspect if none detected
        if not detected_aspects:
            detected_aspects = [self.aspect_names[0]]
        
        return detected_aspects
    
    def detect_ml_based(self, texts: List[str]) -> List[List[str]]:
        """
        Detect aspects using trained ML model.
        
        Args:
            texts: List of feedback texts
            
        Returns:
            List of lists containing detected aspects for each text
        """
        if not self.is_trained or self.model is None or self.vectorizer is None:
            # Fall back to rule-based
            return [self.detect_rule_based(text) for text in texts]
        
        # Vectorize texts
        X = self.vectorizer.transform(texts)
        
        # Predict
        predictions = self.model.predict(X)
        
        # Convert to aspect names
        results = []
        for pred in predictions:
            aspects = [self.aspect_names[i] for i, val in enumerate(pred) if val == 1]
            if not aspects:
                aspects = [self.aspect_names[0]]
            results.append(aspects)
        
        return results
    
    def detect(self, text: str) -> List[str]:
        """
        Detect aspects in a single feedback text.
        
        Args:
            text: Feedback text
            
        Returns:
            List of detected aspects
        """
        if self.use_ml and self.is_trained:
            return self.detect_ml_based([text])[0]
        else:
            return self.detect_rule_based(text)
    
    def detect_batch(self, texts: List[str]) -> List[List[str]]:
        """
        Detect aspects in multiple feedback texts.
        
        Args:
            texts: List of feedback texts
            
        Returns:
            List of lists containing aspects
        """
        if self.use_ml and self.is_trained:
            return self.detect_ml_based(texts)
        else:
            return [self.detect_rule_based(text) for text in texts]
    
    def train(self, texts: List[str], labels: List[List[int]]):
        """
        Train the ML model for aspect detection.
        
        Args:
            texts: List of training texts
            labels: List of binary labels (n_samples x n_aspects)
        """
        # Initialize vectorizer
        self.vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2))
        X = self.vectorizer.fit_transform(texts)
        
        # Initialize and train model
        base_lr = LogisticRegression(max_iter=1000, random_state=42)
        self.model = MultiOutputClassifier(base_lr)
        self.model.fit(X, labels)
        
        self.is_trained = True
        self._save_model()
    
    def _save_model(self):
        """Save trained model to disk."""
        if self.vectorizer is not None:
            joblib.dump(self.vectorizer, os.path.join(self.model_path, "aspect_vectorizer.pkl"))
        
        if self.model is not None:
            joblib.dump(self.model, os.path.join(self.model_path, "aspect_model.pkl"))
    
    def _load_model(self):
        """Load trained model from disk if available."""
        vectorizer_path = os.path.join(self.model_path, "aspect_vectorizer.pkl")
        model_path = os.path.join(self.model_path, "aspect_model.pkl")
        
        if os.path.exists(vectorizer_path) and os.path.exists(model_path):
            try:
                self.vectorizer = joblib.load(vectorizer_path)
                self.model = joblib.load(model_path)
                self.is_trained = True
            except Exception as e:
                print(f"Could not load models: {e}")
                self.is_trained = False
    
    def get_aspect_keywords(self, aspect: str) -> List[str]:
        """
        Get keywords for a specific aspect.
        
        Args:
            aspect: Aspect name
            
        Returns:
            List of keywords
        """
        return self.ASPECT_KEYWORDS.get(aspect, [])
