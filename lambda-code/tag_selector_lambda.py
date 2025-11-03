import json
import os
import boto3
from model_router import select_tags_with_model
from enhanced_common import enhanced_pre_filter_tags
from common import get_article_from_contentful, calculate_cost

# Lambda クライアント
lambda_client = boto3.client('lambda')

def call_summary_lambda(article_id=None, blog_text=None, model_id=None):
    """要約Lambda関数を呼び出し"""
    payload = {
        'model_id': model_id
    }
    
    if article_id:
        payload['article_id'] = article_id
    if blog_text:
        payload['blog_text'] = blog_text
    
    response = lambda_client.invoke(
        FunctionName=os.environ.get('SUMMARY_LAMBDA_NAME', 'tag-selector-summary'),
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )
    
    result = json.loads(response['Payload'].read())
    
    if result['statusCode'] != 200:
        raise Exception(f"Summary Lambda error: {result['body']}")
    
    body = json.loads(result['body'])
    return body['summary_text'], body['cache_info']

def lambda_handler(event, context):
    """タグ選択専用Lambda関数のハンドラー"""
    try:
        # パラメータ取得
        article_id = event.get('article_id')
        model_id = event.get('model_id', os.environ.get('MODEL_ID'))
        
        # 記事取得
        blog_text = get_article_from_contentful(article_id)
        is_long_article = len(blog_text) > 8000
        
        # 要約処理（長文記事の場合）
        if is_long_article:
            summary_text, summary_cache_info = call_summary_lambda(
                blog_text=blog_text, 
                model_id=model_id
            )
            processing_text = summary_text
        else:
            processing_text = blog_text
            summary_cache_info = {'input_tokens': 0, 'output_tokens': 0}
        
        # タグ絞り込み
        filtered_tags, tags_hash = enhanced_pre_filter_tags(processing_text)
        
        # タグ選択
        selected_tags, ranking_cache_info = select_tags_with_model(
            processing_text, filtered_tags, tags_hash, model_id
        )
        
        # コスト計算
        total_cache_info = {
            'summary_input_tokens': summary_cache_info.get('input_tokens', 0),
            'summary_output_tokens': summary_cache_info.get('output_tokens', 0),
            'ranking_input_tokens': ranking_cache_info.get('input_tokens', 0),
            'ranking_output_tokens': ranking_cache_info.get('output_tokens', 0),
            'input_tokens': summary_cache_info.get('input_tokens', 0) + ranking_cache_info.get('input_tokens', 0),
            'output_tokens': summary_cache_info.get('output_tokens', 0) + ranking_cache_info.get('output_tokens', 0),
            'model_id': model_id,
            'used_summary': is_long_article
        }
        
        cost_info = calculate_cost(total_cache_info)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'selected_tags': selected_tags,
                'cost_info': cost_info,
                'cache_info': total_cache_info
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            }, ensure_ascii=False)
        }
