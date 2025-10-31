# Tag Selector Project

AWS Bedrockを使用したAIベースのブログ記事タグ自動選択システム

## 概要

Contentfulから記事を取得し、3つのAIモデル（Claude Haiku、Amazon Nova、OpenAI GPT）を使用して最適なタグを自動選択するシステムです。

## 主な機能

- **記事取得**: Contentful API連携
- **要約作成**: 長文記事の自動要約
- **MeCab処理**: 日本語形態素解析（フォールバック付き）
- **タグ絞り込み**: 2,159→200タグ効率化
- **LLM評価**: 100段階精密評価
- **結果出力**: 上位20タグ選択

## 対応モデル（us-west-2リージョン）

| モデル | コスト | 精度 | 処理時間 | 特徴 | モデルID |
|--------|--------|------|----------|------|----------|
| **Nova Lite** | 0.13円 | 95点 | 7秒 | **最高コスパ** | `us.amazon.nova-lite-v1:0` |
| **GPT-OSS 20B** | 0.43円 | 98点 | 11秒 | 高精度 | `openai.gpt-oss-20b-1:0` |
| **Claude Haiku 4.5** | 0.55円 | 95点 | 9秒 | バランス良好 | `global.anthropic.claude-haiku-4-5-20251001-v1:0` |

## CloudFormationテンプレート

### 環境変数ベース価格設定（推奨）
- **`claude_cloudformation.yaml`** - Claude版
- **`nova_cloudformation.yaml`** - Nova Lite版  
- **`gpt_cloudformation.yaml`** - GPT-OSS 20B版

### 環境変数
- `INPUT_PRICE_PER_MILLION`: 入力トークン価格（USD/100万トークン）
- `OUTPUT_PRICE_PER_MILLION`: 出力トークン価格（USD/100万トークン）  
- `USD_TO_JPY`: 為替レート（USD→JPY）

## デプロイ方法

```bash
# Claude版（推奨）
aws cloudformation deploy \
  --template-file claude_cloudformation.yaml \
  --stack-name tag-selector-claude \
  --capabilities CAPABILITY_IAM

# Nova版
aws cloudformation deploy \
  --template-file nova_cloudformation.yaml \
  --stack-name tag-selector-nova \
  --capabilities CAPABILITY_IAM

# GPT版
aws cloudformation deploy \
  --template-file gpt_cloudformation.yaml \
  --stack-name tag-selector-gpt \
  --capabilities CAPABILITY_IAM
```

## テスト環境

### Dockerテスト

```bash
# Haikuテスト
docker build -f tests/Dockerfile.haiku-test -t haiku-test .
docker run --rm -e AWS_DEFAULT_REGION=us-west-2 -v ~/.aws:/root/.aws:ro haiku-test

# Novaテスト
docker build -f tests/Dockerfile.nova-test -t nova-test .
docker run --rm -e AWS_DEFAULT_REGION=us-west-2 -v ~/.aws:/root/.aws:ro nova-test

# GPTテスト
docker build -f tests/Dockerfile.gpt-test -t gpt-test .
docker run --rm -e AWS_DEFAULT_REGION=us-west-2 -v ~/.aws:/root/.aws:ro gpt-test
```

## プロジェクト構成

```
├── README.md                           # プロジェクト概要
├── claude_cloudformation.yaml          # Claude版（推奨）
├── nova_cloudformation.yaml           # Nova版
├── gpt_cloudformation.yaml            # GPT版
├── lambda-code/                        # 開発用ソースコード
│   ├── enhanced_index.py              # メイン処理
│   ├── common.py                      # 共通関数（環境変数ベース価格）
│   ├── enhanced_common.py             # 改良版共通関数（MeCab対応）
│   ├── *_model.py                     # モデル別処理
│   └── model_router.py                # モデル振り分け
├── tests/                             # テスト環境
│   ├── README.md                      # テスト手順
│   ├── Dockerfile.*-test              # Dockerテスト用
│   └── test_*.py                      # テストスクリプト
└── ec2/                               # EC2環境設定
    └── ec2_spot_template.yaml         # Spot Instance用
```

## 処理フロー

```
記事取得 → 要約作成 → MeCab処理 → 200タグ絞り込み → LLM 100段階評価 → 上位20選択
```

## 技術仕様

- **言語**: Python 3.11
- **AWS リージョン**: us-west-2（オレゴン）
- **AWS サービス**: Lambda, Bedrock, CloudFormation
- **外部API**: Contentful
- **形態素解析**: MeCab（フォールバック付き）
- **価格計算**: 環境変数ベース
- **認証**: Lambda Function URL（CORS対応）

## 開発・運用

### Git操作
```bash
# SSH URL使用（推奨）
git remote set-url origin git@github.com:cm-suzuki-ryo/devio-tag-select.git
git push origin main
```

### 開発フロー
1. `lambda-code/` でソース変更
2. Dockerでローカルテスト
3. CloudFormationテンプレートに反映
4. デプロイ・動作確認

## メリット

- **保守性向上**: 環境変数による価格管理
- **モデル非依存**: 統一されたコード基盤
- **運用効率**: 環境変数変更のみで価格更新
- **高精度**: MeCab + LLM による精密なタグ選択
- **コスパ**: Novaで0.16円の低コスト実現
