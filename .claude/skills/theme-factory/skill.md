---
name: theme-factory
description: スライド、ドキュメント、LP、UIに一貫したテーマを与える補助スキル。ユーザーが配色、テーマ、カラーパレット、雰囲気を整えたいと言ったときに使う。まず用途と印象を決めてからテーマを作るか適用する。
argument-hint: "[対象物とほしい雰囲気]"
---

# theme-factory

色と書体を、`なんとなく` ではなく役割で決める。

## 基本ルール

- 先に用途を決める
- 主役色と補助色を分ける
- 全色を同じ強さで使わない
- 書体もテーマの一部として決める

## 進め方

### Step 1: 目的を確認する

- 何に使うか
- 誰に見せるか
- どんな印象にしたいか

### Step 2: テーマを選ぶか作る

- 既存テーマを当てる
- 合わなければ新規で作る

### Step 3: トークン化する

- primary
- secondary
- accent
- background
- text
- heading font
- body font

## 出力フォーマット

```md
## Theme
- name

## Palette
- primary:
- secondary:
- accent:

## Typography
- heading:
- body:
```
