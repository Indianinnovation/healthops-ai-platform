#!/bin/bash
set -e

STACK_PREFIX="healthops"
REGION="${AWS_REGION:-us-east-1}"

echo "🗑️  HealthOps AI Platform — Tearing Down Infrastructure"
echo "Region: $REGION"
echo "==========================================================="

STACKS=("${STACK_PREFIX}-ecs" "${STACK_PREFIX}-sagemaker" "${STACK_PREFIX}-bedrock" "${STACK_PREFIX}-vpc")

for STACK in "${STACKS[@]}"; do
  echo "Deleting $STACK..."
  aws cloudformation delete-stack --stack-name "$STACK" --region "$REGION"
  aws cloudformation wait stack-delete-complete --stack-name "$STACK" --region "$REGION"
  echo "  ✅ $STACK deleted"
done

echo "==========================================================="
echo "✅ All stacks torn down."
