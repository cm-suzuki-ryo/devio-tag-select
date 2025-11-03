# Tag Selector - 使用ガイド

## 概要
Contentfulから記事を取得し、3つのAIモデル（Claude Haiku、Amazon Nova、OpenAI GPT）を使用して最適なタグを自動選択するシステムです。CloudFrontによるグローバル配信とセキュリティ保護を提供します。

## 主な機能
- **記事取得**: Contentful API連携
- **要約作成**: 長文記事の自動要約
- **MeCab処理**: 日本語形態素解析（フォールバック付き）
- **タグ絞り込み**: 2,159→200タグ効率化
- **LLM評価**: 100段階精密評価
- **結果出力**: 上位20タグ選択
- **CloudFront配信**: グローバルエッジキャッシュ
- **セキュリティ保護**: カスタムヘッダー認証

## 推奨用途
- **Nova Lite**: **コスト重視**プロジェクト（0.0979円、95点精度）
- **GPT-OSS 20B**: **精度重視**プロジェクト（0.2205円、98点精度）
- **Claude Haiku**: **バランス重視**プロジェクト（0.2488円、キャッシュ機能）

## 技術的特徴
- **Claude**: 最も高機能（キャッシュ、システムプロンプト分離）
- **Nova**: 最もシンプル（パラメータ最小、max_tokens不要）
- **GPT**: 標準的（OpenAI互換、thinking機能）

## アーキテクチャ選択

### **分離版（推奨）**
```
Client → CloudFront → Lambda Function URL → tag-selector-main
                                         → tag-selector-tags
                                         → tag-selector-summary
                                         → AI処理 → 結果
```

**メリット:**
- **セキュリティ**: カスタムヘッダー認証による保護
- **パフォーマンス**: CloudFrontエッジキャッシュ（5.27秒 vs 直接7.29秒）
- **スケーラビリティ**: 各Lambda関数を独立してスケール
- **再利用性**: 要約Lambdaを他用途で使用可能
- **グローバル配信**: 世界中のエッジロケーションから配信

### **従来版（レガシー）**
```
Client → Lambda Function URL → 統合処理 → 結果
```

**メリット:**
- **シンプル**: 1つの関数で完結
- **低レイテンシ**: Lambda間通信のオーバーヘッドなし

## セキュリティ機能

### **CloudFrontカスタムヘッダー認証**
- **直接アクセス保護**: Lambda Function URLへの直接アクセスは403エラー
- **カスタムヘッダー**: `X-CloudFront-Secret`による認証
- **秘密値**: CloudFormationパラメータで設定可能

```bash
# 直接アクセス（ブロック）
curl https://lambda-function-url/ 
# → 403 Forbidden: "Access denied - CloudFront access required"

# CloudFront経由（許可）
curl https://cloudfront-domain/
# → 200 OK: 正常なレスポンス
```

## デプロイ方法

### **分離版（推奨）**
```bash
aws cloudformation deploy \
  --template-file separated_cloudformation.yaml \
  --stack-name tag-selector-separated \
  --parameter-overrides CloudFrontSecretHeader=YourSecretValue123 \
  --capabilities CAPABILITY_IAM \
  --region us-west-2
```

### **従来版（レガシー）**
```bash
# Claude版
aws cloudformation deploy \
  --template-file claude_cloudformation.yaml \
  --stack-name tag-selector-claude \
  --capabilities CAPABILITY_IAM \
  --region us-west-2

# Nova版  
aws cloudformation deploy \
  --template-file nova_cloudformation.yaml \
  --stack-name tag-selector-nova \
  --capabilities CAPABILITY_IAM \
  --region us-west-2

# GPT版
aws cloudformation deploy \
  --template-file gpt_cloudformation.yaml \
  --stack-name tag-selector-gpt \
  --capabilities CAPABILITY_IAM \
  --region us-west-2
```

## 選択指針
1. **セキュリティ重視** → 分離版（CloudFront保護）
2. **グローバル配信** → 分離版（エッジキャッシュ）
3. **予算最優先** → Nova Lite (0.0979円)
4. **精度最優先** → GPT-OSS 20B (0.2205円)
5. **機能性重視** → Claude Haiku (0.2488円)

## テスト環境

### **分離版テスト**
```bash
# CloudFront経由テスト
curl -X POST https://d2wfh8k3k94bjx.cloudfront.net/ \
  -H "Content-Type: application/json" \
  -d '{"article_id":"saichan-transition-IMDSv2-netshtrace-20251031"}'

# 直接アクセステスト（ブロック確認）
curl -X POST https://lambda-function-url/ \
  -H "Content-Type: application/json" \
  -d '{"article_id":"test-article"}'
# → 403 Forbidden
```

### **Dockerテスト**
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

## パフォーマンス比較

### **分離版 + CloudFront**
- **処理時間**: 5.27秒（エッジキャッシュ効果）
- **コスト**: 0.41円
- **セキュリティ**: カスタムヘッダー保護
- **可用性**: グローバル配信

### **従来版（直接アクセス）**
- **処理時間**: 7.29秒
- **コスト**: 0.52円
- **セキュリティ**: なし
- **可用性**: 単一リージョン

## プロジェクト構成
```
├── README.md                           # 技術仕様（LLM開発者向け）
├── USAGE.md                           # 使用ガイド（人間向け）
├── separated_cloudformation.yaml      # 分離版（推奨）
├── claude_cloudformation.yaml         # Claude版（レガシー）
├── nova_cloudformation.yaml          # Nova版（レガシー）
├── gpt_cloudformation.yaml           # GPT版（レガシー）
├── lambda-code/                       # 開発用ソースコード
├── tests/                            # テスト環境
└── ec2/                              # EC2環境設定
```

## Git操作
```bash
# SSH URL使用（推奨）
git remote set-url origin git@github.com:cm-suzuki-ryo/devio-tag-select.git
git push origin main
```

## メリット
- **保守性向上**: 環境変数による価格管理
- **モデル非依存**: 統一されたコード基盤
- **運用効率**: 環境変数変更のみで価格更新
- **高精度**: MeCab + LLM による精密なタグ選択
- **コスパ**: Nova Liteで0.0979円の超低コスト実現
- **セキュリティ**: CloudFrontカスタムヘッダー認証
- **グローバル対応**: エッジロケーションによる高速配信
