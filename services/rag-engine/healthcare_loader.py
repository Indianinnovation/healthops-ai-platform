"""HIPAA-aware healthcare document loader with PII masking."""
import re


def mask_phi(text: str) -> str:
    """Mask common PHI patterns before indexing."""
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', text)
    text = re.sub(r'\b\d{10}\b', '[MRN]', text)
    text = re.sub(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', '[NAME]', text)
    return text


def load_healthcare_docs(raw_docs: list[str]) -> list[str]:
    """Load and sanitize healthcare documents for vector indexing."""
    return [mask_phi(doc) for doc in raw_docs if doc.strip()]
