import { Hono } from 'hono'
import { serve } from '@hono/node-server'
import { readFileSync } from 'fs'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const app = new Hono()

// JSONデータを読み込み
let jsonData
try {
  const jsonPath = join(__dirname, '../tag_selector_result_fixed.json')
  jsonData = JSON.parse(readFileSync(jsonPath, 'utf8'))
} catch (error) {
  console.error('JSONファイルの読み込みに失敗:', error.message)
  process.exit(1)
}

app.get('/', (c) => {
  const html = `<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${jsonData.title}</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.6; }
    .header { border-bottom: 2px solid #333; padding-bottom: 20px; margin-bottom: 30px; }
    .section { margin-bottom: 30px; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
    .tags { display: flex; flex-wrap: wrap; gap: 8px; }
    .tag { background: #007acc; color: white; padding: 4px 12px; border-radius: 16px; font-size: 14px; }
    .cost { background: #f5f5f5; padding: 15px; border-radius: 5px; font-family: monospace; }
    pre { background: #f8f8f8; padding: 15px; border-radius: 5px; overflow-x: auto; white-space: pre-wrap; }
  </style>
</head>
<body>
  <div class="header">
    <h1>${jsonData.title}</h1>
  </div>
  
  <div class="section">
    <h2>📝 記事要約</h2>
    <pre>${jsonData.summary}</pre>
  </div>
  
  <div class="section">
    <h2>✨ SEOスニペット</h2>
    <p><strong>${jsonData.snippet}</strong></p>
  </div>
  
  <div class="section">
    <h2>🏷️ 選択されたタグ</h2>
    <div class="tags">
      ${jsonData.selected_tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
    </div>
  </div>
  
  <div class="section">
    <h2>📋 編集フィードバック</h2>
    <pre>${jsonData.review_feedback}</pre>
  </div>
  
  <div class="section">
    <h2>💰 コスト詳細</h2>
    <div class="cost">
      <div><strong>総コスト:</strong> ¥${jsonData.cost_breakdown.total.total_cost_jpy}</div>
      <div><strong>入力トークン:</strong> ${jsonData.cost_breakdown.total.input_tokens.toLocaleString()}</div>
      <div><strong>出力トークン:</strong> ${jsonData.cost_breakdown.total.output_tokens.toLocaleString()}</div>
    </div>
  </div>
</body>
</html>`
  
  return c.html(html)
})

const port = 3000
console.log(`サーバーを起動中... http://localhost:${port}`)
serve({
  fetch: app.fetch,
  port
})
