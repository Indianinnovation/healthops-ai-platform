from fastapi import APIRouter
from pydantic import BaseModel
import boto3, json, os

router = APIRouter()

ENDPOINT_NAME = os.getenv("SAGEMAKER_ENDPOINT", "healthops-anomaly-endpoint")
runtime = boto3.client("sagemaker-runtime", region_name=os.getenv("AWS_REGION", "us-east-1"))


class KPIInput(BaseModel):
    claims_denial_rate: float
    avg_processing_days: float
    member_satisfaction: float
    readmission_rate: float


@router.post("")
async def detect_anomaly(kpi: KPIInput):
    payload = json.dumps([
        [kpi.claims_denial_rate, kpi.avg_processing_days, kpi.member_satisfaction, kpi.readmission_rate]
    ])
    try:
        response = runtime.invoke_endpoint(
            EndpointName=ENDPOINT_NAME, ContentType="application/json", Body=payload
        )
        result = json.loads(response["Body"].read().decode())
        is_anomaly = result["predictions"][0]["label"] == 1
        return {"is_anomaly": is_anomaly, "score": result["predictions"][0]["score"], "input": kpi.model_dump()}
    except Exception:
        # Fallback: simple threshold-based detection for demo
        anomaly = kpi.claims_denial_rate > 0.3 or kpi.readmission_rate > 0.25
        return {"is_anomaly": anomaly, "score": kpi.claims_denial_rate, "input": kpi.model_dump(), "mode": "local-fallback"}
