"""
FastAPI application with endpoints for feedback analysis.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
from typing import List, Dict
import os
import sys

# Add parent directory to path to import src modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.models.aspect_detector import AspectDetector
from src.models.service_line_classifier import ServiceLineClassifier
from src.models.aspect_sentiment_classifier import AspectSentimentClassifier
from src.models.theme_discovery import ThemeDiscovery
from src.engines.feedback_processor import FeedbackProcessor
from src.data.data_loader import DataLoader
from src.api.schemas import (
    FeedbackRequest, FeedbackResponse, MetricsResponse,
    DepartmentSummaryResponse, EmergingTheme, EscalationRecord
)

# Initialize FastAPI app
app = FastAPI(
    title="SentiMeter API",
    description="Patient Experience Intelligence & Smart Complaint Routing Platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
try:
    aspect_detector = AspectDetector()
    service_line_classifier = ServiceLineClassifier()
    aspect_sentiment_classifier = AspectSentimentClassifier()
    theme_discovery = ThemeDiscovery()
    feedback_processor = FeedbackProcessor(
        aspect_detector,
        service_line_classifier,
        aspect_sentiment_classifier
    )
    data_loader = DataLoader()
except Exception as e:
    print(f"Warning: Could not initialize models: {e}")
    feedback_processor = None


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "SentiMeter API is running",
        "version": "1.0.0",
        "status": "operational"
    }


@app.post("/analyze-feedback", response_model=FeedbackResponse)
async def analyze_feedback(request: FeedbackRequest):
    """
    Analyze a single piece of feedback.
    
    Args:
        request: FeedbackRequest with feedback_text
        
    Returns:
        Analyzed feedback with all components
    """
    if not feedback_processor:
        raise HTTPException(status_code=500, detail="Models not initialized")
    
    try:
        result = feedback_processor.process_single(
            request.feedback_text,
            request.feedback_id
        )
        
        return FeedbackResponse(
            feedback_id=result["feedback_id"],
            service_line=result["service_line"],
            aspects=result["aspects"],
            aspect_sentiments=result["aspect_sentiments"],
            overall_sentiment=result["overall_sentiment"],
            staff_category=result["staff_category"],
            severity=result["severity"],
            routing_department=result["routing_department"],
            requires_escalation=result["requires_escalation"],
            escalation_reason=result["escalation_reason"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/bulk-upload")
async def bulk_upload(file: UploadFile = File(...)):
    """
    Upload and analyze a CSV file of feedback.
    
    Args:
        file: CSV file with feedback data
        
    Returns:
        Processing status and file location
    """
    if not feedback_processor:
        raise HTTPException(status_code=500, detail="Models not initialized")
    
    try:
        # Read CSV
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        
        # Process feedback
        text_column = None
        for col in ["feedback_text", "text", "feedback", "comment"]:
            if col in df.columns:
                text_column = col
                break
        
        if text_column is None:
            raise ValueError("No suitable text column found in CSV")
        
        # Process all records
        processed_df = feedback_processor.process_dataframe(df, text_column)
        
        # Save processed feedback
        output_path = os.path.join("data", "processed_feedback.csv")
        os.makedirs("data", exist_ok=True)
        processed_df.to_csv(output_path, index=False)
        
        return {
            "status": "success",
            "total_records": len(processed_df),
            "output_file": output_path,
            "message": f"Successfully processed {len(processed_df)} feedback records"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """
    Get system-wide metrics.
    
    Returns:
        System metrics including sentiment and severity distributions
    """
    try:
        df = data_loader.load_feedback("processed_feedback.csv")
        
        if df.empty:
            return MetricsResponse(
                total_feedbacks=0,
                sentiment_distribution={},
                severity_distribution={},
                department_distribution={},
                escalation_count=0
            )
        
        return MetricsResponse(
            total_feedbacks=len(df),
            sentiment_distribution=df["overall_sentiment"].value_counts().to_dict(),
            severity_distribution=df["severity"].value_counts().to_dict(),
            department_distribution=df["routing_department"].value_counts().to_dict(),
            escalation_count=int(df["requires_escalation"].sum())
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/department-summary")
async def get_department_summary():
    """
    Get summary statistics by department.
    
    Returns:
        Department-wise analysis
    """
    try:
        df = data_loader.load_feedback("processed_feedback.csv")
        
        if df.empty:
            return {"departments": []}
        
        summary = []
        for dept in df["routing_department"].unique():
            dept_df = df[df["routing_department"] == dept]
            
            summary.append({
                "department": dept,
                "total_complaints": len(dept_df),
                "escalation_count": int(dept_df["requires_escalation"].sum()),
                "avg_severity": dept_df["severity"].value_counts().index[0],
                "common_aspects": dept_df["aspects"].str.split("|").explode().value_counts().head(3).index.tolist()
            })
        
        return {"departments": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/emerging-themes")
async def get_emerging_themes():
    """
    Get emerging themes from feedback.
    
    Returns:
        List of emerging themes with statistics
    """
    try:
        df = data_loader.load_feedback("processed_feedback.csv")
        
        if df.empty:
            return {"themes": []}
        
        # For now, return themes from stored data
        themes_df = data_loader.load_themes()
        if not themes_df.empty:
            return {
                "themes": themes_df.to_dict('records')
            }
        
        return {"themes": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/escalations")
async def get_escalations():
    """
    Get list of escalated complaints.
    
    Returns:
        List of escalation records
    """
    try:
        df = data_loader.load_feedback("processed_feedback.csv")
        
        if df.empty:
            return {"escalations": []}
        
        escalations = df[df["requires_escalation"] == True].copy()
        
        return {
            "total_escalations": len(escalations),
            "by_severity": escalations["severity"].value_counts().to_dict(),
            "escalations": escalations[["feedback_id", "severity", "escalation_reason", "routing_department"]].head(20).to_dict('records')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "models_initialized": feedback_processor is not None
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )
