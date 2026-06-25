import logging
import time
import uuid
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from routers import health_query, anomaly, governance

# Structured audit logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("healthops")

app = FastAPI(
    title="HealthOps AI Platform",
    version="1.0.0",
    docs_url="/docs" if __import__("os").getenv("ENVIRONMENT") != "production" else None,
    redoc_url=None,
)

# Security: Restrict CORS to known origins
ALLOWED_ORIGINS = __import__("os").getenv("ALLOWED_ORIGINS", "http://localhost:8501,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
    allow_credentials=False,
)

# Security: Trusted hosts to prevent host header injection
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "*.amazonaws.com", "*"])


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Add security headers and audit logging to every response."""
    request_id = str(uuid.uuid4())
    start_time = time.time()

    response: Response = await call_next(request)

    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Request-ID"] = request_id

    # Audit log
    duration = time.time() - start_time
    logger.info(
        f"request_id={request_id} method={request.method} path={request.url.path} "
        f"status={response.status_code} duration={duration:.3f}s "
        f"client={request.client.host if request.client else 'unknown'}"
    )

    return response


app.include_router(health_query.router, prefix="/query", tags=["RAG"])
app.include_router(anomaly.router, prefix="/anomaly", tags=["Anomaly"])
app.include_router(governance.router, prefix="/governance", tags=["Governance"])


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "healthops-api"}
