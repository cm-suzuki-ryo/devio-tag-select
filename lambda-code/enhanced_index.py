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
        
        # 3. LLMでタグランキング評価
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
                    'step4': f'LLM ranking completed, top 20 selected'
                }
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def evaluate_tags_with_llm(text, tag_scores, model_id):
    """LLMを使用してタグの適合度をランキング評価"""
    import boto3
    
    # タグリストを作成
    tag_list = []
    for i, tag in enumerate(tag_scores, 1):
        tag_list.append(f"{i}. {tag['name']} (ID: {tag['id']})")
    
    tags_text = '\n'.join(tag_list)
    
    # LLMプロンプト
    prompt = f"""以下の記事内容に最も適合するタグを評価してください。

記事内容:
{text}

タグ候補:
{tags_text}

各タグの適合度を1-10で評価し、適合度の高い順にランキングしてください。
出力形式: タグID,適合度スコア,タグ名

例:
12345,9,AWS Lambda
67890,8,機械学習
"""

    bedrock = boto3.client('bedrock-runtime')
    
    if 'anthropic' in model_id:
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2000,
            "messages": [{"role": "user", "content": prompt}]
        }
    elif 'amazon.nova' in model_id:
        body = {
            "messages": [{"role": "user", "content": [{"text": prompt}]}],
            "inferenceConfig": {"temperature": 0.1}
        }
    elif 'openai' in model_id:
        body = {
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 2000,
            "temperature": 0.1
        }
    
    response = bedrock.invoke_model(modelId=model_id, body=json.dumps(body))
    response_body = json.loads(response['body'].read())
    
    # レスポンス解析
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
    
    # 結果をパース
    ranked_tags = parse_llm_ranking(result_text, tag_scores)
    
    return ranked_tags, cache_info

def parse_llm_ranking(result_text, original_tags):
    """LLMの評価結果をパース"""
    ranked_tags = []
    tag_dict = {tag['id']: tag for tag in original_tags}
    
    lines = result_text.strip().split('\n')
    for line in lines:
        if ',' in line:
            parts = line.split(',')
            if len(parts) >= 3:
                try:
                    tag_id = parts[0].strip()
                    llm_score = int(parts[1].strip())
                    
                    if tag_id in tag_dict:
                        tag_info = tag_dict[tag_id].copy()
                        tag_info['llm_score'] = llm_score
                        tag_info['final_score'] = tag_info['score'] + (llm_score * 10)
                        ranked_tags.append(tag_info)
                except:
                    continue
    
    # LLMスコア順でソート
    ranked_tags.sort(key=lambda x: x.get('llm_score', 0), reverse=True)
    
    return ranked_tags
