"""
Business logic layer: coordinates database persistence, vector retrieval,
and LLM calls to fulfill incident analysis workflows.
"""

import uuid

from sqlalchemy.orm import Session

from app.llm.llm_client import generate_postmortem, generate_rca_and_resolution
from app.models.incident import Incident, IncidentStatus
from app.rag.retriever import get_vector_store
from app.schemas.incident import IncidentCreate
from app.utils.logger import get_logger

logger = get_logger(__name__)


def create_incident(db: Session, payload: IncidentCreate) -> Incident:
    incident = Incident(
        title=payload.title,
        description=payload.description,
        logs=payload.logs,
        severity=payload.severity,
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)

    # Index the incident text so future incidents can retrieve it as context.
    store = get_vector_store()
    combined_text = f"{payload.title}\n{payload.description}\n{payload.logs or ''}"
    store.add_incident(str(incident.id), payload.title, combined_text)

    logger.info("Created incident %s", incident.id)
    return incident


def get_incident(db: Session, incident_id: uuid.UUID) -> Incident | None:
    return db.query(Incident).filter(Incident.id == incident_id).first()


def list_incidents(db: Session, skip: int = 0, limit: int = 50) -> list[Incident]:
    return db.query(Incident).order_by(Incident.created_at.desc()).offset(skip).limit(limit).all()


def analyze_incident(db: Session, incident_id: uuid.UUID, top_k: int = 3) -> dict:
    incident = get_incident(db, incident_id)
    if incident is None:
        raise ValueError(f"Incident {incident_id} not found")

    store = get_vector_store()
    query_text = f"{incident.title}\n{incident.description}\n{incident.logs or ''}"
    similar = store.search(query_text, top_k=top_k)
    # Exclude the incident itself if it was already indexed.
    similar = [s for s in similar if s["id"] != str(incident.id)]

    result = generate_rca_and_resolution(
        title=incident.title,
        description=incident.description,
        logs=incident.logs,
        similar_incidents=similar,
    )

    incident.root_cause_analysis = result["root_cause_analysis"]
    incident.suggested_resolution = result["suggested_resolution"]
    incident.status = IncidentStatus.INVESTIGATING
    db.commit()
    db.refresh(incident)

    return {
        "incident_id": incident.id,
        "root_cause_analysis": incident.root_cause_analysis,
        "suggested_resolution": incident.suggested_resolution,
        "similar_incidents": [s["title"] for s in similar],
    }


def generate_incident_postmortem(db: Session, incident_id: uuid.UUID) -> str:
    incident = get_incident(db, incident_id)
    if incident is None:
        raise ValueError(f"Incident {incident_id} not found")

    if not incident.root_cause_analysis:
        raise ValueError("Run analysis before generating a postmortem")

    summary = generate_postmortem(
        title=incident.title,
        description=incident.description,
        root_cause_analysis=incident.root_cause_analysis,
        suggested_resolution=incident.suggested_resolution or "",
    )

    incident.postmortem_summary = summary
    incident.status = IncidentStatus.RESOLVED
    db.commit()
    db.refresh(incident)

    return summary
