import json
import os
from enhanced_common import (
    get_article_from_contentful,
    get_tags_from_contentful_cached,
    enhanced_pre_filter_tags,
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
        
        # 記事取得
        blog_text = get_article_from_contentful(slug)
        if not blog_text:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Article not found'})
            }
        
        # タグデータ取得
        tags_data, tags_hash = get_tags_from_contentful_cached()
        
        # 長文判定（2000文字超）
        is_long_article = len(blog_text) > 2000
        
        # 1. 長文記事の場合は要約作成
        if is_long_article:
            summary_text, summary_cache_info = create_summary(blog_text, model_id)
            processing_text = summary_text
        else:
            processing_text = blog_text
            summary_cache_info = {'input_tokens': 0, 'output_tokens': 0}
        
        # 2. MeCabでキーワード抽出 + タグを200個に絞り込み
        filtered_tags, tag_scores = enhanced_pre_filter_tags(
            processing_text, tags_data, max_tags=200
        )
        
        # 3. LLMでタグランキング評価（簡易版）
        final_tags = evaluate_tags_simple(tag_scores, processing_text)
        
        # コスト計算（簡易版）
        combined_cache_info = {
            'summary_input_tokens': summary_cache_info.get('input_tokens', 0),
            'summary_output_tokens': summary_cache_info.get('output_tokens', 0),
            'ranking_input_tokens': 0,
            'ranking_output_tokens': 0,
            'input_tokens': summary_cache_info.get('input_tokens', 0),
            'output_tokens': summary_cache_info.get('output_tokens', 0),
            'cache_creation_input_tokens': 0,
            'cache_read_input_tokens': 0,
            'used_summary': is_long_article
        }
        
        cost_info = calculate_cost(model_id, combined_cache_info)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'slug': slug,
                'model': model_id,
                'selected_tags': final_tags[:20],  # 上位20個を表示
                'tags_hash': tags_hash[:8],
                'filtered_count': len(filtered_tags),
                'total_tags_count': len(tags_data),
                'is_long_article': is_long_article,
                'article_length': len(blog_text),
                'cache_info': combined_cache_info,
                'cost_jpy': cost_info,
                'processing_flow': {
                    'step1': 'Article retrieved',
                    'step2': f'Summary created (long article: {is_long_article})',
                    'step3': f'MeCab processing + filtered to {len(filtered_tags)} tags',
                    'step4': f'Simple ranking completed, top 20 selected'
                }
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def evaluate_tags_simple(tag_scores, text):
    """簡易版タグ評価（LLMなし）"""
    text_lower = text.lower()
    
    # テキスト内での出現頻度と基本スコアで評価
    for tag in tag_scores:
        tag_name_lower = tag['name'].lower()
        
        # テキスト内出現回数をカウント
        occurrence_count = text_lower.count(tag_name_lower)
        
        # 単語での出現もチェック
        words = tag_name_lower.split()
        word_occurrences = sum(text_lower.count(word) for word in words if len(word) >= 2)
        
        # 最終スコア計算
        final_score = tag['score'] + (occurrence_count * 20) + (word_occurrences * 5)
        tag['final_score'] = final_score
        tag['occurrence_count'] = occurrence_count
    
    # 最終スコア順でソート
    tag_scores.sort(key=lambda x: x['final_score'], reverse=True)
    
    return tag_scores
