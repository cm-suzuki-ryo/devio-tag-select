# Tag Selector Project

AWS Bedrockを使用したAIベースのブログ記事タグ自動選択システム

## 🏗️ **統合アーキテクチャ - Step Functions版**

### **新アーキテクチャ**
- **HTML Formatter Lambda**: Web UI + Step Functions実行
- **Contentful取得Lambda**: 記事取得専用（Preview API対応）
- **要約Lambda**: 記事要約専用（全記事で実行）
- **タグ取得Lambda**: タグ取得専用
- **推薦Lambda**: タグ推薦専用
- **スニペット生成Lambda**: SEO用スニペット生成
- **Step Functions Express**: ワークフロー制御

### **統合のメリット**
- **1つのCloudFormation**: 全機能を統一テンプレートで管理
- **視覚的フロー**: Step Functionsコンソールで実行状況確認
- **独立スケーリング**: 各処理を個別にスケール
- **エラーハンドリング**: 各ステップでリトライ設定
- **コスト効率**: Express版で低コスト実現
- **マルチリージョン対応**: us-east-1, us-west-2等で動作

## 🔄 **処理フロー**
```
Client → CloudFront (Basic認証) → HTML Formatter Lambda → Step Functions
                                                        ├─ Contentful記事取得 (Preview API)
                                                        ├─ タグ一覧取得
                                                        ├─ 要約処理（全記事で実行）
                                                        ├─ 並列実行 ┬─ タグ推薦
                                                        │          └─ スニペット生成
                                                        └─ 結果統合 → HTML表示
```

## ✨ **主要機能**

### **Web UI (Protected)**
- **CloudFront + Basic認証**: cm:cm でアクセス保護
- **Contentful URL入力**: 記事執筆URLから直接解析
- **リアルタイム処理**: Step Functions経由で即座に結果表示
- **美しいHTML出力**: タグ、スニペット、コスト情報を視覚化

### **スニペット生成**
- **SEO最適化**: 160文字制限でGoogle検索結果に最適
- **AI生成**: 記事内容から魅力的な要約を自動生成
- **並列処理**: タグ推薦と同時実行で処理時間短縮
- **複数モデル対応**: Nova Lite, Claude Haiku対応

### **Contentful統合**
- **Preview API**: 未公開記事も解析可能
- **URL検証**: 指定されたspaceのURLのみ受け入れ
- **クエリパラメータ対応**: ?focusedField=title等を自動処理

## LLM開発者向け技術情報

### 🏗️ **アーキテクチャ概要**
- **言語**: Python 3.11 (Lambda), Node.js 20.x (HTML Formatter)
- **AWS リージョン**: マルチリージョン対応（us-east-1, us-west-2等）
- **AWS サービス**: Lambda, Bedrock, Step Functions, CloudFormation, CloudFront
- **外部API**: Contentful (Preview API)
- **ワークフロー**: Step Functions Express
- **価格計算**: 環境変数ベース、動的JPY換算

### 📁 **ソースコード構成**
```
cloudformation-unified.yaml           # 統一テンプレート
lambda-code/
├── stepfunctions_main.py             # メインLambda（SF実行）
├── contentful_getter.py              # Contentful取得
├── snippet_generator_lambda.py       # スニペット生成
├── summary_lambda.py                 # 要約処理（参考）
├── tag_selector_lambda.py            # タグ推薦（参考）
├── tags_lambda.py                    # タグ取得（参考）
└── enhanced_common.py                # 共通関数（参考）
```

### 🔄 **Step Functions定義**
```json
{
### 🔄 **Step Functions定義**
```json
{
  "StartAt": "GetArticle",
  "States": {
    "GetArticle": "記事取得",
    "GetTags": "タグ一覧取得", 
    "SummarizeText": "要約処理（全記事で実行）",
    "ParallelProcessing": {
      "Type": "Parallel",
      "Branches": [
        {"StartAt": "RecommendTags"},
        {"StartAt": "GenerateSnippet"}
      ]
    },
    "FormatOutput": "結果統合・出力"
  }
}
```

### 🧪 **デプロイ方法**

#### **Protected Web UI版（推奨）**
```bash
# デプロイ
aws cloudformation deploy \
  --template-file cloudformation-protected-web-ui.yaml \
  --stack-name tag-selector-protected-web-ui \
  --capabilities CAPABILITY_IAM \
  --region us-east-1 \
  --s3-bucket aws-cloudformation-templates-784693731708-us-east-1 \
  --parameter-overrides \
    ContentfulSpaceId="ct0aopd36mqt" \
    ContentfulAccessToken="6Z4wPWStkHj3d_EA0MQt89nWJpIFSBJcmAQ_YzDpkAg" \
    ContentfulPreviewToken="vSd5M3IdcLZvfiGphiuMsgYc1wf31zGSGRS0lrxlZl0" \
    BasicAuthUser="cm" \
    BasicAuthPassword="cm"
```

### 🌐 **アクセス方法**
- **CloudFront URL**: https://d2yvh52qto32qs.cloudfront.net
- **Basic認証**: cm:cm
- **入力**: Contentful記事執筆URL（例: https://app.contentful.com/spaces/ct0aopd36mqt/entries/ENTRY_ID?focusedField=title）

### 🔧 **モデル別API仕様**

#### **Nova (推奨)**
```python
# リクエスト形式
body = {
    "messages": [{"role": "user", "content": [{"text": prompt}]}],
    "inferenceConfig": {"temperature": 0.1}
}

# レスポンス解析
result_text = response_body['output']['message']['content'][0]['text']
cache_info = {
    'input_tokens': response_body['usage']['inputTokens'],
    'output_tokens': response_body['usage']['outputTokens']
}
```

#### **Claude (フォールバック)**
```python
# リクエスト形式
body = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 8000,
    "messages": [{"role": "user", "content": prompt}]
}

# レスポンス解析
result_text = response_body['content'][0]['text']
cache_info = {
    'input_tokens': response_body['usage']['input_tokens'],
    'output_tokens': response_body['usage']['output_tokens']
}
```

### 📊 **モデル性能・コスト (実測値)**

| モデル | コスト | 精度 | 処理時間 | モデルID |
|--------|--------|------|----------|----------|
| **Nova Lite** | 0.14円 | 95点 | 4.3秒 | `us.amazon.nova-lite-v1:0` |
| **Claude Haiku 4.5** | 0.15円 | 98点 | 4.3秒 | `global.anthropic.claude-haiku-4-5-20251001-v1:0` |
| **Claude Haiku 3** | 0.25円 | 95点 | 4.5秒 | `anthropic.claude-3-haiku-20240307-v1:0` |

### 🔧 **実装同期状況**

#### **CloudFormation版（本番環境）**
- ✅ **統一実装**: 全機能が単一テンプレートで動作
- ✅ **Claude最適化**: Haiku 4.5専用、高品質プロンプト対応
- ✅ **動的モデル**: 指定モデルを柔軟に使用
- ✅ **System プロンプト**: 「記事要約の専門家」で品質向上

#### **lambda-code/版（開発・テスト環境）**
- ✅ **多モデル対応**: Nova, Claude, gpt-oss-20b対応
- ✅ **モジュール分割**: 開発・テスト・デバッグ用
- ✅ **CloudFormation同期**: Claude処理は本番環境と同一仕様
- ✅ **責任分離**: 記事取得は呼び出し元で実施



### 🚀 **デプロイ方法**

#### **統一アーキテクチャ（推奨）**
```bash
# 環境変数読み込み
source .env

# 統一テンプレートデプロイ
aws cloudformation deploy \
  --template-file cloudformation-unified.yaml \
  --stack-name tag-selector-unified \
  --capabilities CAPABILITY_IAM \
  --region us-west-2 \
  --parameter-overrides \
    ContentfulSpaceId="${CONTENTFUL_SPACE_ID}" \
    ContentfulAccessToken="${CONTENTFUL_ACCESS_TOKEN}"
```

### 🧪 **デプロイ後テスト結果 (us-west-2)**

#### **統一版 + Step Functions**
| 項目 | 結果 | 詳細 |
|------|------|------|
| **Lambda Function URL** | ✅ 動作確認済み | 直接アクセス可能 |
| **Step Functions** | ✅ ワークフロー実行 | Express版で高速処理 |
| **並列実行** | ✅ 最適化完了 | タグ推薦+スニペット生成同時処理 |
| **処理時間** | ✅ 4.3秒 | 並列処理で大幅短縮 |
| **コスト** | ✅ 0.14-0.15円 | Nova Lite/Claude Haiku使用 |

### ⚙️ **環境変数**
- `INPUT_PRICE_PER_MILLION`: 入力トークン価格（USD/100万トークン）
- `OUTPUT_PRICE_PER_MILLION`: 出力トークン価格（USD/100万トークン）  
- `USD_TO_JPY`: 為替レート（USD→JPY）
- `MODEL_ID`: 使用するモデルID
- `CONTENTFUL_ACCESS_TOKEN`: Contentful API トークン
- `CONTENTFUL_SPACE_ID`: Contentful Space ID

### 🔍 **開発フロー**
1. `lambda-code/` でソース変更
2. CloudFormationテンプレートに反映
3. デプロイ・動作確認
4. Step Functionsコンソールで実行状況確認

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
    Code:
      ZipFile: |
        # インライン Python コード
        import json
        def lambda_handler(event, context):
            return {'statusCode': 200}
```

#### **Step Functions統合**
```yaml
# Step Functions State Machine
TagSelectorStateMachine:
  Type: AWS::StepFunctions::StateMachine
  Properties:
    StateMachineName: tag-selector-unified
    StateMachineType: EXPRESS
    RoleArn: !GetAtt StepFunctionsRole.Arn
    DefinitionString: !Sub |
      {
        "StartAt": "GetArticle",
        "States": {
          "GetArticle": {
            "Type": "Task",
            "Resource": "arn:aws:states:::lambda:invoke",
            "Parameters": {
              "FunctionName": "${ContentfulGetterFunction}",
              "Payload": {"slug.$": "$.slug"}
            },
            "Next": "ProcessFlow"
          }
        }
      }
```

#### **Function URL設定**
```yaml
# パブリックアクセス許可
LambdaFunctionUrl:
  Type: AWS::Lambda::Url
  Properties:
    TargetFunctionArn: !GetAtt LambdaFunction.Arn
    AuthType: NONE
    Cors:
      AllowCredentials: false
      AllowMethods: [GET, POST]
      AllowOrigins: ["*"]
```

#### **ソースコード統合手順**
1. **lambda-code/**でソース開発
2. **ZipFile**でCloudFormationに埋め込み
3. **環境変数**で設定値を外部化
4. **IAM権限**を適切に設定
5. **Step Functions**でワークフロー制御

---

## 🌐 **HTML Viewer - Web UI**

### **概要**
Tag Selectorの解析結果を美しいHTML形式で表示するWebインターフェース

### **機能**
- **Slug入力フォーム**: 記事slugを入力して解析実行
- **リアルタイム解析**: 既存Tag Selector統合システムと連携
- **美しいHTML表示**: 記事要約、タグ、フィードバック、コストを視覚化
- **レスポンシブデザイン**: モバイル対応のクリーンなUI

### **アーキテクチャ**
```
Browser → HTML Viewer Lambda → Tag Selector統合システム
                              ├─ Step Functions実行
                              ├─ 記事解析処理
                              └─ JSON結果返却
```

### **デプロイ済みURL**
**https://zupizdxckbvx5y74xi3wbsskiy0fufcl.lambda-url.us-west-2.on.aws/**

### **使用方法**
1. 上記URLにアクセス
2. 記事のslugを入力（例: `amazon-ebs-performance-monitoring-metrics-ebs-volumes`）
3. 「記事を解析」ボタンをクリック
4. 解析結果がHTML形式で表示

### **技術スタック**
- **フレームワーク**: Hono v4.0.0 (Node.js)
- **ランタイム**: AWS Lambda (Node.js 20.x)
- **統合**: 外部Lambda URL呼び出し
- **UI**: レスポンシブHTML/CSS

### **ソースコード**
```
html-viewer/
├── integrated-lambda.yaml           # 統合版CloudFormation
├── server.js                        # ローカル開発用
├── index.js                         # Lambda関数コード
└── package.json                     # Node.js依存関係
```

### **ローカル開発**
```bash
cd html-viewer
npm install
npm run dev
# http://localhost:3000 でアクセス
```

---

## 📖 **人間向け情報**
詳細な使用方法、推奨用途、テスト環境については [USAGE.md](USAGE.md) を参照してください。
