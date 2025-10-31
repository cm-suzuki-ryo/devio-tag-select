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
        filtered_tags, tag_scores = pre_filter_tags(blog_text, tags_data, max_tags=1000)
        
        # 文字数チェック
        is_long_article = len(blog_text) > 2000
        
        # modelパラメータが指定されていない場合はデフォルトでHaikuを使用
        if not model_id:
            model_id = 'us.anthropic.claude-haiku-4-5-20251001-v1:0'
        
        # AIによる適合度評価
        ai_scored_tags, cache_info = evaluate_tags_with_ai(
            blog_text, tag_scores, model_id, is_long_article
        )
        cost_info = calculate_cost(model_id, cache_info)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'slug': slug,
                'model': model_id,
                'tag_candidates': ai_scored_tags[:20],  # AI評価による上位20個
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
def evaluate_tags_with_ai(blog_text, tag_scores, model_id, is_long_article):
    """AIを使ってタグの適合度を評価"""
    from model_router import create_summary, select_tags_with_model
    import json
    
    # 長文記事の場合は要約を作成
    if is_long_article:
        summary_text, summary_cache_info = create_summary(blog_text, model_id)
        evaluation_text = summary_text
    else:
        evaluation_text = blog_text
        summary_cache_info = {'input_tokens': 0, 'output_tokens': 0}
    
    # タグリストを作成（上位1000個）
    tag_list = []
    for tag in tag_scores:
        tag_list.append(f"{tag['id']}\t{tag['name']}")
    
    tags_text = '\n'.join(tag_list)
    
    # AIによる適合度評価
    ai_scores, eval_cache_info = evaluate_tag_relevance(
        evaluation_text, tags_text, model_id
    )
    
    # スコアを統合
    enhanced_tags = []
    for tag in tag_scores:
        tag_id = tag['id']
        ai_score = ai_scores.get(tag_id, 0)
        
        # 基本スコア + AI評価スコア
        combined_score = tag['score'] + (ai_score * 10)  # AI評価を10倍重み付け
        
        enhanced_tags.append({
            'id': tag['id'],
            'name': tag['name'],
            'basic_score': tag['score'],
            'ai_score': ai_score,
            'combined_score': combined_score,
            'relevance_percentage': round((combined_score / max([t['combined_score'] for t in enhanced_tags] + [combined_score])) * 100, 1) if combined_score > 0 else 0
        })
    
    # AI評価スコアでソート
    enhanced_tags.sort(key=lambda x: x['combined_score'], reverse=True)
    
    # 適合度パーセンテージを再計算
    if enhanced_tags:
        max_combined_score = enhanced_tags[0]['combined_score']
        for tag in enhanced_tags:
            tag['relevance_percentage'] = round((tag['combined_score'] / max_combined_score * 100) if max_combined_score > 0 else 0, 1)
    
    # キャッシュ情報を統合
    combined_cache_info = {
        'summary_input_tokens': summary_cache_info.get('input_tokens', 0),
        'summary_output_tokens': summary_cache_info.get('output_tokens', 0),
        'eval_input_tokens': eval_cache_info.get('input_tokens', 0),
        'eval_output_tokens': eval_cache_info.get('output_tokens', 0),
        'input_tokens': summary_cache_info.get('input_tokens', 0) + eval_cache_info.get('input_tokens', 0),
        'output_tokens': summary_cache_info.get('output_tokens', 0) + eval_cache_info.get('output_tokens', 0),
        'cache_creation_input_tokens': eval_cache_info.get('cache_creation_input_tokens', 0),
        'cache_read_input_tokens': eval_cache_info.get('cache_read_input_tokens', 0),
        'used_summary': is_long_article
    }
    
    return enhanced_tags, combined_cache_info

def evaluate_tag_relevance(text, tags_text, model_id):
    """AIモデルを使ってタグの適合度を評価"""
    from model_router import select_tags_with_model
    import boto3
    import json
    import re
    
    bedrock = boto3.client('bedrock-runtime')
    
    if 'anthropic' in model_id:
        system_text = f"あなたはブログ記事の内容分析とタグ適合度評価の専門家です。以下のタグリストの各タグについて、記事内容との適合度を0-10のスコアで評価してください。\n\nタグリスト:\n{tags_text}\n\n評価基準:\n10: 完全に一致、記事の核心的内容\n8-9: 高い関連性、重要な要素\n6-7: 中程度の関連性\n4-5: 低い関連性\n1-3: わずかな関連性\n0: 関連性なし\n\n回答は必ずこのJSON形式で出力してください: {{\"scores\": {{\"タグID\": スコア, \"タグID\": スコア}}}}"
        
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 8192,
            "system": [{"type": "text", "text": system_text, "cache_control": {"type": "ephemeral"}}],
            "messages": [{"role": "user", "content": f"以下の記事内容を分析して、各タグの適合度を評価してください：\n\n{text}"}]
        }
    elif 'amazon.nova' in model_id:
        system_part = f"あなたはブログ記事の内容分析とタグ適合度評価の専門家です。以下のタグリストの各タグについて、記事内容との適合度を0-10のスコアで評価してください。\n\nタグリスト:\n{tags_text}\n\n評価基準:\n10: 完全に一致、記事の核心的内容\n8-9: 高い関連性、重要な要素\n6-7: 中程度の関連性\n4-5: 低い関連性\n1-3: わずかな関連性\n0: 関連性なし\n\n回答は必ずこのJSON形式で出力してください: {{\"scores\": {{\"タグID\": スコア, \"タグID\": スコア}}}}\n\n以下の記事内容を分析して、各タグの適合度を評価してください："
        combined_prompt = f"{system_part}\n\n{text}"
        
        body = {
            "messages": [{"role": "user", "content": [{"text": combined_prompt}]}],
            "inferenceConfig": {"temperature": 0}
        }
    else:  # GPT-OSS
        system_content = f"あなたはブログ記事の内容分析とタグ適合度評価の専門家です。以下のタグリストの各タグについて、記事内容との適合度を0-10のスコアで評価してください。\n\nタグリスト:\n{tags_text}\n\n評価基準:\n10: 完全に一致、記事の核心的内容\n8-9: 高い関連性、重要な要素\n6-7: 中程度の関連性\n4-5: 低い関連性\n1-3: わずかな関連性\n0: 関連性なし\n\n<thinking>タグ内で推論を行い、最終的に以下の形式でJSONのみを出力してください: {{\"scores\": {{\"タグID\": スコア, \"タグID\": スコア}}}}"
        
        body = {
            "messages": [
                {"role": "system", "content": system_content},
                {"role": "user", "content": f"以下の記事内容を分析してください。<thinking>タグ内で推論し、最終的にJSONのみを出力してください：\n\n{text}"}
            ],
            "max_tokens": 8192,
            "temperature": 0
        }
    
    response = bedrock.invoke_model(modelId=model_id, body=json.dumps(body))
    response_body = json.loads(response['body'].read())
    
    if 'anthropic' in model_id:
        result_text = response_body['content'][0]['text']
        usage = response_body.get('usage', {})
        cache_info = {
            'cache_creation_input_tokens': usage.get('cache_creation_input_tokens', 0),
            'cache_read_input_tokens': usage.get('cache_read_input_tokens', 0),
            'input_tokens': usage.get('input_tokens', 0),
            'output_tokens': usage.get('output_tokens', 0)
        }
    elif 'amazon.nova' in model_id:
        result_text = response_body['output']['message']['content'][0]['text']
        usage = response_body.get('usage', {})
        cache_info = {
            'cache_creation_input_tokens': 0,
            'cache_read_input_tokens': 0,
            'input_tokens': usage.get('inputTokens', 0),
            'output_tokens': usage.get('outputTokens', 0)
        }
    else:  # GPT-OSS
        result_text = response_body['choices'][0]['message']['content']
        usage = response_body.get('usage', {})
        cache_info = {
            'cache_creation_input_tokens': 0,
            'cache_read_input_tokens': 0,
            'input_tokens': usage.get('prompt_tokens', 0),
            'output_tokens': usage.get('completion_tokens', 0)
        }
    
    # JSONからスコアを抽出
    ai_scores = {}
    try:
        if 'openai' in model_id:
            # OpenAI用：<thinking>タグの外側のJSONを探す
            thinking_pattern = r'</thinking>\s*(\{[^{}]*"scores"[^{}]*\{[^{}]*\}[^{}]*\})'
            thinking_match = re.search(thinking_pattern, result_text)
            if thinking_match:
                json_str = thinking_match.group(1)
                scores_data = json.loads(json_str)['scores']
                ai_scores = scores_data
            else:
                # フォールバック：通常のJSONパターン
                json_matches = re.findall(r'\{[^{}]*"scores"[^{}]*\{[^{}]*\}[^{}]*\}', result_text)
                if json_matches:
                    json_str = json_matches[-1]
                    scores_data = json.loads(json_str)['scores']
                    ai_scores = scores_data
        else:
            # Nova、Claude用：従来の方法
            start = result_text.find('{')
            end = result_text.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = result_text[start:end]
                scores_data = json.loads(json_str)['scores']
                ai_scores = scores_data
    except Exception as e:
        # エラー時は空のスコアを返す
        ai_scores = {}
    
    return ai_scores, cache_info
