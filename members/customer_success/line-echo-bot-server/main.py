"""
LINE Bot の Webhook を FastAPI で受け取り、Claude がクライアント対応の返信を作る。

起動例:
  uvicorn main:app --host 0.0.0.0 --port 8000

LINE Developers の Webhook URL（どちらでも可）:
  https://<公開URL>/callback
  https://<公開URL>/line/webhook   （別サーバーとパスを取り違えたとき用）
"""

from __future__ import annotations

import logging
import os
import time

from anthropic import Anthropic
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Response
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    ApiClient,
    Configuration,
    ApiException,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhook import WebhookParser
from linebot.v3.webhooks import MessageEvent, TextMessageContent

# ローカル開発用に .env を読む。本番環境では環境変数を直接設定する。
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

LINE_CHANNEL_SECRET = (os.environ.get("LINE_CHANNEL_SECRET") or "").strip()
LINE_CHANNEL_ACCESS_TOKEN = (os.environ.get("LINE_CHANNEL_ACCESS_TOKEN") or "").strip()
ANTHROPIC_API_KEY = (os.environ.get("ANTHROPIC_API_KEY") or "").strip()

DEFAULT_CLAUDE_MODEL = "claude-haiku-4-5-20251001"
MODEL_ALIASES = {
    # 人間向けの略称や存在しない名前が .env に入っていても、APIで使える名前へ寄せる。
    "opus-4-6": "claude-opus-4-6",
    "claude-3-5-haiku-latest": DEFAULT_CLAUDE_MODEL,
    "claude-3-haiku-20240307": DEFAULT_CLAUDE_MODEL,
    "haiku": DEFAULT_CLAUDE_MODEL,
}
CLAUDE_MODEL = MODEL_ALIASES.get(
    (os.environ.get("CLAUDE_MODEL") or DEFAULT_CLAUDE_MODEL).strip(),
    (os.environ.get("CLAUDE_MODEL") or DEFAULT_CLAUDE_MODEL).strip(),
)

SECRETARY_SYSTEM_PROMPT = """
あなたはクライアント対応の秘書です。
相手の不安を増やさず、丁寧で短く、次に取る行動が分かる返信を作ってください。

守ること:
- 日本語で返す
- 1〜4文で簡潔に返す
- まだ実行していない作業を「完了しました」と言わない
- 依頼が曖昧なときは、最初の一歩と確認したい情報を短く伝える
- 予約・契約・返金・診断などの確定判断はせず、担当者確認につなぐ
- 医療・法律・お金など専門判断が必要な内容は断定せず、担当者確認を促す
- 個人情報を深掘りしすぎない
- 相手を責める表現を使わない
""".strip()

if not LINE_CHANNEL_SECRET:
    logger.warning("LINE_CHANNEL_SECRET が未設定です")
if not LINE_CHANNEL_ACCESS_TOKEN:
    logger.warning("LINE_CHANNEL_ACCESS_TOKEN が未設定です")
if not ANTHROPIC_API_KEY:
    logger.warning("ANTHROPIC_API_KEY が未設定です")

app = FastAPI(title="LINE Secretary Bot", version="0.1.0")


@app.get("/")
async def root_health():
    """クラウドのヘルスチェック用（既定で GET / を叩くサービス向け）。"""
    return {"ok": True, "service": "line-secretary-bot"}


# WebhookParser は X-Line-Signature を検証しながらイベントをパースする。
parser = WebhookParser(LINE_CHANNEL_SECRET)
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)


def reply_text(reply_token: str, text: str) -> None:
    """LINE Messaging API でテキストを返信する。"""
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text=text)],
            )
        )


def generate_secretary_reply(user_text: str) -> str:
    """Claude API で、クライアント対応の秘書として返信文を作る。"""
    if not ANTHROPIC_API_KEY:
        return "ただいま秘書Botの設定を確認しています。少し時間をおいてから、もう一度送ってください。"

    message = anthropic_client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=500,
        system=SECRETARY_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": user_text,
            }
        ],
    )

    text_parts = []
    for block in message.content:
        if getattr(block, "type", None) == "text":
            text_parts.append(block.text)

    reply = "\n".join(text_parts).strip()
    if not reply:
        return "内容を確認しました。担当者に確認して、必要な次の対応をご案内します。"
    return reply[:4900]


@app.get("/callback")
async def callback_healthcheck():
    """ブラウザ確認用。LINE の Webhook 本番リクエストは POST を使う。"""
    return {
        "ok": True,
        "hint": "LINE Webhook は POST /callback または POST /line/webhook に送ってください",
    }


@app.get("/line/webhook")
async def line_webhook_get_health():
    """ブラウザ・疎通用。LINE 本番は POST /line/webhook を使う。"""
    return {
        "ok": True,
        "hint": "LINE Webhook は POST /line/webhook（または POST /callback）に送ってください",
    }


@app.post("/callback")
@app.post("/line/webhook")
async def callback(request: Request) -> Response:
    """LINE の Webhook を受け取り、Claude が作った返信を返す。"""
    body = (await request.body()).decode("utf-8")
    signature = request.headers.get("X-Line-Signature", "")

    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError as exc:
        # チャネルシークレットが違う、または署名ヘッダがない場合はここに来る。
        raise HTTPException(status_code=400, detail="Invalid LINE signature") from exc

    logger.info("Received %d LINE event(s)", len(events))
    for event in events:
        logger.info("Event type: %s", type(event).__name__)
        if isinstance(event, MessageEvent) and isinstance(event.message, TextMessageContent):
            logger.info("Generating secretary reply for text message: %s", event.message.text)
            try:
                # reply_token の有効時間はおおよそ数十秒。Claude が遅いと返信 API が失敗しやすい。
                t0 = time.monotonic()
                claude_reply = generate_secretary_reply(event.message.text)
                elapsed = time.monotonic() - t0
                logger.info("Claude 応答生成まで %.2f 秒", elapsed)
                if elapsed > 25.0:
                    logger.warning(
                        "生成に %.2f 秒かかりました。reply_token 期限切れで LINE 返信が失敗する場合があります。",
                        elapsed,
                    )
                reply_text(event.reply_token, claude_reply)
            except ApiException as api_err:
                # アクセストークン違い・権限不足・reply_token 期限切れなどはここに来る。
                # ApiException は status / body を含むのでそのままログに出す。
                logger.error("LINE Messaging API（reply）失敗:\n%s", api_err)
            except Exception:
                logger.exception("Claude reply generation failed")
                try:
                    reply_text(
                        event.reply_token,
                        "すみません、返信文の作成中にエラーが起きました。担当者が確認します。",
                    )
                except ApiException as fallback_err:
                    logger.error("フォールバック返信も LINE API で失敗:\n%s", fallback_err)
        else:
            logger.info("Ignored non-text event")

    return Response(status_code=200)
