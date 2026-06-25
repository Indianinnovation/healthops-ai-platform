import numpy as np
import os

# Use local numpy-based similarity for demo (FAISS optional dependency)
DOCS_DIR = os.path.join(os.path.dirname(__file__), "data")

# Pre-loaded healthcare documents for demo
HEALTHCARE_DOCS = [
    "Prior authorization is required for MRI, CT scans, and PET scans. Members must obtain approval from their PCP before scheduling imaging services.",
    "Claims denial rate above 15% triggers an automatic quality review. Average processing time SLA is 30 calendar days for standard claims.",
    "HIPAA requires covered entities to implement safeguards for PHI. Access to member health records requires role-based authorization and audit logging.",
    "Preventive care visits are covered at 100% with no copay for in-network providers. Annual wellness exams include standard lab panels.",
    "Mental health services require prior auth after 20 sessions per calendar year. Telehealth visits are covered at the same rate as in-person.",
    "Emergency department visits have a $250 copay waived if admitted. Urgent care copay is $50 for in-network facilities.",
]

# Simple TF-IDF-like embedding for demo (production would use Bedrock Titan Embeddings)
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
