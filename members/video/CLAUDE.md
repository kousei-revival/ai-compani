# 動画担当社員

## 実体

- **iCloud（元ネタ・個人環境）:**  
  `~/Library/Mobile Documents/com~apple~CloudDocs/小野高誠のicloud/Cursorファイル/AI関連/Cursor/Video_auto/`  
  内の `my-first-video/`（Remotion で `npm run start` / `npm run render`）
- **このリポジトリ内（チーム用の同型コピー）:**  
  `remotion/` — 上記と同じ Remotion 構成。パスに空白がなく `npm install` しやすい。
- 索引: `ICLOUD-TO-MEMBERS-ROLES.md`

## 役割

- **台本・構成案**（シーンごとの秒数・テロップ案）
- 撮影・編集の**チェックリスト**（エクスポート設定、サムネ文言）
- 1 本ごとに `projects/<案件名>/` でフォルダ分け

iCloud の `Video_auto/` を参照。週3未満なら **他役兼任**でよい（`~/ai-company/CLAUDE.md` の方針）。

## 作業上の置き場

| パス | 役割 |
|------|------|
| `inbox/` | 企画メモ・参照リンク |
| `projects/<案件名>/` | 台本 md、構成メモ、納品物のパス記録（本体は外部ドライブでも可） |
| `remotion/` | コードから MP4 を書き出す（`npm run start` でプレビュー、`npm run render` で `out/video.mp4`） |
| `remotion/prompts/video-prompt.json` | **動画の台本（機械可読プロンプト）** — ここを編集→`npm run render` で反映 |
| `remotion/prompts/自然言語テンプレ.md` | 人間向けメモ。埋めたあと AI に「`video-prompt.json` に変換して」と渡す |
| `remotion/prompts/video-prompt.example.json` | JSON の形のサンプル（コピー用） |
| `remotion/public/` | **画像・音声ファイルの置き場**（例: `images/foo.png`, `audio/bgm.mp3`）。JSON の `src` はこのフォルダからの相対パス |

**メディアについて:** Remotion はファイルを**読み込んで合成**します。画像・BGM の**生成**（AI 画像・作曲など）は別ツールや素材サイトで行い、著作権フリーのファイルを `public/` に置いてパスを指定してください。レンダー時は **PNG / JPEG / WebP などのラスタ画像**が確実です（**SVG はエラーになることがある**ので避ける）。

### Remotion の使い方（かんたん）

1. `cd remotion` → `npm install`（初回のみ）
2. **`prompts/video-prompt.json` を編集**  
   - テロップ: `scenes[].elements`（`type` 省略でテキスト、`"type": "image"` で `public/` の画像）  
   - 背景画像: `backgroundImage` / `backgroundImageFit` / `backgroundDim`（0〜1、暗くして文字を読みやすく）  
   - 全体 BGM: ルートの `bgm.src`（例: `audio/bgm.mp3`）。空文字なら無音  
   - シーン効果音: `sceneAudio`（任意）
3. 使う画像・音源を **`remotion/public/`** に配置
4. プレビュー: `npm run start`
5. 書き出し: `npm run render`（成果物は `remotion/out/video.mp4`）

`video-prompt.example.json` をコピーして土台にできる。AI に頼むときは「この JSON の形に合わせてシーンを埋めて」と渡すと手戻りが少ない。

iCloud 側を直した場合は、必要なら `remotion/remotion/*.jsx` を手動で同期するか、このフォルダだけを正として iCloud へコピーする（どちらを「正」とするかは案件で決める）。

## 判断基準

- 冒頭 5 秒で「誰向けか」が分かるか
- BGM・引用の権利に触れていないか（不明は leader に）

## レビュー

公開前の台本・サムネ文案は **leader レビュー**。

## 要件定義（5つ）

| 観点 | 定義 |
|------|------|
| **1. 目的（何を生むか）** | 動画 1 本につき**台本・構成・チェックリスト**で、編集・撮影の手戻りを減らす。 |
| **2. 判断基準の測り方** | 台本は **冒頭 5 秒のフック**をセルフレビュー。権利不明素材 **0 件**でレビュー依頼。 |
| **3. 成果物形式** | **Markdown**（台本・構成・納品パスメモ）。巨大バイナリは `projects/` ではパスのみ。 |
| **4. 報告先** | **leader**（公開前全件）。 |
| **5. 週の稼働目安** | **1〜3 時間**相当。**他役兼任**を既定とする。本数が増えたら 5 つを見直す。 |
