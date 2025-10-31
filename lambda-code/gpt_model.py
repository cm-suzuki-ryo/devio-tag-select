import json
import boto3
from common import extract_tags_from_response

def invoke_gpt_model(blog_text, filtered_tags, tags_hash, model_id):
    """OpenAI GPT-OSSモデルを呼び出し"""
    bedrock = boto3.client('bedrock-runtime')
    tags_text = '\n'.join(filtered_tags)
    
    system_content = f"あなたはブログ記事の内容分析とタグ付けの専門家です。タグデータハッシュ: {tags_hash} 以下のタグリストから、ブログ記事に最も関連するタグを最大5個選択してください： {tags_text} 選択基準：1.記事の主要テーマとの関連性 2.技術的内容との一致度 3.読者にとっての有用性 <thinking>タグ内で推論を行い、最終的に以下の形式でJSONのみを出力してください: {{\"tags\": [{{\"id\": \"123\", \"name\": \"タグ名\"}}]}}"
    
    body = {
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": f"以下のブログ記事を分析してください。<thinking>タグ内で推論し、最終的にJSONのみを出力してください：\n\n{blog_text}"}
        ],
        "max_tokens": 8192,
        "temperature": 0
    }
    
    response = bedrock.invoke_model(modelId=model_id, body=json.dumps(body))
    response_body = json.loads(response['body'].read())
    
    result_text = response_body['choices'][0]['message']['content']
    usage = response_body.get('usage', {})
    
    cache_info = {
        'cache_creation_input_tokens': 0,
        'cache_read_input_tokens': 0,
        'input_tokens': usage.get('prompt_tokens', 0),
        'output_tokens': usage.get('completion_tokens', 0)
    }
    
    tags = extract_tags_from_response(result_text, model_id)
    return tags, cache_info

def create_summary_with_gpt(blog_text, model_id):
    """GPT-OSSモデルで記事要約を作成"""
    bedrock = boto3.client('bedrock-runtime')
    
    body = {
        "messages": [
            {"role": "system", "content": "あなたは記事要約の専門家です。"},
            {"role": "user", "content": f"以下のブログ記事を1000文字程度で要約してください。技術的なキーワードや重要な概念は必ず含めてください：\n\n{blog_text}"}
        ],
        "max_tokens": 8192,
        "temperature": 0
    }
    
    response = bedrock.invoke_model(modelId=model_id, body=json.dumps(body))
    response_body = json.loads(response['body'].read())
    
    summary_text = response_body['choices'][0]['message']['content']
    usage = response_body.get('usage', {})
    
    cache_info = {
        'input_tokens': usage.get('prompt_tokens', 0),
        'output_tokens': usage.get('completion_tokens', 0)
    }
    
    return summary_text, cache_info
