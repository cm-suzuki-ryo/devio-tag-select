# Cloudflare Warp利用者限定アクセス設定

Cloudflare Zero Trustを使用して、Warp接続ユーザーのみにアクセスを制限します。

## 前提条件

- Cloudflare Zero Trustアカウント（無料プランで50ユーザーまで）
- Workers がデプロイ済み

## 設定手順

### 1. Zero Trust ダッシュボードにアクセス

https://one.dash.cloudflare.com/ にアクセス

### 2. Access アプリケーションを作成

1. **Access** → **Applications** → **Add an application**
2. **Self-hosted** を選択
3. 以下を設定：

```
Application name: Tag Selector
Session Duration: 24 hours
Application domain: tag-selector.cloudflare20200301.workers.dev
```

### 3. ポリシーを作成

**Policy name**: Warp Users Only

**Action**: Allow

**Configure rules**:
- **Selector**: Warp
- **Value**: (チェックを入れる)

または、より詳細な設定：

```
Include:
  - Selector: Warp
  - Value: ✓ (有効)

Require (オプション):
  - Selector: Emails
  - Value: @yourdomain.com (特定ドメインのみ)
```

### 4. 保存して適用

設定を保存すると、即座に有効になります。

## 動作確認

### Warp接続時
1. Cloudflare Warpアプリを起動
2. https://tag-selector.cloudflare20200301.workers.dev にアクセス
3. 認証画面が表示される（初回のみ）
4. 認証後、アプリケーションにアクセス可能

### Warp未接続時
- アクセス拒否画面が表示される

## 代替方法: コード内でWarpチェック

Zero Trust設定なしで、コード内でWarp接続を確認する方法：

```javascript
export default {
  async fetch(request) {
    // Warpヘッダーをチェック
    const cfWarp = request.headers.get('CF-Warp-Tag-ID');
    
    if (!cfWarp) {
      return new Response('Cloudflare Warp接続が必要です', { 
        status: 403,
        headers: { 'Content-Type': 'text/plain; charset=utf-8' }
      });
    }
    
    // 通常の処理
    // ...
  }
};
```

この方法は簡易的ですが、Zero Trustほど堅牢ではありません。

## 推奨設定

本番環境では **Zero Trust Access** の使用を推奨します：

- より強固なセキュリティ
- 詳細なログ記録
- 多要素認証対応
- デバイスポスチャーチェック

## 料金

- **Free プラン**: 50ユーザーまで無料
- **Teams Standard**: $7/ユーザー/月

詳細: https://www.cloudflare.com/plans/zero-trust-services/
