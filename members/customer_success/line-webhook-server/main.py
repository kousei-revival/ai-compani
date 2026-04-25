"""
LINE Webhook を受け取り、同じ JSON を Google Apps Script (GAS) の Web アプリに転送する。

- LINE には常に HTTP 200 を返す（検証用）。
- GAS の /exec は 302 で別 URL へ飛ばすことがあるため、Location へ同じ body で再 POST する。
  HTML 内の &amp; は & に直す（GAS 仕様のつまずきやすい点）。

起動例（このディレクトリで）:
  uvicorn main:app --host 0.0.0.0 --port 8000

ngrok 例:
  ngrok http 8000
→ LINE の Webhook URL には https://＜ngrok＞/line/webhook のように指定する。
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import logging
import os
from typing import Optional

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse

# プロジェクト直下の .env を読み込む（なければ無視）
load_dotenv()

# ログ（起動・エラー確認用。レベルは必要に応じて変更）
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="LINE → GAS 転送", version="0.1.0")

# 転送先 GAS（必須でないが、空だと GAS には送らない）
GAS_WEBAPP_URL: str = (os.environ.get("GAS_WEBAPP_URL") or "").strip()
# 空なら署名検証をスキップ（学習用）。本番では必ず LINE_CHANNEL_SECRET を設定すること
LINE_CHANNEL_SECRET: str = (os.environ.get("LINE_CHANNEL_SECRET") or "").strip()

# GAS への 1 回・2 回目の POST 共通
GAS_TIMEOUT = httpx.Timeout(30.0)


def _verify_line_signature(body: bytes, x_line_signature: Optional[str]) -> bool:
    """
    X-Line-Signature ヘッダ（Base64 付き HMAC-SHA256）を検証する。

    チャンネルシークレットが未設定のときは True（開発専用。本番では使わないこと）。
    """
    if not LINE_CHANNEL_SECRET:
        logger.warning("LINE_CHANNEL_SECRET 未設定: 署名検証をスキップしています（本番非推奨）")
        return True
    if not x_line_signature:
        return False
    mac = hmac.new(
        LINE_CHANNEL_SECRET.encode("utf-8"),
        body,
        hashlib.sha256,
    ).digest()
    expected = base64.b64encode(mac).decode("ascii")
    return hmac.compare_digest(expected, x_line_signature)


def _fix_gas_redirect_url(location: str) -> str:
    """
    302 の Location ヘッダに &amp; が含まれる場合、GAS 互換のため & に戻す。
    """
    return location.replace("&amp;", "&")


async def _post_json_to_gas(url: str, body: bytes) -> httpx.Response:
    """JSON 本文を GAS へ POST。リダイレクトは手動追従。"""
    async with httpx.AsyncClient(timeout=GAS_TIMEOUT, follow_redirects=False) as client:
        return await client.post(
            url,
            content=body,
            headers={"Content-Type": "application/json; charset=utf-8"},
        )


async def forward_to_gas(body: bytes) -> None:
    """
    GAS へ転送。302/303 等なら Location（& 修正）へ同じ body で再 POST。

    環境変数 GAS_WEBAPP_URL が空なら何もしない（ローカル試験用）。
    """
    if not GAS_WEBAPP_URL:
        logger.warning("GAS_WEBAPP_URL 未設定: ボディは GAS に転送していません")
        return

    r = await _post_json_to_gas(GAS_WEBAPP_URL, body)
    if r.status_code in (301, 302, 303, 307, 308):
        loc = r.headers.get("Location")
        if not loc:
            r.raise_for_status()
            return
        loc = _fix_gas_redirect_url(loc)
        r2 = await _post_json_to_gas(loc, body)
        r2.raise_for_status()
        return
    r.raise_for_status()


@app.get("/line/webhook")
async def line_webhook_get() -> JSONResponse:
    """
    ブラウザやヘルスチェック用。LINE の本番 Webhook は POST だが、
    疎通で GET したい場合に 200 を返す。
    """
    return JSONResponse(content={"ok": True, "hint": "LINE の Webhook は POST を使います"})


@app.post("/line/webhook")
async def line_webhook(request: Request) -> Response:
    """
    LINE からの Webhook 本文をバイトのまま受け取り、GAS へ同じ内容で転送する。

    - 先に本文を検証（シークレットがあれば）
    - 転送後に 200（本文は空でも可）を返す
    """
    body = await request.body()
    signature = request.headers.get("X-Line-Signature")

    if not _verify_line_signature(body, signature):
        raise HTTPException(status_code=400, detail="Invalid LINE signature")

    try:
        await forward_to_gas(body)
    except httpx.HTTPError as e:
        # ここを 5xx にすると LINE が同じイベントを再送しやすい。
        # 講義では「ログに残して 200」も選択肢（運用方針で決める）
        logger.exception("GAS 転送失敗: %s", e)
        # LINE 再送を減らすなら 200 + 内部ログ。厳格にするなら 500。
        return Response(status_code=200)

    return Response(status_code=200)
