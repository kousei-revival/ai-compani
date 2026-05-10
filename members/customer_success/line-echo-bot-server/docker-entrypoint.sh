#!/bin/sh
# Render / Fly / Railway は起動時に PORT を注入する。ここで必ずその値を使う。
# ダッシュボードの Start Command で --port 10000 などと固定すると、
# 「Port scan timeout … port 3000」 のように PORT と実bindがずれて失敗する。
set -e
PORT="${PORT:-8000}"
echo "docker-entrypoint: binding uvicorn to PORT=${PORT}"
exec uvicorn main:app --host 0.0.0.0 --port "${PORT}"
