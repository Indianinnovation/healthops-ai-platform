import boto3
import json
import os
from faiss_indexer import search_documents

MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
bedrock = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION", "us-east-1"))


def query_healthcare_docs(question: str) -> dict:
    """RAG pipeline: retrieve relevant docs from FAISS, then generate answer via Bedrock."""
    # 1. Retrieve relevant documents
    relevant_docs = search_documents(question, top_k=3)
    context = "\n\n".join(relevant_docs)

    # 2. Build prompt
    prompt = f"""You are a healthcare operations assistant. Answer based ONLY on the provided context.
If the answer isn't in the context, say "I don't have information on that topic."

Context:
{context}

Question: {question}
Answer:"""

    # 3. Invoke Bedrock
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 512,
        "messages": [{"role": "user", "content": prompt}],
    })

    response = bedrock.invoke_model(ModelId=MODEL_ID, Body=body, ContentType="application/json")
    result = json.loads(response["body"].read())
    answer = result["content"][0]["text"]

    return {"answer": answer, "sources": relevant_docs[:2], "model": MODEL_ID}
