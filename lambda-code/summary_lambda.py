import json
import os
from claude_model import create_summary_with_claude
from nova_model import create_summary_with_nova
from gpt_model import create_summary_with_gpt

def create_summary_by_model(blog_text, model_id):
    """モデルに応じて要約を作成"""
    if 'claude' in model_id.lower():
        return create_summary_with_claude(blog_text, model_id)
    elif 'nova' in model_id.lower():
        return create_summary_with_nova(blog_text, model_id)
    elif 'gpt' in model_id.lower():
        return create_summary_with_gpt(blog_text, model_id)
    else:
        raise ValueError(f"Unsupported model for summary: {model_id}")

def lambda_handler(event, context):
    """要約専用Lambda関数のハンドラー"""
    try:
        # パラメータ取得
        model_id = event.get('model_id', os.environ.get('MODEL_ID'))
        blog_text = event.get('blog_text')
        
        # 記事テキスト必須チェック
        if not blog_text:
            raise ValueError("blog_text is required")
        
        # 要約作成
        summary_text, cache_info = create_summary_by_model(blog_text, model_id)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'summary_text': summary_text,
                'cache_info': cache_info,
                'model_id': model_id
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            }, ensure_ascii=False)
        }
        }
