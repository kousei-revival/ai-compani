# LINE Secretary Bot Server

LINE Bot の Webhook を FastAPI で受け取り、Claude API で「クライアント対応の秘書」として返信するサーバー。

## 使う環境変数

`.env.example` を参考に、ローカルでは `.env` を作る。

```env
LINE_CHANNEL_SECRET=your_channel_secret_here
LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
CLAUDE_MODEL=claude-haiku-4-5-20251001
```

- `LINE_CHANNEL_SECRET`: LINE Developers の Channel secret
- `LINE_CHANNEL_ACCESS_TOKEN`: Messaging API の Channel access token
- `ANTHROPIC_API_KEY`: Claude API のキー
- `CLAUDE_MODEL`: 使用するClaudeモデル（未設定なら `claude-haiku-4-5-20251001`）

## 起動

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
```

## Webhook URL

ngrok などで公開したURLに `/callback` を付ける。

```text
https://<公開URL>/callback
```

## クラウドデプロイ

常時起動したい場合は Docker でホスティングします。手順は **`DEPLOY.md`** を参照してください（**Render** はリポジトリ直下の **`render.yaml`**、**Railway** は **`railway.toml`** を利用）。
