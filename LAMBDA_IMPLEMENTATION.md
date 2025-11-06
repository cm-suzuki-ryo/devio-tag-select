# Lambda実装ガイド

## 概要
このドキュメントでは、`lambda-code/`のソースコードからCloudFormationテンプレートのLambda関数を作成する手順と、カスタムヘッダー認証の実装方法を説明します。

## ソースコード構造

### **lambda-code/ディレクトリ**
```
lambda-code/
├── tags_lambda.py              # タグ取得専用Lambda
├── summary_lambda.py           # 要約専用Lambda
├── tag_selector_lambda.py      # タグ選択専用Lambda
├── common.py                   # 共通関数（価格計算等）
├── enhanced_common.py          # MeCab対応共通関数
├── model_router.py             # モデル振り分けロジック
├── claude_model.py             # Claude専用処理
├── nova_model.py               # Nova専用処理
├── gpt_model.py                # GPT専用処理
└── enhanced_index.py           # 統合版（レガシー）
```

## CloudFormationテンプレート作成手順

### **1. 基本Lambda関数定義**
```yaml
LambdaFunction:
  Type: AWS::Lambda::Function
  Properties:
    FunctionName: my-function-name
    Runtime: python3.11
    Handler: index.lambda_handler
    Role: !GetAtt LambdaExecutionRole.Arn
    Timeout: 300
    MemorySize: 1024
    Environment:
      Variables:
        ENV_VAR_NAME: value
    Code:
      ZipFile: |
        # ここにlambda-code/のPythonコードを統合
        import json
        import os
        
        def lambda_handler(event, context):
            # 実装内容
            return {'statusCode': 200}
```

### **2. IAM Role設定**
```yaml
LambdaExecutionRole:
  Type: AWS::IAM::Role
  Properties:
    AssumeRolePolicyDocument:
      Version: '2012-10-17'
      Statement:
        - Effect: Allow
          Principal:
            Service: lambda.amazonaws.com
          Action: sts:AssumeRole
    ManagedPolicyArns:
      - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
    Policies:
      - PolicyName: BedrockAccess
        PolicyDocument:
          Version: '2012-10-17'
          Statement:
            - Effect: Allow
              Action: bedrock:InvokeModel
              Resource: '*'
```

### **3. Function URL設定**
```yaml
LambdaFunctionUrl:
  Type: AWS::Lambda::Url
  Properties:
    TargetFunctionArn: !GetAtt LambdaFunction.Arn
    AuthType: NONE  # カスタムヘッダーで保護
    Cors:
      AllowCredentials: false
      AllowMethods: [GET, POST]
      AllowOrigins: ["*"]

LambdaUrlPermission:
  Type: AWS::Lambda::Permission
  Properties:
    FunctionName: !Ref LambdaFunction
    Action: lambda:InvokeFunctionUrl
    Principal: "*"
    FunctionUrlAuthType: NONE
```

## カスタムヘッダー認証実装

### **1. CloudFormationパラメータ**
```yaml
Parameters:
  CloudFrontSecretHeader:
    Type: String
    Description: 'Secret header value for CloudFront authentication'
    Default: 'MySecretValue123'
    NoEcho: true  # 秘密値を隠蔽
```

### **2. Lambda環境変数設定**
```yaml
Environment:
  Variables:
    CLOUDFRONT_SECRET_HEADER: !Ref CloudFrontSecretHeader
```

### **3. Lambda関数内ヘッダー検証**
```python
def lambda_handler(event, context):
    try:
        # カスタムヘッダー検証
        expected_secret = os.environ.get('CLOUDFRONT_SECRET_HEADER')
        if expected_secret:
            headers = event.get('headers', {})
            # 大文字小文字両方をチェック
            cloudfront_secret = (headers.get('x-cloudfront-secret') or 
                               headers.get('X-CloudFront-Secret'))
            
            if not cloudfront_secret or cloudfront_secret != expected_secret:
                return {
                    'statusCode': 403,
                    'body': json.dumps({
                        'error': 'Access denied - CloudFront access required'
                    })
                }
        
        # Function URL event handling
        if 'body' in event and event['body']:
            if isinstance(event['body'], str):
                params = json.loads(event['body'])
            else:
                params = event['body']
        else:
            params = event
        
        # 通常の処理
        # ...
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

### **4. CloudFront Distribution設定**
```yaml
CloudFrontDistribution:
  Type: AWS::CloudFront::Distribution
  Properties:
    DistributionConfig:
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

## 実装例：Tags Lambda

### **ソースコード（lambda-code/tags_lambda.py）**
```python
import json
import os
import urllib3
import hashlib

def get_tags_from_contentful():
    access_token = os.environ.get('CONTENTFUL_ACCESS_TOKEN')
    space_id = os.environ.get('CONTENTFUL_SPACE_ID')
    # ... 実装
    return tags_data

def lambda_handler(event, context):
    try:
        tags_data = get_tags_from_contentful()
        return {
            'statusCode': 200,
            'body': json.dumps({'tags_data': tags_data})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

### **CloudFormationテンプレート統合**
```yaml
TagsLambdaFunction:
  Type: AWS::Lambda::Function
  Properties:
    FunctionName: tag-selector-tags
    Runtime: python3.11
    Handler: index.lambda_handler
    Role: !GetAtt LambdaExecutionRole.Arn
    Timeout: 60
    MemorySize: 512
    Environment:
      Variables:
        CONTENTFUL_ACCESS_TOKEN: !Ref ContentfulAccessToken
        CONTENTFUL_SPACE_ID: !Ref ContentfulSpaceId
    Code:
      ZipFile: |
        import json
        import os
        import urllib3
        import hashlib

        def get_tags_from_contentful():
            access_token = os.environ.get('CONTENTFUL_ACCESS_TOKEN')
            # ... 上記のソースコードをそのまま統合
        
        def lambda_handler(event, context):
            # ... 上記のハンドラーをそのまま統合
```

## 開発ワークフロー

### **1. ローカル開発**
```bash
cd lambda-code/
# ソースコード編集
vim tags_lambda.py
```

### **2. Dockerテスト**
```bash
# テスト環境構築
docker build -t lambda-test .
docker run --rm -e AWS_DEFAULT_REGION=us-west-2 lambda-test
```

### **3. CloudFormationテンプレート更新**
1. `lambda-code/`のソースコードをコピー
2. CloudFormationの`ZipFile`セクションに貼り付け
3. インデントを調整（YAMLの`|`記法に合わせる）
4. 環境変数を適切に設定

### **4. デプロイ**
```bash
aws cloudformation deploy \
  --template-file separated_cloudformation.yaml \
  --stack-name tag-selector-separated \
  --parameter-overrides CloudFrontSecretHeader=YourSecret123 \
  --capabilities CAPABILITY_IAM \
  --region us-west-2
```

### **5. セキュリティテスト**
```bash
# 直接アクセス（ブロック確認）
curl -X POST https://lambda-function-url/ \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
# → 403 Forbidden

# CloudFront経由（正常確認）
curl -X POST https://cloudfront-domain/ \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
# → 200 OK
```

## ベストプラクティス

### **セキュリティ**
- **秘密値外部化**: CloudFormationパラメータで管理
- **NoEcho設定**: 秘密値をログに出力しない
- **ヘッダー検証**: 大文字小文字両方をチェック
- **適切なエラー**: 403 Forbiddenで不正アクセスを明示

### **パフォーマンス**
- **メモリ設定**: 処理内容に応じて最適化
- **タイムアウト**: API呼び出しを考慮した設定
- **環境変数**: 設定値の外部化

### **保守性**
- **関数分離**: 責任を明確に分離
- **共通関数**: 重複コードの削減
- **エラーハンドリング**: 適切な例外処理

### **テスト**
- **ローカルテスト**: Dockerでの事前検証
- **セキュリティテスト**: 直接アクセスブロック確認
- **統合テスト**: CloudFront経由の動作確認

## トラブルシューティング

### **よくある問題**

#### **1. ヘッダー検証エラー**
```
Error: Access denied - CloudFront access required
```
**解決**: CloudFrontのOriginCustomHeadersが正しく設定されているか確認

#### **2. Function URL 403エラー**
```
Error: Forbidden
```
**解決**: Lambda Permissionが正しく設定されているか確認

#### **3. CloudFormation ZipFileエラー**
```
Error: Invalid YAML syntax
```
**解決**: インデントとYAML記法を確認（`|`記法の使用）

### **デバッグ方法**
1. **CloudWatch Logs**でLambda実行ログを確認
2. **AWS CLI**でLambda関数を直接テスト
3. **curl -v**でHTTPヘッダーを詳細確認

## 参考資料
- [AWS Lambda Developer Guide](https://docs.aws.amazon.com/lambda/)
- [CloudFormation Lambda Reference](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-function.html)
- [CloudFront Custom Headers](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/add-origin-custom-headers.html)
