#!/usr/bin/env bash
# Render 無料枠がスリープ中だと、LINE の Webhook「検証」がタイムアウトしやすい。
# 先に GET / をリトライしてコンテナを起こしてから、任意で smoke_production_webhook.sh を実行する。
#
# 使い方:
#   BASE_URL=https://ai-compani.onrender.com ./scripts/wake_render_for_line_webhook.sh
#
# オプション環境変数:
#   POLL_INTERVAL_SEC  既定のリトライ間隔（秒）。既定 5
#   POLL_MAX_ATTEMPTS  既定の試行回数。既定 30（約 2.5 分）
#   CURL_PER_TRY_SEC   各 curl の -m。既定 60
#   RUN_SMOKE          1 ならウェイク成功後に smoke_production_webhook.sh を実行（既定 1）
#
set -euo pipefail

BASE_URL="${BASE_URL:-}"
if [[ -z "${BASE_URL}" ]]; then
  echo "BASE_URL を指定してください。例: BASE_URL=https://your-app.onrender.com $0" >&2
  exit 1
fi
BASE_URL="${BASE_URL%/}"

POLL_INTERVAL_SEC="${POLL_INTERVAL_SEC:-5}"
POLL_MAX_ATTEMPTS="${POLL_MAX_ATTEMPTS:-30}"
CURL_PER_TRY_SEC="${CURL_PER_TRY_SEC:-60}"
RUN_SMOKE="${RUN_SMOKE:-1}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# /tmp 依存や空応答時の有無で head がコケないよう、必ず mktemp で本文を受ける。
WAKE_BODY="$(mktemp -t wake_poll.XXXXXX)"
cleanup_wake_body() { rm -f "${WAKE_BODY}"; }
trap cleanup_wake_body EXIT

echo "== Render ウェイク: ${BASE_URL}/ （最大 ${POLL_MAX_ATTEMPTS} 回 × 間隔 ${POLL_INTERVAL_SEC}s、curl -m ${CURL_PER_TRY_SEC}）=="
echo ""
echo "HTTP 000 = curl が応答を受け取れませんでした（DNS・接続・URL・Render停止などを疑ってください）。"
echo ""

ok=0
for ((i = 1; i <= POLL_MAX_ATTEMPTS; i++)); do
  echo "--- 試行 ${i}/${POLL_MAX_ATTEMPTS} ---"
  # curl が完了するまで何も出ないとフリーズに見えるので、送信中であることを明示する。
  echo "GET ${BASE_URL}/ を試行中（この1回は最大 ${CURL_PER_TRY_SEC} 秒かかります）…"
  code="000"
  if code="$(curl -sS -m "${CURL_PER_TRY_SEC}" -o "${WAKE_BODY}" -w "%{http_code}" "${BASE_URL}/" 2>/dev/null)"; then
    :
  else
    code="000"
  fi
  echo "GET / → HTTP ${code}"
  if [[ "${code}" == "200" ]]; then
    if [[ -s "${WAKE_BODY}" ]]; then
      head -c 300 "${WAKE_BODY}"
    else
      echo "（本文は空）"
    fi
    echo ""
    ok=1
    break
  fi
  if ((i < POLL_MAX_ATTEMPTS)); then
    echo "まだ 200 ではないので ${POLL_INTERVAL_SEC} 秒待って再試行します。"
    sleep "${POLL_INTERVAL_SEC}"
  fi
done

echo ""
if [[ "${ok}" != "1" ]]; then
  echo "NG: GET / が ${POLL_MAX_ATTEMPTS} 回以内に 200 になりませんでした。" >&2
  echo "    次を確認: (1) Render の **公開URL** が ${BASE_URL} と一致するか" >&2
  echo "            (2) サービスが **Live** でビルド成功しているか" >&2
  echo "            (3) ブラウザで同じ URL を開けるか" >&2
  echo "    **診断: エラーをそのまま表示（1回）**" >&2
  curl -m "${CURL_PER_TRY_SEC}" -w "\nhttp_code:%{http_code}\n" "${BASE_URL}/" -o /dev/null >&2 || true
  exit 1
fi

echo "OK: サービスは応答しています（冷えた状態からの起動に時間がかかった可能性あり）。"
echo ""

if [[ "${RUN_SMOKE}" == "1" ]]; then
  CURL_MAX="${CURL_MAX:-120}" BASE_URL="${BASE_URL}" "${SCRIPT_DIR}/smoke_production_webhook.sh"
fi

echo ""
echo "======== 次の手順（プラン: Webhook 本番タイムアウト切り分け）========"
echo "1) LINE Developers → Messaging API 設定 → すぐ「検証」を押す（このウィンドウは開いたまま）。"
echo "2) まだタイムアウトなら Render → Logs で同時刻付近に POST /callback があるか確認。"
echo "   - ログに POST が無い: スリープ・URL誤り・到達前タイムアウトを疑う → 再度このスクリプト or ブラウザで / を開いてから検証。"
echo "   - POST がある: アプリは受信済み。続きのログで署名エラーや例外を確認。"
echo "3) Render ダッシュボード確認: Root Directory = members/customer_success/line-echo-bot-server、Docker、環境変数。"
echo "4) 再発が多いとき: UptimeRobot 等で GET ${BASE_URL}/ を数分おきに監視するか、有料プランでスリープ回避。"
echo "================================================================"
