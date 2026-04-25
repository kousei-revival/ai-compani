---
name: office-files-playbook
description: PDF、PPTX、DOCX、XLSX の読み取り・編集・新規作成を進めるための補助スキル。ユーザーが pdf、pptx、slides、presentation、docx、word、xlsx、spreadsheet、report、form、table などの作業をしたいときに使う。まずファイル形式と作業モードを判定し、その後に検証まで含む正しい流れへ案内する。
argument-hint: "[対象ファイルややりたいこと]"
---

# office-files-playbook

Anthropic公式Skillsの型を、自分の作業で再現しやすい形にまとめた補助スキル。

## Step 1: まず分類する

最初に次の2つを判定する。

1. ファイル形式は何か
   - `pdf`
   - `pptx`
   - `docx`
   - `xlsx`
2. 作業モードは何か
   - `読む`
   - `直す`
   - `作る`

この判定を曖昧なまま進めない。

## Step 2: 形式ごとの手引きへ進む

- `pdf` または `pptx` は [pdf-pptx.md](pdf-pptx.md) を読む
- `docx` または `xlsx` は [docx-xlsx.md](docx-xlsx.md) を読む

## Step 3: 必ず検証する

どの形式でも、作業後に検証を省略しない。

- `pdf`: 抽出結果や出力PDFを見直す
- `pptx`: 画像化して見た目を確認する
- `docx`: 最小差分で直し、壊れていないか確認する
- `xlsx`: 再計算し、数式エラーがないか確認する

## 共通ルール

- いきなりコードを書かず、先にファイルの状態を観察する
- 既存ファイル編集では、構造変更と本文修正を混ぜない
- 壊れやすい処理ほど、手順を固定しながら進める
- 「作業した」ではなく「検証まで終えた」を完了とみなす
