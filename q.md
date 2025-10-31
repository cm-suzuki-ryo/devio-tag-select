# Tag Selector Project - Git操作メモ

## リポジトリ情報

- **リポジトリ**: `git@github.com:cm-suzuki-ryo/devio-tag-select.git`
- **ブランチ**: `main`

## 開発・デプロイフロー

### 開発方針

1. **デフォルトモデル**: Claude Haiku
2. **開発優先順位**: Haiku → Nova → GPT
3. **変更の流れ**: 
   - Haikuで機能開発・テスト
   - 動作確認後、NovaとGPTに反映

### ソース管理

- **開発**: `lambda-code/` ディレクトリでモジュール開発
- **デプロイ**: CloudFormationテンプレートにコード埋め込み
- **変更順序**: 
  1. `lambda-code/` でソース変更
  2. Haikuで動作確認
  3. 確認後、CloudFormationテンプレートに反映

### デプロイ対象

- **`claude_cloudformation.yaml`** - Claude Haiku専用
- **`nova_cloudformation.yaml`** - Amazon Nova Lite専用
- **`gpt_cloudformation.yaml`** - OpenAI GPT-OSS 20B専用

## Git操作時の注意事項

### SSH URLの使用

このリポジトリの操作には **SSH URL** を使用してください。

```bash
# リモートURLの確認
git remote -v

# HTTPS URLからSSH URLに変更（必要に応じて）
git remote set-url origin git@github.com:cm-suzuki-ryo/devio-tag-select.git

# プッシュ
git push -u origin main
```

### 理由

- HTTPS URLでは認証エラーが発生する場合があります
- SSH URLを使用することで、SSH鍵による認証が可能になります
- より安全で確実なGit操作が実行できます

## 基本的なGit操作

```bash
# ファイルの追加
git add .

# コミット
git commit -m "コミットメッセージ"

# プッシュ
git push origin main

# 状態確認
git status

# ログ確認
git log --oneline
```

## 開発ワークフロー

### 1. ソース変更
```bash
# lambda-code/ ディレクトリで開発
cd lambda-code/
# ファイル編集...
```

### 2. Haikuでテスト
```bash
# Claude用テンプレートをデプロイ
aws cloudformation deploy \
  --template-file claude_cloudformation.yaml \
  --stack-name tag-selector-claude \
  --capabilities CAPABILITY_IAM
```

### 3. 動作確認後、他モデルに反映
```bash
# Nova用テンプレートに反映
# gpt用テンプレートに反映
# 各テンプレートをデプロイ
```

### 4. コミット・プッシュ
```bash
git add .
git commit -m "feat: 機能追加の説明"
git push origin main
```

## Lambdaローカルテスト

### Docker環境でのテスト

AWS Lambda公式イメージを使用してローカルでテスト可能：

```bash
# lambda-code/ ディレクトリに移動
cd lambda-code/

# テスト用Dockerイメージをビルド
docker build -f Dockerfile.test -t lambda-test-local .

# Claudeモデルでテスト
docker run --rm \
  -e CONTENTFUL_ACCESS_TOKEN="6Z4wPWStkHj3d_EA0MQt89nWJpIFSBJcmAQ_YzDpkAg" \
  -e MODEL_ID="us.anthropic.claude-haiku-4-5-20251001-v1:0" \
  -e AWS_DEFAULT_REGION=us-east-1 \
  -v ~/.aws:/root/.aws:ro \
  lambda-test-local

# Novaモデルでテスト
docker run --rm \
  -e MODEL_ID="us.amazon.nova-lite-v1:0" \
  -e CONTENTFUL_ACCESS_TOKEN="6Z4wPWStkHj3d_EA0MQt89nWJpIFSBJcmAQ_YzDpkAg" \
  -e AWS_DEFAULT_REGION=us-east-1 \
  -v ~/.aws:/root/.aws:ro \
  lambda-test-local

# GPTモデルでテスト
docker run --rm \
  -e MODEL_ID="openai.gpt-oss-20b-1:0" \
  -e CONTENTFUL_ACCESS_TOKEN="6Z4wPWStkHj3d_EA0MQt89nWJpIFSBJcmAQ_YzDpkAg" \
  -e AWS_DEFAULT_REGION=us-east-1 \
  -v ~/.aws:/root/.aws:ro \
  lambda-test-local
```

### テスト用ファイル

- **`Dockerfile.test`** - Python環境でのテスト用
- **`Dockerfile`** - Lambda公式イメージ用（本番環境に近い）
- **`test_local.py`** - テスト実行スクリプト
- **`test_event.json`** - テストイベントデータ

### 認証情報

- **Contentfulトークン**: CloudFormationテンプレートのデフォルト値を使用
- **AWS認証**: 現在のEC2のIAM権限でBedrock APIにアクセス

## プロジェクト構成

- CloudFormationテンプレート（モデル別）
- モジュール化されたLambda関数コード
- 3つのAIモデル対応（Claude、Nova、GPT-OSS）
- 要約機能付きタグ選択システム
- Dockerを使用したローカルテスト環境
