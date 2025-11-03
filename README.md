# Tag Selector Project

AWS Bedrockを使用したAIベースのブログ記事タグ自動選択システム

## 🏗️ **アーキテクチャ更新 - Lambda分離版**

### **新アーキテクチャ**
- **要約Lambda**: 記事要約専用（`summary_lambda.py`）
- **タグ選択Lambda**: タグ選択専用（`tag_selector_lambda.py`）
- **Lambda間通信**: boto3によるRequestResponse呼び出し

### **分離のメリット**
- **独立スケーリング**: 要約処理とタグ選択処理を個別にスケール
- **再利用性**: 要約Lambdaを他の用途でも使用可能
- **保守性**: 各処理の責任を明確に分離

## LLM開発者向け技術情報

### 🏗️ **アーキテクチャ概要**
- **言語**: Python 3.11
- **AWS リージョン**: us-west-2（オレゴン）
- **AWS サービス**: Lambda, Bedrock, CloudFormation
- **外部API**: Contentful
- **形態素解析**: MeCab（フォールバック付き）
- **価格計算**: 環境変数ベース

### 📁 **ソースコード構成**
```
lambda-code/
├── summary_lambda.py              # 要約専用Lambda
├── tag_selector_lambda.py         # タグ選択専用Lambda
├── enhanced_index.py              # メイン処理（統合版・レガシー）
├── model_router.py                # モデル振り分け
├── claude_model.py                # Claude専用処理
├── nova_model.py                  # Nova専用処理
├── gpt_model.py                   # GPT専用処理
├── enhanced_common.py             # 共通関数（MeCab対応）
└── common.py                      # 価格計算（環境変数ベース）
```

### 🔄 **処理フロー（分離版）**
1. **記事取得**: Contentful API → `get_article_from_contentful()`
2. **要約Lambda呼び出し**: 長文記事 → boto3 → `summary_lambda.py`
3. **MeCab処理**: 日本語解析 → `enhanced_pre_filter_tags()` → 200タグ絞り込み
4. **LLM評価**: タグランキング → `select_tags_with_model()` → モデル別API
5. **結果統合**: 上位20タグ選択 → 価格計算 → JSON出力

### 🧪 **Dockerテスト**

#### **分離Lambda版テスト**
```bash
# 分離Lambda版テスト
docker build -f Dockerfile.test-separated -t test-separated .
docker run --rm -e AWS_DEFAULT_REGION=us-west-2 -v ~/.aws:/root/.aws:ro test-separated
```

#### **従来版テスト（レガシー）**
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

### 🔧 **モデル別API仕様**

#### **Claude (基準実装)**
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

#### **Nova (API仕様変更)**
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

#### **GPT (ロール分離型)**
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

### 📊 **モデル性能・コスト (実測値)**

| モデル | コスト | 精度 | 処理時間 | モデルID |
|--------|--------|------|----------|----------|
| **Nova Lite** | 0.0979円 | 95点 | 12秒 | `us.amazon.nova-lite-v1:0` |
| **GPT-OSS 20B** | 0.2205円 | 98点 | 11秒 | `openai.gpt-oss-20b-1:0` |
| **Claude Haiku 4.5** | 0.2488円 | 95点 | 9秒 | `global.anthropic.claude-haiku-4-5-20251001-v1:0` |

### 🔧 **CloudFormation実装方針**
- **基準実装**: Claude Haiku版のコード構造
- **API差異対応**: リクエスト・レスポンス処理部分のみモデル別に修正
- **共通処理**: MeCab処理、価格計算、エラーハンドリングは統一
- **テスト完了**: 全3モデルでus-west-2リージョンにて動作確認済み

### 🚀 **デプロイ方法**

```bash
# Claude版（基準実装）
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

### ⚙️ **環境変数**
- `INPUT_PRICE_PER_MILLION`: 入力トークン価格（USD/100万トークン）
- `OUTPUT_PRICE_PER_MILLION`: 出力トークン価格（USD/100万トークン）  
- `USD_TO_JPY`: 為替レート（USD→JPY）
- `MODEL_ID`: 使用するモデルID
- `CONTENTFUL_ACCESS_TOKEN`: Contentful API トークン
- `SUMMARY_LAMBDA_NAME`: 要約Lambda関数名（分離版のみ）

### 🔍 **開発フロー**
1. `lambda-code/` でソース変更
2. Dockerでローカルテスト
3. CloudFormationテンプレートに反映
4. デプロイ・動作確認

---

## 📖 **人間向け情報**
詳細な使用方法、推奨用途、テスト環境については [USAGE.md](USAGE.md) を参照してください。
