from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import health_query, anomaly, governance

app = FastAPI(title="HealthOps AI Platform", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(health_query.router, prefix="/query", tags=["RAG"])
app.include_router(anomaly.router, prefix="/anomaly", tags=["Anomaly"])
app.include_router(governance.router, prefix="/governance", tags=["Governance"])


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "healthops-api"}
