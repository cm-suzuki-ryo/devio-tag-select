#!/usr/bin/env python3
import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add lambda-code to path
sys.path.append('lambda-code')

def test_summary_lambda():
    """要約Lambda関数のテスト"""
    from summary_lambda import lambda_handler as summary_handler
    
    # テスト用記事ID
    test_event = {
        'article_id': 'saichan-transition-IMDSv2-netshtrace-20251031',
        'model_id': os.getenv('MODEL_ID')
    }
    
    print("=== 要約Lambda テスト ===")
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

def test_tag_selector_lambda_mock():
    """タグ選択Lambda関数のテスト（要約Lambda呼び出しをモック）"""
    from tag_selector_lambda import lambda_handler as tag_handler
    
    # 要約Lambda呼び出しをモック化
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
    
    # モック関数を適用
    tag_selector_lambda.call_summary_lambda = mock_call_summary_lambda
    
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
    
    print("🚀 分離Lambda関数テスト開始")
    
    # 要約Lambdaテスト
    summary_result = test_summary_lambda()
    
    if summary_result:
        # タグ選択Lambdaテスト
        tag_result = test_tag_selector_lambda_mock()
        
        if tag_result:
            print("\n🎉 全テスト完了")
        else:
            print("\n❌ タグ選択テスト失敗")
    else:
        print("\n❌ 要約テスト失敗")
