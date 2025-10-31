# デプロイ手順

Dockerコンテナ内ではOAuth認証ができないため、API Tokenを使用します。

## 手順1: Cloudflare API Tokenを取得

1. https://dash.cloudflare.com/profile/api-tokens にアクセス
2. "Create Token" をクリック
3. "Edit Cloudflare Workers" テンプレートを選択
4. トークンを生成してコピー

## 手順2: 環境変数を設定してデプロイ

```bash
cd workers

# API Tokenを環境変数に設定
export CLOUDFLARE_API_TOKEN="your-api-token-here"

# Dockerでデプロイ
docker run -it --rm \
  -v $(pwd):/app \
  -w /app \
  -e CLOUDFLARE_API_TOKEN \
  node:20-alpine \
  sh -c "npm install && npx wrangler deploy"
```

## 手順3: ローカルマシンからデプロイ（推奨）

ローカルマシンにNode.jsがある場合、こちらが簡単です：

```bash
cd workers
npm install
npx wrangler login  # ブラウザで認証
npm run deploy
```

## ローカル開発（認証不要）

```bash
cd workers
npm install
npm run dev
```

http://localhost:8787 でテスト可能
