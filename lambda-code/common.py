import json
import hashlib
import urllib3
import os
import re

# グローバル変数でキャッシュ
TAGS_CACHE = None
TAGS_HASH = None

def get_article_from_contentful(slug):
    """Contentfulから記事を取得"""
    http = urllib3.PoolManager()
    access_token = os.environ.get('CONTENTFUL_ACCESS_TOKEN')
    url = f"https://cdn.contentful.com/spaces/ct0aopd36mqt/entries?limit=1&fields.slug={slug}&locale=ja&access_token={access_token}&content_type=blogPost&select=fields.content,fields.title"
    
    response = http.request('GET', url)
    data = json.loads(response.data.decode('utf-8'))
    
    if data.get('items') and len(data['items']) > 0:
        fields = data['items'][0].get('fields', {})
        title = fields.get('title', '')
        content = fields.get('content', '')
        return f"{title}\n\n{content}"
    
    return None

def get_tags_from_contentful_cached():
    """Contentfulからタグ一覧を取得（キャッシュ付き）"""
    global TAGS_CACHE, TAGS_HASH
    
    if TAGS_CACHE and TAGS_HASH:
        return TAGS_CACHE, TAGS_HASH
    
    http = urllib3.PoolManager()
    access_token = os.environ.get('CONTENTFUL_ACCESS_TOKEN')
    url = f"https://cdn.contentful.com/spaces/ct0aopd36mqt/entries?limit=1&select=fields.tags&access_token={access_token}&content_type=blogTags"
    
    response = http.request('GET', url)
    data = json.loads(response.data.decode('utf-8'))
    
    tags_data = []
    if data.get('items') and len(data['items']) > 0:
        tags = data['items'][0].get('fields', {}).get('tags', [])
        for tag in tags:
            tags_data.append({
                'id': tag.get('id'),
                'name': tag.get('name')
            })
    
    content_str = json.dumps(tags_data, sort_keys=True)
    content_hash = hashlib.md5(content_str.encode('utf-8')).hexdigest()
    
    TAGS_CACHE = tags_data
    TAGS_HASH = content_hash
    
    return tags_data, content_hash

def pre_filter_tags(blog_text, all_tags, max_tags=1000):
    """記事内容に基づいてタグを事前フィルタリング"""
    blog_lower = blog_text.lower()
    keywords = re.findall(r'[A-Za-z0-9]+|[ぁ-んァ-ヶ一-龯]+', blog_text)
    keywords = [k.lower() for k in keywords if len(k) >= 2]
    
    scored_tags = []
    max_score = 0
    
    for tag in all_tags:
        tag_id = str(tag.get('id', ''))
        tag_name = tag.get('name', '')
        
        if not tag_id or not tag_name:
            continue
            
        tag_name_lower = tag_name.lower()
        
        score = 0
        if tag_name_lower in blog_lower:
            score += 10
        
        for keyword in keywords:
            if keyword in tag_name_lower or tag_name_lower in keyword:
                score += 5
        
        for word in tag_name_lower.split():
            if len(word) >= 2 and word in blog_lower:
                score += 2
        
        if score > 0:
            scored_tags.append((score, f"{tag_id}\t{tag_name}", tag_id, tag_name))
            max_score = max(max_score, score)
    
    scored_tags.sort(reverse=True, key=lambda x: x[0])
    
    # タグ情報とスコア情報を分けて返す
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

def calculate_cost(model_id, cache_info):
    """モデル使用料金を計算"""
    usd_to_jpy = 150
    input_tokens = cache_info.get('input_tokens', 0)
    output_tokens = cache_info.get('output_tokens', 0)
    
    pricing = {
        'us.anthropic.claude-haiku-4-5-20251001-v1:0': {'input': 0.25, 'output': 1.25},
        'us.amazon.nova-lite-v1:0': {'input': 0.06, 'output': 0.24},
        'openai.gpt-oss-20b-1:0': {'input': 0.15, 'output': 0.6}
    }
    
    if model_id not in pricing:
        return {'error': 'Unknown model pricing'}
    
    model_pricing = pricing[model_id]
    input_cost_usd = (input_tokens / 1_000_000) * model_pricing['input']
    output_cost_usd = (output_tokens / 1_000_000) * model_pricing['output']
    total_cost_usd = input_cost_usd + output_cost_usd
    
    input_cost_jpy = input_cost_usd * usd_to_jpy
    output_cost_jpy = output_cost_usd * usd_to_jpy
    total_cost_jpy = total_cost_usd * usd_to_jpy
    
    result = {
        'input_cost_jpy': round(input_cost_jpy, 4),
        'output_cost_jpy': round(output_cost_jpy, 4),
        'total_cost_jpy': round(total_cost_jpy, 4),
        'exchange_rate': usd_to_jpy
    }
    
    # 要約使用時の詳細コスト
    if cache_info.get('used_summary'):
        summary_input = cache_info.get('summary_input_tokens', 0)
        summary_output = cache_info.get('summary_output_tokens', 0)
        tag_input = cache_info.get('tag_input_tokens', 0)
        tag_output = cache_info.get('tag_output_tokens', 0)
        
        # 要約作成コスト（Claude Haiku固定）
        haiku_pricing = pricing['us.anthropic.claude-haiku-4-5-20251001-v1:0']
        summary_cost_usd = (summary_input / 1_000_000) * haiku_pricing['input'] + (summary_output / 1_000_000) * haiku_pricing['output']
        
        # タグ選択コスト
        tag_cost_usd = (tag_input / 1_000_000) * model_pricing['input'] + (tag_output / 1_000_000) * model_pricing['output']
        
        result['summary_cost_jpy'] = round(summary_cost_usd * usd_to_jpy, 4)
        result['tag_selection_cost_jpy'] = round(tag_cost_usd * usd_to_jpy, 4)
    
    return result

def extract_tags_from_response(result_text, model_id):
    """レスポンスからタグを抽出"""
    try:
        if 'openai' in model_id:
            # OpenAI用：<thinking>タグの外側のJSONを探す
            thinking_pattern = r'</thinking>\s*(\{[^{}]*"tags"[^{}]*\[[^\]]*\][^{}]*\})'
            thinking_match = re.search(thinking_pattern, result_text)
            if thinking_match:
                json_str = thinking_match.group(1)
                tags = json.loads(json_str)['tags']
                return tags if tags else []
            
            # フォールバック：通常のJSONパターン
            json_matches = re.findall(r'\{[^{}]*"tags"[^{}]*\[[^\]]*\][^{}]*\}', result_text)
            if json_matches:
                json_str = json_matches[-1]
                tags = json.loads(json_str)['tags']
                return tags if tags else []
        
        # Nova、Haiku用：従来の方法
        start = result_text.find('{')
        end = result_text.rfind('}') + 1
        if start >= 0 and end > start:
            json_str = result_text[start:end]
            tags = json.loads(json_str)['tags']
            return tags if tags else []
        
    except Exception as e:
        pass
    
    return []
