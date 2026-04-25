---
name: claude-seo
description: テクニカルSEO、構造化データ、オンページ改善を整理する補助スキル。ユーザーが SEO、検索流入、schema、technical audit、meta 周りを見直したいと言ったときに使う。まず crawlability と indexability から見る。
argument-hint: "[見直したいページやサイト]"
---

# claude-seo

SEOは記事タイトルだけでなく、技術面から点検する。

## 基本ルール

- まず技術的に見つかる状態か確認する
- そのあと構造化データやオンページへ進む
- 重要度の高い修正から優先する

## 進め方

### Step 1: Technical audit

- crawlability
- indexability
- canonical
- robots
- sitemap

### Step 2: Page audit

- title
- meta description
- headings
- alt
- internal links

### Step 3: Schema

- 何の schema が必要か
- 既存の schema は正しいか

## 出力フォーマット

```md
## Critical
- 問題 / 対応

## Important
- 問題 / 対応

## Schema
- 追加 or 修正案
```
