# Deployment Guide

## Prerequisites
- AWS CLI configured with appropriate IAM credentials
- Docker installed locally
- Python 3.11+

## Deploy Full Stack

```bash
cd infrastructure/scripts
chmod +x provision.sh teardown.sh validate.sh
./provision.sh
./validate.sh
```

## Local Development

```bash
docker-compose up --build
# API: http://localhost:8000
# OPA: http://localhost:8181
```

## Test Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Healthcare query (Bedrock RAG)
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are prior auth requirements for MRI?"}'

# Anomaly detection
curl -X POST http://localhost:8000/anomaly \
  -H "Content-Type: application/json" \
  -d '{"claims_denial_rate": 0.45, "avg_processing_days": 35, "member_satisfaction": 2.1, "readmission_rate": 0.35}'

# Governance check
curl -X POST http://localhost:8000/governance/check \
  -H "Content-Type: application/json" \
  -d '{"user": "john", "role": "member", "hipaa_trained": false, "resource": "/query"}'
```
