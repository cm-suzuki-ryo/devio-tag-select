#!/usr/bin/env python3
import json
import sys
import os

# Lambda関数をインポート
sys.path.append(os.path.dirname(__file__))
from snippet_generator_lambda import lambda_handler, extract_keywords, extract_conclusion_content, format_two_sentence_snippet

def test_lambda_function():
    """Lambda関数のテスト"""
    
    # テスト用イベント
    test_event = {
        "title": "[アップデート] Amazon VPC IPAM（IP Address Manager）に追加されたプレフィックスリストリゾルバーを使ってマネージドプレフィックスリストのエントリ管理を自動化できるようになりました",
        "content": """いわさです。

Amazon VPC IPAM（IP Address Manager）は、AWSアカウント全体でIPアドレスの計画、追跡、監視を簡素化するサービスです。

今回、プレフィックスリストリゾルバーという新機能が追加され、マネージドプレフィックスリストのエントリ管理を自動化できるようになりました。

この機能により、IPアドレス管理の運用負荷を大幅に軽減し、ネットワーク設定の自動化が可能になります。

プレフィックスリストリゾルバーは、IPAM プールから自動的にCIDRブロックを取得し、マネージドプレフィックスリストに追加します。これにより、手動でのIPアドレス管理作業が不要になり、運用効率が向上します。

## まとめ

プレフィックスリストリゾルバーにより、IPアドレス管理の自動化が実現できました。これにより運用コストを大幅に削減し、ヒューマンエラーを防止できます。大規模なネットワーク環境での IP アドレス管理に革新をもたらす機能です。

設定方法や具体的な使用例について詳しく解説していきます。""",
        "model_id": "us.amazon.nova-lite-v1:0"
    }
    
    print("=== Lambda関数テスト ===")
    print(f"タイトル: {test_event['title'][:50]}...")
    print(f"コンテンツ長: {len(test_event['content'])}文字")
    
    # 各機能のテスト
    full_text = f"{test_event['title']}\n\n{test_event['content']}"
    
    # キーワード抽出テスト
    keywords = extract_keywords(full_text, test_event['title'])
    print(f"\n抽出キーワード: {keywords[:5]}")
    
    # 結論抽出テスト
    conclusion = extract_conclusion_content(full_text)
    print(f"\n結論部分 ({len(conclusion)}文字): {conclusion[:100]}...")
    
    # 2文構成テスト
    sample_snippet = "運用コスト大幅削減とヒューマンエラー防止を実現。設定手順と効果を詳しく解説します。"
    formatted = format_two_sentence_snippet(sample_snippet)
    print(f"\n2文構成例: {formatted}")
    
    print("\n=== 期待される出力形式 ===")
    expected_output = {
        "snippet": "IPアドレス管理の運用負荷を大幅軽減しヒューマンエラーを防止。CIDRブロック自動取得による設定手順と具体的な効果を詳しく解説します。",
        "cache_info": {
            "input_tokens": 150,
            "output_tokens": 50
        },
        "model_id": "us.amazon.nova-lite-v1:0"
    }
    
    print(json.dumps(expected_output, ensure_ascii=False, indent=2))
    
    # 実際のLambda関数呼び出しはAWS環境でのみ可能
    print("\n注意: 実際のAI生成はAWS Bedrock環境でのみ実行可能です")

if __name__ == "__main__":
    test_lambda_function()
