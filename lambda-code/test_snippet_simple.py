#!/usr/bin/env python3
import json
import re
import collections

def extract_keywords(text, title=""):
    """テキストから主要キーワードを抽出"""
    combined_text = f"{title} {text}"
    tech_terms = re.findall(r'[A-Z][a-zA-Z]+|[ぁ-んァ-ヶー一-龯]{2,8}', combined_text)
    english_words = re.findall(r'[A-Za-z]{3,}', combined_text)
    japanese_words = re.findall(r'[ぁ-んァ-ヶー一-龯]{2,6}', combined_text)
    
    all_keywords = tech_terms + english_words + japanese_words
    
    stop_words = {
        'です', 'ます', 'した', 'する', 'ある', 'いる', 'なる', 'この', 'その',
        'から', 'まで', 'より', 'ため', 'について', 'として', 'による', 'こと',
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had'
    }
    
    filtered_keywords = [
        kw.lower() for kw in all_keywords 
        if len(kw) > 1 and kw.lower() not in stop_words
    ]
    
    keyword_counts = collections.Counter(filtered_keywords)
    unique_keywords = []
    for keyword, count in keyword_counts.most_common(20):
        if keyword not in unique_keywords:
            unique_keywords.append(keyword)
    
    return unique_keywords[:8]

def extract_conclusion_content(text):
    """記事の結論・まとめ部分を抽出"""
    conclusion_patterns = [
        r'##\s*まとめ[\s\S]*?(?=\n##|\n#|$)',
        r'##\s*最後に[\s\S]*?(?=\n##|\n#|$)', 
        r'まとめ\n\n[\s\S]*?(?=\n\n[^\n]|\n##|$)',
    ]
    
    conclusion_text = ""
    for pattern in conclusion_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            conclusion_text = matches[-1].strip()
            break
    
    if not conclusion_text:
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        if len(paragraphs) > 2:
            conclusion_text = paragraphs[-1]
    
    return conclusion_text

def format_two_sentence_snippet(text):
    """2文構成のスニペットを整形"""
    sentences = re.split(r'[。！？]', text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) >= 2:
        first_sentence = sentences[0] + "。"
        second_sentence = sentences[1] + "。"
        
        if len(first_sentence) > 80:
            first_sentence = first_sentence[:77] + "..."
        if len(second_sentence) > 80:
            second_sentence = second_sentence[:77] + "..."
            
        return first_sentence + second_sentence
    else:
        full_text = text.strip()
        if len(full_text) > 160:
            full_text = full_text[:157] + "..."
        return full_text

# テスト実行
title = "[アップデート] Amazon VPC IPAM（IP Address Manager）に追加されたプレフィックスリストリゾルバーを使ってマネージドプレフィックスリストのエントリ管理を自動化できるようになりました"

content = """いわさです。

Amazon VPC IPAM（IP Address Manager）は、AWSアカウント全体でIPアドレスの計画、追跡、監視を簡素化するサービスです。

今回、プレフィックスリストリゾルバーという新機能が追加され、マネージドプレフィックスリストのエントリ管理を自動化できるようになりました。

この機能により、IPアドレス管理の運用負荷を大幅に軽減し、ネットワーク設定の自動化が可能になります。

## まとめ

プレフィックスリストリゾルバーにより、IPアドレス管理の自動化が実現できました。これにより運用コストを大幅に削減し、ヒューマンエラーを防止できます。大規模なネットワーク環境での IP アドレス管理に革新をもたらす機能です。"""

full_text = f"{title}\n\n{content}"

print("=== Lambda関数コンポーネントテスト ===")

# キーワード抽出
keywords = extract_keywords(full_text, title)
print(f"抽出キーワード: {keywords}")

# 結論抽出
conclusion = extract_conclusion_content(full_text)
print(f"\n結論部分 ({len(conclusion)}文字):")
print(conclusion)

# 2文構成テスト
test_snippets = [
    "運用コスト大幅削減とヒューマンエラー防止を実現。設定手順と効果を詳しく解説します。",
    "IPアドレス管理の運用負荷を大幅軽減しネットワーク設定を自動化。CIDRブロック自動取得による具体的な設定方法と効果を詳しく解説します。"
]

print(f"\n=== 2文構成テスト ===")
for i, snippet in enumerate(test_snippets, 1):
    formatted = format_two_sentence_snippet(snippet)
    print(f"テスト{i} ({len(formatted)}文字): {formatted}")

# 期待される出力
expected_output = {
    "snippet": "IPアドレス管理の運用負荷を大幅軽減しヒューマンエラーを防止。CIDRブロック自動取得による設定手順と具体的な効果を詳しく解説します。",
    "cache_info": {"input_tokens": 150, "output_tokens": 50},
    "model_id": "us.amazon.nova-lite-v1:0"
}

print(f"\n=== 期待される出力形式 ===")
print(json.dumps(expected_output, ensure_ascii=False, indent=2))
