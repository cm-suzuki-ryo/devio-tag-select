# Tag Selector - Cloudflare Workers版

シンプルなCloudflare Workers実装。Next.jsなしで動作します。

## セットアップ

```bash
cd workers
npm install
```

## ローカル開発

```bash
npm run dev
```

ブラウザで http://localhost:8787 にアクセス

## デプロイ

### 初回のみ: Cloudflareにログイン
```bash
npx wrangler login
```

### デプロイ実行
```bash
npm run deploy
```

デプロイ後、`https://tag-selector.<your-subdomain>.workers.dev` でアクセス可能

## 特徴

- **軽量**: 依存関係なし、純粋なJavaScript
- **高速**: エッジで実行、グローバル配信
- **シンプル**: 1ファイル完結
- **無料枠**: 1日10万リクエストまで無料

## Lambda URL変更

`index.js` の `LAMBDA_URL` 定数を編集してください。

## 環境変数での管理（オプション）

```bash
npx wrangler secret put LAMBDA_URL
```

その後、`index.js` で以下のように変更：
```javascript
const LAMBDA_URL = env.LAMBDA_URL || 'デフォルトURL';
```
