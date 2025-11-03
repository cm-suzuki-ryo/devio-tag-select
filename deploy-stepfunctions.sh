#!/bin/bash

echo "🚀 Deploying Tag Selector with Step Functions..."

# Deploy CloudFormation stack
aws cloudformation deploy \
  --template-file cloudformation-stepfunctions.yaml \
  --stack-name tag-selector-stepfunctions \
  --capabilities CAPABILITY_IAM \
  --region us-west-2 \
  --parameter-overrides CloudFrontSecretHeader="MySecretValue123"

if [ $? -eq 0 ]; then
    echo "✅ Deployment successful!"
    
    # Get outputs
    echo "📋 Getting stack outputs..."
    aws cloudformation describe-stacks \
      --stack-name tag-selector-stepfunctions \
      --region us-west-2 \
      --query 'Stacks[0].Outputs' \
      --output table
else
    echo "❌ Deployment failed!"
    exit 1
fi
