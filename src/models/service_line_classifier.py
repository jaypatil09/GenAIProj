"""
Service Line Classifier.
Classifies feedback to appropriate service lines in the hospital.
"""

from typing import List, Dict
import joblib
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import numpy as np


class ServiceLineClassifier:
    """Classify feedback to hospital service lines."""
    
    SERVICE_LINES = [
        "Outpatient Department",
        "Emergency Department",
        "Inpatient Ward",
        "Surgery",
        "Diagnostic Services",
        "Billing Department",
        "Administration"
    ]
    
    def __init__(self, model_path: str = "models"):
        """
        Initialize the ServiceLineClassifier.
        
        Args:
            model_path: Path to load/save models
        """
        self.model_path = model_path
        os.makedirs(model_path, exist_ok=True)
        
        self.model = None
        self.is_trained = False
        
        self._load_model()
    
    def classify(self, text: str) -> str:
        """
        Classify a single feedback text to a service line.
        
        Args:
            text: Feedback text
            
        Returns:
            Predicted service line
        """
        if not self.is_trained or self.model is None:
            return "Outpatient Department"  # Default
        
        prediction = self.model.predict([text])[0]
        return prediction
    
    def classify_batch(self, texts: List[str]) -> List[str]:
        """
        Classify multiple feedback texts.
        
        Args:
            texts: List of feedback texts
            
        Returns:
            List of predicted service lines
        """
        if not self.is_trained or self.model is None:
            return ["Outpatient Department"] * len(texts)
        
        predictions = self.model.predict(texts)
        return list(predictions)
    
    def classify_with_confidence(self, text: str) -> Dict[str, float]:
        """
        Classify with confidence scores for all service lines.
        
        Args:
            text: Feedback text
            
        Returns:
            Dictionary with service lines and confidence scores
        """
        if not self.is_trained or self.model is None:
            return {sl: 1.0 / len(self.SERVICE_LINES) for sl in self.SERVICE_LINES}
        
        # Get probability scores
        probabilities = self.model.predict_proba([text])[0]
        
        result = {}
        for service_line, prob in zip(self.SERVICE_LINES, probabilities):
            result[service_line] = float(prob)
        
        return result
    
    def train(self, texts: List[str], labels: List[str]):
        """
        Train the service line classifier.
        
        Args:
            texts: List of training texts
            labels: List of service line labels
        """
        # Create pipeline with TF-IDF and Logistic Regression
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=1000, ngram_range=(1, 2))),
            ('classifier', LogisticRegression(max_iter=1000, random_state=42))
        ])
        
        # Train the model
        self.model.fit(texts, labels)
        self.is_trained = True
        
        self._save_model()
    
    def _save_model(self):
        """Save trained model to disk."""
        if self.model is not None:
            joblib.dump(self.model, os.path.join(self.model_path, "service_line_model.pkl"))
    
    def _load_model(self):
        """Load trained model from disk if available."""
        model_path = os.path.join(self.model_path, "service_line_model.pkl")
        
        if os.path.exists(model_path):
            try:
                self.model = joblib.load(model_path)
                self.is_trained = True
            except Exception as e:
                print(f"Could not load model: {e}")
                self.is_trained = False
    
    def get_service_lines(self) -> List[str]:
        """Get list of all service lines."""
        return self.SERVICE_LINES
