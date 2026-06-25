import boto3
import json
import os

sns = boto3.client("sns", region_name=os.environ.get("AWS_REGION", "us-east-1"))
TOPIC_ARN = os.environ.get("ALERT_TOPIC_ARN", "")


def handler(event, context):
    """Process CloudWatch alarms and send SRE alerts."""
    for record in event.get("Records", []):
        message = json.loads(record["Sns"]["Message"]) if "Sns" in record else record
        alarm_name = message.get("AlarmName", "Unknown")
        state = message.get("NewStateValue", "UNKNOWN")

        alert = {
            "severity": "HIGH" if "critical" in alarm_name.lower() else "MEDIUM",
            "alarm": alarm_name,
            "state": state,
            "runbook": f"https://wiki.internal/runbooks/{alarm_name.lower().replace(' ', '-')}",
        }

        if TOPIC_ARN:
            sns.publish(TopicArn=TOPIC_ARN, Subject=f"[HealthOps] {alarm_name}", Message=json.dumps(alert))

    return {"statusCode": 200}
