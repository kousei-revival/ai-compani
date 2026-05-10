"""
LINE Bot の Webhook を FastAPI で受け取り、Claude がクライアント対応の返信を作る。

起動例:
  uvicorn main:app --host 0.0.0.0 --port 8000

LINE Developers の Webhook URL（どちらでも可）:
  https://<公開URL>/callback
  https://<公開URL>/line/webhook   （別サーバーとパスを取り違えたとき用）
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import os
import threading
import time
from pathlib import Path
from typing import Any, Optional

import httpx
from anthropic import Anthropic
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, Request, Response
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    ApiClient,
    Configuration,
    ApiException,
    MessagingApi,
    PushMessageRequest,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhook import WebhookParser
from linebot.v3.webhooks import MessageEvent, TextMessageContent

# ローカル開発用に .env を読む。本番環境では環境変数を直接設定する。
HERE = Path(__file__).resolve().parent
LINE_WEBHOOK_ENV = HERE.parent / "line-webhook-server" / ".env"
load_dotenv(HERE / ".env")
# 旧GAS転送サーバー側にだけ .env がある環境でも、同じ設定を読めるようにする。
load_dotenv(LINE_WEBHOOK_ENV)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# 外部URLにクエリやGAS識別子が含まれるため、httpxの詳細ログは抑制する。
logging.getLogger("httpx").setLevel(logging.WARNING)


def read_env_value(path: Path, key: str) -> str:
    """指定した.envから、値をログに出さずに1キーだけ読む。"""
    if not path.exists():
        return ""
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        if name.strip() == key:
            return value.strip().strip('"').strip("'")
    return ""


LINE_CHANNEL_SECRET = (os.environ.get("LINE_CHANNEL_SECRET") or "").strip()
LINE_CHANNEL_ACCESS_TOKEN = (os.environ.get("LINE_CHANNEL_ACCESS_TOKEN") or "").strip()
ANTHROPIC_API_KEY = (os.environ.get("ANTHROPIC_API_KEY") or "").strip()
GAS_LINE_LOG_WEBAPP_URL = (
    os.environ.get("GAS_LINE_LOG_WEBAPP_URL") or os.environ.get("GAS_WEBAPP_URL") or ""
).strip()
GAS_GMAIL_WEBAPP_URL = (
    os.environ.get("GAS_GMAIL_WEBAPP_URL") or os.environ.get("GMAIL_GAS_WEBAPP_URL") or ""
).strip()
LOG_COLLECTOR_LINE_CHANNEL_SECRET = (
    os.environ.get("LOG_COLLECTOR_LINE_CHANNEL_SECRET")
    or read_env_value(LINE_WEBHOOK_ENV, "LINE_CHANNEL_SECRET")
    or ""
).strip()
LINE_LOG_MAX_CHARS = int(os.environ.get("LINE_LOG_MAX_CHARS") or "8000")
EMAIL_LOG_MAX_CHARS = int(os.environ.get("EMAIL_LOG_MAX_CHARS") or "12000")

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

LINE会話履歴がユーザープロンプトに含まれている場合:
- その履歴は、このBotがGASから取得した正規の会話ログです
- 「グループで何を話していたか」と聞かれたら、履歴に書かれている範囲で短く要約してください
- 履歴が少ない場合は「履歴上では、〇〇だけ確認できます」と答えてください
- 履歴が渡されているのに「確認できません」「外部からアクセスできません」とは言わないでください

メール一覧がユーザープロンプトに含まれている場合:
- その一覧は、このBotがGASから取得した正規のGmailログです
- LINEとメールの両方を見て、対応漏れ・返信が必要そうな件・次アクションを整理してください
- メールに書かれている範囲で要約してよいですが、未確認の事実は断定しないでください
""".strip()

if not LINE_CHANNEL_SECRET:
    logger.warning("LINE_CHANNEL_SECRET が未設定です")
if not LINE_CHANNEL_ACCESS_TOKEN:
    logger.warning("LINE_CHANNEL_ACCESS_TOKEN が未設定です")
if not ANTHROPIC_API_KEY:
    logger.warning("ANTHROPIC_API_KEY が未設定です")
if not GAS_LINE_LOG_WEBAPP_URL:
    logger.warning("GAS_LINE_LOG_WEBAPP_URL が未設定です（LINEログ履歴なしで返信します）")
if not GAS_GMAIL_WEBAPP_URL:
    logger.warning("GAS_GMAIL_WEBAPP_URL が未設定です（メール履歴なしで返信します）")
if not LOG_COLLECTOR_LINE_CHANNEL_SECRET:
    logger.warning("LOG_COLLECTOR_LINE_CHANNEL_SECRET が未設定です（ログ収集Botの署名検証はできません）")

app = FastAPI(title="LINE Secretary Bot", version="0.1.0")


@app.get("/")
async def root_health():
    """クラウドのヘルスチェック用（既定で GET / を叩くサービス向け）。"""
    return {"ok": True, "service": "line-secretary-bot"}


@app.head("/")
async def root_health_head():
    """Render 等が HEAD / でプローブするとき 405 にならないようにする（ボディなし 200）。"""
    return Response(status_code=200)


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


def push_text(to: str, text: str) -> None:
    """LINE Messaging API でテキストをプッシュ送信する。"""
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.push_message(
            PushMessageRequest(
                to=to,
                messages=[TextMessage(text=text)],
            )
        )


def reply_thinking_ack(reply_token: str) -> None:
    """
    LINE に「受け付けました」相当の短い reply を送る。

    Webhook の HTTP 応答を返した後に呼ぶ想定（タイムアウト回避）。
    """
    try:
        reply_text(reply_token, "考え中...")
    except ApiException as api_err:
        logger.error("LINE Messaging API（reply・考え中）失敗:\n%s", api_err)


def get_push_target_id(event: MessageEvent) -> Optional[str]:
    """
    push_message の宛先IDを取り出す。

    グループ/ルームでは会話全体へ返すため group_id / room_id を優先する。
    1対1では user_id に送る。
    """
    source = event.source
    if not source:
        return None
    for attr_name in ("group_id", "room_id", "user_id"):
        target_id = getattr(source, attr_name, None)
        if target_id:
            return target_id
    return None


def verify_line_signature_with_secret(body: bytes, signature: str, secret: str) -> bool:
    """任意のチャネルシークレットで LINE 署名を検証する。"""
    if not signature or not secret:
        return False
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).digest()
    expected = base64.b64encode(digest).decode("ascii")
    return hmac.compare_digest(expected, signature)


def fetch_line_logs_from_gas(days: int = 3) -> str:
    """
    GAS WebApp から LINE 会話ログを取得する。

    ログ取得に失敗しても Bot 返信は止めないため、呼び出し側で空文字を扱う。
    """
    if not GAS_LINE_LOG_WEBAPP_URL:
        logger.warning("GAS_LINE_LOG_WEBAPP_URL 未設定: LINE会話履歴を取得できません")
        return ""

    try:
        with httpx.Client(timeout=10.0, follow_redirects=True) as client:
            response = client.get(GAS_LINE_LOG_WEBAPP_URL, params={"days": days})
            response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.exception("GAS LINEログ取得に失敗: %s", exc)
        return ""

    raw_line_logs = response.text.strip()
    line_logs = format_line_logs_for_prompt(raw_line_logs)
    logger.info(
        "GAS LINEログ取得成功: days=%d, raw_chars=%d, formatted_chars=%d",
        days,
        len(raw_line_logs),
        len(line_logs),
    )
    if len(line_logs) > LINE_LOG_MAX_CHARS:
        logger.info("LINEログが長いため末尾 %d 文字に切り詰めます", LINE_LOG_MAX_CHARS)
        line_logs = line_logs[-LINE_LOG_MAX_CHARS:]
    return line_logs


def format_line_logs_for_prompt(raw_line_logs: str) -> str:
    """
    GASのJSONログをClaudeが読みやすい会話履歴へ整形する。

    期待形:
    [
      {"timestamp": "...", "sender": "...", "message": "...", ...}
    ]
    """
    if not raw_line_logs:
        return ""

    try:
        data = json.loads(raw_line_logs)
    except json.JSONDecodeError:
        # GAS側がプレーンテキストを返す構成にも対応する。
        return raw_line_logs

    records: list[Any]
    if isinstance(data, list):
        records = data
    elif isinstance(data, dict):
        for key in ("logs", "messages", "events", "data", "rows"):
            value = data.get(key)
            if isinstance(value, list):
                records = value
                break
        else:
            records = [data]
    else:
        return raw_line_logs

    lines = []
    for record in records:
        if not isinstance(record, dict):
            continue
        message = str(record.get("message") or record.get("text") or "").strip()
        if not message:
            continue
        timestamp = str(record.get("timestamp") or record.get("createdAt") or "").strip()
        sender = str(record.get("sender") or record.get("displayName") or record.get("userId") or "不明").strip()
        group = str(record.get("group") or "").strip()
        prefix_parts = [part for part in (timestamp, group, sender) if part]
        prefix = " / ".join(prefix_parts)
        lines.append(f"{prefix}: {message}" if prefix else message)

    return "\n".join(lines)


def count_formatted_log_lines(line_logs: str) -> int:
    """ログ本文を出さずに、Claudeへ渡す履歴の行数だけ数える。"""
    return len([line for line in line_logs.splitlines() if line.strip()])


def fetch_gmail_logs_from_gas(days: int = 3, max_results: int = 50) -> str:
    """
    Gmail取得用GAS WebAppからメール一覧を取得する。

    取得に失敗してもLINE返信は止めないため、空文字を返す。
    """
    if not GAS_GMAIL_WEBAPP_URL:
        logger.warning("GAS_GMAIL_WEBAPP_URL 未設定: メール一覧を取得できません")
        return ""

    try:
        with httpx.Client(timeout=15.0, follow_redirects=True) as client:
            response = client.get(GAS_GMAIL_WEBAPP_URL, params={"days": days, "max": max_results})
            response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.exception("GAS Gmail取得に失敗: %s", exc)
        return ""

    raw_email_logs = response.text.strip()
    email_logs = format_email_logs_for_prompt(raw_email_logs)
    logger.info(
        "GAS Gmail取得成功: days=%d, max=%d, raw_chars=%d, formatted_chars=%d",
        days,
        max_results,
        len(raw_email_logs),
        len(email_logs),
    )
    if len(email_logs) > EMAIL_LOG_MAX_CHARS:
        logger.info("メール一覧が長いため末尾 %d 文字に切り詰めます", EMAIL_LOG_MAX_CHARS)
        email_logs = email_logs[-EMAIL_LOG_MAX_CHARS:]
    return email_logs


def format_email_logs_for_prompt(raw_email_logs: str) -> str:
    """
    GASのメールJSONをClaudeが読みやすい一覧へ整形する。

    テンプレごとにキー名が揺れても拾えるように、複数候補を見ます。
    """
    if not raw_email_logs:
        return ""

    try:
        data = json.loads(raw_email_logs)
    except json.JSONDecodeError:
        return raw_email_logs

    records: list[Any]
    if isinstance(data, list):
        records = data
    elif isinstance(data, dict):
        for key in ("emails", "messages", "threads", "data", "rows", "logs"):
            value = data.get(key)
            if isinstance(value, list):
                records = value
                break
        else:
            records = [data]
    else:
        return raw_email_logs

    lines = []
    for record in records:
        if not isinstance(record, dict):
            continue
        subject = str(record.get("subject") or record.get("件名") or "(件名なし)").strip()
        sender = str(record.get("from") or record.get("sender") or record.get("差出人") or "不明").strip()
        date = str(record.get("date") or record.get("timestamp") or record.get("日時") or "").strip()
        snippet = str(
            record.get("snippet")
            or record.get("body")
            or record.get("text")
            or record.get("本文")
            or ""
        ).strip()
        if not subject and not snippet:
            continue
        parts = [part for part in (date, sender, f"件名: {subject}") if part]
        line = " / ".join(parts)
        if snippet:
            line += f"\n本文抜粋: {snippet[:500]}"
        lines.append(line)

    return "\n---\n".join(lines)


def forward_line_webhook_to_gas(body: bytes) -> None:
    """
    LINE Webhook本文をGASへ保存用に転送する。

    GAS側の doPost がログ保存、doGet?days=3 がログ取得を担当する想定。
    転送失敗でLINE返信を止めないよう、バックグラウンドで実行する。
    """
    if not GAS_LINE_LOG_WEBAPP_URL:
        logger.warning("GAS_LINE_LOG_WEBAPP_URL 未設定: LINE Webhook をGASへ保存できません")
        return

    try:
        with httpx.Client(timeout=10.0, follow_redirects=False) as client:
            response = client.post(
                GAS_LINE_LOG_WEBAPP_URL,
                content=body,
                headers={"Content-Type": "application/json; charset=utf-8"},
            )
        # GASの /exec は302を返すことがある。最初のPOSTで doPost は動くため成功扱いにする。
        if response.status_code in (301, 302, 303, 307, 308):
            logger.info("GAS LINEログ保存: redirect %s を受理扱い", response.status_code)
            return
        response.raise_for_status()
        logger.info("GAS LINEログ保存成功: status=%s, bytes=%d", response.status_code, len(body))
    except httpx.HTTPError as exc:
        logger.exception("GAS LINEログ保存に失敗: %s", exc)


def build_claude_user_prompt(user_text: str, line_logs: str, email_logs: str) -> str:
    """LINE履歴・メール一覧・最新メッセージをClaudeへ渡すプロンプトに整形する。"""
    context_blocks = []
    if line_logs:
        context_blocks.append(
            "以下はクライアントとのLINEの会話履歴です。"
            "これはBotがGASから取得した確認済みのログです。"
            "この履歴に書かれている範囲で、グループ内の話題を要約して構いません。\n"
            + line_logs
        )
    else:
        context_blocks.append(
            "以下はクライアントとのLINEの会話履歴です。\n"
            "（LINE会話履歴は取得できませんでした。履歴を前提に断定しないでください。）"
        )

    if email_logs:
        context_blocks.append(
            "以下はクライアントとのメール一覧です。"
            "これはBotがGmail取得用GASから取得した確認済みのメール情報です。\n"
            + email_logs
        )
    else:
        context_blocks.append(
            "以下はクライアントとのメール一覧です。\n"
            "（メール一覧は取得できませんでした。メールを前提に断定しないでください。）"
        )

    context_blocks.extend(
        [
            "以下が今回ユーザーから届いた最新メッセージです。\n" + user_text,
            "回答ルール: LINE履歴とメール一覧の両方をコンテキストとして見て答えてください。"
            "情報が少ない場合は「確認できる範囲では〜」と説明してください。"
            "履歴やメールがあるのに「確認できません」とは言わないでください。",
        ]
    )
    return "\n\n".join(context_blocks)


def generate_secretary_reply(user_text: str) -> str:
    """Claude API で、クライアント対応の秘書として返信文を作る。"""
    if not ANTHROPIC_API_KEY:
        return "ただいま秘書Botの設定を確認しています。少し時間をおいてから、もう一度送ってください。"

    line_logs = fetch_line_logs_from_gas(days=3)
    logger.info("Claudeへ渡すLINE履歴: lines=%d, chars=%d", count_formatted_log_lines(line_logs), len(line_logs))
    email_logs = fetch_gmail_logs_from_gas(days=3, max_results=50)
    logger.info("Claudeへ渡すメール一覧: lines=%d, chars=%d", count_formatted_log_lines(email_logs), len(email_logs))
    prompt = build_claude_user_prompt(user_text, line_logs, email_logs)

    message = anthropic_client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=500,
        system=SECRETARY_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": prompt,
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


def generate_and_push_secretary_reply(to: str, user_text: str) -> None:
    """
    バックグラウンドで Claude 返信案を作り、LINE に push する。

    reply_token は最初の「考え中...」で使い切るため、完成後は push_message を使う。
    """
    try:
        t0 = time.monotonic()
        claude_reply = generate_secretary_reply(user_text)
        elapsed = time.monotonic() - t0
        logger.info("Claude 応答生成まで %.2f 秒", elapsed)
    except Exception:
        logger.exception("Claude reply generation failed")
        try:
            push_text(
                to,
                "すみません、返信文の作成中にエラーが起きました。担当者が確認します。",
            )
        except ApiException as fallback_err:
            logger.error("フォールバック push も LINE API で失敗:\n%s", fallback_err)
        return

    try:
        push_text(to, claude_reply)
    except ApiException as api_err:
        # アクセストークン違い・権限不足・友だち解除などはここに来る。
        logger.error("LINE Messaging API（push）失敗:\n%s", api_err)


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


def process_secretary_webhook_background(body_bytes: bytes, signature: str) -> None:
    """
    秘書Bot用 Webhook の本体処理。

    ハンドラ側では先に HTTP 200 を返しているため、署名検証や LINE API はここで行う。
    タイムアウト対策（検証・reply・Claude が応答をブロックしない）。
    """
    body = body_bytes.decode("utf-8")
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        # 既に 200 を返しているので LINE はタイムアウトしない。設定ミスはログで確認する。
        logger.warning(
            "LINE 署名が無効です（チャネルシークレット不一致など）。"
            "Render の LINE_CHANNEL_SECRET と LINE Developers を確認してください。"
        )
        return

    logger.info("Received %d LINE event(s)", len(events))
    for event in events:
        logger.info("Event type: %s", type(event).__name__)
        if isinstance(event, MessageEvent) and isinstance(event.message, TextMessageContent):
            logger.info("Accepted text message: %s", event.message.text)
            reply_thinking_ack(event.reply_token)

            target_id = get_push_target_id(event)
            if target_id:
                # Claude は時間がかかるため別スレッドで実行（複数イベントでもブロックしない）
                threading.Thread(
                    target=generate_and_push_secretary_reply,
                    args=(target_id, event.message.text),
                    daemon=True,
                ).start()
            else:
                logger.warning("push_message の宛先IDを取得できないため、Claude 処理をスキップしました")
        else:
            logger.info("Ignored non-text event")

    threading.Thread(target=forward_line_webhook_to_gas, args=(body_bytes,), daemon=True).start()


@app.post("/callback")
async def callback(request: Request, background_tasks: BackgroundTasks) -> Response:
    """本文を読み取ったらすぐ 200。検証・返信・Claude はバックグラウンド。"""
    # 一時デバッグ: Render Logs で到達確認用（不要になったら削除）
    print("=== /callback にリクエストが来たよ ===")
    body_bytes = await request.body()
    print(f"body length: {len(body_bytes)}")
    signature = request.headers.get("X-Line-Signature", "")
    print(f"signature: {signature}")
    background_tasks.add_task(process_secretary_webhook_background, body_bytes, signature)
    return Response(status_code=200)


@app.post("/line/webhook")
async def line_webhook(request: Request, background_tasks: BackgroundTasks) -> Response:
    """
    ログ収集BotのWebhook。

    1本のngrokで運用できるよう、ログ収集Botの署名ならGAS保存だけ行う。
    それ以外は後方互換としてAI秘書BotのWebhookとして処理する。
    """
    body_bytes = await request.body()
    signature = request.headers.get("X-Line-Signature", "")

    if verify_line_signature_with_secret(body_bytes, signature, LOG_COLLECTOR_LINE_CHANNEL_SECRET):
        logger.info("ログ収集BotのWebhookを受信: GAS保存へ転送します")
        background_tasks.add_task(forward_line_webhook_to_gas, body_bytes)
        return Response(status_code=200)

    background_tasks.add_task(process_secretary_webhook_background, body_bytes, signature)
    return Response(status_code=200)
