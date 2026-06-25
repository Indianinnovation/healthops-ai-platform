from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx, os

router = APIRouter()
OPA_URL = os.getenv("OPA_URL", "http://localhost:8181/v1/data/healthops/phi/deny")


class AccessRequest(BaseModel):
    user: str
    role: str
    hipaa_trained: bool
    resource: str


@router.post("/check")
async def check_access(req: AccessRequest):
    opa_input = {
        "input": {
            "user": {"name": req.user, "role": req.role, "hipaa_trained": req.hipaa_trained},
            "request": {"path": req.resource},
        }
    }
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(OPA_URL, json=opa_input, timeout=5)
            result = resp.json()
        denied = bool(result.get("result"))
        return {"allowed": not denied, "denials": result.get("result", []), "user": req.user}
    except httpx.ConnectError:
        # OPA not running — use local policy check
        denied = not req.hipaa_trained and req.resource == "/query"
        msg = "HIPAA training required for PHI queries" if denied else None
        return {"allowed": not denied, "denials": [msg] if denied else [], "user": req.user, "mode": "local-fallback"}
