#!/usr/bin/env python3
import os

# MeCab設定
os.environ['MECABRC'] = '/etc/mecabrc'

try:
    import MeCab
    print("✅ MeCab import successful")
    
    # 設定確認
    print(f"MECABRC: {os.environ.get('MECABRC', 'Not set')}")
    
    # 辞書パス確認
    import subprocess
    try:
        result = subprocess.run(['mecab-config', '--dicdir'], capture_output=True, text=True)
        print(f"Dictionary path: {result.stdout.strip()}")
    except:
        print("mecab-config not available")
    
    # MeCab初期化テスト（複数パターン）
    patterns = [
        "",  # デフォルト
        "-Owakati",  # 分かち書き
        "-d /var/lib/mecab/dic/ipadic-utf8",  # 辞書指定
        "-Owakati -d /var/lib/mecab/dic/ipadic-utf8"  # 両方指定
    ]
    
    tagger = None
    for i, pattern in enumerate(patterns):
        try:
            print(f"Pattern {i+1}: '{pattern}'")
            tagger = MeCab.Tagger(pattern)
            print(f"✅ MeCab tagger initialized with pattern: '{pattern}'")
            break
        except Exception as e:
            print(f"❌ Pattern {i+1} failed: {e}")
    
    if tagger:
        # 日本語テキストのテスト
        test_texts = [
            "機械学習",
            "Amazon Nova",
            "JavaScript開発",
            "データベース設計"
        ]
        
        print("\n=== 日本語解析テスト ===")
        for text in test_texts:
            try:
                result = tagger.parse(text)
                print(f"入力: {text}")
                print(f"解析結果: {result.strip()}")
                print()
            except Exception as e:
                print(f"解析エラー ({text}): {e}")
    else:
        print("❌ MeCab tagger initialization completely failed")
        
        # フォールバック処理のテスト
        print("\n=== フォールバック処理テスト ===")
        def simple_split(text):
            import re
            # 簡易分割
            tokens = []
            current = ""
            for char in text:
                if re.match(r'[ぁ-んァ-ヶ一-龯]', char):
                    current += char
                else:
                    if current:
                        tokens.append(current)
                        current = ""
                    if char.strip():
                        tokens.append(char)
            if current:
                tokens.append(current)
            return [t for t in tokens if len(t) >= 1]
        
        for text in ["機械学習", "Amazon Nova"]:
            result = simple_split(text)
            print(f"フォールバック: {text} → {result}")

except ImportError as e:
    print(f"❌ MeCab import failed: {e}")
