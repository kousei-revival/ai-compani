# LINE 秘書Bot — クラウド（Render / Fly.io / Railway 等）向け
FROM python:3.12-slim-bookworm

WORKDIR /app

# ログをすぐに見えるようにする（コンテナのベストプラクティス）
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# Render / Fly などは $PORT を注入する（Fly は通常 8080）。ローカル Docker では 8000。
EXPOSE 8000
CMD ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
