import json
import os
from common import (
    get_article_from_contentful,
    get_tags_from_contentful_cached,
    pre_filter_tags,
    calculate_cost
)
from model_router import create_summary, select_tags_with_model

def lambda_handler(event, context):
    try:
        if 'body' in event:
            body = json.loads(event.get('body', '{}'))
        else:
            body = event
        
        slug = body.get('slug', '')
        model_id = body.get('model', None) or os.environ.get('MODEL_ID')
        
        if not slug:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'slug is required'})
            }
        
        blog_text = get_article_from_contentful(slug)
        if not blog_text:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Article not found'})
            }
        
        tags_data, tags_hash = get_tags_from_contentful_cached()
        filtered_tags = pre_filter_tags(blog_text, tags_data, max_tags=100)
        
        # 文字数チェック
        is_long_article = len(blog_text) > 2000
        
        # modelパラメータが指定されていない場合はデフォルトでHaikuを使用
        if not model_id:
            model_id = 'us.anthropic.claude-haiku-4-5-20251001-v1:0'
        
        # 単一モデル実行
        selected_tags, cache_info = process_article_with_model(
            blog_text, filtered_tags, tags_hash, model_id, is_long_article
        )
        cost_info = calculate_cost(model_id, cache_info)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'slug': slug,
                'model': model_id,
                'selected_tags': selected_tags,
                'tags_hash': tags_hash[:8],
                'filtered_count': len(filtered_tags),
                'total_tags_count': len(tags_data),
                'is_long_article': is_long_article,
                'article_length': len(blog_text),
                'cache_info': cache_info,
                'cost_jpy': cost_info
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def process_article_with_model(blog_text, filtered_tags, tags_hash, model_id, is_long_article):
    """記事の長さに応じて要約処理を分岐"""
    if is_long_article:
        # 長文記事：要約してからタグ選択（同じモデルを使用）
        summary_text, summary_cache_info = create_summary(blog_text, model_id)
        selected_tags, tag_cache_info = select_tags_with_model(
            summary_text, filtered_tags, tags_hash, model_id
        )
        
        # キャッシュ情報を統合
        combined_cache_info = {
            'summary_input_tokens': summary_cache_info.get('input_tokens', 0),
            'summary_output_tokens': summary_cache_info.get('output_tokens', 0),
            'tag_input_tokens': tag_cache_info.get('input_tokens', 0),
            'tag_output_tokens': tag_cache_info.get('output_tokens', 0),
            'input_tokens': summary_cache_info.get('input_tokens', 0) + tag_cache_info.get('input_tokens', 0),
            'output_tokens': summary_cache_info.get('output_tokens', 0) + tag_cache_info.get('output_tokens', 0),
            'cache_creation_input_tokens': tag_cache_info.get('cache_creation_input_tokens', 0),
            'cache_read_input_tokens': tag_cache_info.get('cache_read_input_tokens', 0),
            'used_summary': True
        }
        
        return selected_tags, combined_cache_info
    else:
        # 短文記事：従来通り
        selected_tags, cache_info = select_tags_with_model(
            blog_text, filtered_tags, tags_hash, model_id
        )
        cache_info['used_summary'] = False
        return selected_tags, cache_info
