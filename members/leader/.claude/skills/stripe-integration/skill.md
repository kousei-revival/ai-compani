---
name: stripe-integration
description: Stripe の決済、Webhook、サブスク設計を安全に進める補助スキル。ユーザーが Stripe、決済、subscription、webhook、課金導線を作りたいと言ったときに使う。まず決済フローと失敗時の扱いを固める。
argument-hint: "[作りたい決済フローやStripe機能]"
---

# stripe-integration

決済は `通すこと` だけでなく `壊れたとき` まで設計する。

## 基本ルール

- まず料金体系と購入導線を決める
- Webhook は後回しにしない
- 冪等性と失敗時の再実行を考える
- 本番前にテストモードで流れを通す

## 進め方

### Step 1: 課金モデルを決める

- 単発
- サブスク
- 分割

### Step 2: イベントを洗う

- 決済成功
- 失敗
- キャンセル
- 更新

### Step 3: Webhook と状態更新を決める

- どのイベントで何を更新するか
- raw body や署名検証をどう扱うか

## 出力フォーマット

```md
## Payment Flow
- 入口
- 成功時
- 失敗時

## Webhooks
- event
- action

## Risks
- 想定リスク
```
