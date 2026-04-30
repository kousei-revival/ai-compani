# LINE 秘書Bot — クラウドデプロイ手順

このフォルダは **Docker** でどのホスティングにも載せられます。代表的な **Render**、**Fly.io**、**Railway** の例です。

## 共通の準備

1. コードを **GitHub などに push** しておく。
2. LINE Developers の Webhook URL を、デプロイ後に **`https://＜あなたのドメイン＞/callback`** または **`…/line/webhook`** に更新する。
3. 次の **環境変数** をホスティング側に設定する（`.env` はリポジトリにコミットしない）。

| 変数 | 説明 |
|------|------|
| `LINE_CHANNEL_SECRET` | Messaging API のチャネルシークレット |
| `LINE_CHANNEL_ACCESS_TOKEN` | チャネルアクセストークン |
| `ANTHROPIC_API_KEY` | Claude API キー |
| `CLAUDE_MODEL` | （任意）未設定時は Haiku 系の既定値 |

## Render（無料枠あり）

1. [Render](https://render.com) で GitHub を連携。
2. リポジトリ直下の **`render.yaml`** を使う場合は Blueprint から作成するか、手動で **Web Service** を追加する。
3. **手動のとき**: Root Directory を **`members/customer_success/line-echo-bot-server`** に設定し、Environment を **Docker** にする（このフォルダに `Dockerfile` がある）。
4. ダッシュボードの **Environment** に上表の変数を追加。
5. デプロイ完了後、表示された URL（例: `https://line-secretary-bot.onrender.com`）を LINE の Webhook に設定。

**注意:** 無料プランはアイドルでスリープすることがあり、初回メッセージが数十秒遅れることがあります。常時すぐ応答したい場合は有料プランの検討が必要です。

## Fly.io（東京リージョン例）

1. [Fly CLI](https://fly.io/docs/hands-on/install-flyctl/) をインストールし `fly auth login`。
2. このディレクトリでデプロイ:

```bash
cd members/customer_success/line-echo-bot-server
fly launch
```

既存の `fly.toml` がある場合は、アプリ名やリージョンを聞かれたら調整。

3. シークレットを設定:

```bash
fly secrets set LINE_CHANNEL_SECRET="..." LINE_CHANNEL_ACCESS_TOKEN="..." ANTHROPIC_API_KEY="..."
```

4. デプロイ:

```bash
fly deploy
```

Fly は **`PORT`** を注入します。`Dockerfile` の `uvicorn` がそのポートで待ち受けます（`internal_port` と一致させてください）。

## Railway

1. [Railway](https://railway.app) で GitHub リポジトリを連携し、**New Project** → **Deploy from GitHub**。
2. 生成されたサービスを開き、**Settings → Root Directory** を  
   **`members/customer_success/line-echo-bot-server`** に設定する（モノレポのため必須）。
3. **Variables** に共通準備の環境変数を追加（`LINE_*`、`ANTHROPIC_API_KEY` など）。
4. **Settings → Networking → Generate Domain** で公開 URL を発行する。
5. LINE Developers の Webhook を **`https://＜発行ドメイン＞/callback`** に設定する。

このフォルダの **`railway.toml`** で Docker ビルドとヘルスチェック（`GET /`）を指定しています。

## Google Cloud Run / AWS など

- **ビルドコンテキスト**: このフォルダ（`Dockerfile` があるディレクトリ）。
- **起動**: `CMD` は Dockerfile に記載済み（`PORT` 対応）。
- **ヘルスチェック**: `GET /` が `200` と `{"ok":true,...}` を返します。

## トラブルシュート

- **404**: Webhook のパスが `/callback` または `/line/webhook` になっているか確認。
- **署名エラー**: `LINE_CHANNEL_SECRET` がそのチャネルと一致しているか確認。
- **返信が来ない**: ログで `LINE Messaging API（reply）失敗` と Claude の所要時間を確認（reply_token の期限など）。
