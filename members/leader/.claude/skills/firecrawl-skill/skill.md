---
name: firecrawl-skill
description: 複雑なWebサイトからページ、一覧、構造化データを取りたいときの補助スキル。ユーザーがスクレイピング、構造化抽出、サイトマップ、検索結果収集をしたいと言ったときに使う。まず何をどの粒度で取りたいかを決める。
argument-hint: "[取得したいサイトやデータ]"
---

# firecrawl-skill

複雑なサイトを、闇雲に取らず段階的に攻める。

## 基本ルール

- 先に `1ページ / 複数ページ / 全体crawl` を決める
- 取るデータの形を先に決める
- JavaScript依存や anti-bot を前提にする
- いきなり全クロールしない

## 進め方

### Step 1: 取得目的を決める

- ページ本文
- 一覧
- 構造化データ
- 全体マップ

### Step 2: 小さく試す

- 1URL
- 一覧1ページ
- schema 1種類

### Step 3: 広げる

- map
- crawl
- extract

## 出力フォーマット

```md
## Target
- どのサイトか

## Data Needed
- 欲しい項目

## Crawl Strategy
- 単ページ / 一覧 / 全体

## Risks
- JS
- anti-bot
- 取りすぎ
```
