#!/usr/bin/env python3
import re

def extract_conclusion_content(text):
    """記事の結論・まとめ部分を抽出"""
    # 結論セクションのキーワード
    conclusion_patterns = [
        r'##\s*まとめ[\s\S]*?(?=\n##|\n#|$)',
        r'##\s*最後に[\s\S]*?(?=\n##|\n#|$)', 
        r'##\s*さいごに[\s\S]*?(?=\n##|\n#|$)',
        r'##\s*終わりに[\s\S]*?(?=\n##|\n#|$)',
        r'##\s*おわりに[\s\S]*?(?=\n##|\n#|$)',
        r'##\s*結論[\s\S]*?(?=\n##|\n#|$)',
        r'まとめ\n\n[\s\S]*?(?=\n\n[^\n]|\n##|$)',
        r'最後に\n\n[\s\S]*?(?=\n\n[^\n]|\n##|$)',
        r'さいごに\n\n[\s\S]*?(?=\n\n[^\n]|\n##|$)'
    ]
    
    conclusion_text = ""
    for pattern in conclusion_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            conclusion_text = matches[-1].strip()  # 最後のマッチを使用
            break
    
    # 結論が見つからない場合は最後の段落を使用
    if not conclusion_text:
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        if len(paragraphs) > 2:
            conclusion_text = paragraphs[-1]  # 最後の段落
    
    return conclusion_text

# テスト用記事
test_article = """
Amazon VPC IPAM��IP Address Manager）は、AWSアカウント全体でIPアドレスの計画、追跡、監視を簡素化するサービスです。

今回、プレフィックスリストリゾルバーという新機能が追加され、マネージドプレフィックスリストのエントリ管理を自動化できるようになりました。

この機能により、IPアドレス管理の運用負荷を大幅に軽減し、ネットワーク設定の自動化が可能になります。

プレフィックスリストリゾルバーは、IPAM プールから自動的にCIDRブロックを取得し、マネージドプレフィックスリストに追加します。

## 設定手順

1. IPAM プールを作成
2. プレフィックスリストリゾルバーを設定
3. 自動化ルールを定義

## まとめ

プレフィックスリストリゾルバーにより、IPアドレス管理の自動化が実現できました。これにより運用コストを大幅に削減し、ヒューマンエラーを防止できます。大規模なネットワーク環境での IP アドレス管理に革新をもたらす機能です。
"""

conclusion = extract_conclusion_content(test_article)

print("=== 抽出された結論部分 ===")
print(conclusion)
print(f"\n文字数: {len(conclusion)}文字")

# 結論ベースのスニペット例
conclusion_based_snippet = "運用コスト大幅削減とヒューマンエラー防止を実現。大規模ネットワーク環境でのIPアドレス管理に革新をもたらす自動化機能の設定手順と効果を詳しく解説します。"

print(f"\n=== 結論重視スニペット例 ===")
print(f"文字数: {len(conclusion_based_snippet)}文字")
print(conclusion_based_snippet)
