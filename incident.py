import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.incident import IncidentStatus, SeverityLevel


class IncidentCreate(BaseModel):
    title: str = Field(..., max_length=255)
    description: str
    logs: Optional[str] = None
    severity: SeverityLevel = SeverityLevel.MEDIUM


class IncidentResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    logs: Optional[str]
    severity: SeverityLevel
    status: IncidentStatus
    root_cause_analysis: Optional[str]
    suggested_resolution: Optional[str]
    postmortem_summary: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AnalysisRequest(BaseModel):
    incident_id: uuid.UUID
    top_k: int = 3


class AnalysisResponse(BaseModel):
    incident_id: uuid.UUID
    root_cause_analysis: str
    suggested_resolution: str
    similar_incidents: list[str] = []


class PostmortemResponse(BaseModel):
    incident_id: uuid.UUID
    postmortem_summary: str
