#!/bin/bash
set -e

STACK_PREFIX="healthops"
REGION="${AWS_REGION:-us-east-1}"
CFN_DIR="$(dirname "$0")/../cloudformation"

echo "🏥 HealthOps AI Platform — Provisioning AWS Infrastructure"
echo "Region: $REGION"
echo "==========================================================="

# 1. VPC
echo "🔧 [1/4] Deploying VPC stack..."
aws cloudformation deploy \
  --template-file "$CFN_DIR/vpc-stack.yaml" \
  --stack-name "${STACK_PREFIX}-vpc" \
  --parameter-overrides EnvironmentName=$STACK_PREFIX \
  --region "$REGION" \
  --capabilities CAPABILITY_NAMED_IAM \
  --no-fail-on-empty-changeset

# 2. Bedrock + S3
echo "🔧 [2/4] Deploying Bedrock & S3 stack..."
aws cloudformation deploy \
  --template-file "$CFN_DIR/bedrock-stack.yaml" \
  --stack-name "${STACK_PREFIX}-bedrock" \
  --parameter-overrides EnvironmentName=$STACK_PREFIX \
  --region "$REGION" \
  --capabilities CAPABILITY_NAMED_IAM \
  --no-fail-on-empty-changeset

# 3. SageMaker
echo "🔧 [3/4] Deploying SageMaker stack..."
aws cloudformation deploy \
  --template-file "$CFN_DIR/sagemaker-stack.yaml" \
  --stack-name "${STACK_PREFIX}-sagemaker" \
  --parameter-overrides EnvironmentName=$STACK_PREFIX \
  --region "$REGION" \
  --capabilities CAPABILITY_NAMED_IAM \
  --no-fail-on-empty-changeset

# 4. ECS Cluster
echo "🔧 [4/4] Deploying ECS cluster..."
aws cloudformation deploy \
  --template-file "$CFN_DIR/ecs-cluster.yaml" \
  --stack-name "${STACK_PREFIX}-ecs" \
  --parameter-overrides EnvironmentName=$STACK_PREFIX \
  --region "$REGION" \
  --capabilities CAPABILITY_NAMED_IAM \
  --no-fail-on-empty-changeset

echo "==========================================================="
echo "✅ All stacks deployed successfully!"
echo "Run './validate.sh' to verify resources."
