import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import boto3
import json
import os

logger = logging.getLogger("healthops")
router = APIRouter()

ENDPOINT_NAME = os.getenv("SAGEMAKER_ENDPOINT", "healthops-anomaly-endpoint")


class KPIInput(BaseModel):
    claims_denial_rate: float = Field(..., ge=0.0, le=1.0)
    avg_processing_days: float = Field(..., ge=0.0, le=365.0)
    member_satisfaction: float = Field(..., ge=0.0, le=5.0)
    readmission_rate: float = Field(..., ge=0.0, le=1.0)


@router.post("")
async def detect_anomaly(kpi: KPIInput):
    payload = json.dumps([
        [kpi.claims_denial_rate, kpi.avg_processing_days, kpi.member_satisfaction, kpi.readmission_rate]
    ])
    try:
        runtime = boto3.client("sagemaker-runtime", region_name=os.getenv("AWS_REGION", "us-east-1"))
        response = runtime.invoke_endpoint(
            EndpointName=ENDPOINT_NAME, ContentType="application/json", Body=payload
        )
        result = json.loads(response["Body"].read().decode())
        is_anomaly = result["predictions"][0]["label"] == 1
        return {"is_anomaly": is_anomaly, "score": result["predictions"][0]["score"], "input": kpi.model_dump()}
    except Exception as e:
        logger.error(f"SageMaker call failed: {type(e).__name__}")
        # Fallback: threshold-based detection
        anomaly = kpi.claims_denial_rate > 0.3 or kpi.readmission_rate > 0.25
        return {"is_anomaly": anomaly, "score": kpi.claims_denial_rate, "input": kpi.model_dump(), "mode": "local-fallback"}
