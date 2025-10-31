#!/usr/bin/env python3
import os
import sys

# 環境変数設定
os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'

# MeCabテスト
try:
    import MeCab
    print("✅ MeCab import successful")
    
    # MeCab初期化テスト
    try:
        tagger = MeCab.Tagger('-Owakati')
        print("✅ MeCab tagger initialized successfully")
        MECAB_AVAILABLE = True
    except:
        try:
            tagger = MeCab.Tagger('-Owakati -d /var/lib/mecab/dic/ipadic-utf8')
            print("✅ MeCab tagger initialized with explicit dictionary path")
            MECAB_AVAILABLE = True
        except Exception as e:
            print(f"❌ MeCab tagger initialization failed: {e}")
            MECAB_AVAILABLE = False
            tagger = None
    
    if MECAB_AVAILABLE and tagger:
        # 日本語テキストのテスト
        test_texts = [
            "Amazon Nova Web Grounding機能が発表されました",
            "機械学習とAIの技術について",
            "Cursor 2.0のアップデート内容",
            "AWS Lambda関数の実装方法"
        ]
        
        print("\n=== MeCab 日本語解析テスト ===")
        for text in test_texts:
            try:
                result = tagger.parse(text).strip()
                tokens = result.split()
                print(f"入力: {text}")
                print(f"解析結果: {tokens}")
                print(f"トークン数: {len(tokens)}")
                print()
            except Exception as e:
                print(f"解析エラー: {e}")
        
        # タグ名の解析テスト
        print("=== タグ名解析テスト ===")
        tag_names = [
            "機械学習",
            "AWS Lambda",
            "JavaScript",
            "データベース設計",
            "セキュリティ対策"
        ]
        
        for tag_name in tag_names:
            try:
                result = tagger.parse(tag_name).strip()
                tokens = result.split()
                print(f"タグ: {tag_name} → {tokens}")
            except Exception as e:
                print(f"タグ解析エラー: {e}")
    
except ImportError:
    print("❌ MeCab not available")

# enhanced_common.pyの関数テスト
print("\n=== enhanced_common.py関数テスト ===")
sys.path.append('/app')

try:
    from enhanced_common import extract_keywords_with_mecab, tokenize_japanese
    
    test_text = "Amazon Nova Web Grounding機能により、機械学習とAIの精度が向上しました。JavaScript開発者にとって重要なアップデートです。"
    
    print(f"テストテキスト: {test_text}")
    
    # キーワード抽出テスト
    keywords = extract_keywords_with_mecab(test_text)
    print(f"抽出キーワード: {keywords}")
    print(f"キーワード数: {len(keywords)}")
    
    # 日本語部分のみの解析
    japanese_part = "機械学習とAIの精度が向上しました"
    tokens = tokenize_japanese(japanese_part)
    print(f"日本語解析: {japanese_part} → {tokens}")
    
except Exception as e:
    print(f"関数テストエラー: {e}")
    import traceback
    traceback.print_exc()
