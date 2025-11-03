#!/usr/bin/env python3
"""
記事添削Lambda関数のテストスクリプト
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from article_review_lambda import lambda_handler
from common import get_article_from_contentful

def test_article_review():
    """記事添削機能のテスト"""
    
    # テスト用記事データ（短縮版）
    test_article = {
        "title": "[アップデート] Amazon VPC IPAM（IP Address Manager）に追加されたプレフィックスリストリゾルバーを使ってマネージドプレフィックスリストのエントリ管理を自動化できるようになりました",
        "content": """いわさです。

Amazon VPC ではマネージドプレフィックスリストを使って IP アドレス範囲をリストとしてまとめることができます。
このリストをセキュリティグループやルートテーブルに使用することが出来るので同じ IP アドレスを様々な場所で定義してしまう場合にメンテナンス性を高めることができます。

この IP アドレスのリストですが、カスタマーマネージドプレフィックスリストの場合はエントリを手動でメンテナンスする必要があったのですが、先日のアップデートで Amazon VPC IPAM（IP Address Manager）を使ってマネージドプレフィックスリストのエントリを自動更新できるようになりました。

VPC IPAM では特定のスコープに設定した、組織内のワークロードの IP アドレスを管理することが出来るサービスです。

VPC IPAM で検出/管理されている IP アドレスから特定条件に該当する IP アドレスをカスタマーマネージドプレフィックスリストに同期できるようになっています。
使ってみましたので紹介します。"""
    }
    
    # テストイベント作成
    event = {
        "title": test_article["title"],
        "content": test_article["content"],
        "model_id": "global.anthropic.claude-haiku-4-5-20251001-v1:0"
    }
    
    print("🔍 記事添削テスト開始...")
    print(f"📝 記事タイトル: {test_article['title'][:50]}...")
    print(f"📄 記事文字数: {len(test_article['content'])}文字")
    print(f"🤖 使用モデル: {event['model_id']}")
    print("-" * 80)
    
    try:
        # Lambda関数実行
        result = lambda_handler(event, {})
        
        if result['statusCode'] == 200:
            body = json.loads(result['body'])
            review_feedback = body['review_feedback']
            
            print("✅ 記事添削成功!")
            print("\n📋 添削フィードバック:")
            print("=" * 80)
            print(review_feedback)
            print("=" * 80)
            
            # フィードバック内容の確認
            required_sections = ["🌟 全体的なフィードバック", "📝 表記と文法の編集", "💡 構成とタイトルの改善提案", "✅ 最終確認"]
            found_sections = []
            
            for section in required_sections:
                if section in review_feedback:
                    found_sections.append(section)
            
            print(f"\n📊 構成チェック: {len(found_sections)}/{len(required_sections)} セクション確認")
            for section in found_sections:
                print(f"  ✅ {section}")
            
            for section in required_sections:
                if section not in found_sections:
                    print(f"  ❌ {section}")
            
        else:
            print(f"❌ エラー: {result['body']}")
            
    except Exception as e:
        print(f"❌ テスト失敗: {str(e)}")

def test_with_contentful_article():
    """Contentfulから取得した記事でテスト"""
    print("\n🌐 Contentful記事での添削テスト...")
    
    # 実際の記事を取得
    article_text = get_article_from_contentful("vpc-ipam-prefix-list-automation")
    
    if article_text:
        lines = article_text.split('\n', 1)
        title = lines[0] if lines else ""
        content = lines[1] if len(lines) > 1 else ""
        
        event = {
            "title": title,
            "content": content[:2000],  # 長すぎる場合は短縮
            "model_id": "global.anthropic.claude-haiku-4-5-20251001-v1:0"
        }
        
        print(f"📝 記事タイトル: {title}")
        print(f"📄 記事文字数: {len(content)}文字（テスト用に{len(event['content'])}文字に短縮）")
        
        try:
            result = lambda_handler(event, {})
            
            if result['statusCode'] == 200:
                body = json.loads(result['body'])
                print("✅ Contentful記事添削成功!")
                print(f"📋 フィードバック文字数: {len(body['review_feedback'])}文字")
            else:
                print(f"❌ エラー: {result['body']}")
                
        except Exception as e:
            print(f"❌ テスト失敗: {str(e)}")
    else:
        print("❌ Contentful記事取得失敗")

if __name__ == "__main__":
    test_article_review()
    test_with_contentful_article()
