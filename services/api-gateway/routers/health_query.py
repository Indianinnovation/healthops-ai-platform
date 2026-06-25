from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import boto3
import json
import numpy as np
import os

router = APIRouter()

MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")

# In-memory healthcare documents for RAG
HEALTHCARE_DOCS = [
    "Prior authorization is required for MRI, CT scans, and PET scans. Members must obtain approval from their PCP before scheduling imaging services.",
    "Claims denial rate above 15% triggers an automatic quality review. Average processing time SLA is 30 calendar days for standard claims.",
    "HIPAA requires covered entities to implement safeguards for PHI. Access to member health records requires role-based authorization and audit logging.",
    "Preventive care visits are covered at 100% with no copay for in-network providers. Annual wellness exams include standard lab panels.",
    "Mental health services require prior auth after 20 sessions per calendar year. Telehealth visits are covered at the same rate as in-person.",
    "Emergency department visits have a $250 copay waived if admitted. Urgent care copay is $50 for in-network facilities.",
]


def _embed(text: str) -> np.ndarray:
    words = text.lower().split()
    vocab = list(set(w for doc in HEALTHCARE_DOCS for w in doc.lower().split()))
    vec = np.array([words.count(w) for w in vocab], dtype=np.float32)
    norm = np.linalg.norm(vec)
    return vec / norm if norm > 0 else vec


_doc_embeddings = np.array([_embed(doc) for doc in HEALTHCARE_DOCS])


def search_documents(query: str, top_k: int = 3) -> list[str]:
    query_vec = _embed(query)
    scores = _doc_embeddings @ query_vec
    top_indices = np.argsort(scores)[-top_k:][::-1]
    return [HEALTHCARE_DOCS[i] for i in top_indices]


class QueryRequest(BaseModel):
    question: str
    user_role: str = "member"


class QueryResponse(BaseModel):
    answer: str
    sources: list[str]
    model: str


@router.post("", response_model=QueryResponse)
async def healthcare_query(req: QueryRequest):
    relevant_docs = search_documents(req.question, top_k=3)
    context = "\n\n".join(relevant_docs)

    prompt = f"""You are a healthcare operations assistant. Answer based ONLY on the provided context.
If the answer isn't in the context, say "I don't have information on that topic."

Context:
{context}

Question: {req.question}
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
    except Exception:
        # Fallback: return the most relevant document directly
        answer = relevant_docs[0]

    return QueryResponse(answer=answer, sources=relevant_docs[:2], model=MODEL_ID)
