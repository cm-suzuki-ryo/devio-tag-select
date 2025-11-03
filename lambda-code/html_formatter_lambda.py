import json
import html
from datetime import datetime

def lambda_handler(event, context):
    """Step Functions出力をHTMLに整形するLambda関数"""
    try:
        # Step Functions出力を取得
        if 'body' in event:
            # Lambda Function URL経由の場合
            data = json.loads(event['body'])
        else:
            # 直接呼び出しの場合
            data = event
        
        # HTMLを生成
        html_content = generate_html(data)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html; charset=utf-8',
                'Cache-Control': 'no-cache'
            },
            'body': html_content
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html; charset=utf-8'},
            'body': f'<html><body><h1>Error</h1><p>{html.escape(str(e))}</p></body></html>'
        }

def generate_html(data):
    """JSON出力をHTMLに変換"""
    title = html.escape(data.get('title', 'No Title'))
    summary = html.escape(data.get('summary', 'No Summary'))
    snippet = html.escape(data.get('snippet', 'No Snippet'))
    selected_tags = data.get('selected_tags', [])
    review_feedback = data.get('review_feedback', 'No Review')
    cost_breakdown = data.get('cost_breakdown', {})
    
    # タグをHTML形式に
    tags_html = ''.join([f'<span class="tag">{html.escape(tag)}</span>' for tag in selected_tags])
    
    # コスト情報をHTML形式に
    total_cost = cost_breakdown.get('total', {})
    cost_html = f"""
    <div class="cost-info">
        <h3>💰 コスト情報</h3>
        <p><strong>総コスト:</strong> {total_cost.get('total_cost_jpy', 0):.4f} 円</p>
        <p><strong>入力トークン:</strong> {total_cost.get('input_tokens', 0):,} tokens</p>
        <p><strong>出力トークン:</strong> {total_cost.get('output_tokens', 0):,} tokens</p>
    </div>
    """
    
    # レビューフィードバックをMarkdownからHTMLに簡易変換
    review_html = convert_markdown_to_html(review_feedback)
    
    html_template = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>記事分析結果</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }}
        .section {{
            margin: 25px 0;
            padding: 20px;
            border: 1px solid #e0e0e0;
            border-radius: 5px;
            background-color: #fafafa;
        }}
        .tag {{
            display: inline-block;
            background: #3498db;
            color: white;
            padding: 5px 12px;
            margin: 3px;
            border-radius: 15px;
            font-size: 0.9em;
        }}
        .cost-info {{
            background: #e8f5e8;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #27ae60;
        }}
        .review-content {{
            background: #fff;
            padding: 20px;
            border-radius: 5px;
            border: 1px solid #ddd;
        }}
        .timestamp {{
            color: #7f8c8d;
            font-size: 0.9em;
            text-align: right;
            margin-top: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        pre {{
            background: #f8f8f8;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📝 記事分析結果</h1>
        
        <div class="section">
            <h2>📰 記事タイトル</h2>
            <p><strong>{title}</strong></p>
        </div>
        
        <div class="section">
            <h2>📋 要約</h2>
            <div style="max-height: 300px; overflow-y: auto; padding: 10px; background: white; border-radius: 3px;">
                <pre style="white-space: pre-wrap; margin: 0;">{summary}</pre>
            </div>
        </div>
        
        <div class="section">
            <h2>✨ SEOスニペット</h2>
            <div style="background: #e3f2fd; padding: 15px; border-radius: 5px; border-left: 4px solid #2196f3;">
                <p>{snippet}</p>
            </div>
        </div>
        
        <div class="section">
            <h2>🏷️ 推薦タグ</h2>
            <div>{tags_html}</div>
        </div>
        
        <div class="section">
            <h2>📝 記事添削フィードバック</h2>
            <div class="review-content">
                {review_html}
            </div>
        </div>
        
        {cost_html}
        
        <div class="timestamp">
            生成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
        </div>
    </div>
</body>
</html>
    """
    
    return html_template

def convert_markdown_to_html(markdown_text):
    """簡易Markdown→HTML変換"""
    if not markdown_text:
        return "<p>フィードバックがありません</p>"
    
    html_text = html.escape(markdown_text)
    
    # 見出し変換
    html_text = html_text.replace('### ', '<h4>').replace('\n\n', '</h4>\n\n')
    html_text = html_text.replace('## ', '<h3>').replace('\n\n', '</h3>\n\n')
    html_text = html_text.replace('# ', '<h2>').replace('\n\n', '</h2>\n\n')
    
    # 太字変換
    html_text = html_text.replace('**', '<strong>').replace('**', '</strong>')
    
    # 表変換（簡易）
    lines = html_text.split('\n')
    in_table = False
    result_lines = []
    
    for line in lines:
        if '|' in line and line.strip().startswith('|'):
            if not in_table:
                result_lines.append('<table>')
                in_table = True
            
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            if all(cell.replace('-', '').strip() == '' for cell in cells):
                continue  # ヘッダー区切り行をスキップ
            
            row_html = '<tr>' + ''.join([f'<td>{cell}</td>' for cell in cells]) + '</tr>'
            result_lines.append(row_html)
        else:
            if in_table:
                result_lines.append('</table>')
                in_table = False
            result_lines.append(line)
    
    if in_table:
        result_lines.append('</table>')
    
    # 段落変換
    html_text = '\n'.join(result_lines)
    html_text = html_text.replace('\n\n', '</p><p>')
    html_text = f'<p>{html_text}</p>'
    
    # 空の段落を削除
    html_text = html_text.replace('<p></p>', '')
    
    return html_text
