# Tag Selector Web Application

Next.js + Docker環境でClaude Haiku版Lambda関数を呼び出すWebアプリケーション

## 起動方法

```bash
cd webapp
docker-compose up --build
```

ブラウザで http://localhost:3000 にアクセス

## 使用方法

記事のSlugをクエリパラメータで指定：

```
http://localhost:3000?slug=saichan-transition-IMDSv2-netshtrace-20251031
```

## 表示内容

- 推奨タグ一覧（タグ名、タグID、適合度）
- コスト情報（入力/出力トークン数、総コスト、モデルID）

## Lambda関数URL

Claude Haiku版: `https://fumsphmmxktt4afevrre332fvu0hfdal.lambda-url.us-west-2.on.aws/`

環境変数 `LAMBDA_URL` で変更可能（docker-compose.yml参照）
