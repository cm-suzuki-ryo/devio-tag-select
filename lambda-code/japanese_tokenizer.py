import re

def split_japanese_text(text):
    """
    日本語テキストを単語に分割
    MeCabが利用できない場合のフォールバック実装
    """
    try:
        import MeCab
        # MeCabを使用した形態素解析
        tagger = MeCab.Tagger('-Owakati')
        result = tagger.parse(text).strip()
        return result.split()
    except ImportError:
        # MeCabが利用できない場合のシンプルな分割
        return simple_japanese_split(text)

def simple_japanese_split(text):
    """
    MeCabなしでの簡易日本語分割
    """
    # ひらがな・カタカナ・漢字を分離
    tokens = []
    current_token = ""
    current_type = None
    
    for char in text:
        char_type = get_char_type(char)
        
        if char_type != current_type:
            if current_token:
                tokens.append(current_token)
            current_token = char
            current_type = char_type
        else:
            current_token += char
    
    if current_token:
        tokens.append(current_token)
    
    # 2文字以上のトークンのみ返す
    return [token for token in tokens if len(token) >= 2]

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

def enhanced_tag_split(tag_name):
    """
    タグ名を適切に分割（日本語対応）
    """
    # スペース区切りで分割
    space_split = tag_name.split()
    
    all_words = []
    for word in space_split:
        # 英数字のみの場合はそのまま
        if re.match(r'^[A-Za-z0-9]+$', word):
            all_words.append(word.lower())
        else:
            # 日本語を含む場合は形態素解析
            japanese_words = split_japanese_text(word)
            all_words.extend([w.lower() for w in japanese_words])
    
    return [w for w in all_words if len(w) >= 2]

# テスト用
if __name__ == "__main__":
    test_tags = [
        "Amazon Bedrock",
        "機械学習",
        "AWS Lambda",
        "データベース設計",
        "Amazon RDS MySQL",
        "自然言語処理"
    ]
    
    for tag in test_tags:
        words = enhanced_tag_split(tag)
        print(f"Tag: {tag}")
        print(f"Split: {words}")
        print("---")
