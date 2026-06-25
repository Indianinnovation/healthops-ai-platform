import boto3
import os

s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION", "us-east-1"))
BUCKET = os.getenv("DATA_BUCKET", "healthops-data")


def ingest_from_s3(prefix: str = "documents/") -> list[str]:
    """Download healthcare docs from S3 for indexing."""
    response = s3.list_objects_v2(Bucket=BUCKET, Prefix=prefix)
    documents = []
    for obj in response.get("Contents", []):
        body = s3.get_object(Bucket=BUCKET, Key=obj["Key"])["Body"].read().decode("utf-8")
        documents.append(body)
    return documents
