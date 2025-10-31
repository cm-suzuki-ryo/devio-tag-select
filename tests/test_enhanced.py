#!/usr/bin/env python3
import json
import os

# 環境変数設定
os.environ['CONTENTFUL_ACCESS_TOKEN'] = "6Z4wPWStkHj3d_EA0MQt89nWJpIFSBJcmAQ_YzDpkAg"
os.environ['MODEL_ID'] = "global.anthropic.claude-haiku-4-5-20251001-v1:0"  # ap-northeast-1用
# 価格設定（環境変数ベース）
os.environ['INPUT_PRICE_PER_MILLION'] = '0.25'
os.environ['OUTPUT_PRICE_PER_MILLION'] = '1.25'
os.environ['USD_TO_JPY'] = '150'

from enhanced_index import lambda_handler

# テストイベント
test_event = {
    'body': json.dumps({
        'slug': 'cursor-2-0'
    })
}

if __name__ == "__main__":
    try:
        print("=== Enhanced Lambda Function Test ===")
        print(f"Model: {os.environ.get('MODEL_ID')}")
        print(f"Article: cursor-2-0")
        print()
        
        result = lambda_handler(test_event, {})
        
        if result['statusCode'] == 200:
            response_body = json.loads(result['body'])
            
            print("✅ Test Success!")
            print(f"Status: {result['statusCode']}")
            print(f"Model: {response_body['model']}")
            print(f"Article length: {response_body['article_length']} chars")
            print(f"Long article: {response_body['is_long_article']}")
            print(f"Filtered tags: {response_body['filtered_count']}")
            print(f"Total cost: {response_body['cost_jpy']['total_cost_jpy']}円")
            
            print("\n=== Processing Flow ===")
            for step, desc in response_body['processing_flow'].items():
                print(f"{step}: {desc}")
            
            print("\n=== Top 5 Selected Tags ===")
            for i, tag in enumerate(response_body['selected_tags'][:5], 1):
                llm_score = tag.get('llm_score', 'N/A')
                basic_score = tag.get('score', 'N/A')
                print(f"{i}. {tag['name']} (LLM: {llm_score}, Basic: {basic_score})")
                
        else:
            print("❌ Test Failed!")
            print(f"Status: {result['statusCode']}")
            print(f"Error: {result['body']}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
