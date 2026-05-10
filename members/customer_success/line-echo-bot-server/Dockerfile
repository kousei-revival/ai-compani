# LINE 秘書Bot — クラウド（Render / Fly.io / Railway 等）向け
FROM python:3.12-slim-bookworm

WORKDIR /app

# ログをすぐに見えるようにする（コンテナのベストプラクティス）
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Render / Fly などは $PORT を注入する。ENTRYPOINT が必ずそれを使う（ローカルは 8000 既定）。
EXPOSE 8000
ENTRYPOINT ["/app/docker-entrypoint.sh"]
