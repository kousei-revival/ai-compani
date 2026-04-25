---
name: git-guardrails-claude-code
description: Claude Code で危険な git 操作をブロックするフックを入れる補助スキル。ユーザーが git safety、guardrails、dangerous git commands を防ぎたい、push や reset --hard を止めたいと言ったときに使う。まず適用範囲を確認してから hook を設定する。
argument-hint: "[project か global か、追加したい禁止コマンド]"
---

# git-guardrails-claude-code

危険な git 操作を、Claude Code 実行前に止める。

## 基本ルール

- 先に `project` か `global` かを決める
- 既存の `.claude/settings.json` は上書きしない
- ブロック対象は最初は厳しめでよい
- あとから例外を足せる形で置く

## 最初に決めること

- この project のみで使うか
- すべての project で使うか
- 何を止めたいか

## 標準で止める候補

- `git push`
- `git reset --hard`
- `git clean -f`
- `git branch -D`
- `git checkout .`
- `git restore .`

## 進め方

### Step 1: hook script を置く

- project: `.claude/hooks/`
- global: `~/.claude/hooks/`

### Step 2: settings に hook を足す

- `PreToolUse`
- matcher は `Bash`
- 既存 hooks があれば merge する

### Step 3: 必要なら禁止パターンを調整する

- 追加で止めたいもの
- 逆に許可したいもの

### Step 4: テストする

疑似入力で block されることを確認する。

## このプロジェクト向けのルール

- まずは `project` 適用を優先
- 本当に必要になってから `global` へ広げる

## 出力フォーマット

```md
## Scope
- project / global

## Blocked Commands
- command1
- command2

## Updated Files
- settings
- hook script

## Verification
- blocked test result
```
