---
name: api-documentation-generator
description: 既存APIやルート定義から、使えるAPIドキュメントやOpenAPIのたたき台を作る補助スキル。ユーザーが API docs、OpenAPI、Swagger、エンドポイント一覧、認証やエラー例を整えたいと言ったときに使う。まずコードから事実を回収してから文書化する。
argument-hint: "[対象APIやサービス]"
---

# api-documentation-generator

APIを実装だけで終わらせず、`使う人が読める文書` にする。

## 基本ルール

- 先にコードやルート定義を確認する
- 想像で埋めず、事実ベースで書く
- 認証、入力、成功例、失敗例を最低限入れる
- 変更が多い箇所ほど、薄くても先に文書化する

## 進め方

### Step 1: エンドポイントを洗う

- パス
- メソッド
- 概要
- 認証有無

### Step 2: 入出力を整理する

- リクエスト
- レスポンス
- エラー

### Step 3: 使う人向けに整える

- cURL 例
- 必須パラメータ
- エラーコード
- 注意点

### Step 4: 保存する

- `docs/` に API docs
- 必要なら OpenAPI 形式

## 出力フォーマット

~~~md
## Endpoint
`METHOD /path`

### Description
- 何をするか

### Auth
- 必要な認証

### Request
- parameter

### Success Response
```json
{}
```

### Error Response
```json
{}
```
~~~
