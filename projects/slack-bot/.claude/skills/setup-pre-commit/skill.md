---
name: setup-pre-commit
description: リポジトリに pre-commit の安全装置を入れる補助スキル。ユーザーが Husky、lint-staged、Prettier、型チェック、テストをコミット前に回したいと言ったときに使う。まず package manager と既存 scripts を見て、無理のない最小構成で入れる。
argument-hint: "[対象リポジトリや追加したいチェック]"
---

# setup-pre-commit

コミット前に最低限の整形と検証が走る状態を作る。

## 基本ルール

- 既存の `package.json` と lockfile を先に確認する
- repo にない script は勝手に前提にしない
- まずは `format + 既存typecheck/test` の最小構成にする
- 既存設定を壊さず、足りないものだけ追加する

## 進め方

### Step 1: package manager を判定する

次を順に見る。

- `pnpm-lock.yaml`
- `package-lock.json`
- `yarn.lock`
- `bun.lockb`

### Step 2: 既存 script を確認する

- `typecheck`
- `test`
- `lint`
- `format`

なければ無理に追加せず、使えるものだけ hook に入れる。

### Step 3: 必要なものを追加する

- `husky`
- `lint-staged`
- `prettier`

### Step 4: hook を作る

基本はこの順。

1. `lint-staged`
2. `typecheck` があれば実行
3. `test` があれば実行

### Step 5: 検証する

- `.husky/pre-commit` があるか
- `.lintstagedrc` があるか
- `prepare` script が入っているか
- 実行して破綻しないか

## このプロジェクト向けのルール

- ない script を勝手に作るより、先に相談する
- 新規repoでは `最初に入れる安全装置` として使う

## 出力フォーマット

```md
## 追加したもの
- 依存
- ファイル

## Hook構成
- 1. lint-staged
- 2. typecheck
- 3. test

## 注意点
- まだ無い script
- 後で足したいもの
```
