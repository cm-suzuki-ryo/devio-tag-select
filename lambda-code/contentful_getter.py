import json
import requests
import os

def lambda_handler(event, context):
    try:
        slug = event['slug']
        model_id = event.get('model_id', 'us.amazon.nova-lite-v1:0')
        
        # Contentful API呼び出し
        space_id = os.environ['CONTENTFUL_SPACE_ID']
        access_token = os.environ['CONTENTFUL_ACCESS_TOKEN']
        
        url = f"https://cdn.contentful.com/spaces/{space_id}/entries"
        params = {
            'access_token': access_token,
            'content_type': 'blogPost',
            'fields.slug': slug,
            'limit': 1
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if not data['items']:
            raise Exception(f"Article not found: {slug}")
        
        item = data['items'][0]['fields']
        title = item.get('title', '')
        content = item.get('content', '')
        blog_text = f"{title}\n\n{content}"
        
        return {
            'blog_text': blog_text,
            'text_length': len(blog_text),
            'model_id': model_id
        }
        
    except Exception as e:
        raise Exception(f"Failed to get article: {str(e)}")
