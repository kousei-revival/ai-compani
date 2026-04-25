---
name: dependency-auditor
description: 依存パッケージの古さ、脆弱性、放棄状態をざっと監査し、優先順位つきで直す補助スキル。ユーザーが package.json、dependencies、vulnerability、古い package を見直したいと言ったときに使う。まず lockfile と package manager を確認して、重大度順に整理する。
argument-hint: "[package.json や dependency を見たいリポジトリ]"
---

# dependency-auditor

依存関係を `全部更新する` のではなく、危ない順に整理する。

## 基本ルール

- まず package manager を確認する
- `脆弱性`、`古さ`、`放棄状態` を分けて見る
- 重大度と影響範囲で優先順位を付ける
- いきなり一括更新を提案しない

## 見るもの

- `package.json`
- lockfile
- audit コマンドの結果
- deprecated 警告
- メンテ状況が怪しい package

## 進め方

### Step 1: 依存一覧を把握する

- 本番依存
- dev依存
- どの package manager か

### Step 2: リスクを分ける

- `CRITICAL / HIGH` の脆弱性
- 更新が止まっている package
- 非推奨 package
- 破壊的更新が必要な package

### Step 3: 優先順位を付ける

優先度はこの順。

1. セキュリティ影響が大きい
2. 本番影響が大きい
3. 代替が明確
4. 更新コストが低い

### Step 4: 修正方針を出す

- 今すぐ上げる
- 置き換え候補を探す
- いったん保留して監視する

## 出力フォーマット

```md
## Critical
- package: 問題 / 推奨対応

## Important
- package: 問題 / 推奨対応

## Watchlist
- package: いまは保留だが注意
```
