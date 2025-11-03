import json
import boto3

def lambda_handler(event, context):
    """Function URL対応の要約テスト用Lambda"""
    try:
        # Function URLの場合、bodyにJSONが文字列として入っている
        if 'body' in event:
            body = json.loads(event['body'])
        else:
            body = event
        
        # パラメータ取得
        blog_text = body.get('blog_text', '')
        model_id = body.get('model_id', 'global.anthropic.claude-haiku-4-5-20251001-v1:0')
        
        if not blog_text:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'blog_text is required'})
            }
        
        # Bedrock クライアント
        bedrock = boto3.client('bedrock-runtime')
        
        # Claude用リクエスト
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "system": [{"type": "text", "text": "あなたは記事要約の専門家です。"}],
            "messages": [{
                "role": "user",
                "content": f"以下の記事を300文字程度で要約してください：\n\n{blog_text}"
            }]
        }
        
        # Bedrock API呼び出し
        response = bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body)
        )
        
        response_body = json.loads(response['body'].read())
        summary_text = response_body['content'][0]['text']
        
        cache_info = {
            'input_tokens': response_body['usage']['input_tokens'],
            'output_tokens': response_body['usage']['output_tokens']
        }
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'summary_text': summary_text,
                'cache_info': cache_info,
                'model_id': model_id
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
