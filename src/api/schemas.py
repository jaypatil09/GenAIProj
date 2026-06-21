"""
FastAPI schemas for request/response models.
"""

from pydantic import BaseModel
from typing import List, Dict, Optional


class FeedbackRequest(BaseModel):
    """Request model for single feedback analysis."""
    feedback_text: str
    feedback_id: Optional[str] = None
    source: Optional[str] = None


class BulkUploadRequest(BaseModel):
    """Request model for bulk upload."""
    pass  # File uploaded via multipart


class FeedbackResponse(BaseModel):
    """Response model for feedback analysis."""
    feedback_id: str
    service_line: str
    aspects: List[str]
    aspect_sentiments: Dict[str, str]
    overall_sentiment: str
    staff_category: str
    severity: str
    routing_department: str
    requires_escalation: bool
    escalation_reason: Optional[str]


class MetricsResponse(BaseModel):
    """Response model for system metrics."""
    total_feedbacks: int
    sentiment_distribution: Dict[str, int]
    severity_distribution: Dict[str, int]
    department_distribution: Dict[str, int]
    escalation_count: int


class DepartmentSummaryResponse(BaseModel):
    """Response model for department summary."""
    department: str
    total_complaints: int
    avg_severity: str
    common_aspects: List[str]
    resolution_rate: float


class EmergingTheme(BaseModel):
    """Model for emerging theme."""
    id: int
    name: str
    size: int
    percentage: str


class EscalationRecord(BaseModel):
    """Model for escalation record."""
    feedback_id: str
    severity: str
    reason: str
    department: str
    timestamp: str
