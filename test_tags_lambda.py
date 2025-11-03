#!/usr/bin/env python3
import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add lambda-code to path
sys.path.append('lambda-code')

def test_tags_lambda_standalone():
    """タグ取得Lambda関数の単体テスト"""
    from tags_lambda import lambda_handler as tags_handler
    
    print("🚀 タグ取得Lambda 単体テスト開始")
    print(f"Contentful Access Token: {os.getenv('CONTENTFUL_ACCESS_TOKEN')[:10]}...")
    print(f"Contentful Space ID: {os.getenv('CONTENTFUL_SPACE_ID', 'ct0aopd36mqt')}")
    
    try:
        result = tags_handler({}, {})
        
        print(f"ステータスコード: {result['statusCode']}")
        
        if result['statusCode'] == 200:
            body = json.loads(result['body'])
            print(f"✅ タグ取得成功")
            print(f"タグ数: {body['tags_count']}")
            print(f"ハッシュ: {body['tags_hash']}")
            print(f"タイムスタンプ: {body['timestamp']}")
            
            # 最初の5つのタグを表示
            if body['tags_data']:
                print("\n📋 取得されたタグ（最初の5つ）:")
                for i, tag in enumerate(body['tags_data'][:5]):
                    print(f"  {i+1}. ID: {tag['id']}, Name: {tag['name']}")
                
                if len(body['tags_data']) > 5:
                    print(f"  ... 他 {len(body['tags_data']) - 5} タグ")
            
            return True
        else:
            body = json.loads(result['body'])
            print(f"❌ エラー: {body.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ 例外発生: {str(e)}")
        return False

if __name__ == "__main__":
    # 環境変数チェック
    if not os.getenv('CONTENTFUL_ACCESS_TOKEN'):
        print("❌ CONTENTFUL_ACCESS_TOKEN環境変数が設定されていません")
        print("📝 .envファイルを確認してください")
        sys.exit(1)
    
    success = test_tags_lambda_standalone()
    
    if success:
        print("\n🎉 タグ取得Lambdaテスト完了")
    else:
        print("\n❌ タグ取得Lambdaテスト失敗")
        sys.exit(1)
