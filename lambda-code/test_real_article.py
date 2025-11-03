#!/usr/bin/env python3
import json
import re
import collections

def extract_keywords(text, title=""):
    """テキストから主要キーワードを抽出"""
    # 結合テキスト
    combined_text = f"{title} {text}"
    
    # 技術用語・重要語句の抽出
    tech_terms = re.findall(r'[A-Z][a-zA-Z]+|[ぁ-んァ-ヶー一-龯]{2,8}', combined_text)
    
    # 英数字キーワード
    english_words = re.findall(r'[A-Za-z]{3,}', combined_text)
    
    # 日本語キーワード（2-6文字）
    japanese_words = re.findall(r'[ぁ-んァ-ヶー一-龯]{2,6}', combined_text)
    
    # 全キーワード結合
    all_keywords = tech_terms + english_words + japanese_words
    
    # ストップワード除去
    stop_words = {
        'です', 'ます', 'した', 'する', 'ある', 'いる', 'なる', 'れる', 'られる',
        'この', 'その', 'あの', 'どの', 'ここ', 'そこ', 'あそこ', 'どこ', 'では',
        'から', 'まで', 'より', 'ため', 'について', 'として', 'による', 'こと',
        'もの', 'とき', 'ところ', 'ので', 'けれど', 'しかし', 'でも', 'また',
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had',
        'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his',
        'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy'
    }
    
    # フィルタリング
    filtered_keywords = [
        kw.lower() for kw in all_keywords 
        if len(kw) > 1 and kw.lower() not in stop_words
    ]
    
    # 頻度カウント
    keyword_counts = collections.Counter(filtered_keywords)
    
    # 上位キーワード取得（重複除去）
    unique_keywords = []
    for keyword, count in keyword_counts.most_common(20):
        if keyword not in unique_keywords:
            unique_keywords.append(keyword)
    
    return unique_keywords[:8]

def create_snippet_prompt(text, title, keywords):
    """タイトル補完型のプロンプト生成"""
    keywords_text = "、".join(keywords)
    
    return f"""以下の記事から、Google検索結果用のスニペット（説明文）を作成してください。

タイトル: {title}

要件:
- 150-160文字以内
- タイトルと重複しない内容で補完する
- 記事の具体的な価値・メリットを明示
- 主要キーワードを含める: {keywords_text}
- 検索ユーザーの行動を促す表現

記事内容:
{text[:1000]}

タイトルを補完するスニペット:"""

# 実際の記事データでテスト
title = "[アップデート] Amazon VPC IPAM（IP Address Manager）に追加されたプレフィックスリストリゾルバーを使ってマネージドプレフィックスリストのエントリ管理を自動化できるようになりました"

content = """いわさです。

Amazon VPC IPAM（IP Address Manager）は、AWSアカウント全体でIPアドレスの計画、追跡、監視を簡素化するサービスです。

今回、プレフィックスリストリゾルバーという新機能が追加され、マネージドプレフィックスリストのエントリ管理を自動化できるようになりました。

この機能により、IPアドレス管理の運用負荷を大幅に軽減し、ネットワーク設定の自動化が可能になります。

プレフィックスリストリゾルバーは、IPAM プールから自動的にCIDRブロックを取得し、マネージドプレフィックスリストに追加します。これにより、手動でのIPアドレス管理作業が不要になり、運用効率が向上します。

設定方法や具体的な使用例について詳しく解説していきます。"""

keywords = extract_keywords(content, title)
prompt = create_snippet_prompt(content, title, keywords)

print("=== 記事タイトル ===")
print(title)
print(f"\n=== 抽出されたキーワード ===")
print(keywords)
print(f"\n=== 生成されたプロンプト ===")
print(prompt)

# 期待されるスニペット例を生成
expected_snippet = "IPアドレス管理の運用負荷を大幅軽減。CIDRブロック自動取得でネットワーク設定を効率化。手動作業不要で運用効率向上を実現する設定方法と具体例を詳しく解説します。"

print(f"\n=== 期待されるスニペット例 ===")
print(f"文字数: {len(expected_snippet)}文字")
print(expected_snippet)
