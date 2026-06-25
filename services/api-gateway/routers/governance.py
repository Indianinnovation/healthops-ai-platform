import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import httpx
import os

logger = logging.getLogger("healthops")
router = APIRouter()
OPA_URL = os.getenv("OPA_URL", "http://localhost:8181") + "/v1/data/healthops/phi/deny"


class AccessRequest(BaseModel):
    user: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-zA-Z0-9_.-]+$")
    role: str = Field(..., pattern=r"^(member|clinician|admin)$")
    hipaa_trained: bool
    resource: str = Field(..., pattern=r"^/[a-zA-Z0-9_/.-]+$")


@router.post("/check")
async def check_access(req: AccessRequest):
    opa_input = {
        "input": {
            "user": {"name": req.user, "role": req.role, "hipaa_trained": req.hipaa_trained},
            "request": {"path": req.resource},
        }
    }
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.post(OPA_URL, json=opa_input)
            resp.raise_for_status()
            result = resp.json()
        denied = bool(result.get("result"))
        decision = "DENIED" if denied else "ALLOWED"
        logger.info(f"governance_decision={decision} user={req.user} role={req.role} resource={req.resource}")
        return {"allowed": not denied, "denials": result.get("result", []), "user": req.user}
    except httpx.ConnectError:
        logger.warning("OPA unavailable, using local fallback")
        denied = not req.hipaa_trained and req.resource == "/query"
        msg = "HIPAA training required for PHI queries" if denied else None
        return {"allowed": not denied, "denials": [msg] if denied else [], "user": req.user, "mode": "local-fallback"}
    except Exception as e:
        logger.error(f"Governance check failed: {type(e).__name__}")
        raise HTTPException(status_code=503, detail="Governance service unavailable")
