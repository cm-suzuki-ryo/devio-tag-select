import re
import os
import json
import urllib3
import hashlib

# MeCabのインポート（フォールバック付き）
try:
    import MeCab
    MECAB_AVAILABLE = True
    tagger = MeCab.Tagger('-Owakati')
except ImportError:
    MECAB_AVAILABLE = False
    tagger = None

def tokenize_japanese(text):
    """日本語テキストの形態素解析"""
    if MECAB_AVAILABLE and tagger:
        try:
            result = tagger.parse(text).strip()
            return result.split()
        except:
            pass
    
    # フォールバック: 簡易分割
    return simple_japanese_split(text)

def simple_japanese_split(text):
    """MeCabなしでの簡易日本語分割"""
    tokens = []
    current_token = ""
    current_type = None
    
    for char in text:
        char_type = get_char_type(char)
        
        if char_type != current_type:
            if current_token and len(current_token) >= 2:
                tokens.append(current_token)
            current_token = char
            current_type = char_type
        else:
            current_token += char
    
    if current_token and len(current_token) >= 2:
        tokens.append(current_token)
    
    return tokens

def get_char_type(char):
    """文字種別を判定"""
    if re.match(r'[ぁ-ん]', char):
        return 'hiragana'
    elif re.match(r'[ァ-ヶ]', char):
        return 'katakana'
    elif re.match(r'[一-龯]', char):
        return 'kanji'
    elif re.match(r'[A-Za-z0-9]', char):
        return 'ascii'
    else:
        return 'other'

def extract_keywords_with_mecab(text):
    """MeCabを使用してキーワードを抽出"""
    # 英数字キーワード
    english_keywords = re.findall(r'[A-Za-z0-9]+', text)
    english_keywords = [k.lower() for k in english_keywords if len(k) >= 2]
    
    # 日本語キーワード（MeCab処理）
    japanese_text = re.sub(r'[A-Za-z0-9\s]+', '', text)
    japanese_keywords = tokenize_japanese(japanese_text)
    japanese_keywords = [k.lower() for k in japanese_keywords if len(k) >= 2]
    
    return english_keywords + japanese_keywords

def split_tag_name(tag_name):
    """タグ名を適切に分割（日本語・英語対応）"""
    words = []
    
    # スペース区切りで分割
    space_parts = tag_name.split()
    
    for part in space_parts:
        if re.match(r'^[A-Za-z0-9]+$', part):
            # 英数字のみ
            words.append(part.lower())
        else:
            # 日本語を含む場合
            japanese_words = tokenize_japanese(part)
            words.extend([w.lower() for w in japanese_words])
    
    return [w for w in words if len(w) >= 2]

def enhanced_pre_filter_tags(blog_text, all_tags, max_tags=200):
    """
    MeCabを使用した改良版タグフィルタリング
    200個まで絞り込み
    """
    # キーワード抽出（MeCab使用）
    keywords = extract_keywords_with_mecab(blog_text)
    blog_lower = blog_text.lower()
    
    scored_tags = []
    max_score = 0
    
    for tag in all_tags:
        tag_id = str(tag.get('id', ''))
        tag_name = tag.get('name', '')
        
        if not tag_id or not tag_name:
            continue
            
        tag_name_lower = tag_name.lower()
        score = 0
        
        # 1. 完全一致チェック（+15点）
        if tag_name_lower in blog_lower:
            score += 15
        
        # 2. キーワードマッチング（+10点）
        for keyword in keywords:
            if keyword in tag_name_lower or tag_name_lower in keyword:
                score += 10
                break
        
        # 3. 単語レベルマッチング（MeCab処理、+5点）
        tag_words = split_tag_name(tag_name)
        for word in tag_words:
            if word in keywords or word in blog_lower:
                score += 5
        
        # 4. 部分マッチング（+2点）
        for keyword in keywords:
            if len(keyword) >= 3:
                if keyword in tag_name_lower or tag_name_lower in keyword:
                    score += 2
        
        if score > 0:
            scored_tags.append((score, f"{tag_id}\t{tag_name}", tag_id, tag_name))
            max_score = max(max_score, score)
    
    # スコア順でソート
    scored_tags.sort(reverse=True, key=lambda x: x[0])
    
    # 上位200個に絞り込み
    filtered_tags = [tag for _, tag, _, _ in scored_tags[:max_tags]]
    tag_scores = []
    
    for score, _, tag_id, tag_name in scored_tags[:max_tags]:
        relevance_percentage = round((score / max_score * 100) if max_score > 0 else 0, 1)
        tag_scores.append({
            'id': tag_id,
            'name': tag_name,
            'score': score,
            'relevance_percentage': relevance_percentage
        })
    
    return filtered_tags, tag_scores

# 既存の関数もインポート
from common import get_article_from_contentful, get_tags_from_contentful_cached, calculate_cost
