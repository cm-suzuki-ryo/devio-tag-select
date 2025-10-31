#!/usr/bin/env python3
import json
import os
import sys

os.environ['CONTENTFUL_ACCESS_TOKEN'] = "6Z4wPWStkHj3d_EA0MQt89nWJpIFSBJcmAQ_YzDpkAg"
os.environ['MODEL_ID'] = "openai.gpt-oss-20b-1:0"
os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'
os.environ['INPUT_PRICE_PER_MILLION'] = '0.15'
os.environ['OUTPUT_PRICE_PER_MILLION'] = '0.6'
os.environ['USD_TO_JPY'] = '150'

from enhanced_index import lambda_handler

test_event = {
    'body': json.dumps({
        'slug': 'saichan-transition-IMDSv2-netshtrace-20251031'
    })
}

try:
    result = lambda_handler(test_event, {})
    response_body = json.loads(result['body'])
    
    print("GPT Results:")
    print(f"Cost: {response_body['cost_jpy']['total_cost_jpy']}円")
    
    tags = response_body['selected_tags'][:5]
    for i, tag in enumerate(tags, 1):
        score = tag.get('llm_score', 'N/A')
        name = tag['name']
        print(f"{i}. {name} ({score})")
        sys.stdout.flush()
        
except Exception as e:
    print(f"Error: {e}")
    sys.stdout.flush()
