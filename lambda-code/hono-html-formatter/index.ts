import { Hono } from 'hono'
import { handle } from 'hono/aws-lambda'
import { html } from 'hono/html'

type ArticleData = {
  title: string
  summary: string
  snippet: string
  selected_tags: string[]
  review_feedback: string
  cost_breakdown: {
    total: {
      total_cost_jpy: number
      input_tokens: number
      output_tokens: number
    }
  }
}

const app = new Hono()

// HTMLテンプレート関数
const articleTemplate = (data: ArticleData) => html`
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>記事分析結果 - ${data.title}</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      line-height: 1.6;
      max-width: 1200px;
      margin: 0 auto;
      padding: 20px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
    }
    .container {
      background: white;
      border-radius: 12px;
      padding: 30px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.2);
      backdrop-filter: blur(10px);
    }
    h1 {
      color: #2c3e50;
      border-bottom: 3px solid #3498db;
      padding-bottom: 15px;
      margin-bottom: 30px;
      font-size: 2.2em;
    }
    h2 {
      color: #34495e;
      margin-top: 35px;
      border-left: 4px solid #3498db;
      padding-left: 15px;
      font-size: 1.4em;
    }
    .section {
      margin: 25px 0;
      padding: 25px;
      border: 1px solid #e0e0e0;
      border-radius: 8px;
      background: linear-gradient(145deg, #f8f9fa, #e9ecef);
      box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
    }
    .tag {
      display: inline-block;
      background: linear-gradient(45deg, #3498db, #2980b9);
      color: white;
      padding: 8px 16px;
      margin: 5px;
      border-radius: 20px;
      font-size: 0.9em;
      font-weight: 500;
      box-shadow: 0 2px 5px rgba(52, 152, 219, 0.3);
      transition: transform 0.2s;
    }
    .tag:hover {
      transform: translateY(-2px);
    }
    .cost-info {
      background: linear-gradient(145deg, #d4edda, #c3e6cb);
      padding: 20px;
      border-radius: 8px;
      border-left: 4px solid #28a745;
      box-shadow: 0 2px 10px rgba(40, 167, 69, 0.2);
    }
    .snippet-box {
      background: linear-gradient(145deg, #e3f2fd, #bbdefb);
      padding: 20px;
      border-radius: 8px;
      border-left: 4px solid #2196f3;
      font-size: 1.1em;
      box-shadow: 0 2px 10px rgba(33, 150, 243, 0.2);
    }
    .review-content {
      background: white;
      padding: 25px;
      border-radius: 8px;
      border: 1px solid #ddd;
      max-height: 600px;
      overflow-y: auto;
      box-shadow: inset 0 2px 5px rgba(0,0,0,0.05);
    }
    .summary-box {
      background: white;
      padding: 20px;
      border-radius: 8px;
      max-height: 400px;
      overflow-y: auto;
      border: 1px solid #ddd;
      box-shadow: inset 0 2px 5px rgba(0,0,0,0.05);
    }
    .timestamp {
      color: #6c757d;
      font-size: 0.9em;
      text-align: right;
      margin-top: 30px;
      padding-top: 20px;
      border-top: 1px solid #dee2e6;
    }
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 15px;
      margin-top: 15px;
    }
    .stat-item {
      background: white;
      padding: 15px;
      border-radius: 6px;
      text-align: center;
      box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .stat-value {
      font-size: 1.5em;
      font-weight: bold;
      color: #2c3e50;
    }
    .stat-label {
      color: #6c757d;
      font-size: 0.9em;
      margin-top: 5px;
    }
    pre {
      background: #f8f9fa;
      padding: 15px;
      border-radius: 6px;
      overflow-x: auto;
      white-space: pre-wrap;
      font-size: 0.9em;
      line-height: 1.4;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>📝 記事分析結果</h1>
    
    <div class="section">
      <h2>📰 記事タイトル</h2>
      <p style="font-size: 1.1em; font-weight: 500; color: #2c3e50;">${data.title}</p>
    </div>
    
    <div class="section">
      <h2>📋 要約</h2>
      <div class="summary-box">
        <pre>${data.summary}</pre>
      </div>
    </div>
    
    <div class="section">
      <h2>✨ SEOスニペット</h2>
      <div class="snippet-box">
        <p style="margin: 0; font-weight: 500;">${data.snippet}</p>
      </div>
    </div>
    
    <div class="section">
      <h2>🏷️ 推薦タグ</h2>
      <div>
        ${data.selected_tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
      </div>
    </div>
    
    <div class="section">
      <h2>📝 記事添削フィードバック</h2>
      <div class="review-content">
        <pre>${data.review_feedback}</pre>
      </div>
    </div>
    
    <div class="cost-info">
      <h3 style="margin-top: 0; color: #155724;">💰 コスト情報</h3>
      <div class="stats-grid">
        <div class="stat-item">
          <div class="stat-value">¥${data.cost_breakdown.total.total_cost_jpy.toFixed(4)}</div>
          <div class="stat-label">総コスト</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">${data.cost_breakdown.total.input_tokens.toLocaleString()}</div>
          <div class="stat-label">入力トークン</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">${data.cost_breakdown.total.output_tokens.toLocaleString()}</div>
          <div class="stat-label">出力トークン</div>
        </div>
      </div>
    </div>
    
    <div class="timestamp">
      生成日時: ${new Date().toLocaleString('ja-JP', { timeZone: 'Asia/Tokyo' })}
    </div>
  </div>
</body>
</html>
`

// ルート定義
app.get('/', (c) => {
  return c.html(html`
    <html>
      <body>
        <h1>記事分析HTML生成API</h1>
        <p>POST /format でJSON形式の記事分析結果をHTMLに変換します</p>
        <pre>
POST /format
Content-Type: application/json

{
  "title": "記事タイトル",
  "summary": "記事要約",
  "snippet": "SEOスニペット", 
  "selected_tags": ["タグ1", "タグ2"],
  "review_feedback": "添削フィードバック",
  "cost_breakdown": {
    "total": {
      "total_cost_jpy": 1.5,
      "input_tokens": 1000,
      "output_tokens": 500
    }
  }
}
        </pre>
      </body>
    </html>
  `)
})

app.post('/format', async (c) => {
  try {
    const data: ArticleData = await c.req.json()
    
    // 必須フィールドのチェック
    if (!data.title || !data.summary) {
      return c.json({ error: 'title and summary are required' }, 400)
    }
    
    // デフォルト値の設定
    const articleData: ArticleData = {
      title: data.title,
      summary: data.summary,
      snippet: data.snippet || 'スニペットが生成されませんでした',
      selected_tags: data.selected_tags || [],
      review_feedback: data.review_feedback || 'フィードバックが生成されませんでした',
      cost_breakdown: data.cost_breakdown || {
        total: { total_cost_jpy: 0, input_tokens: 0, output_tokens: 0 }
      }
    }
    
    return c.html(articleTemplate(articleData))
    
  } catch (error) {
    console.error('Error processing request:', error)
    return c.json({ error: 'Invalid JSON format' }, 400)
  }
})

// 健康チェック
app.get('/health', (c) => {
  return c.json({ status: 'healthy', timestamp: new Date().toISOString() })
})

// AWS Lambda handler
export const handler = handle(app)
