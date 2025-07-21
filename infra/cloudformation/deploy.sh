#!/bin/bash
set -euo pipefail

# === Configurable Variables ===
PROJECT_NAME="currency-exchange"
ENVIRONMENT="dev"
REGION="us-west-1"
STACK_NAME="${PROJECT_NAME}-stack"
TEMPLATE_DIR="infra/cloudformation/templates"
TEMPLATE_BUCKET="${PROJECT_NAME}-${ENVIRONMENT}-templates"
MAIN_TEMPLATE="${TEMPLATE_DIR}/main.yaml"
PARAMS_FILE="cloudformation/parameters/parameters.json"

echo "Region: $REGION"
echo "Stack Name: $STACK_NAME"
echo "Template Directory: $TEMPLATE_DIR"
echo

# === Step 1: Create S3 Bucket (if it doesn't exist) ===
echo "Checking or creating S3 bucket: $TEMPLATE_BUCKET..."
if ! aws s3 ls "s3://${TEMPLATE_BUCKET}" --region "$REGION" >/dev/null 2>&1; then
  aws s3api create-bucket \
    --bucket "$TEMPLATE_BUCKET" \
    --region "$REGION" \
    --create-bucket-configuration LocationConstraint="$REGION"
  echo "Bucket created."
else
  echo "Bucket already exists."
fi

# === Step 2: Upload templates ===
echo
echo "Uploading templates to S3..."
for file in ${TEMPLATE_DIR}/*.yaml; do
  filename=$(basename "$file")
  echo " - Uploading: $filename"
  aws s3 cp "$file" "s3://${TEMPLATE_BUCKET}/${filename}" --region "$REGION"
done
echo "All templates uploaded."

# === Step 3: Deploy stack ===
echo
echo "Deploying main CloudFormation stack: $STACK_NAME..."
aws cloudformation create-stack \
  --stack-name "$STACK_NAME" \
  --template-url "https://s3.${REGION}.amazonaws.com/${TEMPLATE_BUCKET}/${MAIN_TEMPLATE}" \
  --capabilities CAPABILITY_NAMED_IAM \
  --region "$REGION" \
  --parameters file://$PARAMS_FILE

echo
echo "Stack deployed successfully."

# === Step 4: Show Outputs ===
echo
echo "Stack Outputs:"
aws cloudformation describe-stacks \
  --stack-name "$STACK_NAME" \
  --region "$REGION" \
  --query "Stacks[0].Outputs" \
  --output table
