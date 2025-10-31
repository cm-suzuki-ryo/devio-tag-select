import json
import boto3
from common import extract_tags_from_response

def invoke_claude_model(blog_text, filtered_tags, tags_hash, model_id):
    """Anthropicモデル（Claude）を呼び出し"""
    bedrock = boto3.client('bedrock-runtime')
    tags_text = '\n'.join(filtered_tags)
    
    system_text = f"あなたはブログ記事の内容分析とタグ付けの専門家です。タグデータハッシュ: {tags_hash} 以下のタグリストから、ブログ記事に最も関連するタグを最大5個選択してください： {tags_text} 選択基準：1.記事の主要テーマとの関連性 2.技術的内容との一致度 3.読者にとっての有用性 回答は必ずこのJSON形式で出力してください: {{\"tags\": [{{\"id\": \"123\", \"name\": \"タグ名\"}}]}}"
    
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 8192,
        "system": [{"type": "text", "text": system_text, "cache_control": {"type": "ephemeral"}}],
        "messages": [{"role": "user", "content": f"以下のブログ記事を分析して適切なタグを選択してください：\n\n{blog_text}"}]
    }
    
    response = bedrock.invoke_model(modelId=model_id, body=json.dumps(body))
    response_body = json.loads(response['body'].read())
    
    result_text = response_body['content'][0]['text']
    usage = response_body.get('usage', {})
    
    cache_info = {
        'cache_creation_input_tokens': usage.get('cache_creation_input_tokens', 0),
        'cache_read_input_tokens': usage.get('cache_read_input_tokens', 0),
        'input_tokens': usage.get('input_tokens', 0),
        'output_tokens': usage.get('output_tokens', 0)
    }
    
    tags = extract_tags_from_response(result_text, model_id)
    return tags, cache_info

def create_summary_with_claude(blog_text, model_id):
    """Claudeモデルで記事要約を作成"""
    bedrock = boto3.client('bedrock-runtime')
    
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 8192,
        "system": [{"type": "text", "text": "あなたは記事要約の専門家です。"}],
        "messages": [{
            "role": "user",
            "content": f"以下のブログ記事を1000文字程度で要約してください。技術的なキーワードや重要な概念は必ず含めてください：\n\n{blog_text}"
        }]
    }
    
    response = bedrock.invoke_model(modelId=model_id, body=json.dumps(body))
    response_body = json.loads(response['body'].read())
    
    summary_text = response_body['content'][0]['text']
    usage = response_body.get('usage', {})
    
    cache_info = {
        'input_tokens': usage.get('input_tokens', 0),
        'output_tokens': usage.get('output_tokens', 0)
    }
    
    return summary_text, cache_info
