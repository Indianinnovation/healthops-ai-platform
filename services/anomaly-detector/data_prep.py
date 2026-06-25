"""Prepare health KPI data for SageMaker training."""
import pandas as pd
import numpy as np
import boto3
import os

S3_BUCKET = os.getenv("DATA_BUCKET", "healthops-data")
s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION", "us-east-1"))


def generate_and_upload():
    np.random.seed(42)
    df = pd.DataFrame({
        "claims_denial_rate": np.random.normal(0.12, 0.03, 1000),
        "avg_processing_days": np.random.normal(14, 3, 1000),
        "member_satisfaction": np.random.normal(4.2, 0.3, 1000),
        "readmission_rate": np.random.normal(0.10, 0.02, 1000),
    })
    csv_buffer = df.to_csv(index=False)
    s3.put_object(Bucket=S3_BUCKET, Key="training/health_kpis.csv", Body=csv_buffer)
    print(f"Uploaded {len(df)} records to s3://{S3_BUCKET}/training/health_kpis.csv")


if __name__ == "__main__":
    generate_and_upload()
