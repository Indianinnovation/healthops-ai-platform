import json
import boto3
import os

bedrock = boto3.client("bedrock-runtime", region_name=os.environ.get("AWS_REGION", "us-east-1"))
MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")


def handler(event, context):
    """API Gateway → Lambda router → Bedrock for lightweight queries."""
    body = json.loads(event.get("body", "{}"))
    question = body.get("question", "")

    if not question:
        return {"statusCode": 400, "body": json.dumps({"error": "question is required"})}

    prompt = f"You are a healthcare assistant. Answer briefly: {question}"
    bedrock_body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 256,
        "messages": [{"role": "user", "content": prompt}],
    })

    response = bedrock.invoke_model(ModelId=MODEL_ID, Body=bedrock_body, ContentType="application/json")
    result = json.loads(response["body"].read())
    answer = result["content"][0]["text"]

    return {"statusCode": 200, "body": json.dumps({"answer": answer, "model": MODEL_ID})}
