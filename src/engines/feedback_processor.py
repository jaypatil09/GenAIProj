"""
Feedback Processor.
Orchestrates the complete feedback analysis pipeline.
"""

from typing import Dict, List
import pandas as pd
from datetime import datetime

from ..data.text_cleaning import TextCleaner
from .staff_detector import StaffDetector
from .severity_engine import SeverityEngine
from .routing_engine import RoutingEngine


class FeedbackProcessor:
    """Process feedback through the complete analysis pipeline."""
    
    def __init__(
        self,
        aspect_detector,
        service_line_classifier,
        aspect_sentiment_classifier
    ):
        """
        Initialize the FeedbackProcessor.
        
        Args:
            aspect_detector: AspectDetector instance
            service_line_classifier: ServiceLineClassifier instance
            aspect_sentiment_classifier: AspectSentimentClassifier instance
        """
        self.aspect_detector = aspect_detector
        self.service_line_classifier = service_line_classifier
        self.aspect_sentiment_classifier = aspect_sentiment_classifier
        
        self.text_cleaner = TextCleaner()
        self.staff_detector = StaffDetector()
        self.severity_engine = SeverityEngine()
        self.routing_engine = RoutingEngine()
    
    def process_single(self, feedback_text: str, feedback_id: str = None) -> Dict:
        """
        Process a single feedback item through the pipeline.
        
        Args:
            feedback_text: The feedback text
            feedback_id: Optional feedback ID
            
        Returns:
            Dictionary with complete analysis results
        """
        # Generate ID if not provided
        if feedback_id is None:
            feedback_id = f"FBK{datetime.now().timestamp()}"
        
        # Clean text
        cleaned_text = self.text_cleaner.clean(feedback_text)
        
        # Classify service line
        service_line = self.service_line_classifier.classify(feedback_text)
        
        # Detect aspects
        aspects = self.aspect_detector.detect(feedback_text)
        
        # Classify aspect sentiments
        aspect_sentiments = {}
        for aspect in aspects:
            sentiment = self.aspect_sentiment_classifier.classify(
                feedback_text,
                aspect=aspect
            )
            aspect_sentiments[aspect] = sentiment
        
        # Determine overall sentiment (majority vote of aspect sentiments)
        sentiments = list(aspect_sentiments.values())
        if sentiments:
            if sentiments.count("positive") > len(sentiments) / 2:
                overall_sentiment = "positive"
            elif sentiments.count("negative") > len(sentiments) / 2:
                overall_sentiment = "negative"
            else:
                overall_sentiment = "neutral"
        else:
            overall_sentiment = "neutral"
        
        # Detect staff category
        staff_category = self.staff_detector.detect(feedback_text)
        
        # Determine severity
        severity = self.severity_engine.determine_severity(
            feedback_text,
            overall_sentiment
        )
        
        # Route to department
        routing_info = self.routing_engine.route(
            aspects,
            severity,
            service_line
        )
        
        # Compile result
        result = {
            "feedback_id": feedback_id,
            "timestamp": datetime.now().isoformat(),
            "original_text": feedback_text,
            "cleaned_text": cleaned_text,
            "service_line": service_line,
            "aspects": aspects,
            "aspect_sentiments": aspect_sentiments,
            "overall_sentiment": overall_sentiment,
            "staff_category": staff_category,
            "severity": severity,
            "routing_department": routing_info["routing_department"],
            "requires_escalation": routing_info["requires_escalation"],
            "escalation_reason": routing_info["escalation_reason"]
        }
        
        return result
    
    def process_batch(self, feedback_items: List[Dict]) -> pd.DataFrame:
        """
        Process multiple feedback items.
        
        Args:
            feedback_items: List of dictionaries with 'text' and optional 'id' keys
            
        Returns:
            DataFrame with processed results
        """
        results = []
        
        for item in feedback_items:
            if isinstance(item, str):
                text = item
                item_id = None
            elif isinstance(item, dict):
                text = item.get("text") or item.get("feedback_text")
                item_id = item.get("id") or item.get("feedback_id")
            else:
                continue
            
            result = self.process_single(text, item_id)
            results.append(result)
        
        return pd.DataFrame(results)
    
    def process_dataframe(self, df: pd.DataFrame, text_column: str = "feedback_text") -> pd.DataFrame:
        """
        Process a DataFrame of feedback.
        
        Args:
            df: DataFrame with feedback data
            text_column: Name of column containing feedback text
            
        Returns:
            DataFrame with added analysis columns
        """
        processed_records = []
        
        for idx, row in df.iterrows():
            feedback_text = row[text_column]
            feedback_id = row.get("feedback_id") if isinstance(row, dict) else None
            
            result = self.process_single(feedback_text, feedback_id)
            
            # Merge with original row data
            for key, value in row.to_dict().items():
                if key not in result:
                    result[key] = value
            
            processed_records.append(result)
        
        return pd.DataFrame(processed_records)
