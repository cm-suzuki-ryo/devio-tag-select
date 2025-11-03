import json
import boto3
import os

def lambda_handler(event, context):
    """記事添削・確認Lambda関数"""
    try:
        title = event.get('title', '')
        content = event.get('content', '')
        model_id = event.get('model_id', 'global.anthropic.claude-haiku-4-5-20251001-v1:0')
        
        if not title and not content:
            raise ValueError("title or content is required")
        
        article_json = {"title": title, "content": content}
        review_feedback = generate_review_feedback(article_json, model_id)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'review_feedback': review_feedback,
                'model_id': model_id
            }, ensure_ascii=False)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            }, ensure_ascii=False)
        }

def generate_review_feedback(article_json, model_id):
    """AIを使用して記事添削フィードバックを生成"""
    bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
    
    prompt = f"""# 役割と目標
あなたは、テックブログの**「編集者と校正役」**です。
提供されたJSON形式の記事データ（タイトルと本文）を、技術的な正確性を保ちつつ、**検索性・可読性・説得力**を高めるために編集サポートをします。
読者は**AWSの基礎知識を持つ技術者**と想定し、**建設的なトーン**を維持してください。

# 実行手順と出力形式

以下の順序でフィードバックを構成し、Markdownを使って構造化して出力すること。

## 1. 🌟 全体的なフィードバック
* 記事の**技術的正確性、構成、検証の流れ**について簡潔に評価する。

## 2. 📝 表記と文法の編集
* 修正提案を必ず**表形式**（オリジナル/提案/理由）で出力する。
* **冗長表現、口語表現、文法ミス**（句読点、助詞の重複）、**専門用語の表記統一**を指摘し、修正案を提示する。

## 3. 💡 構成とタイトルの改善提案
* **タイトル:** 長すぎるタイトルを指摘し、SEO/可読性を考慮した**複数の代替案**を提案する。
* **概要（スニペット）:** 記事の価値を伝える**100字程度**の概要文を新規に作成して提案する。
* **導入:** 読者の関心を引く**「課題提起」**を冒頭に追加する工夫を提案する。

## 4. ✅ 最終確認
* 最後に、他にサポートが必要な点がないかユーザーに尋ねること。

# 記事データ
{json.dumps(article_json, ensure_ascii=False, indent=2)}"""
    
    if 'nova' in model_id.lower():
        body = {
            "messages": [{"role": "user", "content": [{"text": prompt}]}],
            "inferenceConfig": {"temperature": 0.3, "maxTokens": 8192}
        }
        response = bedrock.invoke_model(modelId=model_id, body=json.dumps(body))
        response_body = json.loads(response['body'].read())
        review_feedback = response_body['output']['message']['content'][0]['text']
    else:
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 8192,
            "temperature": 0.3,
            "system": [{"type": "text", "text": "あなたはテックブログの編集者と校正役です。"}],
            "messages": [{"role": "user", "content": prompt}]
        }
        response = bedrock.invoke_model(modelId=model_id, body=json.dumps(body))
        response_body = json.loads(response['body'].read())
        review_feedback = response_body['content'][0]['text']
    
    return review_feedback
