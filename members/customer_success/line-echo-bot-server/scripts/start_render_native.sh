#!/usr/bin/env sh
# Render「Native Python」用。注入された PORT だけで uvicorn を起動する。
#
# Render ダッシュボードの Environment に PORT を手で入れないこと
# （プラットフォーム注入値と食い違うと「scan は 3000 / listen は 10000」のようになる）。
#
# Start Command 例（Root Directory がこのフォルダのとき）:
#   ./scripts/start_render_native.sh
set -e
if [ -z "${PORT}" ]; then
  echo "FATAL: PORT が空です。Render の注入を確認するか、Environment の余計な PORT 定義を削除してください。" >&2
  exit 1
fi
echo "start_render_native.sh: PORT=${PORT} で uvicorn を起動します"
exec uvicorn main:app --host 0.0.0.0 --port "${PORT}"
