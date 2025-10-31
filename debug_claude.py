import json
import boto3
import re

def test_claude_response():
    """Claudeの応答をテスト"""
    bedrock = boto3.client('bedrock-runtime', region_name='ap-northeast-1')
    
    # テスト用のタグリスト（少数）
    test_tags = [
        "20036:Amazon Nova",
        "1446:AWS",
        "739:API",
        "20081:Web",
        "1450:JavaScript"
    ]
    
    tags_text = '\n'.join(test_tags)
    text = "Amazon Nova Web Grounding announced with new API features for JavaScript developers"
    
    # LLMプロンプト
    prompt = f"記事: {text}\n\nタグ適合度ランキング:\n{tags_text}\n\n最適合=100, 無関係=1\nタグID:数値:"
    
    print("=== PROMPT ===")
    print(prompt)
    print("\n=== CLAUDE RESPONSE ===")
    
    # Claude用のリクエスト形式
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "temperature": 0.1,
        "messages": [{"role": "user", "content": prompt}]
    }
    
    response = bedrock.invoke_model(
        modelId='global.anthropic.claude-haiku-4-5-20251001-v1:0', 
        body=json.dumps(body)
    )
    response_body = json.loads(response['body'].read())
    
    result_text = response_body['content'][0]['text']
    print(result_text)
    
    print("\n=== PARSED SCORES ===")
    scores = parse_llm_scores_final(result_text)
    print(scores)
    
    return result_text, scores

def parse_llm_scores_final(result_text):
    """LLMの評価結果をパース（表形式対応版）"""
    scores = {}
    
    # 表形式とシンプル形式の両方に対応
    lines = result_text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        print(f"Processing line: '{line}'")
        
        # パターン1: タグID:数値
        match1 = re.match(r'^(\d+):(\d+)$', line)
        if match1:
            try:
                tag_id = match1.group(1)
                score = int(match1.group(2))
                if 1 <= score <= 100:
                    scores[tag_id] = score
                    print(f"  -> Pattern 1 match: {tag_id}={score}")
                    continue
            except (ValueError, TypeError):
                continue
        
        # パターン2: 表形式 | タグID | タグ名 | 数値 |
        match2 = re.match(r'^\|\s*(\d+)\s*\|.*?\|\s*\*?\*?(\d+)\*?\*?\s*\|', line)
        if match2:
            try:
                tag_id = match2.group(1)
                score = int(match2.group(2))
                if 1 <= score <= 100:
                    scores[tag_id] = score
                    print(f"  -> Pattern 2 match: {tag_id}={score}")
                    continue
            except (ValueError, TypeError):
                continue
        
        # パターン3: タグID タグ名 数値
        match3 = re.search(r'(\d+)\s+.*?\s+(\d+)', line)
        if match3:
            try:
                tag_id = match3.group(1)
                score = int(match3.group(2))
                if 1 <= score <= 100:
                    scores[tag_id] = score
                    print(f"  -> Pattern 3 match: {tag_id}={score}")
            except (ValueError, TypeError):
                continue
    
    return scores

if __name__ == "__main__":
    test_claude_response()
