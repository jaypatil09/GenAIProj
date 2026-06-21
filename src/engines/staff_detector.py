"""
Staff Category Detector.
Identifies which staff category the feedback relates to.
"""

from typing import List, Optional


class StaffDetector:
    """Detect staff category mentioned in feedback."""
    
    # Keyword mappings for staff categories
    STAFF_KEYWORDS = {
        "doctor": ["doctor", "physician", "consultant", "specialist", "surgeon", "cardiologist", "neurologist"],
        "nursing_staff": ["nurse", "nursing", "ward nurse", "icu nurse", "staff nurse", "nursing assistant"],
        "reception_staff": ["receptionist", "reception", "front desk", "check-in staff", "billing counter"],
        "billing_staff": ["billing", "finance", "accounts", "payment", "cashier", "billing department"],
        "diagnostics_staff": ["lab", "technician", "radiologist", "pathologist", "phlebotomist", "lab technician"],
        "housekeeping": ["housekeeping", "cleaning", "janitor", "housekeeping staff", "cleaning staff"],
        "security": ["security", "guard", "security guard", "security staff"],
    }
    
    def __init__(self):
        """Initialize the StaffDetector."""
        self.categories = list(self.STAFF_KEYWORDS.keys())
    
    def detect(self, text: str) -> str:
        """
        Detect staff category from feedback text.
        
        Args:
            text: Feedback text
            
        Returns:
            Staff category name
        """
        text_lower = text.lower()
        
        # Check each category
        for category, keywords in self.STAFF_KEYWORDS.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        
        # Default to general staff if no specific category detected
        return "general_staff"
    
    def detect_batch(self, texts: List[str]) -> List[str]:
        """
        Detect staff categories for multiple texts.
        
        Args:
            texts: List of feedback texts
            
        Returns:
            List of staff categories
        """
        return [self.detect(text) for text in texts]
    
    def get_confidence(self, text: str) -> dict:
        """
        Get confidence scores for each staff category.
        
        Args:
            text: Feedback text
            
        Returns:
            Dictionary with categories and confidence scores
        """
        text_lower = text.lower()
        scores = {}
        
        # Count keyword matches for each category
        for category, keywords in self.STAFF_KEYWORDS.items():
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            scores[category] = float(matches)
        
        # Normalize scores
        total = sum(scores.values())
        if total > 0:
            scores = {cat: score / total for cat, score in scores.items()}
        else:
            scores = {cat: 1.0 / len(self.categories) for cat in self.categories}
        
        return scores
    
    def get_staff_categories(self) -> List[str]:
        """Get list of all staff categories."""
        return self.categories
    
    def get_keywords(self, category: str) -> List[str]:
        """
        Get keywords for a staff category.
        
        Args:
            category: Staff category name
            
        Returns:
            List of keywords for that category
        """
        return self.STAFF_KEYWORDS.get(category, [])
