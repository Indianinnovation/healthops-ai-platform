import pytest
from fastapi.testclient import TestClient
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../services/api-gateway"))
from main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_anomaly_detection_local_fallback():
    response = client.post("/anomaly", json={
        "claims_denial_rate": 0.45,
        "avg_processing_days": 35,
        "member_satisfaction": 2.1,
        "readmission_rate": 0.35,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["is_anomaly"] is True


def test_anomaly_detection_normal():
    response = client.post("/anomaly", json={
        "claims_denial_rate": 0.12,
        "avg_processing_days": 14,
        "member_satisfaction": 4.2,
        "readmission_rate": 0.10,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["is_anomaly"] is False


def test_governance_denies_untrained_user():
    response = client.post("/governance/check", json={
        "user": "test_user",
        "role": "member",
        "hipaa_trained": False,
        "resource": "/query",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["allowed"] is False


def test_governance_allows_trained_user():
    response = client.post("/governance/check", json={
        "user": "test_user",
        "role": "member",
        "hipaa_trained": True,
        "resource": "/query",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["allowed"] is True
