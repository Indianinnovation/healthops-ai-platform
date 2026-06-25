"""HIPAA-aware healthcare document loader with comprehensive PII/PHI masking."""
import re
import logging

logger = logging.getLogger("healthops")

# PHI patterns to mask before indexing
PHI_PATTERNS = [
    (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN_REDACTED]'),           # SSN
    (r'\b\d{9,10}\b', '[MRN_REDACTED]'),                      # MRN
    (r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', '[NAME_REDACTED]'),     # Names
    (r'\b\d{1,5}\s\w+\s(St|Ave|Blvd|Rd|Dr|Ln)\b', '[ADDRESS_REDACTED]'),  # Addresses
    (r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE_REDACTED]'),  # Phone numbers
    (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REDACTED]'),  # Email
    (r'\b\d{2}/\d{2}/\d{4}\b', '[DOB_REDACTED]'),            # Date of birth
]


def mask_phi(text: str) -> str:
    """Mask all PHI patterns before indexing. Logs redaction counts."""
    total_redactions = 0
    for pattern, replacement in PHI_PATTERNS:
        matches = len(re.findall(pattern, text))
        if matches:
            text = re.sub(pattern, replacement, text)
            total_redactions += matches

    if total_redactions > 0:
        logger.info(f"Masked {total_redactions} PHI instances")

    return text


def load_healthcare_docs(raw_docs: list[str]) -> list[str]:
    """Load and sanitize healthcare documents for vector indexing."""
    sanitized = []
    for doc in raw_docs:
        if not doc or not doc.strip():
            continue
        if len(doc) > 1_000_000:  # Skip oversized docs
            logger.warning("Skipping oversized document during load")
            continue
        sanitized.append(mask_phi(doc))
    return sanitized
