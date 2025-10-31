#!/bin/bash

# Contentfulトークン（CloudFormationのデフォルト値）
export CONTENTFUL_ACCESS_TOKEN="6Z4wPWStkHj3d_EA0MQt89nWJpIFSBJcmAQ_YzDpkAg"
export MODEL_ID="us.anthropic.claude-haiku-4-5-20251001-v1:0"

# AWS認証情報を引き継ぎ
docker run --rm \
  -e CONTENTFUL_ACCESS_TOKEN \
  -e MODEL_ID \
  -e AWS_DEFAULT_REGION=us-east-1 \
  -e AWS_REGION=us-east-1 \
  -v ~/.aws:/root/.aws:ro \
  -v "$PWD":/var/task:ro \
  lambda-test python3 -c "
import json
import os
from index import lambda_handler

# テストイベント
event = {
    'body': json.dumps({
        'slug': 'test-article',
        'model': 'claude'
    })
}

print('Environment variables:')
print(f'CONTENTFUL_ACCESS_TOKEN: {os.environ.get(\"CONTENTFUL_ACCESS_TOKEN\", \"Not set\")}')
print(f'MODEL_ID: {os.environ.get(\"MODEL_ID\", \"Not set\")}')
print()

try:
    result = lambda_handler(event, {})
    print('Test Result:')
    print(json.dumps(result, indent=2, ensure_ascii=False))
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
"
