#!/usr/bin/env bash
# リーダーが書いた「約束付き依頼」Markdownを、指定した役職の inbox へ同時に配信する。
# Cursor は別チャットに自動挿入できないため、このスクリプト＋inbox ファイル名が「配管」に相当する。
#
# 使い方:
#   chmod +x ~/ai-company/scripts/dispatch-instruction.sh   # 初回のみ
#   ~/ai-company/scripts/dispatch-instruction.sh 依頼.md sns writer
#   ~/ai-company/scripts/dispatch-instruction.sh --id LEAD-2026-04-22-01 依頼.md researcher
#
# 環境変数 AI_COMPANY_ROOT でルートを上書き可（未設定時は ~/ai-company）。

set -euo pipefail

AI_COMPANY_ROOT="${AI_COMPANY_ROOT:-$HOME/ai-company}"
DISPATCH_SENT="${AI_COMPANY_ROOT}/dispatch/sent"
VALID_ROLES=(
  academic customer_success designer operations researcher sns video web writer
)

usage() {
  echo "使い方: $0 [--id 依頼ID] <依頼.md> <役1> [役2] ..." >&2
  echo "  有効な役: ${VALID_ROLES[*]}" >&2
  echo "  例: $0 ./my-request.md sns writer" >&2
  exit 1
}

# --- 引数解決 ---
ID=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --id) ID="${2:-}"; shift 2 ;;
    -h|--help) usage ;;
    *) break ;;
  esac
done

if [[ $# -lt 2 ]]; then
  usage
fi

FILE="$1"
shift
ROLES=("$@")

if [[ ! -f "$FILE" ]]; then
  echo "error: ファイルが見つかりません: $FILE" >&2
  exit 1
fi

# 依頼ID: --id またはファイル先頭の LEAD-... を使う。なければ日時ベース
if [[ -z "$ID" ]]; then
  if grep -qE '^[|[:space:]]*\*\*依頼ID\*\*' "$FILE" 2>/dev/null; then
    ID=$(grep -E '\*\*依頼ID\*\*' -A1 "$FILE" | tail -1 | sed -E 's/^\|[[:space:]]*//;s/\|.*$//;s/^[[:space:]]+//;s/[[:space:]]+$//' | tr -d '`')
  fi
fi
if [[ -z "$ID" || "$ID" == *（* ]]; then
  ID="DISPATCH-$(date '+%Y%m%d-%H%M%S')"
fi

TS="$(date '+%Y%m%d-%H%M%S')"

for r in "${ROLES[@]}"; do
  ok=0
  for v in "${VALID_ROLES[@]}"; do
    if [[ "$r" == "$v" ]]; then ok=1; break; fi
  done
  if [[ "$ok" -ne 1 ]]; then
    echo "error: 不明な役職名: $r （有効: ${VALID_ROLES[*]}）" >&2
    exit 1
  fi
done

SENT_DIR="${DISPATCH_SENT}/$(date '+%Y-%m-%d')"
mkdir -p "$SENT_DIR"

for r in "${ROLES[@]}"; do
  INBOX="${AI_COMPANY_ROOT}/members/${r}/inbox"
  mkdir -p "$INBOX"
  DEST_NAME="INSTRUCTION-${ID}-${r}-${TS}.md"
  DEST="${INBOX}/${DEST_NAME}"
  cp "$FILE" "$DEST"
  # 配信履歴: 同じ内容へのシンボリックリンク（どこに送ったか一覧しやすい）
  mkdir -p "${SENT_DIR}/by-role/${r}"
  ln -snf "$DEST" "${SENT_DIR}/by-role/${r}/${DEST_NAME}"
  echo "ok: $DEST"
done

echo "---"
echo "配信先メモ: 各役は cd ~/ai-company/members/<役> から開き、inbox の INSTRUCTION- を最優先で読む。"
echo "返却先: ~/ai-company/members/leader/inbox/replies/ （テンプレ参照）"
