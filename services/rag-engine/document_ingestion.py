"""Secure S3 document ingestion with input validation."""
import boto3
import logging
import os
import re

logger = logging.getLogger("healthops")

s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION", "us-east-1"))
BUCKET = os.getenv("DATA_BUCKET", "healthops-data")
MAX_DOCUMENT_SIZE = 1_000_000  # 1MB per document
ALLOWED_EXTENSIONS = {".txt", ".md", ".json"}


def _validate_key(key: str) -> bool:
    """Prevent path traversal and validate S3 key."""
    if ".." in key or key.startswith("/"):
        return False
    ext = os.path.splitext(key)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def ingest_from_s3(prefix: str = "documents/") -> list[str]:
    """Download healthcare docs from S3 for indexing."""
    # Validate prefix to prevent injection
    if not re.match(r"^[a-zA-Z0-9_/.-]+$", prefix):
        raise ValueError("Invalid prefix")

    response = s3.list_objects_v2(Bucket=BUCKET, Prefix=prefix, MaxKeys=100)
    documents = []

    for obj in response.get("Contents", []):
        key = obj["Key"]
        if not _validate_key(key):
            logger.warning(f"Skipping invalid key: {key}")
            continue
        if obj.get("Size", 0) > MAX_DOCUMENT_SIZE:
            logger.warning(f"Skipping oversized document: {key}")
            continue

        try:
            body = s3.get_object(Bucket=BUCKET, Key=key)["Body"].read().decode("utf-8")
            documents.append(body)
        except Exception as e:
            logger.error(f"Failed to read {key}: {type(e).__name__}")

    logger.info(f"Ingested {len(documents)} documents from s3://{BUCKET}/{prefix}")
    return documents
