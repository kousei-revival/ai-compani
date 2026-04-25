---
name: web-artifacts-builder
description: 複数要素からなるWeb artifactや小さなUIツールを構築するときの補助スキル。ユーザーがダッシュボード、計算機、インタラクティブなHTML、artifact を作りたいと言ったときに使う。単なる1画面でなく、状態や複数コンポーネントがある場合に使う。
argument-hint: "[作りたい artifact やUIツール]"
---

# web-artifacts-builder

少し複雑な artifact を、構成を決めてから作る。

## 基本ルール

- まず何を触れる artifact かを決める
- 状態、入力、出力を先に整理する
- 単なる飾りより、使って意味があることを優先する
- 見た目も `frontend-design` と合わせて考える

## 進め方

### Step 1: artifact の役割を定義する

- 何を操作できるか
- 何を見せるか
- 何を計算するか

### Step 2: 構成を決める

- 入力
- 表示
- 状態
- 補助UI

### Step 3: 実装方針を決める

- 単一HTMLで足りるか
- 複数コンポーネントが必要か
- テストや確認が必要か

## 出力フォーマット

```md
## Artifact Goal
- 目的

## Components
- component1
- component2

## State
- state1

## Output
- 何が見えるか
```
