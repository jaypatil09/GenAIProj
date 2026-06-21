"""
Data loading and management utilities.
Handles loading feedback data from CSV files.
"""

import pandas as pd
import os
from typing import Optional, List


class DataLoader:
    """Load and manage feedback data from CSV files."""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the DataLoader.
        
        Args:
            data_dir: Directory containing data files
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def load_feedback(self, filename: str = "feedback.csv") -> pd.DataFrame:
        """
        Load feedback data from CSV.
        
        Args:
            filename: Name of the CSV file to load
            
        Returns:
            DataFrame containing feedback data
        """
        filepath = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(filepath):
            return pd.DataFrame()
        
        return pd.read_csv(filepath)
    
    def save_feedback(self, df: pd.DataFrame, filename: str = "feedback.csv"):
        """
        Save feedback data to CSV.
        
        Args:
            df: DataFrame to save
            filename: Name of the CSV file
        """
        filepath = os.path.join(self.data_dir, filename)
        df.to_csv(filepath, index=False)
    
    def load_processed_feedback(self) -> pd.DataFrame:
        """Load processed feedback data."""
        return self.load_feedback("processed_feedback.csv")
    
    def save_processed_feedback(self, df: pd.DataFrame):
        """Save processed feedback data."""
        self.save_feedback(df, "processed_feedback.csv")
    
    def load_themes(self) -> pd.DataFrame:
        """Load emerging themes data."""
        return self.load_feedback("themes.csv")
    
    def save_themes(self, df: pd.DataFrame):
        """Save emerging themes data."""
        self.save_feedback(df, "themes.csv")
    
    def load_escalations(self) -> pd.DataFrame:
        """Load escalated complaints data."""
        return self.load_feedback("escalations.csv")
    
    def save_escalations(self, df: pd.DataFrame):
        """Save escalated complaints data."""
        self.save_feedback(df, "escalations.csv")
    
    def get_feedback_subset(
        self, 
        filename: str = "feedback.csv",
        service_line: Optional[str] = None,
        severity: Optional[str] = None,
        sentiment: Optional[str] = None,
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Get a filtered subset of feedback data.
        
        Args:
            filename: CSV file to load from
            service_line: Filter by service line
            severity: Filter by severity
            sentiment: Filter by sentiment
            limit: Limit number of records
            
        Returns:
            Filtered DataFrame
        """
        df = self.load_feedback(filename)
        
        if df.empty:
            return df
        
        if service_line and "service_line" in df.columns:
            df = df[df["service_line"] == service_line]
        
        if severity and "severity" in df.columns:
            df = df[df["severity"] == severity]
        
        if sentiment and "overall_sentiment" in df.columns:
            df = df[df["overall_sentiment"] == sentiment]
        
        if limit:
            df = df.head(limit)
        
        return df
    
    def get_summary_stats(self, filename: str = "feedback.csv") -> dict:
        """
        Get summary statistics from feedback data.
        
        Args:
            filename: CSV file to analyze
            
        Returns:
            Dictionary with summary statistics
        """
        df = self.load_feedback(filename)
        
        if df.empty:
            return {}
        
        stats = {
            "total_records": len(df),
            "sentiment_dist": df["overall_sentiment"].value_counts().to_dict() if "overall_sentiment" in df.columns else {},
            "severity_dist": df["severity"].value_counts().to_dict() if "severity" in df.columns else {},
            "service_line_dist": df["service_line"].value_counts().to_dict() if "service_line" in df.columns else {},
            "source_dist": df["source"].value_counts().to_dict() if "source" in df.columns else {},
        }
        
        return stats
