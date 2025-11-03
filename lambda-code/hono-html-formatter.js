const { Hono } = require('hono')
const { handle } = require('hono/aws-lambda')

const app = new Hono()

// HTMLテンプレート生成関数
function generateHTML(data) {
  const escapeHtml = (text) => {
    if (!text) return ''
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;')
  }

  const title = escapeHtml(data.title || 'No Title')
  const summary = escapeHtml(data.summary || 'No Summary')
  const snippet = escapeHtml(data.snippet || 'No Snippet')
  const selectedTags = data.selected_tags || []
  const reviewFeedback = escapeHtml(data.review_feedback || 'No Review')
  const costBreakdown = data.cost_breakdown || {}
  const totalCost = costBreakdown.total || {}

  const tagsHtml = selectedTags
    .map(tag => `<span class="tag">${escapeHtml(tag)}</span>`)
    .join('')

  return `<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>記事分析結果 - ${title}</title>
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
      margin: 0;
    }
    .timestamp {
      color: #6c757d;
      font-size: 0.9em;
      text-align: right;
      margin-top: 30px;
      padding-top: 20px;
      border-top: 1px solid #dee2e6;
    }
    .hono-badge {
      position: absolute;
      top: 20px;
      right: 20px;
      background: linear-gradient(45deg, #ff6b6b, #ee5a24);
      color: white;
      padding: 5px 12px;
      border-radius: 15px;
      font-size: 0.8em;
      font-weight: bold;
    }
  </style>
</head>
<body>
  <div class="hono-badge">Powered by Hono</div>
  <div class="container">
    <h1>📝 記事分析結果</h1>
    
    <div class="section">
      <h2>📰 記事タイトル</h2>
      <p style="font-size: 1.1em; font-weight: 500; color: #2c3e50;">${title}</p>
    </div>
    
    <div class="section">
      <h2>📋 要約</h2>
      <div class="summary-box">
        <pre>${summary}</pre>
      </div>
    </div>
    
    <div class="section">
      <h2>✨ SEOスニペット</h2>
      <div class="snippet-box">
        <p style="margin: 0; font-weight: 500;">${snippet}</p>
      </div>
    </div>
    
    <div class="section">
      <h2>🏷️ 推薦タグ</h2>
      <div>${tagsHtml}</div>
    </div>
    
    <div class="section">
      <h2>📝 記事添削フィードバック</h2>
      <div class="review-content">
        <pre>${reviewFeedback}</pre>
      </div>
    </div>
    
    <div class="cost-info">
      <h3 style="margin-top: 0; color: #155724;">💰 コスト情報</h3>
      <div class="stats-grid">
        <div class="stat-item">
          <div class="stat-value">¥${(totalCost.total_cost_jpy || 0).toFixed(4)}</div>
          <div class="stat-label">総コスト</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">${(totalCost.input_tokens || 0).toLocaleString()}</div>
          <div class="stat-label">入力トークン</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">${(totalCost.output_tokens || 0).toLocaleString()}</div>
          <div class="stat-label">出力トークン</div>
        </div>
      </div>
    </div>
    
    <div class="timestamp">
      生成日時: ${new Date().toLocaleString('ja-JP', { timeZone: 'Asia/Tokyo' })} | Powered by Hono + AWS Lambda
    </div>
  </div>
</body>
</html>`
}

// ルート定義
app.get('/', (c) => {
  return c.html(`
    <html>
      <head>
        <title>記事分析HTML生成API</title>
        <style>
          body { font-family: system-ui; max-width: 800px; margin: 50px auto; padding: 20px; }
          .api-info { background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #007bff; }
          pre { background: #e9ecef; padding: 15px; border-radius: 5px; overflow-x: auto; }
        </style>
      </head>
      <body>
        <h1>🎨 記事分析HTML生成API (Hono版)</h1>
        <div class="api-info">
          <h3>使用方法</h3>
          <p><code>POST /format</code> でJSON形式の記事分析結果をHTMLに変換します</p>
          
          <h4>リクエスト例:</h4>
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
          
          <h4>特徴:</h4>
          <ul>
            <li>🎨 モダンなグラデーションデザイン</li>
            <li>📱 レスポンシブ対応</li>
            <li>📊 コスト情報の視覚化</li>
            <li>🏷️ タグのインタラクティブ表示</li>
            <li>📝 添削フィードバックの構造化表示</li>
          </ul>
        </div>
      </body>
    </html>
  `)
})

app.post('/format', async (c) => {
  try {
    const data = await c.req.json()
    
    // 必須フィールドのチェック
    if (!data.title) {
      return c.json({ error: 'title is required' }, 400)
    }
    
    const htmlContent = generateHTML(data)
    
    return c.html(htmlContent, 200, {
      'Cache-Control': 'no-cache',
      'X-Powered-By': 'Hono + AWS Lambda'
    })
    
  } catch (error) {
    console.error('Error processing request:', error)
    return c.html(`
      <html>
        <body style="font-family: system-ui; padding: 50px; text-align: center;">
          <h1>❌ エラー</h1>
          <p>リクエストの処理中にエラーが発生しました</p>
          <pre style="background: #f8d7da; padding: 15px; border-radius: 5px; text-align: left;">${error.message}</pre>
        </body>
      </html>
    `, 500)
  }
})

// 健康チェック
app.get('/health', (c) => {
  return c.json({ 
    status: 'healthy', 
    timestamp: new Date().toISOString(),
    service: 'hono-html-formatter'
  })
})

// tag-selector-unified-main の出力を直接受け取るエンドポイント
app.post('/tag-selector', async (c) => {
  try {
    const data = await c.req.json()
    
    // tag-selector-unified-main の出力形式に対応
    let articleData
    
    if (data.body && typeof data.body === 'string') {
      // Lambda Function URL経由の場合
      articleData = JSON.parse(data.body)
    } else {
      // 直接呼び出しの場合
      articleData = data
    }
    
    const htmlContent = generateHTML(articleData)
    
    return c.html(htmlContent, 200, {
      'Cache-Control': 'no-cache',
      'X-Powered-By': 'Hono + AWS Lambda',
      'X-Source': 'tag-selector-unified-main'
    })
    
  } catch (error) {
    console.error('Error processing tag-selector output:', error)
    return c.html(`
      <html>
        <body style="font-family: system-ui; padding: 50px; text-align: center;">
          <h1>❌ tag-selector出力の処理エラー</h1>
          <p>tag-selector-unified-mainの出力形式が正しくありません</p>
          <pre style="background: #f8d7da; padding: 15px; border-radius: 5px; text-align: left;">${error.message}</pre>
        </body>
      </html>
    `, 500)
  }
})

// AWS Lambda handler
exports.handler = handle(app)
