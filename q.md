# Tag Selector Project - Git操作メモ

## リポジトリ情報

- **リポジトリ**: `git@github.com:cm-suzuki-ryo/devio-tag-select.git`
- **ブランチ**: `main`

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

## プロジェクト構成

- CloudFormationテンプレート
- モジュール化されたLambda関数コード
- 3つのAIモデル対応（Claude、Nova、GPT-OSS）
- 要約機能付きタグ選択システム
