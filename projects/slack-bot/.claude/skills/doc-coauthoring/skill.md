---
name: doc-coauthoring
description: ユーザーと一緒にドキュメント、提案書、仕様書、意思決定文書を書く補助スキル。ユーザーが docs、proposal、spec、RFC、提案書を一緒に作りたいと言ったときに使う。情報収集 -> 構成化 -> 共同推敲の順に進める。
argument-hint: "[一緒に書きたい文書のテーマ]"
---

# doc-coauthoring

長い文書を、対話しながら一緒に作る。

## 3段階

1. Context Gathering
2. Refinement & Structure
3. Reader Testing

## Step 1: Context Gathering

- 文書の種類
- 読者
- 期待する影響
- テンプレの有無
- 背景情報

## Step 2: Refinement & Structure

- セクションを決める
- 各セクションの要点を出す
- 書く
- 直す

## Step 3: Reader Testing

- 初見の読者がわかるか
- 前提知識を置きすぎていないか
- 足りない説明はないか

## このプロジェクト向けのルール

- 文書化前に、関連する `projects/` と `now.md` を見る
- 完成版だけでなく、途中の論点整理もファイルに残す

## 出力フォーマット

```md
## Doc Type
- 何の文書か

## Audience
- 誰向けか

## Structure
- セクション1
- セクション2

## Next Draft Task
- 次に書くもの
```
