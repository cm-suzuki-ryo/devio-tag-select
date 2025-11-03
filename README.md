# Tag Selector Project

AWS Bedrockを使用したAIベースのブログ記事タグ自動選択システム

## 🏗️ **アーキテクチャ更新 - Lambda分離版 + CloudFront保護**

### **新アーキテクチャ**
- **要約Lambda**: 記事要約専用（`summary_lambda.py`）
- **タグ取得Lambda**: タグ取得専用（`tags_lambda.py`）
- **タグ選択Lambda**: タグ選択専用（`tag_selector_lambda.py`）
- **CloudFront**: グローバル配信 + カスタムヘッダー認証
- **Lambda間通信**: boto3によるRequestResponse呼び出し

### **分離のメリット**
- **独立スケーリング**: 要約処理とタグ選択処理を個別にスケール
- **再利用性**: 要約Lambdaを他の用途でも使用可能
- **保守性**: 各処理の責任を明確に分離
- **セキュリティ**: CloudFrontカスタムヘッダーによる保護
- **パフォーマンス**: エッジキャッシュによる高速化

## 🔒 **セキュリティ機能**

### **CloudFrontカスタムヘッダー認証**
- **直接アクセス保護**: Lambda Function URLへの直接アクセスをブロック
- **カスタムヘッダー**: `X-CloudFront-Secret`による認証
- **パラメータ化**: CloudFormationデプロイ時に秘密値を設定可能
- **完全保護**: 秘密値を知らない限りアクセス不可

```bash
# 直接アクセス（ブロック）
curl https://lambda-url/ → 403 Forbidden

# CloudFront経由（許可）  
curl https://cloudfront-domain/ → 200 OK
```

## LLM開発者向け技術情報

### 🏗️ **アーキテクチャ概要**
- **言語**: Python 3.11
- **AWS リージョン**: us-west-2（オレゴン）
- **AWS サービス**: Lambda, Bedrock, CloudFront, CloudFormation
- **外部API**: Contentful
- **形態素解析**: MeCab（フォールバック付き）
- **価格計算**: 環境変数ベース
- **セキュリティ**: カスタムヘッダー認証

### 📁 **ソースコード構成**
```
lambda-code/
├── summary_lambda.py              # 要約専用Lambda
├── tag_selector_lambda.py         # タグ選択専用Lambda
├── tags_lambda.py                 # タグ取得専用Lambda
├── enhanced_index.py              # メイン処理（統合版・レガシー）
├── model_router.py                # モデル振り分け
├── claude_model.py                # Claude専用処理
├── nova_model.py                  # Nova専用処理
├── gpt_model.py                   # GPT専用処理
├── enhanced_common.py             # 共通関数（MeCab対応）
└── common.py                      # 価格計算（環境変数ベース）
```

### 🔄 **処理フロー（分離版 + CloudFront）**
```
Client → CloudFront → Lambda Function URL → tag-selector-main
                                         → tag-selector-tags (タグ取得)
                                         → tag-selector-summary (要約)
                                         → AI処理 → 結果
```

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
- **セキュリティ**: カスタムヘッダー認証による保護
- **テスト完了**: 全3モデルでus-west-2リージョンにて動作確認済み

### 🚀 **デプロイ方法**

#### **分離版（推奨）**
```bash
# カスタムヘッダー付き分離版
aws cloudformation deploy \
  --template-file separated_cloudformation.yaml \
  --stack-name tag-selector-separated \
  --parameter-overrides CloudFrontSecretHeader=YourSecretValue123 \
  --capabilities CAPABILITY_IAM \
  --region us-west-2
```

#### **従来版（レガシー）**
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

#### **分離版 + CloudFront**
| 項目 | 結果 | 詳細 |
|------|------|------|
| **CloudFront URL** | ✅ 動作確認済み | `https://d2wfh8k3k94bjx.cloudfront.net` |
| **直接アクセス** | ✅ ブロック成功 | 403 Forbidden |
| **処理時間** | ✅ 高速化 | CloudFront: 5.27秒 vs 直接: 7.29秒 |
| **コスト** | ✅ 最適化 | 0.41円（CloudFront経由） |

#### **従来版（レガシー）**
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
- `CONTENTFUL_SPACE_ID`: Contentful Space ID
- `SUMMARY_LAMBDA_NAME`: 要約Lambda関数名（分離版のみ）
- `TAGS_LAMBDA_NAME`: タグ取得Lambda関数名（分離版のみ）
- `CLOUDFRONT_SECRET_HEADER`: CloudFront認証用秘密ヘッダー（分離版のみ）

### 🔍 **開発フロー**
1. `lambda-code/` でソース変更
2. Dockerでローカルテスト
3. CloudFormationテンプレートに反映
4. デプロイ・動作確認
5. セキュリティテスト実施

### 📝 **Lambda実装ガイド**

#### **CloudFormationでのLambda関数作成**
```yaml
# 基本構造
LambdaFunction:
  Type: AWS::Lambda::Function
  Properties:
    FunctionName: function-name
    Runtime: python3.11
    Handler: index.lambda_handler
    Role: !GetAtt LambdaExecutionRole.Arn
    Timeout: 300
    MemorySize: 1024
    Environment:
      Variables:
        ENV_VAR: value
    Code:
      ZipFile: |
        # インライン Python コード
        import json
        def lambda_handler(event, context):
            return {'statusCode': 200}
```

#### **カスタムヘッダー認証実装**
```python
# Lambda関数内でのヘッダー検証
def lambda_handler(event, context):
    try:
        # カスタムヘッダー検証
        expected_secret = os.environ.get('CLOUDFRONT_SECRET_HEADER')
        if expected_secret:
            headers = event.get('headers', {})
            cloudfront_secret = headers.get('x-cloudfront-secret') or headers.get('X-CloudFront-Secret')
            if not cloudfront_secret or cloudfront_secret != expected_secret:
                return {
                    'statusCode': 403,
                    'body': json.dumps({'error': 'Access denied - CloudFront access required'})
                }
        
        # 通常の処理
        # ...
```

#### **CloudFrontカスタムヘッダー設定**
```yaml
# CloudFront Distribution設定
Origins:
  - Id: LambdaOrigin
    DomainName: !Select [2, !Split ["/", !GetAtt LambdaFunctionUrl.FunctionUrl]]
    CustomOriginConfig:
      HTTPPort: 443
      OriginProtocolPolicy: https-only
    OriginCustomHeaders:
      - HeaderName: X-CloudFront-Secret
        HeaderValue: !Ref CloudFrontSecretHeader
```

#### **パラメータ化された秘密値**
```yaml
Parameters:
  CloudFrontSecretHeader:
    Type: String
    Description: 'Secret header value for CloudFront authentication'
    Default: 'MySecretValue123'
    NoEcho: true

# Lambda環境変数で参照
Environment:
  Variables:
    CLOUDFRONT_SECRET_HEADER: !Ref CloudFrontSecretHeader
```

#### **Function URL設定**
```yaml
# NONE認証タイプ（カスタムヘッダーで保護）
LambdaFunctionUrl:
  Type: AWS::Lambda::Url
  Properties:
    TargetFunctionArn: !GetAtt LambdaFunction.Arn
    AuthType: NONE
    Cors:
      AllowCredentials: false
      AllowMethods: [GET, POST]
      AllowOrigins: ["*"]

# パブリックアクセス許可
LambdaUrlPermission:
  Type: AWS::Lambda::Permission
  Properties:
    FunctionName: !Ref LambdaFunction
    Action: lambda:InvokeFunctionUrl
    Principal: "*"
    FunctionUrlAuthType: NONE
```

#### **ソースコード統合手順**
1. **lambda-code/**でソース開発
2. **ZipFile**でCloudFormationに埋め込み
3. **環境変数**で設定値を外部化
4. **IAM権限**を適切に設定
5. **テスト**でセキュリティ検証

---

## 📖 **人間向け情報**
詳細な使用方法、推奨用途、テスト環境については [USAGE.md](USAGE.md) を参照してください。
