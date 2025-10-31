# Lambda Code

## 現在使用中のファイル

### メインファイル
- `enhanced_index.py` - 改良版メイン処理（テスト用）
- `index.py` - 従来版メイン処理

### 共通ライブラリ
- `common.py` - 共通関数（環境変数ベース価格計算）
- `enhanced_common.py` - 改良版共通関数（MeCab対応）

### モデル別処理
- `claude_model.py` - Claude Haiku処理
- `nova_model.py` - Amazon Nova処理
- `gpt_model.py` - OpenAI GPT処理
- `model_router.py` - モデル振り分け

### 設定ファイル
- `requirements.txt` - Python依存関係
- `Dockerfile` - 基本Dockerイメージ

## CloudFormationテンプレート

全てのCloudFormationテンプレートはコードを直接埋め込んでいるため、
これらのファイルは開発・テスト用途のみです。

## テスト

テストファイルは `../tests/` ディレクトリに移動済み。
