import json
import os
from enhanced_common import (
    get_article_from_contentful,
    get_tags_from_contentful_cached,
    enhanced_pre_filter_tags,
    calculate_cost
)
from model_router import create_summary

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
        
        # 3. LLMでタグマッチング評価
        final_tags, ranking_cache_info = evaluate_tags_with_llm(
            processing_text, tag_scores, model_id
        )
        
        # コスト計算
        combined_cache_info = {
            'summary_input_tokens': summary_cache_info.get('input_tokens', 0),
            'summary_output_tokens': summary_cache_info.get('output_tokens', 0),
            'ranking_input_tokens': ranking_cache_info.get('input_tokens', 0),
            'ranking_output_tokens': ranking_cache_info.get('output_tokens', 0),
            'input_tokens': summary_cache_info.get('input_tokens', 0) + ranking_cache_info.get('input_tokens', 0),
            'output_tokens': summary_cache_info.get('output_tokens', 0) + ranking_cache_info.get('output_tokens', 0),
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
                    'step4': f'LLM 100-scale ranking with {model_id} completed, top 20 selected'
                }
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def evaluate_tags_with_llm(text, tag_scores, model_id):
    """LLMを使用してタグと記事のマッチング評価"""
    import boto3
    
    # 上位50個のタグのみLLM評価（コスト効率化）
    top_tags = tag_scores[:50]
    
    # タグリストを作成
    tag_list = []
    for i, tag in enumerate(top_tags, 1):
        tag_list.append(f"{i}. {tag['name']} (ID: {tag['id']})")
    
    tags_text = '\n'.join(tag_list)
    
    # LLMプロンプト（100段階評価）
    prompt = f"""以下の記事内容に対して、各タグの適合度を1-100の数値で評価してください。

記事内容:
{text[:1500]}...

タグ候補:
{tags_text}

各タグについて、記事内容との関連性を1-100で評価し、以下の形式で出力してください：
タグID:スコア

例:
12345:95
67890:78
11111:23

評価基準:
- 90-100: 記事の核心的なテーマ、主要技術
- 80-89: 記事内容に強く関連、重要な要素
- 70-79: 記事内容に明確に関連
- 60-69: 記事内容に関連、言及あり
- 50-59: 部分的に関連、間接的言及
- 40-49: 弱い関連性
- 30-39: 関連性が薄い
- 20-29: ほとんど関連なし
- 10-19: 関連性なし
- 1-9: 全く関連なし

より細かい差異を数値で表現してください。同じ評価レベルでも微細な違いがあれば異なる数値を使用してください。
"""

    bedrock = boto3.client('bedrock-runtime')
    
    # モデル別のリクエスト形式
    if 'anthropic' in model_id:
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "temperature": 0.1,
            "messages": [{"role": "user", "content": prompt}]
        }
    elif 'amazon.nova' in model_id:
        body = {
            "messages": [{"role": "user", "content": [{"text": prompt}]}],
            "inferenceConfig": {
                "max_new_tokens": 1000,
                "temperature": 0.1
            }
        }
    elif 'openai' in model_id:
        body = {
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000,
            "temperature": 0.1
        }
    
    response = bedrock.invoke_model(modelId=model_id, body=json.dumps(body))
    response_body = json.loads(response['body'].read())
    
    # レスポンス解析（モデル別）
    if 'anthropic' in model_id:
        result_text = response_body['content'][0]['text']
        cache_info = {
            'input_tokens': response_body['usage']['input_tokens'],
            'output_tokens': response_body['usage']['output_tokens']
        }
    elif 'amazon.nova' in model_id:
        result_text = response_body['output']['message']['content'][0]['text']
        cache_info = {
            'input_tokens': response_body['usage']['inputTokens'],
            'output_tokens': response_body['usage']['outputTokens']
        }
    elif 'openai' in model_id:
        result_text = response_body['choices'][0]['message']['content']
        cache_info = {
            'input_tokens': response_body['usage']['prompt_tokens'],
            'output_tokens': response_body['usage']['completion_tokens']
        }
    
    # LLM評価結果をパース（100段階）
    llm_scores = parse_llm_scores_100(result_text)
    
    # スコアを統合
    enhanced_tags = []
    tag_dict = {tag['id']: tag for tag in tag_scores}
    
    for tag in tag_scores:
        tag_id = tag['id']
        llm_score = llm_scores.get(tag_id, 0)
        
        # 最終スコア = 基本スコア + (LLMスコア × 重み)
        final_score = tag['score'] + (llm_score * 5)  # 100段階なので重みを調整
        
        enhanced_tag = tag.copy()
        enhanced_tag['llm_score'] = llm_score
        enhanced_tag['final_score'] = final_score
        enhanced_tags.append(enhanced_tag)
    
    # LLMスコア重視でソート
    enhanced_tags.sort(key=lambda x: (x['llm_score'], x['final_score']), reverse=True)
    
    return enhanced_tags, cache_info

def parse_llm_scores_100(result_text):
    """LLMの評価結果をパース（100段階）"""
    scores = {}
    lines = result_text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if ':' in line:
            try:
                parts = line.split(':')
                if len(parts) >= 2:
                    tag_id = parts[0].strip()
                    score = int(parts[1].strip())
                    if 1 <= score <= 100:  # 1-100の範囲チェック
                        scores[tag_id] = score
            except ValueError:
                continue
    
    return scores
