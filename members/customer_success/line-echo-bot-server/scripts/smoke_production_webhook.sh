#!/usr/bin/env bash
# Render 本番 URL が秘書Bot（FastAPI）として応答するか簡易チェックする。
# 使い方:
#   BASE_URL=https://あなたのサービス.onrender.com ./scripts/smoke_production_webhook.sh
#
# 無料プランはスリープからの初回が数十秒〜90秒超かかることがあります。
# タイムアウトしたら Render ダッシュボードで Manual Deploy またはブラウザで URL を開いて起こしてから再実行してください。
set -euo pipefail

BASE_URL="${BASE_URL:-}"
if [[ -z "${BASE_URL}" ]]; then
  echo "環境変数 BASE_URL を指定してください。例:" >&2
  echo "  BASE_URL=https://your-app.onrender.com ./scripts/smoke_production_webhook.sh" >&2
  exit 1
fi
BASE_URL="${BASE_URL%/}"

CURL_MAX="${CURL_MAX:-120}"

echo "== Smoke: ${BASE_URL} (curl -m ${CURL_MAX}) =="

echo ""
echo "--- GET / (ヘルス・サービス識別) ---"
code="$(curl -sS -m "${CURL_MAX}" -o /tmp/smoke_root.json -w "%{http_code}" "${BASE_URL}/")"
echo "HTTP ${code}"
head -c 400 /tmp/smoke_root.json
echo ""

if [[ "${code}" != "200" ]]; then
  echo "NG: GET / が 200 ではありません。Render が Sleep / Root Directory 違い / デプロイ失敗を確認してください。" >&2
  exit 1
fi

echo ""
echo "--- GET /callback (ルート存在確認・LINE 本番は POST) ---"
code="$(curl -sS -m "${CURL_MAX}" -o /tmp/smoke_cb.json -w "%{http_code}" "${BASE_URL}/callback")"
echo "HTTP ${code}"
head -c 400 /tmp/smoke_cb.json
echo ""

if [[ "${code}" != "200" ]]; then
  echo "NG: GET /callback が 200 ではありません。404 のときは Root Directory が line-echo-bot-server か確認。" >&2
  exit 1
fi

echo ""
echo "--- POST /callback (本文読取後すぐ 200 の確認・署名なしでもハンドラは 200 を返す) ---"
code="$(curl -sS -m "${CURL_MAX}" -o /tmp/smoke_post.json -w "%{http_code}" \
  -X POST "${BASE_URL}/callback" \
  -H "Content-Type: application/json" \
  -d '{}')"
echo "HTTP ${code}"
head -c 200 /tmp/smoke_post.json
echo ""

if [[ "${code}" != "200" ]]; then
  echo "NG: POST /callback が 200 ではありません。" >&2
  exit 1
fi

echo ""
echo "OK: 本番 URL は秘書Botの応答パターンと一致しています。"
echo "次: LINE Developers で Webhook を ${BASE_URL}/callback に設定し「検証」を実行してください。"
