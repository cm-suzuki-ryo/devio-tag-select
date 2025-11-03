const fs = require('fs');

// ACM記事のレスポンスデータを読み込み
const responseData = JSON.parse(fs.readFileSync('/tmp/acm_response.json', 'utf8'));
const bodyData = JSON.parse(responseData.body);

// テスト用のLambdaイベント作成
const testEvent = {
  httpMethod: 'POST',
  path: '/format',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(bodyData)
};

// Honoアプリケーションをテスト
async function testHonoApp() {
  try {
    // Node.js環境でのテスト用サーバー
    const { serve } = require('@hono/node-server');
    const { Hono } = require('hono');
    
    const app = new Hono();
    
    // 簡易版のルート（テスト用）
    app.post('/format', async (c) => {
      const data = await c.req.json();
      
      const html = `
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>記事分析結果</title>
  <style>
    body { font-family: system-ui; max-width: 1200px; margin: 0 auto; padding: 20px; }
    .section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
    .tag { background: #007bff; color: white; padding: 5px 10px; margin: 3px; border-radius: 15px; display: inline-block; }
    pre { background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; white-space: pre-wrap; }
  </style>
</head>
<body>
  <h1>📝 記事分析結果</h1>
  
  <div class="section">
    <h2>📰 記事タイトル</h2>
    <p><strong>${data.title}</strong></p>
  </div>
  
  <div class="section">
    <h2>📋 要約</h2>
    <pre>${data.summary}</pre>
  </div>
  
  <div class="section">
    <h2>✨ SEOスニペット</h2>
    <p>${data.snippet}</p>
  </div>
  
  <div class="section">
    <h2>🏷️ 推薦タグ</h2>
    ${data.selected_tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
  </div>
  
  <div class="section">
    <h2>💰 コスト情報</h2>
    <p>総コスト: ¥${data.cost_breakdown.total.total_cost_jpy.toFixed(4)}</p>
    <p>入力トークン: ${data.cost_breakdown.total.input_tokens.toLocaleString()}</p>
    <p>出力トークン: ${data.cost_breakdown.total.output_tokens.toLocaleString()}</p>
  </div>
  
  <div class="section">
    <h2>📝 記事添削フィードバック</h2>
    <pre>${data.review_feedback}</pre>
  </div>
</body>
</html>`;
      
      return c.html(html);
    });
    
    // テスト用のHTTP POST リクエストをシミュレート
    const mockRequest = {
      method: 'POST',
      url: 'http://localhost:3000/format',
      headers: new Headers({ 'Content-Type': 'application/json' }),
      json: () => Promise.resolve(bodyData),
      text: () => Promise.resolve(JSON.stringify(bodyData))
    };
    
    const mockContext = {
      req: mockRequest,
      html: (content) => ({ 
        headers: { 'Content-Type': 'text/html' },
        body: content 
      })
    };
    
    console.log('✅ Hono HTML Formatter テスト準備完了');
    console.log('📄 記事タイトル:', bodyData.title.substring(0, 50) + '...');
    console.log('💰 総コスト:', bodyData.cost_breakdown.total.total_cost_jpy, '円');
    console.log('🏷️ タグ数:', bodyData.selected_tags.length);
    
    // HTMLファイルを直接生成
    const htmlContent = `
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>記事分析結果</title>
  <style>
    body { font-family: system-ui; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
    .container { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
    h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 15px; }
    .section { margin: 25px 0; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px; background: #fafafa; }
    .tag { background: #3498db; color: white; padding: 8px 15px; margin: 5px; border-radius: 20px; display: inline-block; font-size: 0.9em; }
    pre { background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; white-space: pre-wrap; line-height: 1.4; }
    .cost-info { background: #e8f5e8; padding: 20px; border-radius: 8px; border-left: 4px solid #27ae60; }
  </style>
</head>
<body>
  <div class="container">
    <h1>📝 記事分析結果</h1>
    
    <div class="section">
      <h2>📰 記事タイトル</h2>
      <p><strong>${bodyData.title}</strong></p>
    </div>
    
    <div class="section">
      <h2>📋 要約</h2>
      <div style="max-height: 400px; overflow-y: auto;">
        <pre>${bodyData.summary}</pre>
      </div>
    </div>
    
    <div class="section">
      <h2>✨ SEOスニペット</h2>
      <div style="background: #e3f2fd; padding: 15px; border-radius: 5px; border-left: 4px solid #2196f3;">
        <p>${bodyData.snippet}</p>
      </div>
    </div>
    
    <div class="section">
      <h2>🏷️ 推薦タグ</h2>
      <div>
        ${bodyData.selected_tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
      </div>
    </div>
    
    <div class="cost-info">
      <h3>💰 コスト情報</h3>
      <p><strong>総コスト:</strong> ¥${bodyData.cost_breakdown.total.total_cost_jpy.toFixed(4)}</p>
      <p><strong>入力トークン:</strong> ${bodyData.cost_breakdown.total.input_tokens.toLocaleString()} tokens</p>
      <p><strong>出力トークン:</strong> ${bodyData.cost_breakdown.total.output_tokens.toLocaleString()} tokens</p>
    </div>
    
    <div class="section">
      <h2>📝 記事添削フィードバック</h2>
      <div style="max-height: 600px; overflow-y: auto; background: white; padding: 20px; border-radius: 5px;">
        <pre>${bodyData.review_feedback}</pre>
      </div>
    </div>
    
    <div style="color: #6c757d; font-size: 0.9em; text-align: right; margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6;">
      生成日時: ${new Date().toLocaleString('ja-JP', { timeZone: 'Asia/Tokyo' })}
    </div>
  </div>
</body>
</html>`;
    
    fs.writeFileSync('/tmp/hono_article_analysis.html', htmlContent, 'utf8');
    console.log('✅ HTML生成完了: /tmp/hono_article_analysis.html');
    
  } catch (error) {
    console.error('❌ テストエラー:', error);
  }
}

testHonoApp();
