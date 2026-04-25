# シャットダウン

1日の終わりに、翌日を気持ちよく迎えるための夜ルーティン。

## 起動時

### Step 1: 現在地の把握

- `date` コマンドで現在時刻を確認する
- `now.md` を読む（明日の予定を把握するため）
- 今日の `days/YYYY-MM-DD.md` を読む（今日何をしたか把握するため）

### Step 2: 夜ルーティンの読み込み（初回はセットアップ）

同ディレクトリの `items.json` を読む。

**ファイルが存在しない場合（初回）：**

1. ユーザーに聞く：
   - 「寝る前にいつもやってることってある？（歯磨き、お風呂、ストレッチとか）」
   - 「他にやりたいこと・習慣にしたいことはある？」
2. 回答をもとにチェックリスト項目を作成する
   - 自然な順番に並べる（準備→身支度→最後に布団）
   - 最後の項目は「布団に入る」にする
3. `items.json` に保存する（形式: `["項目1", "項目2", ...]`）

**ファイルが存在する場合：** そのまま読み込んで使う。

### Step 3: アプリを閉じる

不要なアプリをすべて閉じる。以下を実行：

```bash
# Finderとターミナル以外のアプリを閉じる（graceful quit）
osascript -e '
tell application "System Events"
  set appList to name of every application process whose visible is true
  repeat with appName in appList
    if appName is not in {"Finder", "Terminal", "iTerm2"} then
      try
        tell application appName to quit
      end try
    end if
  end repeat
end tell
'
```

閉じたアプリの一覧をユーザーに報告する。

### Step 4: HTMLチェックリストを生成して開く

1. `template.html`（同ディレクトリ）を読み込む
2. テンプレート内のプレースホルダを置換する：
   - `["{{ITEMS}}"]` → `items.json` の内容（Step 2で読み込んだ配列）
   - `["{{SCHEDULE}}"]` → now.mdから抽出した明日の予定（配列の各要素として）
   - `"{{MESSAGE}}"` → 今日の一言（Step 5参照）
3. `/tmp/shutdown-YYYY-MM-DD.html` に書き出す
4. `open /tmp/shutdown-YYYY-MM-DD.html` でブラウザで開く

### Step 5: 今日の一言

今日の記録を振り返って、短く一言添える。
- 頑張った日なら労う
- 普通の日なら「今日もお疲れさま」
- HTMLの `{{MESSAGE}}` に埋め込む

### Step 6: 記録

- 今日の `days/YYYY-MM-DD.md` にシャットダウン時刻を追記する
- `now.md` に翌日の準備で気づいたことがあれば反映する

### Step 7: 端末での出力

短く。

```
シャットダウン完了。チェックリストをブラウザで開いた。
[アプリ名, ...] を閉じた。
おやすみ。
```

## 心がけ

- 短く。夜は情報量を減らす
- 説教しない
- 23:30就寝を意識させるが、強制しない
