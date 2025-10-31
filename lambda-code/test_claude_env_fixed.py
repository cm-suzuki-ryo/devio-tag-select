#!/usr/bin/env python3
import json
import os
import sys

# 環境変数を設定
os.environ['CONTENTFUL_ACCESS_TOKEN'] = '6Z4wPWStkHj3d_EA0MQt89nWJpIFSBJcmAQ_YzDpkAg'
os.environ['MODEL_ID'] = 'global.anthropic.claude-haiku-4-5-20251001-v1:0'
os.environ['INPUT_PRICE_PER_MILLION'] = '0.25'
os.environ['OUTPUT_PRICE_PER_MILLION'] = '1.25'
os.environ['USD_TO_JPY'] = '150'

# CloudFormationテンプレートのコードを直接実行
exec(open('claude_env_code_fixed.py').read())

# テスト用のイベントデータ
test_event = {
    "body": json.dumps({
        "slug": "amazon-nova-web-grounding-announced"
    })
}

# Lambda関数をローカルでテスト
if __name__ == "__main__":
    try:
        result = lambda_handler(test_event, {})
        print("=== Claude Environment Variable Test Result ===")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # LLMスコアの確認
        if result.get('statusCode') == 200:
            body = json.loads(result['body'])
            selected_tags = body.get('selected_tags', [])
            print(f"\n=== LLM Score Analysis ===")
            print(f"Total tags: {len(selected_tags)}")
            llm_scores = [tag.get('llm_score', 0) for tag in selected_tags]
            print(f"LLM scores: {llm_scores[:10]}...")  # 最初の10個
            print(f"Non-zero LLM scores: {[s for s in llm_scores if s > 0]}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
