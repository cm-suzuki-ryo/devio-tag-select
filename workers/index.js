const LAMBDA_URL = 'https://fumsphmmxktt4afevrre332fvu0hfdal.lambda-url.us-west-2.on.aws/';

export default {
  async fetch(request) {
    const url = new URL(request.url);
    const slug = url.searchParams.get('slug');

    if (!slug) {
      return new Response(renderForm(), {
        headers: { 'Content-Type': 'text/html; charset=utf-8' }
      });
    }

    try {
      const response = await fetch(LAMBDA_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ slug })
      });

      if (!response.ok) {
        const error = await response.text();
        return new Response(renderError(slug, error), {
          headers: { 'Content-Type': 'text/html; charset=utf-8' }
        });
      }

      const data = await response.json();
      return new Response(renderResults(slug, data), {
        headers: { 'Content-Type': 'text/html; charset=utf-8' }
      });
    } catch (error) {
      return new Response(renderError(slug, error.message), {
        headers: { 'Content-Type': 'text/html; charset=utf-8' }
      });
    }
  }
};

function renderForm() {
  return `<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>タグ選択システム</title>
  <style>
    body { font-family: sans-serif; padding: 2rem; max-width: 1200px; margin: 0 auto; }
    input { flex: 1; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem; }
    button { padding: 0.5rem 1.5rem; background: #0070f3; color: white; border: none; border-radius: 4px; font-size: 1rem; cursor: pointer; }
    button:hover { background: #0051cc; }
    form { display: flex; gap: 0.5rem; margin-bottom: 1.5rem; }
  </style>
</head>
<body>
  <h1>タグ選択システム</h1>
  <form method="GET">
    <input type="text" name="slug" placeholder="記事のSlugを入力" required>
    <button type="submit">送信</button>
  </form>
  <p>使用方法: 記事のSlugを入力して送信してください</p>
  <p>例: saichan-transition-IMDSv2-netshtrace-20251031</p>
</body>
</html>`;
}

function renderError(slug, error) {
  return `<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>エラー - タグ選択システム</title>
  <style>
    body { font-family: sans-serif; padding: 2rem; max-width: 1200px; margin: 0 auto; }
    .error { color: red; padding: 1rem; background: #fee; border: 1px solid red; border-radius: 4px; }
    input { flex: 1; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem; }
    button { padding: 0.5rem 1.5rem; background: #0070f3; color: white; border: none; border-radius: 4px; font-size: 1rem; cursor: pointer; }
    form { display: flex; gap: 0.5rem; margin-bottom: 1.5rem; }
  </style>
</head>
<body>
  <h1>エラー</h1>
  <form method="GET">
    <input type="text" name="slug" value="${slug}" placeholder="記事のSlugを入力" required>
    <button type="submit">送信</button>
  </form>
  <div class="error">
    <strong>エラーが発生しました:</strong><br>
    ${error}
  </div>
</body>
</html>`;
}

function renderResults(slug, data) {
  const tags = data.selected_tags || [];
  const cost = data.cache_info || {};
  const costJpy = data.cost_jpy || {};

  const tagsHtml = tags.map(tag => `
    <tr>
      <td>${tag.name}</td>
      <td>${tag.id}</td>
      <td style="text-align: right">${tag.score}</td>
    </tr>
  `).join('');

  return `<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>推奨タグ一覧 - タグ選択システム</title>
  <style>
    body { font-family: sans-serif; padding: 2rem; max-width: 1200px; margin: 0 auto; }
    table { width: 100%; border-collapse: collapse; margin-top: 1rem; border: 1px solid #ddd; }
    th, td { padding: 0.75rem; border: 1px solid #ddd; text-align: left; }
    th { background: #f5f5f5; }
    input { flex: 1; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem; }
    button { padding: 0.5rem 1.5rem; background: #0070f3; color: white; border: none; border-radius: 4px; font-size: 1rem; cursor: pointer; }
    button:hover { background: #0051cc; }
    form { display: flex; gap: 0.5rem; margin-bottom: 1.5rem; }
    .info-box { margin-top: 2rem; padding: 1rem; background: #f9f9f9; border: 1px solid #ddd; border-radius: 4px; }
    .info-box ul { list-style: none; padding: 0; }
    .debug-box { margin-top: 2rem; padding: 1rem; background: #fff3cd; border: 1px solid #ffc107; border-radius: 4px; }
    pre { font-size: 0.85rem; overflow: auto; white-space: pre-wrap; word-break: break-all; }
  </style>
</head>
<body>
  <h1>推奨タグ一覧</h1>
  <form method="GET">
    <input type="text" name="slug" value="${slug}" placeholder="記事のSlugを入力" required>
    <button type="submit">送信</button>
  </form>
  <p><strong>記事Slug:</strong> ${slug}</p>
  
  <table>
    <thead>
      <tr>
        <th>タグ名</th>
        <th>タグID</th>
        <th style="text-align: right">適合度</th>
      </tr>
    </thead>
    <tbody>
      ${tagsHtml}
    </tbody>
  </table>

  <div class="info-box">
    <h3>コスト情報</h3>
    <ul>
      <li>入力トークン: ${cost.input_tokens?.toLocaleString() || 'N/A'}</li>
      <li>出力トークン: ${cost.output_tokens?.toLocaleString() || 'N/A'}</li>
      <li>総コスト: ${costJpy.total_cost_jpy || 'N/A'} 円</li>
      <li>モデル: ${data.model || 'N/A'}</li>
    </ul>
  </div>

  <div class="debug-box">
    <h3>デバッグ情報</h3>
    <pre>${JSON.stringify({
      slug: data.slug,
      model: data.model,
      tagsCount: tags.length,
      articleLength: data.article_length,
      isLongArticle: data.is_long_article,
      processingFlow: data.processing_flow
    }, null, 2)}</pre>
  </div>
</body>
</html>`;
}
