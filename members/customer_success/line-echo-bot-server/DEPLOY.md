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

### PORT と Start Command（`Port scan timeout … port 3000` 対策）

Render はコンテナに **`PORT` 環境変数**（例: `3000`）を注入し、そのポートで待ち受けているか確認します。

| やること | 理由 |
|----------|------|
| **Environment に `PORT` を自分で追加しない** | プラットフォーム注入値と食い違うと、スキャンが失敗する。 |
| **Start Command を空にする**（推奨） | `Dockerfile` の `ENTRYPOINT`（`docker-entrypoint.sh`）が **`$PORT`** で uvicorn を起動する。 |
| Start Command が **空にできない** UI のとき | 次の **どちらか1つ**をそのまま貼る（`$PORT` は Render が注入するので **引用符で囲まない**）。<br>• `/app/docker-entrypoint.sh`<br>• `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| Start Command を別の形で自前にするとき | 必ず **`--port $PORT`** を使う。**`--port 10000` など固定は NG**（ログでは起動できても Render の検出だけ失敗する）。 |

デプロイログに `docker-entrypoint: binding uvicorn to PORT=…` と出るので、**その数字が Render の期待と一致しているか**を確認してください。

**コピペ用（Start Command 欄に1行で入れる）:**

```text
/app/docker-entrypoint.sh
```

または（`WORKDIR /app` 想定。`uvicorn` が PATH にあるため動く）:

```text
uvicorn main:app --host 0.0.0.0 --port $PORT
```

※ `"$PORT"` のようにダブルクォートで囲むと、**シェルによっては空扱いになり 8000 固定になる**ことがあります。**`$PORT` だけ**を推奨します。

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

**タイムアウトのとき:** 無料 Render の **スリープ／APPLICATION LOADING** で、アプリが応答する前に LINE が諦めることがあります。詳しくは下記 **STEP4**。**変更が Git に無いままだと本番コードが古いので `git push` と再デプロイ**も確認してください。

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

### STEP4: 「Webhookイベントオブジェクト送信時にタイムアウト」の対処（運用）

無料 Render が **スリープ中／APPLICATION LOADING 中**だと、FastAPI が **`POST /callback` に応答する前**に時間がかかり、LINE が **タイムアウト**と表示することがあります。このサーバーは **`request.body()` の読み取り後にすぐ HTTP 200** を返す実装のため、**コンテナが起ききった状態で検証する**ことが効きます。

#### 手順 A: ウェイクしてから Webhook「検証」する

1. ブラウザで `https://＜あなたの Render のホスト＞.onrender.com/` を開く。
2. **APPLICATION LOADING** が終わり、`{"ok":true,...}` のような JSON が **すぐ**表示されるまで待つ（必要なら再読み込み）。
   - Safari 等では **黒いターミナル風の「サービス起動ログ」画面**のまま **数十秒〜1分以上**かかることがあります。この間に LINE の「検証」を押すと、**アプリがまだ `GET /` にも答えられない**ため LINE 側が先にタイムアウトします。**JSON が画面に出たあと**に検証してください。
3. **すぐあとに** LINE Developers → **Messaging API 設定** → **Webhook「検証」** を実行する。
4. 失敗したら **1〜3 を繰り返す**（検証・テスト送信はウェイク直後が確実）。

**コマンドでウェイク＋疎通までまとめて行う場合**（無料枠の初回が遅いとき、GET `/` を数分かけてリトライします）:

```bash
cd members/customer_success/line-echo-bot-server
BASE_URL=https://＜あなたの Render のホスト＞.onrender.com ./scripts/wake_render_for_line_webhook.sh
```

成功したら **その直後**に LINE の「検証」を押してください。スクリプト末尾に Logs / 設定 / UptimeRobot の確認メモも出ます。

実メッセージのテストも、できれば **ブラウザで `/` を開いた直後**に送ると安定しやすいです。

#### 手順 B: Render Logs とタイムアウト時刻を突き合わせる

1. LINE でタイムアウトが出た **時刻（自分の時計）** をメモする。
2. Render → サービス → **Logs**。ログが **UTC** のことが多いので、日本時間なら **−9 時間**で UTC に寄せて読む。
3. その付近に **`POST /callback`**、`Received`、`INFO:` などアプリのログがあるか確認する。
   - **ログに POST が無い**: リクエストがアプリに届く前に諦められたパターン（スリープ・ロード中・URL 誤り）。手順 A と Root Directory／Webhook URL を再確認。
   - **ログに POST がある**: アプリは受け付けている。続きのログで署名エラーや例外が無いか見る。

**チェックリスト（コピー用）**

| 確認 | 内容 |
|------|------|
| 時刻 | LINE エラー表示時刻（JST）→ UTC に換算して Logs で同時間帯を開く |
| POST の有無 | その窓で `POST`、`/callback`、`Received` が出るか |
| 分岐 | POST 無し → ウェイク・URL・到達前タイムアウト。POST あり → 署名・例外ログを追う |

#### 手順 B2: Render ダッシュボード設定の再確認

| 項目 | 期待値 |
|------|--------|
| **Status** | Live（ビルド失敗・停止でない） |
| **URL** | LINE に書いた `https://…onrender.com` と一致 |
| **Root Directory** | `members/customer_success/line-echo-bot-server` |
| **Environment** | **Docker**（このリポの `Dockerfile` を使う） |
| **Env** | `LINE_CHANNEL_SECRET`, `LINE_CHANNEL_ACCESS_TOKEN`, `ANTHROPIC_API_KEY` など必要変数が設定済み |

#### 手順 C: 頻発するときの恒久対策

| 手段 | 内容 |
|------|------|
| 無料 | **UptimeRobot** 等で **`GET https://＜ホスト＞.onrender.com/`** を **約 5 分ごと**に監視する。**監視タイプは HTTP(s)**、期待ステータス **200** を選ぶ。 |
| 課金 | Render で **スリープしない／常時起動**できるプランへ変更する。 |

**切り分け:** 「長時間放置後の **最初の 1 回だけ**タイムアウト／遅い」なら **スリープ起因**として手順 A〜C でほぼ説明できます。**毎回**タイムアウトなら URL・チャネル・ビルド失敗も疑ってください。

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
- **Webhook タイムアウト**: 無料 Render のスリープ中は **`POST /callback` がアプリに届く前に諦められる**ことがある。**STEP4**（ウェイク後に検証・Logs・定期監視）を参照。
