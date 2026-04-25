---
name: prd-to-issues
description: PRDを、着手しやすい垂直スライスの issue や作業単位へ分解する補助スキル。ユーザーが PRD を issue に分けたい、タスク化したい、依存関係つきで並べたい、と言ったときに使う。GitHubがなければ `projects/` にローカル issue 一覧を作る。
argument-hint: "[対象PRDや企画名]"
---

# prd-to-issues

PRDを読んで、実際に掴める作業単位へ落とす。

## 基本ルール

- issue は `細いが完結した垂直スライス`
- `APIだけ`、`UIだけ` の水平分割はなるべく避ける
- 依存関係を明記する
- `HITL` と `AFK` を分ける
  - `HITL`: 人の判断や確認が必要
  - `AFK`: なるべく一人で進められる

## 進め方

### Step 1: 対象PRDを特定する

- GitHub issue があるならそれを見る
- なければ `projects/` のPRDファイルを見る

### Step 2: ストーリーを束ねる

関連するユーザーストーリーごとに、1本の縦スライスへまとめる。

### Step 3: issue候補を作る

各 issue で次を決める。

- タイトル
- 種類 (`HITL` / `AFK`)
- 何を作るか
- ブロッカー
- 受け入れ条件

### Step 4: ユーザーに粒度を確認する

- 太すぎるなら分ける
- 細かすぎるならまとめる

### Step 5: issue化する

テンプレートは [template.md](template.md) を使う。

- GitHub があるなら issue を作る
- なければローカル issue 一覧として残す

## このプロジェクト向けのルール

- ローカル保存なら `projects/<テーマ>-issues.md` を基本にする
- 順番は `着手しやすさ` と `依存関係` の両方で決める
- 人の判断待ちが多いものは `HITL` と明記する
