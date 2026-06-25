"""Integration tests — require docker-compose running."""
import httpx
import pytest

BASE_URL = "http://localhost:8000"


@pytest.mark.asyncio
async def test_full_governance_flow():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # Untrained user should be blocked
        resp = await client.post("/governance/check", json={
            "user": "new_hire", "role": "member", "hipaa_trained": False, "resource": "/query"
        })
        assert resp.status_code == 200
        assert resp.json()["allowed"] is False

        # Trained user should pass
        resp = await client.post("/governance/check", json={
            "user": "trained_user", "role": "clinician", "hipaa_trained": True, "resource": "/query"
        })
        assert resp.status_code == 200
        assert resp.json()["allowed"] is True
