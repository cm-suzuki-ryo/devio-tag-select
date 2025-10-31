# Tag Selector - 使用ガイド

## 概要
Contentfulから記事を取得し、3つのAIモデル（Claude Haiku、Amazon Nova、OpenAI GPT）を使用して最適なタグを自動選択するシステムです。

## 主な機能
- **記事取得**: Contentful API連携
- **要約作成**: 長文記事の自動要約
- **MeCab処理**: 日本語形態素解析（フォールバック付き）
- **タグ絞り込み**: 2,159→200タグ効率化
- **LLM評価**: 100段階精密評価
- **結果出力**: 上位20タグ選択

## 推奨用途
- **Nova Lite**: **コスト重視**プロジェクト（0.0979円、95点精度）
- **GPT-OSS 20B**: **精度重視**プロジェクト（0.2205円、98点精度）
- **Claude Haiku**: **バランス重視**プロジェクト（0.2488円、キャッシュ機能）

## 技術的特徴
- **Claude**: 最も高機能（キャッシュ、システムプロンプト分離）
- **Nova**: 最もシンプル（パラメータ最小、max_tokens不要）
- **GPT**: 標準的（OpenAI互換、thinking機能）

## 選択指針
1. **予算最優先** → Nova Lite (0.0979円)
2. **精度最優先** → GPT-OSS 20B (0.2205円)
3. **機能性重視** → Claude Haiku (0.2488円)

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
├── README.md                           # 技術仕様（LLM開発者向け）
├── USAGE.md                           # 使用ガイド（人間向け）
├── claude_cloudformation.yaml          # Claude版（基準実装）
├── nova_cloudformation.yaml           # Nova版
├── gpt_cloudformation.yaml            # GPT版
├── lambda-code/                        # 開発用ソースコード
├── tests/                             # テスト環境
└── ec2/                               # EC2環境設定
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
