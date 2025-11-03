#!/usr/bin/env python3
import re

def format_two_sentence_snippet(text):
    """2文構成のスニペットを整形"""
    # 文を分割
    sentences = re.split(r'[。！？]', text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) >= 2:
        first_sentence = sentences[0] + "。"
        second_sentence = sentences[1] + "。"
        
        # 文字数調整
        if len(first_sentence) > 80:
            first_sentence = first_sentence[:77] + "..."
        if len(second_sentence) > 80:
            second_sentence = second_sentence[:77] + "..."
            
        return first_sentence + second_sentence
    else:
        # 1文の場合は適切に分割
        full_text = text.strip()
        if len(full_text) > 160:
            full_text = full_text[:157] + "..."
        return full_text

# テスト用スニペット
test_snippets = [
    "運用コストを大幅削減しヒューマンエラーを防止する自動化機能を実現。大規模ネットワーク環境でのIPアドレス管理に革新をもたらす設定手順と効果を詳しく解説します。",
    
    "IPアドレス管理の運用負荷を大幅軽減。CIDRブロック自動取得でネットワーク設定を効率化し手動作業不要で運用効率向上を実現する設定方法と具体例を詳しく解説します。",
    
    "プレフィックスリストリゾルバーによりIPアドレス管理を完全自動化。運用コスト削減とヒューマンエラー防止を同時に実現する革新的機能の導入手順を解説。"
]

print("=== 2文構成スニペットテスト ===")
for i, snippet in enumerate(test_snippets, 1):
    formatted = format_two_sentence_snippet(snippet)
    sentences = re.split(r'[。！？]', formatted)
    sentences = [s.strip() + "。" for s in sentences if s.strip()]
    
    print(f"\n--- テスト {i} ---")
    print(f"元の文字数: {len(snippet)}文字")
    print(f"整形後文字数: {len(formatted)}文字")
    
    if len(sentences) >= 2:
        print(f"第1文 ({len(sentences[0])}文字): {sentences[0]}")
        print(f"第2文 ({len(sentences[1])}文字): {sentences[1]}")
    else:
        print(f"全体: {formatted}")
    
    print(f"結果: {formatted}")

# 理想的な2文構成例
ideal_example = "運用コスト大幅削減とヒューマンエラー防止を実現。設定手順と効果を詳しく解説します。"
formatted_ideal = format_two_sentence_snippet(ideal_example)

print(f"\n=== 理想例 ===")
print(f"文字数: {len(formatted_ideal)}文字")
print(f"内容: {formatted_ideal}")

sentences = re.split(r'[。！？]', formatted_ideal)
sentences = [s.strip() + "。" for s in sentences if s.strip()]
if len(sentences) >= 2:
    print(f"第1文 ({len(sentences[0])}文字): {sentences[0]}")
    print(f"第2文 ({len(sentences[1])}文字): {sentences[1]}")
