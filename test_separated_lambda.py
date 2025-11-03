#!/usr/bin/env python3
import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add lambda-code to path
sys.path.append('lambda-code')

def test_tags_lambda():
    """タグ取得Lambda関数のテスト"""
    from tags_lambda import lambda_handler as tags_handler
    
    print("=== タグ取得Lambda テスト ===")
    print(f"Contentful Space ID: {os.getenv('CONTENTFUL_SPACE_ID', 'ct0aopd36mqt')}")
    
    try:
        result = tags_handler({}, {})
        
        if result['statusCode'] == 200:
            body = json.loads(result['body'])
            print(f"✅ タグ取得成功")
            print(f"タグ数: {body['tags_count']}")
            print(f"ハッシュ: {body['tags_hash'][:8]}...")
            return body['tags_data']
        else:
            print(f"❌ エラー: {result['body']}")
            return None
            
    except Exception as e:
        print(f"❌ 例外発生: {str(e)}")
        return None

def test_summary_lambda():
    """要約Lambda関数のテスト"""
    from summary_lambda import lambda_handler as summary_handler
    
    # テスト用記事ID
    test_event = {
        'article_id': 'saichan-transition-IMDSv2-netshtrace-20251031',
        'model_id': os.getenv('MODEL_ID')
    }
    
    print("\n=== 要約Lambda テスト ===")
    print(f"記事ID: {test_event['article_id']}")
    print(f"モデル: {test_event['model_id']}")
    
    try:
        result = summary_handler(test_event, {})
        
        if result['statusCode'] == 200:
            body = json.loads(result['body'])
            print(f"✅ 要約作成成功")
            print(f"要約文字数: {len(body['summary_text'])}文字")
            print(f"入力トークン: {body['cache_info'].get('input_tokens', 0)}")
            print(f"出力トークン: {body['cache_info'].get('output_tokens', 0)}")
            return body
        else:
            print(f"❌ エラー: {result['body']}")
            return None
            
    except Exception as e:
        print(f"❌ 例外発生: {str(e)}")
        return None

def test_tag_selector_lambda_mock(tags_data):
    """タグ選択Lambda関数のテスト（Lambda呼び出しをモック）"""
    from tag_selector_lambda import lambda_handler as tag_handler
    
    # Lambda呼び出しをモック化
    import tag_selector_lambda
    
    def mock_call_summary_lambda(article_id=None, blog_text=None, model_id=None):
        # 実際の要約Lambdaの代わりにローカル実行
        from summary_lambda import lambda_handler as summary_handler
        
        event = {'model_id': model_id}
        if article_id:
            event['article_id'] = article_id
        if blog_text:
            event['blog_text'] = blog_text
            
        result = summary_handler(event, {})
        body = json.loads(result['body'])
        return body['summary_text'], body['cache_info']
    
    def mock_call_tags_lambda():
        # 実際のタグデータまたはモックデータを返す
        return tags_data if tags_data else [
            {"id": "1", "name": "AWS"},
            {"id": "2", "name": "EC2"},
            {"id": "3", "name": "Lambda"},
            {"id": "4", "name": "Python"},
            {"id": "5", "name": "Docker"}
        ]
    
    # モック関数を適用
    tag_selector_lambda.call_summary_lambda = mock_call_summary_lambda
    tag_selector_lambda.call_tags_lambda = mock_call_tags_lambda
    
    # テスト実行
    test_event = {
        'article_id': 'saichan-transition-IMDSv2-netshtrace-20251031',
        'model_id': os.getenv('MODEL_ID')
    }
    
    print("\n=== タグ選択Lambda テスト（モック版） ===")
    print(f"記事ID: {test_event['article_id']}")
    print(f"モデル: {test_event['model_id']}")
    
    try:
        result = tag_handler(test_event, {})
        
        if result['statusCode'] == 200:
            body = json.loads(result['body'])
            print(f"✅ タグ選択成功")
            print(f"選択タグ数: {len(body['selected_tags'])}")
            print(f"総コスト: {body['cost_info'].get('total_cost_jpy', 0)}円")
            # タグ名を抽出して表示
            tag_names = []
            for tag in body['selected_tags'][:10]:
                if isinstance(tag, dict):
                    tag_names.append(tag.get('name', str(tag)))
                else:
                    tag_names.append(str(tag))
            print(f"選択されたタグ: {', '.join(tag_names)}...")
            return body
        else:
            print(f"❌ エラー: {result['body']}")
            return None
            
    except Exception as e:
        print(f"❌ 例外発生: {str(e)}")
        return None

if __name__ == "__main__":
    # 環境変数チェック
    required_vars = ['CONTENTFUL_ACCESS_TOKEN', 'MODEL_ID']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ 必要な環境変数が設定されていません: {missing_vars}")
        print("📝 .envファイルを確認してください")
        sys.exit(1)
    
    print("🚀 3分離Lambda関数テスト開始")
    
    # タグ取得Lambdaテスト
    tags_data = test_tags_lambda()
    
    # 要約Lambdaテスト
    summary_result = test_summary_lambda()
    
    if summary_result:
        # タグ選択Lambdaテスト
        tag_result = test_tag_selector_lambda_mock(tags_data)
        
        if tag_result:
            print("\n🎉 全テスト完了")
            print(f"📊 アーキテクチャ: タグ取得Lambda → 要約Lambda → タグ選択Lambda")
        else:
            print("\n❌ タグ選択テスト失敗")
    else:
        print("\n❌ 要約テスト失敗")
