# 🏗️ Architecture Design Document

## HealthOps AI Platform — Technical Architecture

**Author:** Dilip Tandekar
**Version:** 1.0
**Last Updated:** June 2025

---

## 1. Executive Summary

HealthOps AI Platform is a cloud-native healthcare operations system built on AWS. It combines generative AI (Amazon Bedrock), machine learning (SageMaker), policy-as-code governance (OPA), and containerized microservices (ECS Fargate) into a single, cohesive platform designed for HIPAA-regulated healthcare environments.

This document captures the architectural decisions, tradeoffs, and rationale behind each component.

---

## 2. Design Principles

| Principle | Application |
|-----------|-------------|
| **Cloud-Native First** | Built from scratch on AWS managed services — not a lift-and-shift |
| **Security by Default** | Private subnets, encryption, least-privilege IAM, OPA enforcement |
| **Graceful Degradation** | Every external dependency has a local fallback |
| **Infrastructure as Code** | All resources defined in CloudFormation/Terraform — no manual provisioning |
| **Observable** | CloudWatch metrics, alarms, dashboards, and runbooks for every component |
| **Cost-Aware** | Demo-friendly architecture that scales to zero when not in use |

---

## 3. Architecture Decisions

### ADR-001: ECS Fargate over EKS

**Decision:** Use ECS Fargate for container orchestration.

**Context:** The platform needs containerized deployment. Both ECS and EKS are viable.

**Rationale:**
- Lower operational overhead (no cluster management)
- Faster time-to-deploy for a small team
- Native AWS integration with IAM task roles
- Cost-effective for 2-5 services

**EKS Migration Path:**
Every ECS construct maps 1:1 to Kubernetes:
- ECS Task Definition → K8s Pod Spec
- ECS Service → K8s Deployment + Service
- ALB Target Group → K8s Ingress
- Task IAM Role → K8s ServiceAccount with IRSA

**Status:** Accepted

---

### ADR-002: Bedrock RAG over Fine-Tuned Models

**Decision:** Use Amazon Bedrock with RAG (Retrieval-Augmented Generation) rather than fine-tuning a custom model.

**Context:** Healthcare Q&A requires accurate, grounded answers from policy documents.

**Rationale:**
- No model training or hosting cost
- Answers are grounded in retrieved documents (reduces hallucination)
- Bedrock is HIPAA-eligible
- Claude 3 Haiku provides excellent quality at $0.00025/1K tokens
- Documents can be updated without retraining

**Tradeoff:** Slightly higher per-query latency vs. fine-tuned model, but acceptable for this use case.

**Status:** Accepted

---

### ADR-003: FAISS for Vector Search

**Decision:** Use FAISS (Facebook AI Similarity Search) for document retrieval.

**Context:** RAG requires fast similarity search across document embeddings.

**Alternatives Considered:**
- Amazon OpenSearch (managed, but adds cost + complexity)
- Pinecone (SaaS, external dependency)
- FAISS (in-memory, zero infrastructure)

**Rationale:**
- Zero infrastructure cost
- Sub-millisecond search for <10K documents
- No network hop (in-process)
- Sufficient for healthcare policy corpus (~100-1000 documents)

**Tradeoff:** Not suitable for >1M documents. Would migrate to OpenSearch Serverless at scale.

**Status:** Accepted

---

### ADR-004: Isolation Forest for Anomaly Detection

**Decision:** Use Isolation Forest algorithm on SageMaker for KPI anomaly detection.

**Context:** Need to detect anomalous patterns in healthcare operational metrics.

**Rationale:**
- Unsupervised — doesn't require labeled anomaly data
- Fast training (<1 minute on synthetic data)
- Interpretable anomaly scores
- Well-suited for tabular KPI data with 4-10 features
- Native SageMaker support via sklearn container

**Status:** Accepted

---

### ADR-005: OPA for Policy Enforcement

**Decision:** Use Open Policy Agent (OPA) for runtime policy enforcement.

**Context:** HIPAA compliance requires programmatic access control with audit capability.

**Alternatives Considered:**
- AWS IAM alone (limited to AWS service calls)
- Custom middleware (tightly coupled, hard to audit)
- OPA (decoupled, auditable, policy-as-code)

**Rationale:**
- Separates policy from application code
- Policies are version-controlled and auditable
- Supports complex rules (HIPAA training + role + resource)
- Industry standard for cloud-native policy enforcement
- Enables "shift-left" compliance testing

**Status:** Accepted

---

### ADR-006: Dual IaC (CloudFormation + Terraform)

**Decision:** Provide both CloudFormation and Terraform implementations.

**Context:** Enterprise teams use varying IaC tools.

**Rationale:**
- CloudFormation: Deepest AWS integration, native stack management
- Terraform: Multi-cloud awareness, module ecosystem, state management
- Demonstrates proficiency in both (common interview requirement)

**Status:** Accepted

---

## 4. Component Architecture

### 4.1 Network Architecture

```
VPC (10.0.0.0/16)
├── Public Subnet 1 (10.0.1.0/24) — AZ-a
│   └── NAT Gateway, ALB
├── Public Subnet 2 (10.0.2.0/24) — AZ-b
│   └── ALB (multi-AZ)
├── Private Subnet 1 (10.0.10.0/24) — AZ-a
│   └── ECS Tasks, SageMaker Notebook
└── Private Subnet 2 (10.0.11.0/24) — AZ-b
    └── ECS Tasks (multi-AZ)
```

**Security Groups:**
- ALB SG: Inbound 443 from 0.0.0.0/0
- ECS SG: Inbound 8000 from ALB SG only
- No direct internet access to compute resources

### 4.2 IAM Architecture

```
ECS Task Execution Role (pulls images, writes logs)
├── AmazonECSTaskExecutionRolePolicy

ECS Task Role (application permissions)
├── bedrock:InvokeModel (scoped to foundation models)
├── sagemaker:InvokeEndpoint (scoped to healthops-* endpoints)
└── s3:GetObject (scoped to healthops-data-* buckets)

Bedrock Lambda Role
├── bedrock:InvokeModel
├── s3:GetObject (data lake)
└── AWSLambdaBasicExecutionRole

SageMaker Execution Role
├── AmazonSageMakerFullAccess
└── s3:GetObject/PutObject (model artifacts bucket)
```

### 4.3 Data Flow Architecture

```
                    ┌─────────────────────┐
                    │   Healthcare Docs   │
                    │   (S3 Data Lake)    │
                    └─────────┬───────────┘
                              │ Ingest + PHI Mask
                              ▼
                    ┌─────────────────────┐
                    │   FAISS Index       │
                    │   (In-Memory)       │
                    └─────────┬───────────┘
                              │ Similarity Search
                              ▼
┌──────────┐    ┌─────────────────────────────────┐    ┌──────────────┐
│  User    │───▶│   FastAPI Gateway                │───▶│  Bedrock     │
│  Query   │    │   + OPA Policy Check             │    │  Claude 3    │
└──────────┘    └─────────────────────────────────┘    └──────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │   Grounded Answer   │
                    │   + Source Docs     │
                    └─────────────────────┘
```

---

## 5. Scalability Considerations

| Component | Current | Scale Path |
|-----------|---------|-----------|
| API | 2 ECS tasks | Auto-scale on CPU/request count |
| Vector Search | In-memory FAISS | → OpenSearch Serverless |
| Bedrock | On-demand | Provisioned Throughput |
| SageMaker | Single endpoint | Multi-model endpoint + auto-scaling |
| OPA | Sidecar per task | OPA bundle distribution |

---

## 6. Failure Modes & Resilience

| Failure | Impact | Mitigation |
|---------|--------|-----------|
| Bedrock unavailable | No AI-generated answers | Fallback: return best-matching document directly |
| SageMaker endpoint down | No ML predictions | Fallback: threshold-based anomaly detection |
| OPA container down | No policy decisions | Fallback: local policy logic in API |
| S3 unavailable | No document updates | In-memory index continues serving |
| Single AZ failure | Partial traffic loss | Multi-AZ ECS tasks + ALB |

---

## 7. Monitoring & Alerting Strategy

### Golden Signals (SRE)

| Signal | Metric | Alarm Threshold |
|--------|--------|----------------|
| Latency | RequestLatency p99 | > 5000ms for 3 periods |
| Traffic | RequestCount | Informational |
| Errors | ErrorRate | > 5% for 2 periods |
| Saturation | CPU/Memory utilization | > 80% |

### Custom Metrics

| Metric | Source | Purpose |
|--------|--------|---------|
| BedrockInvocations | API | Track GenAI usage |
| BedrockLatency | API | Model response time |
| AnomaliesDetected | SageMaker | Spike detection |
| OPADenials | Governance | Compliance monitoring |
| PHIAccessAttempts | Governance | Security audit |

---

## 8. Security Architecture

### Defense in Depth

```
Layer 1: Network     — VPC, private subnets, security groups
Layer 2: Identity    — IAM roles, least-privilege policies
Layer 3: Application — OPA policy enforcement, input validation
Layer 4: Data        — S3 encryption, PHI masking, audit logs
Layer 5: Runtime     — Container scanning, prompt injection blocking
```

### HIPAA Alignment

| HIPAA Requirement | Implementation |
|-------------------|---------------|
| Access Controls (§164.312(a)) | OPA role-based access + HIPAA training check |
| Audit Controls (§164.312(b)) | CloudWatch logging of all access attempts |
| Integrity Controls (§164.312(c)) | S3 versioning, encryption at rest |
| Transmission Security (§164.312(e)) | TLS for all communications |
| Minimum Necessary (§164.502(b)) | IAM least-privilege, scoped S3 access |

---

## 9. Future Enhancements

| Enhancement | Effort | Value |
|-------------|--------|-------|
| EKS migration | 2 weeks | K8s skills demonstration |
| Bedrock Knowledge Bases | 1 week | Managed RAG pipeline |
| Amazon Kendra | 1 week | Enterprise document search |
| Step Functions orchestration | 3 days | Complex workflow automation |
| AWS Config compliance rules | 2 days | Continuous compliance monitoring |
| Multi-region deployment | 1 week | Disaster recovery |

---

## 10. Technology Comparison

### Why These Choices Over Alternatives

| Choice | Alternative | Why This |
|--------|-------------|----------|
| Bedrock | OpenAI API | HIPAA-eligible, no data leaving AWS |
| FAISS | Pinecone | Zero cost, no external dependency |
| OPA | Custom auth | Industry standard, auditable, declarative |
| ECS | EKS | Lower ops overhead, same containerization benefits |
| CloudFormation | CDK | Direct template control, no abstraction layer |
| Isolation Forest | Deep learning | Simple, fast, interpretable for tabular data |
| FastAPI | Flask | Async, auto-docs, Pydantic validation |
| Streamlit | React | Rapid prototyping, Python-native |
