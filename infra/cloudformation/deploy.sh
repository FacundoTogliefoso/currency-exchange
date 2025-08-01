#!/bin/bash
set -euo pipefail

# === Configurable Variables ===
PROJECT_NAME="currency-exchange"
ENVIRONMENT="dev"
REGION="us-west-1"
STACK_NAME="${PROJECT_NAME}-stack"
TEMPLATE_DIR="infra/cloudformation/templates"
TEMPLATE_BUCKET="${PROJECT_NAME}-${ENVIRONMENT}-templates-facu"
MAIN_TEMPLATE="${TEMPLATE_DIR}/main.yaml"
PACKAGED_TEMPLATE="infra/cloudformation/packaged-main.yaml"
PARAMS_FILE="infra/cloudformation/parameters/parameters.json"

# === Step 1: Create S3 Bucket if needed ===
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

# === Step 2: Upload nested templates (excluding main.yaml) ===
echo "Uploading templates to S3..."
aws s3 cp "${TEMPLATE_DIR}" "s3://${TEMPLATE_BUCKET}/" --recursive --region "$REGION" \
  --exclude "main.yaml"
echo "Templates uploaded."

# === Step 3: Package main template ===
echo "Packaging main CloudFormation template..."
aws cloudformation package \
  --template-file "$MAIN_TEMPLATE" \
  --s3-bucket "$TEMPLATE_BUCKET" \
  --output-template-file "$PACKAGED_TEMPLATE" \
  --region "$REGION"
echo "Main template packaged to $PACKAGED_TEMPLATE"

# === Step 4: Deploy the stack ===
echo "Deploying CloudFormation stack: $STACK_NAME..."
aws cloudformation deploy \
  --stack-name "$STACK_NAME" \
  --template-file "$PACKAGED_TEMPLATE" \
  --capabilities CAPABILITY_NAMED_IAM \
  --region "$REGION" \
  --parameter-overrides \
    $(jq -r '.[] | "\(.ParameterKey)=\(.ParameterValue)"' "$PARAMS_FILE")

echo
echo "✅ Stack deployment complete."
