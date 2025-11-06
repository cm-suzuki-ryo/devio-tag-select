import json
import boto3
import os
import uuid

def lambda_handler(event, context):
    try:
        # CloudFront認証
        expected_secret = os.environ.get('CLOUDFRONT_SECRET_HEADER')
        if expected_secret:
            headers = event.get('headers', {})
            cloudfront_secret = headers.get('x-cloudfront-secret') or headers.get('X-CloudFront-Secret')
            if not cloudfront_secret or cloudfront_secret != expected_secret:
                return {
                    'statusCode': 403,
                    'body': json.dumps({'error': 'Access denied - CloudFront access required'})
                }

        # パラメータ取得
        if event.get('httpMethod'):
            # API Gateway経由
            if event['httpMethod'] == 'GET':
                params = event.get('queryStringParameters') or {}
            else:
                params = json.loads(event.get('body', '{}'))
        else:
            # 直接呼び出し
            params = event

        slug = params.get('slug')
        model_id = params.get('model_id', 'us.amazon.nova-lite-v1:0')

        if not slug:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'slug parameter is required'})
            }

        # Step Functions実行
        stepfunctions = boto3.client('stepfunctions')
        execution_name = f"tag-selector-{uuid.uuid4().hex[:8]}"
        
        response = stepfunctions.start_sync_execution(
            stateMachineArn=os.environ['STATE_MACHINE_ARN'],
            name=execution_name,
            input=json.dumps({
                'slug': slug,
                'model_id': model_id
            })
        )

        if response['status'] == 'SUCCEEDED':
            result = json.loads(response['output'])
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(result['result'])
            }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': 'Step Functions execution failed',
                    'details': response.get('error', 'Unknown error')
                })
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
