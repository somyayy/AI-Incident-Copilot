import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.schemas.incident import (
    AnalysisResponse,
    IncidentCreate,
    IncidentResponse,
    PostmortemResponse,
)
from app.services import incident_service

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.post("", response_model=IncidentResponse, status_code=201)
def create_incident(payload: IncidentCreate, db: Session = Depends(get_db)):
    return incident_service.create_incident(db, payload)


@router.get("", response_model=list[IncidentResponse])
def list_incidents(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return incident_service.list_incidents(db, skip, limit)


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(incident_id: uuid.UUID, db: Session = Depends(get_db)):
    incident = incident_service.get_incident(db, incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.post("/{incident_id}/analyze", response_model=AnalysisResponse)
def analyze_incident(incident_id: uuid.UUID, top_k: int = 3, db: Session = Depends(get_db)):
    try:
        result = incident_service.analyze_incident(db, incident_id, top_k)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return result


@router.post("/{incident_id}/postmortem", response_model=PostmortemResponse)
def generate_postmortem(incident_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        summary = incident_service.generate_incident_postmortem(db, incident_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"incident_id": incident_id, "postmortem_summary": summary}
