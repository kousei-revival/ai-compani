#!/bin/zsh
# ローカルで「1項目ずつ」検証する（Slack 管理画面は手動チェックリスト参照）
# 使い方: ./verify.sh

set -e
cd "$(dirname "$0")"
export PATH="${HOME}/.local/node-v24.15.0-darwin-arm64/bin:${PATH}"

PASS="OK"
FAIL="NG"

step() {
  local n="$1"
  local name="$2"
  printf "[%s] %2d. %s\n" "---" "$n" "$name"
}

ok() { printf "    → %s %s\n" "$PASS" "$1"; }
ng() { printf "    → %s %s\n" "$FAIL" "$1"; }

echo "========== slack-bot ローカル検証（順番に実行）=========="
echo ""

step 1 "Node / npm が使える"
if command -v node >/dev/null 2>&1 && command -v npm >/dev/null 2>&1; then
  ok "node $(node -v) / npm $(npm -v)"
else
  ng "PATH に node/npm がありません。~/.zshrc か Node インストールを確認"
  exit 1
fi

step 2 "プロジェクト直下にいる"
ok "$(pwd)"

step 3 ".env が存在する"
if [[ -f .env ]]; then
  ok ".env あり"
else
  ng ".env がありません（.env.example をコピー）"
  exit 1
fi

step 4 "必須環境変数（空でない行があるか・値は表示しません）"
# Socket 運用想定: 3つ + LLM
missing=()
for key in SLACK_SIGNING_SECRET SLACK_BOT_TOKEN SLACK_APP_TOKEN; do
  if ! grep -q "^[[:space:]]*${key}=[^[:space:]]" .env 2>/dev/null; then
    missing+=("$key")
  fi
done
if [[ ${#missing[@]} -eq 0 ]]; then
  ok "SLACK_SIGNING_SECRET / SLACK_BOT_TOKEN / SLACK_APP_TOKEN はいずれも非空っぽい"
else
  ng "未設定っぽい: ${missing[*]}"
fi

step 5 "LLM 用（OPENAI または ANTHROPIC）"
if grep -q "^[[:space:]]*LLM_PROVIDER=anthropic" .env 2>/dev/null; then
  if grep -q "^[[:space:]]*ANTHROPIC_API_KEY=[^[:space:]]" .env 2>/dev/null; then
    ok "LLM_PROVIDER=anthropic と ANTHROPIC_API_KEY あり"
  else
    ng "LLM_PROVIDER=anthropic だが ANTHROPIC_API_KEY が空っぽい"
  fi
elif grep -q "^[[:space:]]*LLM_PROVIDER=openai" .env 2>/dev/null || ! grep -q "^[[:space:]]*LLM_PROVIDER=" .env 2>/dev/null; then
  if grep -q "^[[:space:]]*OPENAI_API_KEY=[^[:space:]]" .env 2>/dev/null; then
    ok "OPENAI_API_KEY あり（openai 系）"
  else
    ng "OPENAI 利用想定だが OPENAI_API_KEY が空っぽい"
  fi
fi

step 6 "TypeScript ビルド"
if npm run build >/tmp/slack-bot-verify-build.log 2>&1; then
  ok "npm run build 成功"
else
  ng "ビルド失敗。ログ: /tmp/slack-bot-verify-build.log"
  cat /tmp/slack-bot-verify-build.log
  exit 1
fi

step 7 "dist/app.js にデバッグ用ミドルウェアが入っている"
if grep -q "registerDebugEventLogger" dist/app.js 2>/dev/null; then
  ok "最新ビルドにイベントログ用コードあり"
else
  ng "古い dist の可能性。npm run build し直し"
fi

step 8 "起動スクリプト"
if [[ -x ./start-bot.sh ]]; then
  ok "start-bot.sh 実行可能"
else
  ng "chmod +x start-bot.sh してください"
fi

echo ""
echo "========== ここまでがローカル自動検証 =========="
echo "Slack 側は起きたあと、手動で MANUAL_CHECKLIST.txt を上から順に。"
echo ""
