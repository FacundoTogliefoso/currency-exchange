#!/bin/bash
set -euo pipefail

# Configuration
PROJECT_NAME="currency-exchange"
ENV="dev"
AWS_REGION="us-west-1"
ECR_REPO_NAME="currency-api"
IMAGE_TAG="$(date +%Y%m%d-%H%M%S)"
TEMPLATE_FILE="infra/cloudformation/templates/main.yaml"
STACK_NAME="${PROJECT_NAME}-${ENV}-stack"

echo "Starting deployment..."

# Get AWS Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}"

echo "Deploying ${PROJECT_NAME} to ${ENV} environment"
echo "Using image: ${ECR_URI}:${IMAGE_TAG}"

# Check if ECR repo exists
if ! aws ecr describe-repositories --repository-names "$ECR_REPO_NAME" --region "$AWS_REGION" > /dev/null 2>&1; then
    echo "Creating ECR repository..."
    aws ecr create-repository \
        --repository-name "$ECR_REPO_NAME" \
        --image-tag-mutability MUTABLE \
        --encryption-configuration encryptionType=AES256 \
        --region "$AWS_REGION" > /dev/null
    echo "ECR repository created"
else
    echo "ECR repository exists"
fi

# Login to ECR
echo "Logging into ECR..."
aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$ECR_URI"

# Build and push image
echo "Building Docker image..."
docker build -t "$ECR_REPO_NAME:$IMAGE_TAG" .

docker tag "$ECR_REPO_NAME:$IMAGE_TAG" "$ECR_URI:$IMAGE_TAG"
echo "Pushing to ECR..."
docker push "$ECR_URI:$IMAGE_TAG"

# Package templates if using nested stacks
if [ -d "infra/cloudformation" ]; then
    echo "Packaging nested templates..."
    aws cloudformation package \
        --template-file "$TEMPLATE_FILE" \
        --s3-bucket "${PROJECT_NAME}-${ENV}-templates-$(echo $AWS_ACCOUNT_ID | tail -c 5)" \
        --output-template-file "packaged-template.yaml" \
        --region "$AWS_REGION"
    TEMPLATE_FILE="packaged-template.yaml"
fi

# Deploy stack
echo "Deploying CloudFormation stack..."
aws cloudformation deploy \
    --template-file "$TEMPLATE_FILE" \
    --stack-name "$STACK_NAME" \
    --parameter-overrides \
        ProjectName="$PROJECT_NAME" \
        Environment="$ENV" \
        ContainerImage="$ECR_URI:$IMAGE_TAG" \
        DbPassword="$(openssl rand -base64 32)" \
        NotificationEmail="your-email@example.com" \
    --capabilities CAPABILITY_NAMED_IAM \
    --region "$AWS_REGION"

# Get the application URL
APP_URL=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$AWS_REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`ApplicationUrl`].OutputValue' \
    --output text)

echo "Stack deployed successfully"
echo "Application available at: ${APP_URL}"

# Force ECS to pick up the new image
echo "Updating ECS service..."
CLUSTER_NAME="${PROJECT_NAME}-${ENV}-cluster"
SERVICE_NAME="${PROJECT_NAME}-${ENV}-service"

aws ecs update-service \
    --cluster "$CLUSTER_NAME" \
    --service "$SERVICE_NAME" \
    --force-new-deployment \
    --region "$AWS_REGION" > /dev/null

echo "ECS service update started"
echo "Done. Give it a couple minutes to spin up the new container."

# Clean up
rm -f packaged-template.yaml