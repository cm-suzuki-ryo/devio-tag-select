import json
import os
import time
import urllib3
import hashlib

def get_tags_from_contentful():
    """Contentfulからタグ一覧を取得"""
    access_token = os.environ.get('CONTENTFUL_ACCESS_TOKEN')
    if not access_token:
        raise ValueError("CONTENTFUL_ACCESS_TOKEN environment variable is required")
    
    space_id = os.environ.get('CONTENTFUL_SPACE_ID', 'ct0aopd36mqt')
    http = urllib3.PoolManager()
    
    # タグ一覧を取得
    url = f"https://cdn.contentful.com/spaces/{space_id}/entries?limit=1&select=fields.tags&access_token={access_token}&content_type=blogTags"
    
    response = http.request('GET', url)
    if response.status != 200:
        raise Exception(f"Contentful API error: {response.status}")
    
    data = json.loads(response.data.decode('utf-8'))
    
    # タグデータを抽出
    tags_data = []
    if data.get('items') and len(data['items']) > 0:
        fields = data['items'][0].get('fields', {})
        tags_list = fields.get('tags', [])
        
        for i, tag_obj in enumerate(tags_list):
            if tag_obj and isinstance(tag_obj, dict):
                tag_name = tag_obj.get('name', '')
                if tag_name:
                    tags_data.append({
                        'id': str(i + 1),
                        'name': tag_name
                    })
    
    # ハッシュ値計算
    content_str = json.dumps(tags_data, sort_keys=True, ensure_ascii=False)
    content_hash = hashlib.md5(content_str.encode('utf-8')).hexdigest()
    
    return tags_data, content_hash

def lambda_handler(event, context):
    """タグ取得専用Lambda関数のハンドラー"""
    try:
        # タグデータ取得
        tags_data, tags_hash = get_tags_from_contentful()
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'tags_data': tags_data,
                'tags_hash': tags_hash,
                'tags_count': len(tags_data),
                'timestamp': time.time()
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            }, ensure_ascii=False)
        }
