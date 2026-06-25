import boto3
import json
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sns = boto3.client("sns", region_name=os.environ.get("AWS_REGION", "us-east-1"))
TOPIC_ARN = os.environ.get("ALERT_TOPIC_ARN", "")


def handler(event, context):
    """Process CloudWatch alarms and send SRE alerts."""
    if not TOPIC_ARN:
        logger.error("ALERT_TOPIC_ARN not configured")
        return {"statusCode": 500, "body": json.dumps({"error": "alerting not configured"})}

    for record in event.get("Records", []):
        try:
            message = json.loads(record["Sns"]["Message"]) if "Sns" in record else record
        except (json.JSONDecodeError, KeyError):
            logger.warning("Skipping malformed record")
            continue

        alarm_name = message.get("AlarmName", "Unknown")[:200]  # Limit length
        state = message.get("NewStateValue", "UNKNOWN")

        if state not in ("ALARM", "OK", "INSUFFICIENT_DATA", "UNKNOWN"):
            continue

        alert = {
            "severity": "HIGH" if "critical" in alarm_name.lower() else "MEDIUM",
            "alarm": alarm_name,
            "state": state,
        }

        sns.publish(
            TopicArn=TOPIC_ARN,
            Subject=f"[HealthOps] {alarm_name[:100]}",
            Message=json.dumps(alert),
        )
        logger.info(f"Alert sent for {alarm_name}")

    return {"statusCode": 200}
