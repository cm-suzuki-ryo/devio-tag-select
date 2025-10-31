#!/usr/bin/env python3
import json
import os

# 環境変数を設定（テスト用）
os.environ['CONTENTFUL_ACCESS_TOKEN'] = '6Z4wPWStkHj3d_EA0MQt89nWJpIFSBJcmAQ_YzDpkAg'
os.environ['INPUT_PRICE_PER_MILLION'] = '0.25'  # Claude Haiku価格
os.environ['OUTPUT_PRICE_PER_MILLION'] = '1.25'
os.environ['USD_TO_JPY'] = '150'

from index import lambda_handler

# テスト用のイベントデータ
test_event = {
    "body": json.dumps({
        "slug": "test-article",
        "model": "claude"
    })
}

# Lambda関数をローカルでテスト
if __name__ == "__main__":
    try:
        result = lambda_handler(test_event, {})
        print("Test Result:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}")
