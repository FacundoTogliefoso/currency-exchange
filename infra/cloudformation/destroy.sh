#!/bin/bash
set -euo pipefail

# === Configurable Variables ===
PROJECT_NAME="currency-exchange"
ENVIRONMENT="dev"
REGION="us-west-1"
STACK_NAME="${PROJECT_NAME}-stack"

# === Delete the CloudFormation Stack ===
echo "Deleting CloudFormation stack: $STACK_NAME..."
aws cloudformation delete-stack \
  --stack-name "$STACK_NAME" \
  --region "$REGION"

echo "Waiting for stack deletion to complete..."
aws cloudformation wait stack-delete-complete \
  --stack-name "$STACK_NAME" \
  --region "$REGION"

echo "Stack deletion complete."
