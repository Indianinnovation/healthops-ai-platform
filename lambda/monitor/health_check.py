import boto3
import json
import logging
import os
from datetime import datetime, timezone

logger = logging.getLogger()
logger.setLevel(logging.INFO)

cloudwatch = boto3.client("cloudwatch", region_name=os.environ.get("AWS_REGION", "us-east-1"))

ALLOWED_METRICS = {"RequestLatency", "ErrorRate", "BedrockInvocations", "AnomaliesDetected", "OPADenials"}
MAX_METRIC_VALUE = 1_000_000


def handler(event, context):
    """Publish custom health metrics to CloudWatch."""
    metrics = event.get("metrics", {})
    metric_data = []

    for name, value in metrics.items():
        # Validate metric name against allowlist
        if name not in ALLOWED_METRICS:
            logger.warning(f"Rejected unknown metric: {name}")
            continue

        # Validate numeric value
        try:
            val = float(value)
            if val < 0 or val > MAX_METRIC_VALUE:
                continue
        except (ValueError, TypeError):
            continue

        metric_data.append({
            "MetricName": name,
            "Value": val,
            "Unit": "None",
            "Timestamp": datetime.now(timezone.utc),
            "Dimensions": [{"Name": "Service", "Value": "healthops-api"}],
        })

    if metric_data:
        cloudwatch.put_metric_data(Namespace="HealthOps", MetricData=metric_data)
        logger.info(f"Published {len(metric_data)} metrics")

    return {"statusCode": 200, "body": json.dumps({"published": len(metric_data)})}
