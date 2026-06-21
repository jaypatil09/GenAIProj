"""
Severity Engine.
Determines the severity level of feedback/complaints.
"""

from typing import List


class SeverityEngine:
    """Determine severity of feedback based on content and sentiment."""
    
    # Severity levels in order of importance
    SEVERITY_LEVELS = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    
    # Keywords that indicate each severity level
    SEVERITY_KEYWORDS = {
        "CRITICAL": [
            "safety", "medication error", "patient fall", "allergy", "infection",
            "heart attack", "critical", "died", "death", "wrong medication",
            "overdose", "misdiagnosis", "surgical error", "blood infection",
            "life threatening", "emergency", "urgent"
        ],
        "HIGH": [
            "wrong", "error", "major issue", "serious", "harm", "injury",
            "severe pain", "major delay", "3 hours", "4 hours", "5 hours",
            "incorrect", "failed", "complication", "adverse", "significant"
        ],
        "MEDIUM": [
            "rude", "delayed", "2 hours", "inconvenience", "confusion",
            "poor quality", "unsatisfactory", "uncomfortable", "unhappy",
            "disappointed", "frustrated", "lengthy wait", "disrespectful"
        ],
        "LOW": [
            "positive", "good", "satisfied", "excellent", "happy", "great",
            "helpful", "polite", "courteous", "professional", "clean",
            "efficient", "quick", "pleasant"
        ]
    }
    
    def __init__(self):
        """Initialize the SeverityEngine."""
        pass
    
    def determine_severity(self, text: str, sentiment: str = None) -> str:
        """
        Determine severity level of feedback.
        
        Args:
            text: Feedback text
            sentiment: Overall sentiment (positive, neutral, negative)
            
        Returns:
            Severity level (CRITICAL, HIGH, MEDIUM, LOW)
        """
        text_lower = text.lower()
        
        # Check for CRITICAL severity
        if any(keyword in text_lower for keyword in self.SEVERITY_KEYWORDS["CRITICAL"]):
            return "CRITICAL"
        
        # Check for HIGH severity
        if any(keyword in text_lower for keyword in self.SEVERITY_KEYWORDS["HIGH"]):
            return "HIGH"
        
        # Check for MEDIUM severity
        if any(keyword in text_lower for keyword in self.SEVERITY_KEYWORDS["MEDIUM"]):
            return "MEDIUM"
        
        # Check for LOW severity
        if any(keyword in text_lower for keyword in self.SEVERITY_KEYWORDS["LOW"]):
            return "LOW"
        
        # Default based on sentiment
        if sentiment:
            if sentiment == "positive":
                return "LOW"
            elif sentiment == "negative":
                return "MEDIUM"
            else:
                return "MEDIUM"
        
        return "MEDIUM"  # Default
    
    def determine_severity_batch(self, texts: List[str], sentiments: List[str] = None) -> List[str]:
        """
        Determine severity for multiple feedbacks.
        
        Args:
            texts: List of feedback texts
            sentiments: List of sentiments (optional)
            
        Returns:
            List of severity levels
        """
        if sentiments is None:
            sentiments = [None] * len(texts)
        
        return [
            self.determine_severity(text, sentiment)
            for text, sentiment in zip(texts, sentiments)
        ]
    
    def get_severity_score(self, severity: str) -> int:
        """
        Get numeric score for severity level.
        
        Args:
            severity: Severity level string
            
        Returns:
            Numeric score (higher = more severe)
        """
        severity_scores = {
            "CRITICAL": 4,
            "HIGH": 3,
            "MEDIUM": 2,
            "LOW": 1
        }
        return severity_scores.get(severity, 1)
    
    def get_severity_levels(self) -> List[str]:
        """Get list of all severity levels."""
        return self.SEVERITY_LEVELS
    
    def get_keywords(self, severity: str) -> List[str]:
        """
        Get keywords for a severity level.
        
        Args:
            severity: Severity level
            
        Returns:
            List of keywords
        """
        return self.SEVERITY_KEYWORDS.get(severity, [])
