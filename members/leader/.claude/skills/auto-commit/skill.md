---
name: auto-commit
description: ステージ済み差分を読んで、意味のあるコミットメッセージ案を作る補助スキル。ユーザーが commit message、コミット文、Conventional Commit、何て書けばいいか迷うと言ったときに使う。変更の目的を短く言語化する。
argument-hint: "[差分の意図やコミット対象]"
---

# auto-commit

`fix stuff` で終わらせず、変更の意味がわかるコミット文を作る。

## 基本ルール

- `何を変えたか` だけでなく `なぜ変えたか` を入れる
- 1コミット1意図を前提に考える
- Conventional Commit が合うなら寄せる
- 秘密情報っぽいファイルは混ぜない

## 進め方

### Step 1: 差分の種類を判定する

- `feat`
- `fix`
- `refactor`
- `docs`
- `test`
- `chore`

### Step 2: スコープを言葉にする

- どの機能か
- 何のための変更か

### Step 3: 本文を作る

- なぜ必要だったか
- 何が改善されるか

## 出力フォーマット

```md
type(scope): short summary

Reason the change was needed.
```

## コツ

- 自分が1週間後に見て意味がわかる文にする
- 曖昧な単語より具体的な機能名を使う
