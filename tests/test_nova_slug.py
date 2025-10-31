#!/usr/bin/env python3
import json
import os

# 環境変数設定
os.environ['CONTENTFUL_ACCESS_TOKEN'] = "6Z4wPWStkHj3d_EA0MQt89nWJpIFSBJcmAQ_YzDpkAg"
os.environ['MODEL_ID'] = "us.amazon.nova-lite-v1:0"
os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'
os.environ['INPUT_PRICE_PER_MILLION'] = '0.06'
os.environ['OUTPUT_PRICE_PER_MILLION'] = '0.24'
os.environ['USD_TO_JPY'] = '150'

from enhanced_index import lambda_handler

# 指定された記事でテスト
article_slug = 'saichan-transition-IMDSv2-netshtrace-20251031'
test_event = {
    'body': json.dumps({
        'slug': article_slug
    })
}

print(f"=== Nova Testing Article: {article_slug} ===")
result = lambda_handler(test_event, {})

if result['statusCode'] == 200:
    response_body = json.loads(result['body'])
    print("✅ Success!")
    print(f"Cost: {response_body['cost_jpy']['total_cost_jpy']}円")
    print(f"Article length: {response_body['article_length']} chars")
    print(f"Top 5 tags:")
    for i, tag in enumerate(response_body['selected_tags'][:5], 1):
        print(f"{i}. {tag['name']} (Score: {tag.get('llm_score', 'N/A')})")
else:
    print(f"❌ Failed: {result['statusCode']}")
    print(result['body'])
