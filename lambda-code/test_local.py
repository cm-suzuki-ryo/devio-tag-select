#!/usr/bin/env python3
import json
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
