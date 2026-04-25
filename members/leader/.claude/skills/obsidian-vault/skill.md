---
name: obsidian-vault
description: このワークスペースを Obsidian 風のノート置き場として扱い、ノート検索、作成、リンク整理を進める補助スキル。ユーザーがノートを探したい、残したい、整理したい、関連メモをつなぎたいと言ったときに使う。`now.md`、`days/`、`projects/`、`reflections/` の構造を前提にする。
argument-hint: "[探したいノートや作りたいメモ]"
---

# obsidian-vault

このリポジトリ全体を、実質的なノート保管庫として扱う。

## この vault の基本構造

- `now.md`: 今の全体像
- `days/`: 日次ログ
- `projects/`: 継続テーマ
- `reflections/`: 振り返り
- `archive/`: 終了済み

## 基本ルール

- 単発の出来事は `days/`
- 複数日にまたがるテーマは `projects/`
- 今の方針やフォーカスは `now.md`
- 完了済みは `archive/`

## 進め方

### Step 1: 置き場所を決める

- 今日の出来事か
- 継続テーマか
- 振り返りか

### Step 2: 既存ノートを探す

- 同じ話題の `projects/`
- 今日の `days/`
- 関連する `reflections/`

### Step 3: 必要なら新規作成する

- 話題が複数日にまたがるなら `projects/` へ昇格
- `now.md` には索引だけ残す

### Step 4: リンクをつなぐ

- 日次から project へ
- 必要なら `now.md` からも参照

## このプロジェクト向けのルール

- `memory` よりファイルを正とする
- 口で言う前に、まず該当ファイルへ書く
- `days/` と `projects/` を混ぜない

## 出力フォーマット

```md
## 保存先
- `days/...` / `projects/...` / `now.md`

## 追記内容
- 何を書くか

## 関連ノート
- 参照先
```
