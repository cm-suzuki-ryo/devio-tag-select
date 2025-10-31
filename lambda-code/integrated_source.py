import json
import os
import re
import urllib3
import hashlib
import boto3

# グローバルキャッシュ
TAGS_CACHE = None
TAGS_HASH = None

def extract_keywords_with_mecab(text):
    """MeCabを使用してキーワードを抽出"""
    # 英数字キーワード
    english_keywords = re.findall(r'[A-Za-z0-9]+', text)
    english_keywords = [k.lower() for k in english_keywords if len(k) >= 2]
    
    # 日本語キーワード（MeCab処理）
    japanese_text = re.sub(r'[A-Za-z0-9\s]+', '', text)
    japanese_keywords = tokenize_japanese(japanese_text)
    japanese_keywords = [k.lower() for k in japanese_keywords if len(k) >= 2]
    
    return english_keywords + japanese_keywords


def split_tag_name(tag_name):
    """タグ名を適切に分割（日本語・英語対応）"""
    words = []
    
    # スペース区切りで分割
    space_parts = tag_name.split()
    
    for part in space_parts:
        if re.match(r'^[A-Za-z0-9]+$', part):
            # 英数字のみ
            words.append(part.lower())
        else:
            # 日本語を含む場合
            japanese_words = tokenize_japanese(part)
            words.extend([w.lower() for w in japanese_words])
    
    return [w for w in words if len(w) >= 2]


def simple_japanese_split(text):
    """MeCabなしでの簡易日本語分割"""
    tokens = []
    current_token = ""
    current_type = None
    
    for char in text:
        char_type = get_char_type(char)
        
        if char_type != current_type:
            if current_token and len(current_token) >= 2:
                tokens.append(current_token)
            current_token = char
            current_type = char_type
        else:
            current_token += char
    
    if current_token and len(current_token) >= 2:
        tokens.append(current_token)
    
    return tokens


def get_char_type(char):
    """文字種別を判定"""
    if re.match(r'[ぁ-ん]', char):
        return 'hiragana'
    elif re.match(r'[ァ-ヶ]', char):
        return 'katakana'
    elif re.match(r'[一-龯]', char):
        return 'kanji'
    elif re.match(r'[A-Za-z0-9]', char):
        return 'ascii'
    else:
        return 'other'


import json
import os
    get_article_from_contentful,
    get_tags_from_contentful_cached,
    calculate_cost
)

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
        
        # 2. MeCabでキーワード抽出 + タグを100個に絞り込み
        filtered_tags, tag_scores = enhanced_pre_filter_tags_100(
            processing_text, tags_data, max_tags=100
        )
        
        # 3. LLMで全100タグを評価（最終修正版）
        final_tags, ranking_cache_info = evaluate_all_tags_with_llm_final(
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
                    'step4': f'LLM 100-scale evaluation of all {len(tag_scores)} tags completed (FINAL), top 20 selected'
                }
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def enhanced_pre_filter_tags_100(blog_text, all_tags, max_tags=100):
    """
    MeCabを使用した改良版タグフィルタリング
    100個まで絞り込み
    """
        
    # キーワード抽出（MeCab使用）
    keywords = extract_keywords_with_mecab(blog_text)
    blog_lower = blog_text.lower()
    
    scored_tags = []
    max_score = 0
    
    for tag in all_tags:
        tag_id = str(tag.get('id', ''))
        tag_name = tag.get('name', '')
        
        if not tag_id or not tag_name:
            continue
            
        tag_name_lower = tag_name.lower()
        score = 0
        
        # 1. 完全一致チェック（+15点）
        if tag_name_lower in blog_lower:
            score += 15
        
        # 2. キーワードマッチング（+10点）
        for keyword in keywords:
            if keyword in tag_name_lower or tag_name_lower in keyword:
                score += 10
                break
        
        # 3. 単語レベルマッチング（MeCab処理、+5点）
        tag_words = split_tag_name(tag_name)
        for word in tag_words:
            if word in keywords or word in blog_lower:
                score += 5
        
        # 4. 部分マッチング（+2点）
        for keyword in keywords:
            if len(keyword) >= 3:
                if keyword in tag_name_lower or tag_name_lower in keyword:
                    score += 2
        
        if score > 0:
            scored_tags.append((score, f"{tag_id}\t{tag_name}", tag_id, tag_name))
            max_score = max(max_score, score)
    
    # スコア順でソート
    scored_tags.sort(reverse=True, key=lambda x: x[0])
    
    # 上位100個に絞り込み
    filtered_tags = [tag for _, tag, _, _ in scored_tags[:max_tags]]
    tag_scores = []
    
    for score, _, tag_id, tag_name in scored_tags[:max_tags]:
        relevance_percentage = round((score / max_score * 100) if max_score > 0 else 0, 1)
        tag_scores.append({
            'id': tag_id,
            'name': tag_name,
            'score': score,
            'relevance_percentage': relevance_percentage
        })
    
    return filtered_tags, tag_scores

def evaluate_all_tags_with_llm_fixed(text, tag_scores, model_id):
    """LLMを使用して全100タグを評価（改良パーサー）"""
    import boto3
    
    # 全100タグをLLM評価
    all_tags = tag_scores
    
    # タグリストを作成
    tag_list = []
    for i, tag in enumerate(all_tags, 1):
        tag_list.append(f"{i}. {tag['name']} (ID: {tag['id']})")
    
    tags_text = '\n'.join(tag_list)
    
    # LLMプロンプト（100段階評価、簡潔な出力指示）
    prompt = f"""以下の記事内容に対して、各タグの適合度を1-100の数値で評価してください。

記事内容:
{text[:1200]}...

タグ候補（全{len(all_tags)}個）:
{tags_text}

各タグについて、記事内容との関連性を1-100で評価し、以下の形式のみで出力してください：
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

全{len(all_tags)}個のタグすべてに対して「タグID:スコア」の形式のみで出力してください。説明は不要です。
"""

    bedrock = boto3.client('bedrock-runtime')
    
    # モデル別のリクエスト形式（トークン数を大幅増加）
    if 'anthropic' in model_id:
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,  # 大幅に増加
            "temperature": 0.1,
            "messages": [{"role": "user", "content": prompt}]
        }
    elif 'amazon.nova' in model_id:
        body = {
            "messages": [{"role": "user", "content": [{"text": prompt}]}],
            "inferenceConfig": {
                "max_new_tokens": 4000,
                "temperature": 0.1
            }
        }
    elif 'openai' in model_id:
        body = {
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 4000,
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
    
    # LLM評価結果をパース（改良版）
    llm_scores = parse_llm_scores_improved(result_text)
    
    # スコアを統合
    enhanced_tags = []
    
    for tag in tag_scores:
        tag_id = tag['id']
        llm_score = llm_scores.get(tag_id, 0)
        
        # 最終スコア = 基本スコア + (LLMスコア × 重み)
        final_score = tag['score'] + (llm_score * 5)
        
        enhanced_tag = tag.copy()
        enhanced_tag['llm_score'] = llm_score
        enhanced_tag['final_score'] = final_score
        enhanced_tags.append(enhanced_tag)
    
    # LLMスコア重視でソート
    enhanced_tags.sort(key=lambda x: (x['llm_score'], x['final_score']), reverse=True)
    
    return enhanced_tags, cache_info

def evaluate_all_tags_with_llm_final(text, tag_scores, model_id):
    """LLMを使用して全100タグを評価（最終修正版）"""
    import boto3
    
    # 全100タグをLLM評価
    all_tags = tag_scores
    
    # タグリストを作成（シンプルな形式）
    tag_list = []
    for tag in all_tags:
        tag_list.append(f"{tag['id']}:{tag['name']}")
    
    tags_text = '\n'.join(tag_list)
    
    # LLMプロンプト（最も簡潔で明確）
    prompt = f"""記事内容に対して各タグの適合度を1-100で評価してください。

記事内容:
{text[:800]}

タグリスト:
{tags_text}

各タグIDに対して1-100のスコアを付けて、以下の形式で出力してください：
タグID:スコア

必ず全{len(all_tags)}個のタグすべてに対してスコアを付けてください。
説明は不要です。タグID:スコアの形式のみで出力してください。

評価基準: 90-100:核心テーマ, 80-89:強く関連, 70-79:明確に関連, 60-69:関連あり, 50-59:部分的関連, 40-49:弱い関連, 30-39:薄い関連, 20-29:ほぼ無関係, 10-19:無関係, 1-9:全く無関係
"""

    bedrock = boto3.client('bedrock-runtime')
    
    # モデル別のリクエスト形式（最大トークン数）
    if 'anthropic' in model_id:
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 8000,  # 最大に設定
            "temperature": 0.1,
            "messages": [{"role": "user", "content": prompt}]
        }
    elif 'amazon.nova' in model_id:
        body = {
            "messages": [{"role": "user", "content": [{"text": prompt}]}],
            "inferenceConfig": {
                "max_new_tokens": 8000,
                "temperature": 0.1
            }
        }
    elif 'openai' in model_id:
        body = {
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 8000,
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
    
    # LLM評価結果をパース（シンプル版）
    llm_scores = parse_llm_scores_final(result_text)
    
    # スコアを統合
    enhanced_tags = []
    
    for tag in tag_scores:
        tag_id = tag['id']
        llm_score = llm_scores.get(tag_id, 0)
        
        # 最終スコア = 基本スコア + (LLMスコア × 重み)
        final_score = tag['score'] + (llm_score * 5)
        
        enhanced_tag = tag.copy()
        enhanced_tag['llm_score'] = llm_score
        enhanced_tag['final_score'] = final_score
        enhanced_tags.append(enhanced_tag)
    
    # LLMスコア重視でソート
    enhanced_tags.sort(key=lambda x: (x['llm_score'], x['final_score']), reverse=True)
    
    return enhanced_tags, cache_info

def parse_llm_scores_final(result_text):
    """LLMの評価結果をパース（最終版）"""
    import re
    
    scores = {}
    
    # 行ごとに処理
    lines = result_text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        # 基本パターン: 数字:数字
        match = re.match(r'^(\d+):(\d+)$', line)
        if match:
            try:
                tag_id = match.group(1)
                score = int(match.group(2))
                if 1 <= score <= 100:
                    scores[tag_id] = score
            except ValueError:
                continue
    
    return scores

def create_summary(blog_text, model_id):
    """記事の要約を作成"""
    bedrock = boto3.client('bedrock-runtime')
    
    prompt = f"""以下の記事を300文字程度で要約してください。技術的なキーワードは残してください。

{blog_text[:3000]}"""
    
    if 'anthropic' in model_id:
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
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
    
    return result_text, cache_info
