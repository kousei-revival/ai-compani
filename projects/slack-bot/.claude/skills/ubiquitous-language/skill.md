---
name: ubiquitous-language
description: 会話やメモからドメイン用語を抽出して、意味のズレや呼び分けを整理する補助スキル。ユーザーが用語集、DDD、言葉をそろえたい、概念を整理したいと言ったときに使う。必要なら `UBIQUITOUS_LANGUAGE.md` や `projects/` に残す。
argument-hint: "[整理したいテーマや会話]"
---

# ubiquitous-language

同じ言葉で違う意味を話さないための整理。

## 基本ルール

- まず会話やメモの中の名詞と概念を拾う
- 同義語と曖昧語を見つける
- どの言葉を正とするかを決める
- 定義は短くする

## 進め方

### Step 1: 用語候補を集める

- 名詞
- 状態
- 役割
- 関係

### Step 2: 問題を見つける

- 同じ言葉が複数の意味で使われている
- 違う言葉が同じ意味を指している
- ぼんやりしていて境界がない

### Step 3: 正式語を決める

- どの語を使うか
- 避けたい別名は何か
- 用語同士の関係は何か

### Step 4: ファイルに残す

- 汎用なら `UBIQUITOUS_LANGUAGE.md`
- プロジェクト固有なら `projects/` の関連ファイル

## 出力フォーマット

```md
## Terms
| Term | Definition | Aliases to avoid |

## Relationships
- A は B に属する

## Flagged ambiguities
- 曖昧語の指摘
```
