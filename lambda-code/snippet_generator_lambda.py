import json
import boto3
import os
import re
import collections

def lambda_handler(event, context):
    """Google検索用スニペット生成Lambda関数"""
    try:
        # パラメータ取得
        title = event.get('title', '')
        content = event.get('content', '')
        model_id = event.get('model_id', 'us.amazon.nova-lite-v1:0')
        
        if not title and not content:
            raise ValueError("title or content is required")
        
        # テキスト結合
        full_text = f"{title}\n\n{content}" if title and content else (title or content)
        
        # スニペット生成
        snippet_text, cache_info = generate_snippet_with_ai(full_text, model_id, title)
        
        return {
            'snippet': snippet_text,
            'cache_info': cache_info,
            'model_id': model_id
        }
        
    except Exception as e:
        raise Exception(f"Snippet generation failed: {str(e)}")

def extract_keywords(text, title=""):
    """テキストから主要キーワードを抽出"""
    # 結合テキスト
    combined_text = f"{title} {text}"
    
    # 技術用語・重要語句の抽出
    tech_terms = re.findall(r'[A-Z][a-zA-Z]+|[ぁ-んァ-ヶー一-龯]{2,8}', combined_text)
    english_words = re.findall(r'[A-Za-z]{3,}', combined_text)
    japanese_words = re.findall(r'[ぁ-んァ-ヶー一-龯]{2,6}', combined_text)
    
    # 全キーワード結合
    all_keywords = tech_terms + english_words + japanese_words
    
    # ストップワード除去
    stop_words = {
        'です', 'ます', 'した', 'する', 'ある', 'いる', 'なる', 'れる', 'られる',
        'この', 'その', 'あの', 'どの', 'ここ', 'そこ', 'あそこ', 'どこ', 'では',
        'から', 'まで', 'より', 'ため', 'について', 'として', 'による', 'こと',
        'もの', 'とき', 'ところ', 'ので', 'けれど', 'しかし', 'でも', 'また',
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had',
        'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his',
        'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy'
    }
    
    # フィルタリング
    filtered_keywords = [
        kw.lower() for kw in all_keywords 
        if len(kw) > 1 and kw.lower() not in stop_words
    ]
    
    # 頻度カウント
    keyword_counts = collections.Counter(filtered_keywords)
    
    # 上位キーワード取得（重複除去）
    unique_keywords = []
    for keyword, count in keyword_counts.most_common(20):
        if keyword not in unique_keywords:
            unique_keywords.append(keyword)
    
    return unique_keywords[:8]

def extract_conclusion_content(text):
    """記事の結論・まとめ部分を抽出"""
    # 結論セクションのキーワード
    conclusion_patterns = [
        r'##\s*まとめ[\s\S]*?(?=\n##|\n#|$)',
        r'##\s*最後に[\s\S]*?(?=\n##|\n#|$)', 
        r'##\s*さいごに[\s\S]*?(?=\n##|\n#|$)',
        r'##\s*終わりに[\s\S]*?(?=\n##|\n#|$)',
        r'##\s*おわりに[\s\S]*?(?=\n##|\n#|$)',
        r'##\s*結論[\s\S]*?(?=\n##|\n#|$)',
        r'まとめ\n\n[\s\S]*?(?=\n\n[^\n]|\n##|$)',
        r'最後に\n\n[\s\S]*?(?=\n\n[^\n]|\n##|$)',
        r'さいごに\n\n[\s\S]*?(?=\n\n[^\n]|\n##|$)'
    ]
    
    conclusion_text = ""
    for pattern in conclusion_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            conclusion_text = matches[-1].strip()
            break
    
    # 結論が見つからない場合は最後の段落を使用
    if not conclusion_text:
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        if len(paragraphs) > 2:
            conclusion_text = paragraphs[-1]
    
    return conclusion_text

def format_two_sentence_snippet(text):
    """2文構成のスニペットを整形"""
    # 文を分割
    sentences = re.split(r'[。！？]', text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) >= 2:
        first_sentence = sentences[0] + "。"
        second_sentence = sentences[1] + "。"
        
        # 文字数調整
        if len(first_sentence) > 80:
            first_sentence = first_sentence[:77] + "..."
        if len(second_sentence) > 80:
            second_sentence = second_sentence[:77] + "..."
            
        return first_sentence + second_sentence
    else:
        # 1文の場合は適切に分割
        full_text = text.strip()
        if len(full_text) > 160:
            full_text = full_text[:157] + "..."
        return full_text

def generate_snippet_with_ai(text, model_id, title=""):
    """AIを使用してスニペットを生成"""
    bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
    
    # キーワード抽出
    keywords = extract_keywords(text, title)
    keywords_text = "、".join(keywords[:8])
    
    # 結論部分を抽出
    conclusion = extract_conclusion_content(text)
    
    # プロンプト作成
    prompt_parts = [
        f"タイトル: {title}",
        "",
        "要件:",
        "- 160文字前後を目安（必須ではない）",
        "- 文数は自由（1文でも複数文でも可）",
        "",
        "優先順位:",
        "1. タイトルとの連続性・補足説明を最優先",
        "2. 記事のまとめ・結論内容を反映", 
        "3. 重要なキーワードを自然に含める",
        "4. SEO効果と検索結果での理解促進",
        "",
        f"- 主要キーワード: {keywords_text}",
        "- 検索ユーザーが記事内容を適切に理解できる説明",
        "- タイトルで言及されていない価値・詳細を補完",
        ""
    ]
    
    if conclusion:
        prompt_parts.extend([
            "記事の結論・まとめ:",
            conclusion[:500],
            "",
            "記事全体:",
            text[:1500]
        ])
    else:
        prompt_parts.extend([
            "記事内容:",
            text[:2000]
        ])
    
    prompt_parts.extend([
        "",
        "タイトルを補完し、記事内容の理解を促進するスニペット:"
    ])
    prompt = "\n".join(prompt_parts)
    
    if 'nova' in model_id.lower():
        # Nova API
        body = {
            "messages": [{"role": "user", "content": [{"text": prompt}]}],
            "inferenceConfig": {"temperature": 0.3, "maxTokens": 300}
        }
        response = bedrock.invoke_model(modelId=model_id, body=json.dumps(body))
        response_body = json.loads(response['body'].read())
        
        snippet_text = response_body['output']['message']['content'][0]['text'].strip()
        cache_info = {
            'input_tokens': response_body['usage']['inputTokens'],
            'output_tokens': response_body['usage']['outputTokens']
        }
    else:
        # Claude fallback
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 300,
            "temperature": 0.3,
            "messages": [{"role": "user", "content": prompt}]
        }
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0', 
            body=json.dumps(body)
        )
        response_body = json.loads(response['body'].read())
        
        snippet_text = response_body['content'][0]['text'].strip()
        cache_info = {
            'input_tokens': response_body['usage']['input_tokens'],
            'output_tokens': response_body['usage']['output_tokens']
        }
    
    # 2文構成に整形
    snippet_text = format_two_sentence_snippet(snippet_text)
    
    return snippet_text, cache_info
