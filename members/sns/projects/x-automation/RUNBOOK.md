# X 自動投稿 — 担当割（ai-company）

**秘密情報（API キー等）はこのファイルに書かない。** 置き場は `your-perfect-days/.env` および各プロジェクトの `.env` のみ。

---

## 二本の仕組み（経営者が「主戦場」を決める）

| 系統 | 場所 | 中身のイメージ |
|------|------|----------------|
| **A: Cursor / Python パイプライン** | `~/Desktop/your-perfect-days/tools/x_automation/` | `data/topics/*.json` → 文生成 → 画像 → `X API` 直投稿。`run_daily_pipeline.py` が軸。 |
| **B: iCloud / Sheets・Buffer 運用** | `~/Library/Mobile Documents/com~apple~CloudDocs/小野高誠のicloud/Cursorファイル/AI関連/Cursor/x-auto-post/` | スプレッドシート・`launchd`・`prebuffer` 等。`x-auto-post/CLAUDE.md` が仕様の正。 |

両方動かす場合は、**どちらが「投稿の正」か**を `sns/inbox/` か本書末尾に一行で固定すること（ブレると二重投稿の原因になる）。

---

## 誰が何をするか（RACI 例）

| 内容 | 経営者 | leader | sns（社員） | designer（社員） |
|------|--------|--------|-------------|------------------|
| API キー・課金・本番 ON/OFF | **決定・保持** | 記録確認 | 使い方だけメモ | — |
| トピック・文案・パイプライン実行 | — | 週次サマリに盛り込む | **主担当** | トーン相談 |
| 投稿画像の仕様・生成・差し替え | — | レビュー | 依頼書を出す | **主担当** |
| iCloud 側シート・Buffer・cron | — | 欠損が出たらエスカレーション | **運用メモ・手順更新** | 画像列の指示 |
| 失敗時の原因切り分け | 鍵まわり | **一次受付** → sns/designer に振る | ログ収集 | 画像ログ |

---

## よく使うコマンド（系統 A）

リポジトリルートは `your-perfect-days` を想定。

```bash
cd ~/Desktop/your-perfect-days
python3 tools/x_automation/run_daily_pipeline.py --dry-run
# 本番は .env と X 側クレジット確認のうえで（経営者合意）
```

詳細は **`tools/x_automation/README.md`**。

---

## よく使う参照（系統 B）

- **`x-auto-post/CLAUDE.md`**（iCloud 上のプロジェクト直下）

---

## 成果物の置き場（この sns 部屋）

- 週次の「投稿できた／できなかった」メモ → `projects/x-automation/weekly-YYYY-MM-DD.md`（自由命名で可）
- 方針変更（どの系統を正にするか等）→ 本 `RUNBOOK.md` か `sns/CLAUDE.md` に追記（**月次メンテ**で薄くする）

---

## NG 事例（追記用）

- （運用で分かったら日付付きで足す）
