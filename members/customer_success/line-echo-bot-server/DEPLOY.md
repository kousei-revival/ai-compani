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
| `GAS_LINE_LOG_WEBAPP_URL` | LINEログを返す GAS WebApp URL。Bot が `?days=3` を付けて取得 |
| `GAS_GMAIL_WEBAPP_URL` | Gmail一覧を返す GAS WebApp URL。Bot が `?days=3&max=50` を付けて取得 |
| `CLAUDE_MODEL` | （任意）未設定時は Haiku 系の既定値 |

## Render（無料枠あり）

1. [Render](https://render.com) で GitHub を連携。
2. リポジトリ直下の **`render.yaml`** を使う場合は Blueprint から作成するか、手動で **Web Service** を追加する。
3. **手動のとき**: Root Directory を **`members/customer_success/line-echo-bot-server`** に設定し、Environment を **Docker** にする（このフォルダに `Dockerfile` がある）。
4. ダッシュボードの **Environment** に上表の変数を追加。
5. デプロイ完了後、表示された URL（例: `https://line-secretary-bot.onrender.com`）を LINE の Webhook に設定。

**注意:** 無料プランはアイドルでスリープすることがあり、初回メッセージが数十秒遅れることがあります。常時すぐ応答したい場合は有料プランの検討が必要です。

### Blueprint と Root Directory（404 対策）

リポジトリ直下の [`render.yaml`](../../../render.yaml) では `rootDir: members/customer_success/line-echo-bot-server` が指定されています。手動で Web Service を作った場合も、この値と一致させないと **`POST /callback` が 404** になります。

---

## 本番 Webhook 切り替えと検証（スマホまで）

このサービスは **FastAPI** です。`POST /callback` は本文を読み取ったあと **すぐ HTTP 200** を返し、署名検証・Messaging API・Claude はバックグラウンドで実行します。

### STEP1: LINE Developers で Webhook を本番 URL にする

1. [LINE Developers](https://developers.line.biz/) → 秘書Botの **Messaging API チャネル** → **Messaging API 設定**。
2. **Webhook URL** を  
   `https://＜Render のサービス URL のホスト＞/callback`  
   に設定（末尾は **`/callback`** で統一）。
3. **Webhook の利用** をオン。
4. **検証** で成功することを確認。

**404 のとき:** Render の **Settings → Root Directory** が **`members/customer_success/line-echo-bot-server`** か確認。**ログ転送のみ**の [`line-webhook-server`](../line-webhook-server/) を載せていると **`/callback` が無く 404** になります。

**タイムアウトのとき:** アプリがスリープから起動するまでに時間がかかっている可能性があります。Render を **Live** にしたうえで、ブラウザで **`GET /`** を開いてウェイクしてから再度検証。変更が Git に無いままだと本番コードが古いので **`git push` と再デプロイ**も確認してください。

### コマンドからの簡易チェック（デプロイ直後）

```bash
cd members/customer_success/line-echo-bot-server
BASE_URL=https://あなたのサービス.onrender.com ./scripts/smoke_production_webhook.sh
```

初回は `curl -m 120` でもタイムアウトすることがあります。そのときはダッシュボードからサービスを開くか **Manual Deploy** でウェイクしてから再実行してください。

スクリプトが **`curl: (28) Operation timed out`** で終わるときは、**(1) Web の URL が Render に表示されているものと一致するか**、**(2) サービスが停止やビルド失敗になっていないか**（Dashboard のステータスと Logs）、**(3) ブラウザで `GET /` が開けるか** を確認してください。

### STEP2: スマホだけでの動作確認（チェックリスト）

PC は不要です。**LINE アプリ**だけで次を確認します。

| 確認項目 | 期待される動き |
|----------|----------------|
| 通常の短文 | 「考え中…」が先に届き、少ししてから **push** で本文が届く |
| 「まとめ」など | コードに **`まとめ` 専用ルートは無い**ため、**Claude＋GAS のコンテキスト**で応答。ログやメール取得 URL が未設定だと薄くなることがあります |
| 環境変数 | Render に **`LINE_CHANNEL_SECRET`**, **`LINE_CHANNEL_ACCESS_TOKEN`**, **`ANTHROPIC_API_KEY`** が入っていること |

**ログ収集用チャネル**を別に運用している場合: その Bot の Webhook は **`…/line/webhook`**。秘書Botは **`…/callback`**。チャネルと URL を取り違えないでください。

### STEP3（任意）: スリープからの復帰

無料プランでは **15 分以上アクセスが無い**とスリープしやすく、**初回メッセージだけ遅い／まれにタイムアウト**することがあります。

- **対策例:** UptimeRobot 等で **`GET /`** を数分おきに監視する、または有料プランでスリープを避ける。
- **体感:** アプリが起動していれば「考え中…」→ push で自然な流れになりやすいです。

---

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
fly secrets set LINE_CHANNEL_SECRET="..." LINE_CHANNEL_ACCESS_TOKEN="..." ANTHROPIC_API_KEY="..." GAS_LINE_LOG_WEBAPP_URL="..." GAS_GMAIL_WEBAPP_URL="..."
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
- **返信が来ない**: ログで `LINE Messaging API（reply）失敗`、`LINE Messaging API（push）失敗`、Claude の所要時間を確認。
- **会話履歴が反映されない**: `GAS_LINE_LOG_WEBAPP_URL` が設定されているか、GAS WebApp が `GET ?days=3` に `200` でログ本文を返すか確認。
- **メールが反映されない**: `GAS_GMAIL_WEBAPP_URL` が設定されているか、Gmail取得用GAS WebApp が `GET ?days=3&max=50` に `200` でメール一覧を返すか確認。
- **グループに入れるとすぐ退会する**: LINE Developers Console の Messaging API タブで **Allow bot to join group chats** を有効にする。さらに、同じグループに別の LINE公式アカウントが入っていないか確認する（グループ/複数人チャットに参加できる LINE公式アカウントは通常1つ）。
