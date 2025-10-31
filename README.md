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

## モデル間の技術的違い

### 🔧 **API仕様**

| モデル | リクエスト形式 | 特殊機能 |
|--------|---------------|----------|
| **Claude** | `anthropic_version` + `system` + `messages` | キャッシュ機能、システムプロンプト分離 |
| **Nova** | `messages` + `inferenceConfig` | シンプル構造、max_tokens不要 |
| **GPT** | `messages` + `max_tokens` + `temperature` | thinking機能、ロールベース |

### 📝 **プロンプト構造**

#### **Claude (分離型)**
```python
# システムプロンプト分離 + キャッシュ対応
"system": [{"type": "text", "text": system_text, "cache_control": {"type": "ephemeral"}}]
"messages": [{"role": "user", "content": "記事分析..."}]
```

#### **Nova (統合型)**
```python
# システム+ユーザーを統合、最小パラメータ
"messages": [{"role": "user", "content": [{"text": combined_prompt}]}]
"inferenceConfig": {"temperature": 0}
```

#### **GPT (ロール分離型)**
```python
# システムとユーザーを明確分離
"messages": [
    {"role": "system", "content": system_content},
    {"role": "user", "content": "記事分析..."}
]
```

### 📊 **レスポンス解析**

| モデル | レスポンス構造 | トークン使用量キー |
|--------|---------------|-------------------|
| **Claude** | `response_body['content'][0]['text']` | `input_tokens`, `output_tokens` |
| **Nova** | `response_body['output']['message']['content'][0]['text']` | `inputTokens`, `outputTokens` |
| **GPT** | `response_body['choices'][0]['message']['content']` | `prompt_tokens`, `completion_tokens` |

## CloudFormationテンプレート

### 環境変数ベース価格設定（推奨）
- **`claude_cloudformation.yaml`** - Claude版 (基準実装)
- **`nova_cloudformation.yaml`** - Nova Lite版  
- **`gpt_cloudformation.yaml`** - GPT-OSS 20B版

### 🔧 **テンプレート実装の違い**

**基準**: Claude Haiku版のコード構造をベースとし、各モデルのAPI仕様に合わせてリクエスト・レスポンス処理部分のみを変更

#### **Claude版 (基準実装)**
```python
# リクエスト形式
body = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 8000,
    "system": [{"type": "text", "text": system_text}],
    "messages": [{"role": "user", "content": prompt}]
}

# レスポンス解析
result_text = response_body['content'][0]['text']
cache_info = {
    'input_tokens': response_body['usage']['input_tokens'],
    'output_tokens': response_body['usage']['output_tokens']
}
```

#### **Nova版 (API仕様変更)**
```python
# リクエスト形式 (max_tokens不要、content配列形式)
body = {
    "messages": [{"role": "user", "content": [{"text": combined_prompt}]}],
    "inferenceConfig": {"temperature": 0.1}
}

# レスポンス解析 (異なるパス構造)
result_text = response_body['output']['message']['content'][0]['text']
cache_info = {
    'input_tokens': response_body['usage']['inputTokens'],
    'output_tokens': response_body['usage']['outputTokens']
}
```

#### **GPT版 (ロール分離型)**
```python
# リクエスト形式 (system/userロール分離)
body = {
    "messages": [
        {"role": "system", "content": system_content},
        {"role": "user", "content": prompt}
    ],
    "max_tokens": 8000,
    "temperature": 0.1
}

# レスポンス解析 (OpenAI互換形式)
result_text = response_body['choices'][0]['message']['content']
cache_info = {
    'input_tokens': response_body['usage']['prompt_tokens'],
    'output_tokens': response_body['usage']['completion_tokens']
}
```

### ✅ **テスト済み実装**
- **Claude**: 完全動作確認済み (基準実装)
- **Nova**: API仕様修正完了、動作確認済み
- **GPT**: ロール分離実装完了、動作確認済み

**全モデルで同一の処理フロー**を維持しながら、各APIの仕様差異に対応した実装となっています。

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

### 🧪 **デプロイ後テスト結果 (us-west-2)**

| モデル | ステータス | コスト | Function URL |
|--------|------------|--------|--------------|
| **Claude Haiku** | ✅ 動作確認済み | 0.2488円 | `https://fumsphmmxktt4afevrre332fvu0hfdal.lambda-url.us-west-2.on.aws/` |
| **Nova Lite** | ✅ 動作確認済み | 0.0979円 | `https://e4bqqc3dcn3rpb3xztchkd6lti0agbax.lambda-url.us-west-2.on.aws/` |
| **GPT-OSS 20B** | ✅ 動作確認済み | 0.2205円 | `https://ezhpxoqh3yfkoakt3dv7ruegba0frjoe.lambda-url.us-west-2.on.aws/` |

**テスト記事**: `saichan-transition-IMDSv2-netshtrace-20251031` (21,070文字)

## 実装アーキテクチャ

### 📁 **ソースコード構成**
```
lambda-code/
├── enhanced_index.py              # メイン処理（統合版）
├── model_router.py                # モデル振り分け
├── claude_model.py                # Claude専用処理
├── nova_model.py                  # Nova専用処理
├── gpt_model.py                   # GPT専用処理
├── enhanced_common.py             # 共通関数（MeCab対応）
└── common.py                      # 価格計算（環境変数ベース）
```

### 🔄 **処理フロー**
1. **記事取得**: Contentful API → `get_article_from_contentful()`
2. **要約作成**: 長文記事 → `create_summary()` → モデル別実装
3. **MeCab処理**: 日本語解析 → `enhanced_pre_filter_tags()` → 200タグ絞り込み
4. **LLM評価**: タグランキング → `evaluate_tags_with_llm()` → モデル別API
5. **結果統合**: 上位20タグ選択 → 価格計算 → JSON出力

### ⚙️ **モデル別実装の違い**

#### **要約処理**
- **Claude**: `create_summary_with_claude()` - システムプロンプト分離
- **Nova**: `create_summary_with_nova()` - 統合プロンプト
- **GPT**: `create_summary_with_gpt()` - ロール分離

#### **タグ選択処理**  
- **Claude**: `invoke_claude_model()` - キャッシュ機能活用
- **Nova**: `invoke_nova_model()` - シンプル構造
- **GPT**: `invoke_gpt_model()` - thinking機能対応

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

## モデル別特徴まとめ

### 🏆 **推奨用途**
- **Nova Lite**: **コスト重視**プロジェクト（0.13円、95点精度）
- **Claude Haiku**: **バランス重視**プロジェクト（0.55円、キャッシュ機能）
- **GPT-OSS 20B**: **精度重視**プロジェクト（0.43円、98点精度）

### 🔧 **技術的特徴**
- **Claude**: 最も高機能（キャッシュ、システムプロンプト分離）
- **Nova**: 最もシンプル（パラメータ最小、max_tokens不要）
- **GPT**: 標準的（OpenAI互換、thinking機能）

### 💡 **選択指針**
1. **予算最優先** → Nova Lite
2. **精度最優先** → GPT-OSS 20B  
3. **機能性重視** → Claude Haiku

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

### 🔄 **CloudFormation実装方針**
- **基準実装**: Claude Haiku版のコード構造
- **API差異対応**: リクエスト・レスポンス処理部分のみモデル別に修正
- **共通処理**: MeCab処理、価格計算、エラーハンドリングは統一
- **テスト完了**: 全3モデルでus-west-2リージョンにて動作確認済み

## メリット

- **保守性向上**: 環境変数による価格管理
- **モデル非依存**: 統一されたコード基盤
- **運用効率**: 環境変数変更のみで価格更新
- **高精度**: MeCab + LLM による精密なタグ選択
- **コスパ**: Novaで0.16円の低コスト実現
