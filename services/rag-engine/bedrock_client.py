"""Bedrock RAG client with input validation and safe error handling."""
import boto3
import json
import logging
import os
import re
from faiss_indexer import search_documents

logger = logging.getLogger("healthops")

MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")

MAX_QUESTION_LENGTH = 500
INJECTION_PATTERNS = [
    r"ignore\s+(previous|above|all)\s+(instructions|prompts)",
    r"system\s*prompt",
    r"you\s+are\s+now",
]


def _validate_input(question: str) -> str:
    """Validate and sanitize user input."""
    question = question.strip()
    if len(question) > MAX_QUESTION_LENGTH:
        raise ValueError("Question too long")
    if not question:
        raise ValueError("Question is empty")
    # Strip HTML tags
    question = re.sub(r"<[^>]+>", "", question)
    # Check for prompt injection
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, question, re.IGNORECASE):
            raise ValueError("Invalid query detected")
    return question


def query_healthcare_docs(question: str) -> dict:
    """RAG pipeline: retrieve relevant docs from FAISS, then generate answer via Bedrock."""
    question = _validate_input(question)

    relevant_docs = search_documents(question, top_k=3)
    context = "\n\n".join(relevant_docs)

    prompt = f"""You are a healthcare operations assistant. Answer based ONLY on the provided context.
If the answer isn't in the context, say "I don't have information on that topic."

Context:
{context}

Question: {question}
Answer:"""

    try:
        bedrock = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION", "us-east-1"))
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 512,
            "messages": [{"role": "user", "content": prompt}],
        })
        response = bedrock.invoke_model(ModelId=MODEL_ID, Body=body, ContentType="application/json")
        result = json.loads(response["body"].read())
        answer = result["content"][0]["text"]
    except Exception as e:
        logger.error(f"Bedrock invocation failed: {type(e).__name__}")
        answer = relevant_docs[0]

    return {"answer": answer, "sources": relevant_docs[:2], "model": MODEL_ID}
