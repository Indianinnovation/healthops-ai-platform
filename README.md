# 🏥 HealthOps AI Platform

**Cloud-Native Healthcare AI Operations Platform on AWS**

> Intelligent, secure, cloud-native healthcare AI platform demonstrating AWS infrastructure provisioning, GenAI on Bedrock, containerized microservices, SageMaker ML, OPA governance, and SRE-aligned operations — built for regulated healthcare environments.

[![CI/CD](https://github.com/yourusername/healthops-ai-platform/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/yourusername/healthops-ai-platform/actions)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://python.org)
[![AWS](https://img.shields.io/badge/AWS-Cloud--Native-orange.svg)](https://aws.amazon.com)
[![HIPAA](https://img.shields.io/badge/Compliance-HIPAA--Aware-green.svg)](#security--compliance)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Features](#features)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Component Deep Dive](#component-deep-dive)
- [API Reference](#api-reference)
- [Deployment](#deployment)
- [Security & Compliance](#security--compliance)
- [Cost Analysis](#cost-analysis)
- [Demo Scenarios](#demo-scenarios)
- [Contributing](#contributing)

---

## Overview

HealthOps AI Platform is a production-grade, cloud-native healthcare operations platform built entirely on AWS. It demonstrates end-to-end capabilities across infrastructure provisioning, generative AI, machine learning, containerized microservices, policy-as-code governance, and SRE observability.

### Business Problem

Healthcare organizations need intelligent platforms that can:
- Answer complex coverage and policy questions instantly using AI
- Detect anomalies in operational KPIs (claims denial rates, processing times)
- Enforce HIPAA compliance programmatically at every access point
- Scale elastically while maintaining security posture

### Solution

This platform addresses all four needs through a modular, event-driven architecture deployed on AWS managed services, designed from day one for HIPAA-regulated workloads.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         HealthOps AI Platform                                │
│                         AWS Cloud Architecture                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌────────────────────────────────┐  │
│  │  Streamlit  │    │  API GW /   │    │      Amazon Bedrock            │  │
│  │  Frontend   │───▶│  FastAPI    │───▶│   Claude 3 Haiku (RAG)        │  │
│  │  (Port 8501)│    │  (Port 8000)│    │   FAISS Vector Search         │  │
│  └─────────────┘    └──────┬──────┘    └────────────────────────────────┘  │
│                            │                                                │
│                     ┌──────┼──────────────────────┐                         │
│                     │      │                      │                         │
│              ┌──────▼──┐  ┌▼──────────┐  ┌───────▼──────────────────────┐  │
│              │   OPA   │  │ SageMaker │  │   AWS Lambda                 │  │
│              │  Policy │  │ Anomaly   │  │   Router + Monitor           │  │
│              │  Engine │  │ Detection │  │   (Serverless)               │  │
│              └─────────┘  └───────────┘  └──────────────────────────────┘  │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  ECS Fargate │ S3 Data Lake │ CloudWatch │ IAM │ VPC │ CloudFormation│  │
│  │                    AWS Foundation Layer                                │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
User Question → Streamlit UI → FastAPI Gateway → OPA Policy Check
    → FAISS Vector Search (retrieve relevant docs)
    → Amazon Bedrock Claude 3 Haiku (generate answer)
    → Response with sources → UI Display
```

```
Health KPIs → FastAPI Gateway → SageMaker Endpoint (Isolation Forest)
    → Anomaly Score + Label → Alert if anomalous
```

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Streamlit | Interactive demo UI with tabs |
| **API** | FastAPI + Uvicorn | High-performance async REST API |
| **GenAI** | Amazon Bedrock (Claude 3 Haiku) | Healthcare document Q&A |
| **Vector Search** | FAISS + NumPy | Document retrieval for RAG pipeline |
| **ML** | Amazon SageMaker (Isolation Forest) | Health KPI anomaly detection |
| **Governance** | Open Policy Agent (OPA) | HIPAA policy enforcement |
| **Compute** | ECS Fargate | Serverless container orchestration |
| **Serverless** | AWS Lambda | Event-driven routing & monitoring |
| **Storage** | Amazon S3 | Healthcare document & model artifact lake |
| **IaC** | CloudFormation + Terraform | Dual infrastructure-as-code |
| **Networking** | VPC, Subnets, NAT, Security Groups | Network isolation & security |
| **Identity** | IAM Roles & Policies | Least-privilege access control |
| **Observability** | CloudWatch Dashboards + Alarms | SRE metrics & alerting |
| **CI/CD** | GitHub Actions | Automated test, build, deploy |
| **Containers** | Docker + Docker Compose | Local dev & production deployment |

---

## Features

### 🤖 GenAI Healthcare Q&A (Bedrock RAG)
- Retrieval-Augmented Generation using FAISS vector search
- Grounded answers from healthcare policy documents
- Automatic fallback to document retrieval if Bedrock is unavailable
- Prompt injection protection via OPA policies

### 📊 Health KPI Anomaly Detection (SageMaker)
- Isolation Forest model trained on synthetic healthcare KPIs
- Real-time inference endpoint for claims denial rate, processing time, satisfaction, readmission
- Local threshold-based fallback for offline demos
- SageMaker training pipeline with data prep automation

### 🔒 HIPAA Governance (OPA)
- Policy-as-code enforcement for PHI access control
- HIPAA training verification before data access
- Role-based authorization (admin, clinician, member)
- Bedrock usage rate limiting and prompt injection blocking

### 🏗️ Infrastructure as Code
- CloudFormation stacks: VPC, ECS, SageMaker, Bedrock/S3/IAM
- Terraform modules: VPC, S3 with encryption
- One-command provisioning and teardown scripts
- Infrastructure validation automation

### 📈 SRE Observability
- CloudWatch dashboards for API, Bedrock, SageMaker, and governance metrics
- Alarm definitions for error rate, latency, anomaly spikes
- Incident response and deployment runbooks
- Custom health check Lambda with metric publishing

---

## Quick Start

### Prerequisites

- Docker Desktop installed and running
- (Optional) AWS CLI configured for cloud deployment
- (Optional) Python 3.11+ for local development without Docker

### Run Locally (Docker)

```bash
# Clone the repository
git clone https://github.com/yourusername/healthops-ai-platform.git
cd healthops-ai-platform

# Start all services
docker-compose up --build

# Access:
# - Streamlit UI:  http://localhost:8501
# - FastAPI Docs:  http://localhost:8000/docs
# - OPA Console:   http://localhost:8181
```

### Run Without Docker

```bash
cd services/api-gateway
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Deploy to AWS

```bash
cd infrastructure/scripts
chmod +x provision.sh teardown.sh validate.sh
./provision.sh      # Creates VPC, ECS, S3, SageMaker, IAM
./validate.sh       # Confirms all stacks are healthy
./teardown.sh       # Clean removal of all resources
```

---

## Project Structure

```
healthops-ai-platform/
│
├── README.md                          ← You are here
├── ARCHITECTURE.md                    ← Design decisions & tradeoffs
├── docker-compose.yml                 ← Local multi-service orchestration
│
├── frontend/                          ← STREAMLIT UI
│   ├── app.py                         ← 3-tab demo interface
│   ├── Dockerfile
│   └── requirements.txt
│
├── infrastructure/                    ← AWS INFRASTRUCTURE AS CODE
│   ├── cloudformation/
│   │   ├── vpc-stack.yaml             ← VPC, subnets, NAT, security groups
│   │   ├── ecs-cluster.yaml           ← ECS Fargate cluster + task definitions
│   │   ├── sagemaker-stack.yaml       ← SageMaker notebook + IAM roles
│   │   └── bedrock-stack.yaml         ← S3 buckets + Bedrock IAM + data lake
│   ├── terraform/
│   │   ├── main.tf                    ← VPC module + S3 with encryption
│   │   ├── variables.tf               ← Configurable parameters
│   │   └── outputs.tf                 ← Stack outputs
│   └── scripts/
│       ├── provision.sh               ← One-command deploy all stacks
│       ├── teardown.sh                ← One-command destroy all stacks
│       └── validate.sh                ← Health check all stacks
│
├── services/                          ← MICROSERVICES
│   ├── api-gateway/                   ← FastAPI REST API
│   │   ├── main.py                    ← App entry + router registration
│   │   ├── routers/
│   │   │   ├── health_query.py        ← Bedrock RAG endpoint
│   │   │   ├── anomaly.py             ← SageMaker inference endpoint
│   │   │   └── governance.py          ← OPA policy check endpoint
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── rag-engine/                    ← BEDROCK RAG PIPELINE
│   │   ├── bedrock_client.py          ← Bedrock invocation + prompt construction
│   │   ├── faiss_indexer.py           ← Vector similarity search
│   │   ├── document_ingestion.py      ← S3 document loading
│   │   ├── healthcare_loader.py       ← PHI masking + sanitization
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── anomaly-detector/              ← SAGEMAKER ML SERVICE
│   │   ├── train.py                   ← Isolation Forest training job
│   │   ├── inference.py               ← SageMaker endpoint handler
│   │   ├── data_prep.py               ← Synthetic KPI data generation
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── governance/                    ← OPA POLICY ENGINE
│       ├── policies/
│       │   ├── healthcare_phi.rego    ← PHI access + HIPAA enforcement
│       │   ├── api_authz.rego         ← Role-based API authorization
│       │   └── bedrock_limits.rego    ← LLM usage limits + injection protection
│       └── opa_client.py              ← Python OPA client
│
├── lambda/                            ← SERVERLESS FUNCTIONS
│   ├── router/
│   │   ├── handler.py                 ← API Gateway → Bedrock routing
│   │   └── template.yaml             ← SAM deployment template
│   └── monitor/
│       ├── health_check.py            ← CloudWatch metric publisher
│       └── alerting.py                ← SNS alert dispatcher
│
├── monitoring/                        ← SRE OBSERVABILITY
│   ├── cloudwatch/
│   │   ├── dashboards.json            ← CloudWatch dashboard definition
│   │   └── alarms.json                ← SRE alarm configurations
│   └── runbooks/
│       ├── incident_response.md       ← Severity levels + response procedures
│       └── deployment_guide.md        ← Step-by-step deployment instructions
│
├── tests/                             ← TEST SUITE
│   ├── unit/
│   │   └── test_api.py                ← API endpoint unit tests
│   ├── integration/
│   │   └── test_governance.py         ← End-to-end governance flow tests
│   └── load/
│       └── load_test.py               ← Concurrent load testing
│
└── .github/
    └── workflows/
        └── ci-cd.yml                  ← GitHub Actions: test → build → deploy
```

---

## Component Deep Dive

### 1. Bedrock RAG Engine

The RAG (Retrieval-Augmented Generation) pipeline ensures the AI only answers from verified healthcare documents — never hallucinating policy information.

**Flow:**
1. User submits a healthcare question
2. Question is embedded using TF-IDF vectorization
3. FAISS performs cosine similarity search against indexed healthcare documents
4. Top-3 relevant documents are retrieved
5. A structured prompt with context is sent to Bedrock Claude 3 Haiku
6. The model generates a grounded answer constrained to the context

**Key Design Decisions:**
- FAISS for fast, in-memory vector search (no external database dependency)
- Claude 3 Haiku for cost-efficiency ($0.00025/1K input tokens)
- Fallback to direct document retrieval if Bedrock is unavailable
- PHI masking applied during document ingestion (SSN, MRN, names)

### 2. SageMaker Anomaly Detection

Detects operational anomalies in healthcare KPIs using an Isolation Forest model.

**KPIs Monitored:**
| Metric | Normal Range | Anomaly Threshold |
|--------|-------------|-------------------|
| Claims Denial Rate | 9-15% | >30% |
| Avg Processing Days | 11-17 | >30 |
| Member Satisfaction | 3.9-4.5 | <2.5 |
| Readmission Rate | 8-12% | >25% |

**Training Pipeline:**
1. `data_prep.py` generates synthetic KPI data and uploads to S3
2. `train.py` trains Isolation Forest with 5% contamination factor
3. Model artifact saved to S3 / SageMaker model registry
4. `inference.py` serves predictions via SageMaker real-time endpoint

### 3. OPA Governance Engine

Three policy layers enforce healthcare compliance:

| Policy | File | Purpose |
|--------|------|---------|
| PHI Access | `healthcare_phi.rego` | Blocks PHI access without HIPAA training |
| API Authorization | `api_authz.rego` | Role-based endpoint access |
| Bedrock Limits | `bedrock_limits.rego` | Rate limiting + prompt injection blocking |

**Example Policy Enforcement:**
```
Input: User "john" (role: member, hipaa_trained: false) → /query
Result: ❌ DENIED — "HIPAA training required for PHI queries"

Input: User "jane" (role: clinician, hipaa_trained: true) → /query
Result: ✅ ALLOWED
```

### 4. Infrastructure as Code

**CloudFormation (4 stacks):**
- `vpc-stack.yaml` — VPC with 2 public + 2 private subnets, NAT Gateway, Security Groups
- `ecs-cluster.yaml` — Fargate cluster, task definitions, IAM roles (EKS-migration-ready)
- `bedrock-stack.yaml` — S3 data lake with encryption, Bedrock IAM roles
- `sagemaker-stack.yaml` — SageMaker notebook in private subnet, execution role

**Terraform:**
- VPC module with HIPAA compliance tags
- S3 bucket with AES-256 encryption + public access block
- Remote state in S3 backend

---

## API Reference

### `GET /health`
Health check endpoint.
```json
{"status": "healthy", "service": "healthops-api"}
```

### `POST /query`
Healthcare document Q&A via Bedrock RAG.
```json
// Request
{"question": "What are prior auth requirements for MRI?", "user_role": "member"}

// Response
{
  "answer": "Prior authorization is required for MRI, CT scans, and PET scans...",
  "sources": ["Prior authorization is required for MRI..."],
  "model": "anthropic.claude-3-haiku-20240307-v1:0"
}
```

### `POST /anomaly`
Health KPI anomaly detection.
```json
// Request
{
  "claims_denial_rate": 0.45,
  "avg_processing_days": 35,
  "member_satisfaction": 2.1,
  "readmission_rate": 0.35
}

// Response
{"is_anomaly": true, "score": 0.45, "input": {...}}
```

### `POST /governance/check`
HIPAA policy compliance check.
```json
// Request
{"user": "john", "role": "member", "hipaa_trained": false, "resource": "/query"}

// Response
{"allowed": false, "denials": ["HIPAA training required for PHI queries"], "user": "john"}
```

---

## Deployment

### Local Development
```bash
docker-compose up --build
```

### AWS Production Deployment
```bash
# 1. Deploy infrastructure
./infrastructure/scripts/provision.sh

# 2. Build and push Docker image
aws ecr get-login-password | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker build -t healthops-api services/api-gateway
docker tag healthops-api:latest <account>.dkr.ecr.us-east-1.amazonaws.com/healthops-api:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/healthops-api:latest

# 3. Deploy SageMaker model
cd services/anomaly-detector
python data_prep.py
python train.py

# 4. Validate
./infrastructure/scripts/validate.sh
```

### CI/CD Pipeline (GitHub Actions)
- **Push to PR** → Run unit tests
- **Merge to main** → Build Docker → Push to ECR → Deploy to ECS

---

## Security & Compliance

| Control | Implementation |
|---------|---------------|
| Network Isolation | Private subnets for data services, NAT for outbound only |
| Encryption at Rest | S3 AES-256, SageMaker encrypted volumes |
| Encryption in Transit | TLS for all API communication |
| Access Control | IAM least-privilege roles per service |
| PHI Protection | OPA policy-as-code, HIPAA training verification |
| Data Masking | SSN, MRN, name masking during document ingestion |
| Audit Trail | CloudWatch logs for all API access, OPA decision logs |
| Prompt Security | OPA blocks prompt injection patterns |
| Container Security | Non-root user, minimal base images, no secrets in images |

---

## Cost Analysis

### Demo/POC Mode (deploy only during demos)

| Service | Cost per Demo Session | Notes |
|---------|----------------------|-------|
| ECS Fargate | ~$0.50/hour | 2 tasks × 0.5 vCPU |
| Bedrock (Haiku) | ~$0.01/demo | ~40 queries × $0.00025 |
| SageMaker Endpoint | ~$0.12/hour | ml.m5.large (stop after demo) |
| NAT Gateway | ~$0.045/hour | While stack is up |
| S3 + CloudWatch | <$0.01 | Minimal usage |
| **Total per demo** | **$5–15** | **2-3 hour session** |

### Always-On Development

| Service | Monthly | Notes |
|---------|---------|-------|
| Full stack 24/7 | ~$170/month | Not recommended for POC |
| **Recommended: Local Docker** | **$0** | Use `docker-compose up` |

### Cost Optimization Strategy
1. Use `docker-compose` for all development (free)
2. Deploy AWS stack only for live demos → `provision.sh`
3. Tear down immediately after → `teardown.sh`
4. Anomaly detector has local fallback (no SageMaker needed locally)
5. Bedrock Haiku is cheapest model (~$0.001/query)

---

## Demo Scenarios

### Scenario 1: Infrastructure Provisioning
```bash
./infrastructure/scripts/provision.sh
# Creates: VPC → S3 → IAM → SageMaker → ECS in ~3 minutes
```

### Scenario 2: Healthcare Q&A
Open http://localhost:8501 → "Healthcare Q&A" tab
- Ask: "What are prior auth requirements for MRI?"
- Ask: "What is the copay for emergency visits?"
- Ask: "How are mental health services covered?"

### Scenario 3: Anomaly Detection
Open http://localhost:8501 → "Anomaly Detection" tab
- Slide "Claims Denial Rate" to 0.45 → 🚨 Anomaly detected
- Reset to 0.12 → ✅ Normal

### Scenario 4: Governance Enforcement
Open http://localhost:8501 → "Governance Check" tab
- Uncheck "HIPAA Trained" → 🚫 Access Denied
- Check "HIPAA Trained" → ✅ Access Granted

### Scenario 5: Observability
- CloudWatch Dashboard shows real-time API metrics
- Alarms trigger on >5% error rate or >5s p99 latency
- Runbooks provide step-by-step incident resolution

---

## Running Tests

```bash
# Unit tests
pip install pytest httpx
pytest tests/unit -v

# Integration tests (requires docker-compose running)
pytest tests/integration -v

# Load test
python tests/load/load_test.py
```

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m "Add feature"`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Author

**Dilip Tandekar**
Cloud & AI Solutions Architect

---

*Built with ❤️ on AWS — demonstrating cloud-native healthcare AI at scale.*
