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

## 完全版CloudFormationテンプレート

### 概要
テスト済みソースコードを完全統合したCloudFormationテンプレートを作成。機能の低下なしで本番デプロイ可能。

### テンプレート一覧
- **`claude_cloudformation_complete.yaml`** - Claude Haiku 4.5完全版
- **`claude_cloudformation_env_pricing.yaml`** - Claude環境変数価格版（推奨）
- **`nova_cloudformation_enhanced.yaml`** - Nova Lite改良版  
- **`gpt_cloudformation_enhanced.yaml`** - GPT-OSS 20B改良版

### 環境変数ベース価格設定（推奨）
モデル価格をハードコードではなく環境変数で管理する改良版を実装：

#### 環境変数
- `INPUT_PRICE_PER_MILLION`: 入力トークン価格（USD/100万トークン）
- `OUTPUT_PRICE_PER_MILLION`: 出力トークン価格（USD/100万トークン）  
- `USD_TO_JPY`: 為替レート（USD→JPY）

#### メリット
- **保守性向上**: 価格変更時にコード修正不要
- **モデル非依存**: 同一コードで複数モデル対応
- **運用効率**: 環境変数変更のみで価格更新

### 完全版の特徴

#### 統合されたソースコード
- **enhanced_index_final.py** - メイン処理ロジック完全統合
- **enhanced_common.py** - 共通関数群完全統合
- **MeCab対応** - 日本語形態素解析（フォールバック付き）
- **100段階LLM評価** - 精密なタグランキング

#### 実装機能
1. **記事取得**: Contentful API連携
2. **要約作成**: 長文記事の自動要約
3. **MeCab処理**: 日本語・英語キーワード抽出
4. **タグ絞り込み**: 2159→100タグ効率化
5. **LLM評価**: 100段階精密評価
6. **結果出力**: 上位20タグ選択

#### デプロイ方法
```bash
# Claude完全版
aws cloudformation deploy \
  --template-file claude_cloudformation_complete.yaml \
  --stack-name tag-selector-claude-complete \
  --capabilities CAPABILITY_IAM

# Claude環境変数価格版（推奨）
aws cloudformation deploy \
  --template-file claude_cloudformation_env_pricing.yaml \
  --stack-name tag-selector-claude-env \
  --capabilities CAPABILITY_IAM

# Nova改良版
aws cloudformation deploy \
  --template-file nova_cloudformation_enhanced.yaml \
  --stack-name tag-selector-nova-enhanced \
  --capabilities CAPABILITY_IAM

# GPT改良版
aws cloudformation deploy \
  --template-file gpt_cloudformation_enhanced.yaml \
  --stack-name tag-selector-gpt-enhanced \
  --capabilities CAPABILITY_IAM
```

#### テスト実績モデルID
- **Claude**: `global.anthropic.claude-haiku-4-5-20251001-v1:0`
- **Nova**: `apac.amazon.nova-lite-v1:0`
- **GPT**: `openai.gpt-oss-20b-1:0`

#### 性能比較
| モデル | コスト | 精度 | 処理時間 | 特徴 | 価格設定 |
|--------|--------|------|----------|------|----------|
| **Claude Haiku 4.5** | 0.21円 | 95点 | 9秒 | バランス良好 | 環境変数対応 |
| **Nova Lite** | 0.14円 | 95点 | 7秒 | 最高コスパ | 従来版 |
| **GPT-OSS 20B** | 0.50円 | 98点 | 11秒 | 最高精度 | 従来版 |

#### 価格設定方式
- **環境変数版**: INPUT_PRICE_PER_MILLION, OUTPUT_PRICE_PER_MILLION, USD_TO_JPY
- **従来版**: モデル別ハードコード価格辞書

#### Lambda関数URL
- **認証**: NONE（パブリックアクセス）
- **CORS**: 設定済み
- **メソッド**: POST
- **形式**: JSON

#### テスト例
```bash
curl -X POST https://[FUNCTION-URL]/ \
  -H "Content-Type: application/json" \
  -d '{"slug": "cursor-2-0"}'
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

### CloudFormationテンプレート
- **完全版**: `claude_cloudformation_complete.yaml` - テスト済みソースコード完全統合
- **改良版**: `nova_cloudformation_enhanced.yaml`, `gpt_cloudformation_enhanced.yaml`
- **従来版**: `claude_cloudformation.yaml`, `nova_cloudformation.yaml`, `gpt_cloudformation.yaml`

### Lambda関数コード
- **完全版**: `enhanced_index_final.py` + `enhanced_common.py` 統合
- **改良版**: MeCab対応 + 100段階LLM評価
- **従来版**: 基本的なタグ選択機能

### 処理フロー
```
記事取得 → 要約作成 → MeCab処理 → 100タグ絞り込み → LLM 100段階評価 → 上位20選択
```

### 対応モデル
- **3つのAIモデル**: Claude Haiku 4.5, Nova Lite, GPT-OSS 20B
- **要約機能付きタグ選択システム**
- **日本語対応**: MeCab形態素解析
- **Dockerローカルテスト環境**
- **完全版CloudFormationテンプレート**
