import json
import logging
import re
import boto3
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

bedrock = boto3.client("bedrock-runtime", region_name=os.environ.get("AWS_REGION", "us-east-1"))
MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")

MAX_QUESTION_LENGTH = 500
INJECTION_PATTERNS = [
    r"ignore\s+(previous|above|all)\s+(instructions|prompts)",
    r"system\s*prompt",
    r"you\s+are\s+now",
]


def handler(event, context):
    """API Gateway → Lambda router → Bedrock for lightweight queries."""
    try:
        body = json.loads(event.get("body", "{}"))
    except json.JSONDecodeError:
        return {"statusCode": 400, "body": json.dumps({"error": "Invalid JSON"})}

    question = body.get("question", "").strip()

    if not question:
        return {"statusCode": 400, "body": json.dumps({"error": "question is required"})}

    if len(question) > MAX_QUESTION_LENGTH:
        return {"statusCode": 400, "body": json.dumps({"error": "question too long"})}

    # Block prompt injection
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, question, re.IGNORECASE):
            logger.warning(f"Prompt injection blocked in Lambda: {question[:50]}")
            return {"statusCode": 400, "body": json.dumps({"error": "Invalid query"})}

    prompt = f"You are a healthcare assistant. Answer briefly: {question}"
    bedrock_body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 256,
        "messages": [{"role": "user", "content": prompt}],
    })

    try:
        response = bedrock.invoke_model(ModelId=MODEL_ID, Body=bedrock_body, ContentType="application/json")
        result = json.loads(response["body"].read())
        answer = result["content"][0]["text"]
        return {"statusCode": 200, "body": json.dumps({"answer": answer, "model": MODEL_ID})}
    except Exception as e:
        logger.error(f"Bedrock invocation failed: {type(e).__name__}")
        return {"statusCode": 503, "body": json.dumps({"error": "Service temporarily unavailable"})}
