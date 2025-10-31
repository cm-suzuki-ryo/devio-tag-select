#!/usr/bin/env python3
import json
import os

os.environ['CONTENTFUL_ACCESS_TOKEN'] = "6Z4wPWStkHj3d_EA0MQt89nWJpIFSBJcmAQ_YzDpkAg"
os.environ['MODEL_ID'] = "us.amazon.nova-lite-v1:0"
os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'
os.environ['INPUT_PRICE_PER_MILLION'] = '0.06'
os.environ['OUTPUT_PRICE_PER_MILLION'] = '0.24'
os.environ['USD_TO_JPY'] = '150'

from enhanced_index import lambda_handler

test_event = {
    'body': json.dumps({
        'slug': 'saichan-transition-IMDSv2-netshtrace-20251031'
    })
}

print("=== Nova Results ===")
result = lambda_handler(test_event, {})

if result['statusCode'] == 200:
    response_body = json.loads(result['body'])
    print(f"Cost: {response_body['cost_jpy']['total_cost_jpy']}円")
    print("Top tags:")
    for i, tag in enumerate(response_body['selected_tags'][:10], 1):
        score = tag.get('llm_score', 'N/A')
        print(f"{i}. {tag['name']} ({score})")
else:
    print(f"Error: {result['body']}")
