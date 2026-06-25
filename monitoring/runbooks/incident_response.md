# Incident Response Runbook

## Severity Levels

| Level | Description | Response Time |
|-------|-------------|---------------|
| SEV1 | Complete service outage | 15 min |
| SEV2 | Degraded performance | 30 min |
| SEV3 | Non-critical feature failure | 2 hours |

## Common Scenarios

### High Error Rate (>5%)
1. Check CloudWatch logs: `/ecs/healthops-api`
2. Verify Bedrock endpoint health: `aws bedrock-runtime invoke-model --model-id anthropic.claude-3-haiku-20240307-v1:0 --body '{}' /dev/null`
3. Check ECS task status: `aws ecs describe-services --cluster healthops-cluster --services healthops-api-service`
4. Scale if needed: `aws ecs update-service --desired-count 4 ...`

### SageMaker Endpoint Down
1. Check endpoint: `aws sagemaker describe-endpoint --endpoint-name healthops-anomaly-endpoint`
2. Fallback: API uses local threshold detection automatically
3. Redeploy if needed: `aws sagemaker create-endpoint-config ...`

### OPA Policy Blocking Legitimate Requests
1. Check OPA logs: `docker logs opa`
2. Test policy: `curl localhost:8181/v1/data/healthops/phi/deny -d '{"input": {...}}'`
3. Update policy in `services/governance/policies/` and restart OPA
