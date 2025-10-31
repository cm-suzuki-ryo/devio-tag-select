# Tag Selector Lambda Function

ContentfulのAPIを使ってブログ記事のタグを自動選択するLambda関数です。

## 機能

- 記事の文字数に応じた処理分岐（2000文字超で要約実行）
- 単一モデル実行（デフォルト：Claude Haiku）
- 要約とタグ選択で同じモデルを使用
- プロンプトキャッシュによるコスト最適化
- 詳細なコスト計算

## ファイル構成

- `index.py` - メインのLambda関数（エントリーポイント）
- `common.py` - 共通処理（Contentful API、フィルタリング、コスト計算）
- `model_router.py` - モデル選択のルーティング処理
- `claude_model.py` - Claude専用の処理
- `nova_model.py` - Nova専用の処理
- `gpt_model.py` - GPT-OSS専用の処理
- `requirements.txt` - 依存関係
- `README.md` - このファイル

## 環境変数

- `CONTENTFUL_ACCESS_TOKEN` - ContentfulのAPIアクセストークン

## 対応モデル

- `us.anthropic.claude-haiku-4-5-20251001-v1:0` (デフォルト)
- `us.amazon.nova-lite-v1:0`
- `openai.gpt-oss-20b-1:0`

## リクエスト例

```json
{
  "slug": "article-slug",
  "model": "us.amazon.nova-lite-v1:0"
}
```

modelパラメータを省略した場合は、Claude Haikuが使用されます。

## モジュール構成

### common.py
- Contentful API呼び出し
- タグの事前フィルタリング
- コスト計算
- レスポンス解析

### model_router.py
- モデル選択のルーティング
- 要約作成の振り分け
- タグ選択の振り分け

### claude_model.py
- Claude用のタグ選択処理
- Claude用の要約作成処理

### nova_model.py
- Nova用のタグ選択処理
- Nova用の要約作成処理

### gpt_model.py
- GPT-OSS用のタグ選択処理
- GPT-OSS用の要約作成処理

### index.py
- Lambda関数のエントリーポイント
- リクエスト処理とレスポンス構築

## 要約処理の改善

長文記事（2000文字超）の場合、要約作成とタグ選択で同じモデルを使用するため：
- 一貫性のある処理結果
- モデル特性を活かした最適化
- コスト計算の正確性

## デプロイ

CloudFormationテンプレート `contentful_cloudformation_with_summary.yaml` を使用してデプロイしてください。
