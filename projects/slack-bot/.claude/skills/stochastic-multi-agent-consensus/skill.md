---
name: stochastic-multi-agent-consensus
description: 複数の視点やサブエージェント案を集めて、合意点と相違点を整理する補助スキル。ユーザーが戦略判断、設計選択、リスク比較をしたいと言ったときに使う。1案に飛びつかず、複数案を比較してから結論を出す。
argument-hint: "[比較したい論点や判断]"
---

# stochastic-multi-agent-consensus

大きな判断を、複数視点でぶつけてからまとめる。

## 基本ルール

- 最初から正解を1つに決めない
- 3案以上あるときに特に有効
- 合意点と対立点を分けて扱う
- 最後は推奨案を1つ出す

## 進め方

### Step 1: 問いを固定する

- 何を決めたいか
- 評価軸は何か

### Step 2: 案を並べる

- 案A
- 案B
- 案C

### Step 3: 比較する

- メリット
- リスク
- いつ強いか

### Step 4: まとめる

- 共通で良い点
- 意見が割れる点
- 推奨案

## 出力フォーマット

```md
## Options
- A
- B
- C

## Consensus
- 一致点

## Disagreements
- 割れた点

## Recommendation
- 推奨案
```
