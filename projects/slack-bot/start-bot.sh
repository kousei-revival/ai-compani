#!/bin/zsh
# Slack ボットをビルドして起動（コマンドの貼り付けミス防止用）
# 使い方: ./start-bot.sh  または  zsh start-bot.sh

cd "$(dirname "$0")" || exit 1

# Node は ~/.zshrc と同じパス（未設定なら公式バイナリの一般的な場所）
export PATH="${HOME}/.local/node-v24.15.0-darwin-arm64/bin:${PATH}"

if ! command -v npm >/dev/null 2>&1; then
  echo "npm が見つかりません。~/.zshrc の PATH か Node のインストールを確認してください。"
  exit 1
fi

echo "==> npm run build"
npm run build || exit 1

echo "==> npm start（止めるときは Ctrl+C）"
exec npm start
