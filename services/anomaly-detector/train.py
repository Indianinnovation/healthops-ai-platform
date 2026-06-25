"""SageMaker training job for Health KPI Anomaly Detection using Isolation Forest."""
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib
import os

MODEL_DIR = os.getenv("SM_MODEL_DIR", "/opt/ml/model")
DATA_DIR = os.getenv("SM_CHANNEL_TRAINING", "/opt/ml/input/data/training")


def generate_synthetic_data(n_normal=1000, n_anomaly=50):
    """Generate synthetic healthcare KPI data."""
    np.random.seed(42)
    normal = pd.DataFrame({
        "claims_denial_rate": np.random.normal(0.12, 0.03, n_normal),
        "avg_processing_days": np.random.normal(14, 3, n_normal),
        "member_satisfaction": np.random.normal(4.2, 0.3, n_normal),
        "readmission_rate": np.random.normal(0.10, 0.02, n_normal),
    })
    anomalies = pd.DataFrame({
        "claims_denial_rate": np.random.normal(0.45, 0.1, n_anomaly),
        "avg_processing_days": np.random.normal(35, 5, n_anomaly),
        "member_satisfaction": np.random.normal(2.1, 0.5, n_anomaly),
        "readmission_rate": np.random.normal(0.35, 0.05, n_anomaly),
    })
    return pd.concat([normal, anomalies], ignore_index=True)


def train():
    # Load or generate data
    data_path = os.path.join(DATA_DIR, "health_kpis.csv")
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
    else:
        df = generate_synthetic_data()

    model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
    model.fit(df)

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, os.path.join(MODEL_DIR, "model.joblib"))
    print(f"Model saved to {MODEL_DIR}")


if __name__ == "__main__":
    train()
