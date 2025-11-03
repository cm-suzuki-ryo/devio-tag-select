#!/usr/bin/env python3
"""
記事添削Lambda関数の簡易テストスクリプト（boto3直接実行）
"""

import json
import boto3
import os

def test_article_review_direct():
    """記事添削機能の直接テスト"""
    
    # テスト用記事データ
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
    
    print("🔍 記事添削テスト開始...")
    print(f"📝 記事タイトル: {test_article['title'][:50]}...")
    print(f"📄 記事文字数: {len(test_article['content'])}文字")
    print(f"🤖 使用モデル: global.anthropic.claude-haiku-4-5-20251001-v1:0")
    print("-" * 80)
    
    try:
        # Bedrock直接呼び出し
        bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
        
        article_json = {"title": test_article["title"], "content": test_article["content"]}
        
        prompt = f"""# 役割と目標
あなたは、テックブログの**「編集者と校正役」**です。
提供されたJSON形式の記事データ（タイトルと本文）を、技術的な正確性を保ちつつ、**検索性・可読性・説得力**を高めるために編集サポートをします。
読者は**AWSの基礎知識を持つ技術者**と想定し、**建設的なトーン**を維持してください。

# 実行手順と出力形式

以下の順序でフィードバックを構成し、Markdownを使って構造化して出力すること。

## 1. 🌟 全体的なフィードバック
* 記事の**技術的正確性、構成、検証の流れ**について簡潔に評価する。

## 2. 📝 表記と文法の編集
* 修正提案を必ず**表形式**（オリジナル/提案/理由）で出力する。
* **冗長表現、口語表現、文法ミス**（句読点、助詞の重複）、**専門用語の表記統一**を指摘し、修正案を提示する。

## 3. 💡 構成とタイトルの改善提案
* **タイトル:** 長すぎるタイトルを指摘し、SEO/可読性を考慮した**複数の代替案**を提案する。
* **概要（スニペット）:** 記事の価値を伝える**100字程度**の概要文を新規に作成して提案する。
* **導入:** 読者の関心を引く**「課題提起」**を冒頭に追加する工夫を提案する。

## 4. ✅ 最終確認
* 最後に、他にサポートが必要な点がないかユーザーに尋ねること。

# 記事データ
{json.dumps(article_json, ensure_ascii=False, indent=2)}"""
        
        # Claude Haiku 4.5で実行
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 8192,
            "temperature": 0.3,
            "system": [{"type": "text", "text": "あなたはテックブログの編集者と校正役です。"}],
            "messages": [{"role": "user", "content": prompt}]
        }
        
        response = bedrock.invoke_model(
            modelId='global.anthropic.claude-haiku-4-5-20251001-v1:0', 
            body=json.dumps(body)
        )
        response_body = json.loads(response['body'].read())
        review_feedback = response_body['content'][0]['text']
        
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
        
        # トークン使用量
        usage = response_body.get('usage', {})
        print(f"\n📈 トークン使用量:")
        print(f"  入力: {usage.get('input_tokens', 0)} tokens")
        print(f"  出力: {usage.get('output_tokens', 0)} tokens")
        print(f"  フィードバック文字数: {len(review_feedback)} 文字")
            
    except Exception as e:
        print(f"❌ テスト失敗: {str(e)}")

if __name__ == "__main__":
    test_article_review_direct()
