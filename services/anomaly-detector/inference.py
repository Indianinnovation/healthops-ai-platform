"""SageMaker inference handler for anomaly detection endpoint."""
import joblib
import json
import numpy as np
import os


def model_fn(model_dir):
    return joblib.load(os.path.join(model_dir, "model.joblib"))


def input_fn(request_body, content_type="application/json"):
    data = json.loads(request_body)
    return np.array(data)


def predict_fn(input_data, model):
    predictions = model.predict(input_data)
    scores = model.decision_function(input_data)
    # Convert: -1=anomaly(label=1), 1=normal(label=0)
    labels = [1 if p == -1 else 0 for p in predictions]
    return {"predictions": [{"label": l, "score": round(float(s), 4)} for l, s in zip(labels, scores)]}


def output_fn(prediction, accept="application/json"):
    return json.dumps(prediction)
