#!/bin/bash
set -e

STACK_PREFIX="healthops"
REGION="${AWS_REGION:-us-east-1}"

echo "🔍 HealthOps AI Platform — Validating Infrastructure"
echo "==========================================================="

STACKS=("${STACK_PREFIX}-vpc" "${STACK_PREFIX}-bedrock" "${STACK_PREFIX}-sagemaker" "${STACK_PREFIX}-ecs")
ALL_GOOD=true

for STACK in "${STACKS[@]}"; do
  STATUS=$(aws cloudformation describe-stacks --stack-name "$STACK" --region "$REGION" \
    --query 'Stacks[0].StackStatus' --output text 2>/dev/null || echo "NOT_FOUND")
  if [ "$STATUS" == "CREATE_COMPLETE" ] || [ "$STATUS" == "UPDATE_COMPLETE" ]; then
    echo "  ✅ $STACK — $STATUS"
  else
    echo "  ❌ $STACK — $STATUS"
    ALL_GOOD=false
  fi
done

echo "==========================================================="
if [ "$ALL_GOOD" = true ]; then
  echo "✅ All infrastructure validated."
else
  echo "⚠️  Some stacks are not healthy. Check above."
  exit 1
fi
