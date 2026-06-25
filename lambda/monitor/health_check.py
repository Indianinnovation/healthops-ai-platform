import boto3
import json
import os
from datetime import datetime

cloudwatch = boto3.client("cloudwatch", region_name=os.environ.get("AWS_REGION", "us-east-1"))


def handler(event, context):
    """Publish custom health metrics to CloudWatch."""
    metrics = event.get("metrics", {})
    metric_data = []
    for name, value in metrics.items():
        metric_data.append({
            "MetricName": name,
            "Value": float(value),
            "Unit": "None",
            "Timestamp": datetime.utcnow(),
            "Dimensions": [{"Name": "Service", "Value": "healthops-api"}],
        })

    if metric_data:
        cloudwatch.put_metric_data(Namespace="HealthOps", MetricData=metric_data)

    return {"statusCode": 200, "body": json.dumps({"published": len(metric_data)})}
