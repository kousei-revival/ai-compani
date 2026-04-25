# ai-company Slack ボット（@メンション返信）

`app_mention` だけ受け、**チャンネル ID**に応じた `personas/<key>.md` に加え、**任意の `.claude/skills/<skill名>/skill.md`** をシステムプロンプトに含めて LLM が返信します。ユーザーの会話は **Slack だけ**で完結。裏で **小さな Node プロセス**と **LLM API** は必要です（Cursor は不要）。

## 必要なもの

- Node.js 20 以上
- Slack App の **Signing Secret** / **Bot User OAuth Token**（`xoxb-`）
- **OpenAI** または **Anthropic** の API キー
-（推奨・ローカル向け）**Socket Mode** 用 `SLACK_APP_TOKEN`（`xapp-`）

## `.claude` スキル

デスクトップ `your-perfect-days/.claude` を **`projects/slack-bot/.claude` にコピー済み**です。`config/channel-persona.json` の各チャンネルに **`"skill": "edit-article"`** のように **スキルディレクトリ名**を書くと、その `skill.md`（冒頭の YAML フロントマターは除去）をプロンプトに取り込みます。役割に合わせて **[config/channel-persona.json](config/channel-persona.json)** を編集してください。長大なスキルは `SKILL_PROMPT_MAX_CHARS`（デフォルト 12000 文字）で切り捨てます。

## ローカル動作

### 推奨: Socket Mode（公開 URL・ngrok 不要）

1. Slack App → **Settings → Socket Mode** → On。  
2. **App-Level Token** を作成（**Scope: `connections:write`**）。`xapp-1-` を `.env` の `SLACK_APP_TOKEN` に入れる。  
3. **Event Subscriptions** では、Socket Mode 利用時は **Request URL の検証を不要**（Slack 管理画面の案内に従う）。`app_mention` を **Subscribe to bot events** に入れる。  
4. 起動:

```bash
cd ~/ai-company/projects/slack-bot
cp .env.example .env
# SLACK_SIGNING_SECRET, SLACK_BOT_TOKEN, SLACK_APP_TOKEN, LLM キー
npm install
npm run build
npm start
# → "Socket Mode 起動" と出ればOK（/health は使わない）
```

### HTTP モード（本番・ngrok）

`SLACK_APP_TOKEN` を**未設定**にすると従来どおり **Express** で `PORT` 待受。**ngrok** 等で `https` を **Request URL** に登録:

```text
ngrok http 3000
# https://xxxx.ngrok.io/slack/events
```

`npm start` 後 `http://127.0.0.1:3000/health` → `ok`

## Slack App の設定

1. [Slack API: Your Apps](https://api.slack.com/apps) で **Create New App**（From scratch）。
2. **OAuth & Permissions** → **Bot Token Scopes** を追加:  
   - `app_mentions:read`  
   - `chat:write`  
   - （会話文脈を取りに行くなら `channels:history` 等も。初版はメンション本文だけで可）
3. **Install to Workspace** し、**Bot User OAuth Token**（`xoxb-`）を `.env` の `SLACK_BOT_TOKEN` に入れる。
4. **Event Subscriptions**（HTTP モードのとき）: Enable Events → **Request URL** に `https://<あなたのホスト>/slack/events`、Challenge **Verified**。**Socket Mode 利用時**は UI の指示に従い、Request URL は不要。  
5. **Subscribe to bot events** に `app_mention` を追加。保存のあと**再 Install**を促されたら従う。  
6. 各 `#ai-*` や `#general` で **アプリを招待**（「統合」または `/invite @アプリ名`）。Bot が居ないと `app_mention` が来ません。

**Signing Secret**は **Basic Information** ページの **App Credentials** から。`.env` の `SLACK_SIGNING_SECRET` に入れる。

## デプロイ（本番）

- **Railway / Fly.io / Render / Google Cloud Run** など、**常時 1 プロセス** + **公開 HTTPS** が付くホスト向け。  
- 環境変数に `.env.example` 相当をすべて設定。  
- **PORT**（ホストが渡す場合は従う。未設定時は `3000`）。  
- ヘルスチェック: `GET /health` → `ok`  
- Slack の Request URL を本番の `https://.../slack/events` に差し替え。

**注意:** Vercel 等の**純サーバレス**は長時間 LLM 待ちでタイムアウトしがち。初版は**コンテナ/常時プロセス**推奨。

## リポジトリ内の配置

| パス | 内容 |
|------|------|
| [config/channel-persona.json](config/channel-persona.json) | チャンネル ID → ペルソナ `key` + 任意 `skill`。**ワークスペース違いで ID は変わる**ので上書き。 |
| [personas/*.md](personas) | 役職ごとの短い定義。 |
| [.claude/skills/](.claude/skills) | `your-perfect-days` からのコピー。`channel-persona.json` の `skill` が参照。 |
| [src/app.ts](src/app.ts) | Bolt + `app_mention`、スレ返信。 |
| [src/llm.ts](src/llm.ts) | OpenAI / Anthropic 切替。 |

## チャンネル ID の合わせ方

1. Slack デスクトップでチャンネルを開き、**チャンネル名 → リンクをコピー** などで URL から `C0…` / `G0…`（プライベート）を得る。  
2. [config/channel-persona.json](config/channel-persona.json) に `"(チャンネルID)": { "key": "writer", "label": "writer" }` のように追記。  
3. 未知のチャンネルは JSON の `"_default"` のペルソナ（`personas/_default.md`）を使う。

## トラブルシュート

| 症状 | 確認 |
|------|------|
| Request URL 失敗 | サーバ起動、HTTPS、パスが `/slack/events`、ファイアウォール。 |
| メンションに反応しない | チャンネルに **Bot 招待**済みか。スコープに `app_mentions:read` があるか。 |
| 3 秒タイムアウト | レア。ホストのタイムアウト値を上げるか、LLM を速いモデルに。 |
| LLM エラー | `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` と `LLM_PROVIDER`、クレジット。 |

## 既存 `ai-company` 文書との関係

- リポの「正」: 引き続き [members/*/CLAUDE.md](../../members/) や [dispatch](../../dispatch/README.md)。  
- このボットは **Slack 上の対話**用。週1で `personas/*.md` を手短に同期するとブレにくい。

## セキュリティ

- トークンと API キーは**リポにコミットしない**。本番はホストのシークレット管理を使う。  
- ログにユーザー全文を**垂れ流さない**運用推奨。
