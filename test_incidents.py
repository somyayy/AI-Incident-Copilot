"""
API-level tests for incident CRUD endpoints.

LLM and embedding calls are monkeypatched so tests run offline without an
OpenAI API key.
"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.db import Base, get_db
from app.main import app

# --- Test database setup (in-memory SQLite) ---
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@patch("app.services.incident_service.get_vector_store")
def test_create_incident(mock_store, client):
    mock_store.return_value.add_incident.return_value = None

    response = client.post(
        "/incidents",
        json={
            "title": "Database connection pool exhausted",
            "description": "API pods started returning 500s under load.",
            "logs": "ERROR: too many connections",
            "severity": "HIGH",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Database connection pool exhausted"
    assert body["status"] == "OPEN"


@patch("app.services.incident_service.get_vector_store")
def test_list_incidents_empty(mock_store, client):
    response = client.get("/incidents")
    assert response.status_code == 200
    assert response.json() == []


@patch("app.services.incident_service.generate_rca_and_resolution")
@patch("app.services.incident_service.get_vector_store")
def test_analyze_incident(mock_store, mock_generate, client):
    mock_store.return_value.add_incident.return_value = None
    mock_store.return_value.search.return_value = []
    mock_generate.return_value = {
        "root_cause_analysis": "Connection pool size too small for peak load.",
        "suggested_resolution": "Increase max pool size and add circuit breaker.",
    }

    create_resp = client.post(
        "/incidents",
        json={
            "title": "Connection pool exhausted",
            "description": "Pods returning 500s.",
        },
    )
    incident_id = create_resp.json()["id"]

    analyze_resp = client.post(f"/incidents/{incident_id}/analyze")
    assert analyze_resp.status_code == 200
    body = analyze_resp.json()
    assert "Connection pool size" in body["root_cause_analysis"]


def test_get_nonexistent_incident(client):
    response = client.get("/incidents/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
