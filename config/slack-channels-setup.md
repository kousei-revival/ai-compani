# AI 社員用・専用 Slack チャンネル（作成手順）

**注意:** Cursor の Slack MCP から **チャンネルの新規作成はできない**（投稿・検索のみ）。  
以下の **公開チャンネル** を、ワークスペースで **手動作成**する（管理者権限が必要な場合あり）。

## 作り方（Slack クライアント）

1. 左サイドバー **「チャンネルを追加」** → **チャンネルを作成**  
2. **名前**に下表の **チャンネル名（# なし）** をそのまま入力（例: `ai-writer`）  
3. **公開チャンネル**を選ぶ  
4. **目的**に下表の説明をコピー（任意だが推奨）

## 作成するチャンネル一覧（10 本＋任意 1）

| 作成する名前（`#` 除く） | 紐づく `members/` | 目的（トピック用の例文） |
|-------------------------|-------------------|-------------------------|
| `ai-writer` | `writer` | AI 社員 writer：ブログ・メルマガ・note 長文の依頼・中間案 |
| `ai-designer` | `designer` | AI 社員 designer：画像・バナー・ビジュアルの依頼・たたき案 |
| `ai-sns` | `sns` | AI 社員 sns：X 文案・運用メモ・投稿まわり |
| `ai-academic` | `academic` | AI 社員 academic：学術班・症例・スライドまわり |
| `ai-cs` | `customer_success` | AI 社員 CS：伴走クライアント資料・日報設計 |
| `ai-ops` | `operations` | AI 社員 operations：ルーチン・週次オペ |
| `ai-researcher` | `researcher` | AI 社員 researcher：案件探索・候補整理 |
| `ai-web` | `web` | AI 社員 web：HP・LP 構成・コピーたたき台 |
| `ai-video` | `video` | AI 社員 video：動画台本・構成チェック |
| `ai-leader` | `leader` | AI 社員 leader：横断・レビュー・集約のすり合わせ（日次の全社速報は `#general` のままでも可） |

**任意:** 上記以外に **全役職のリンク用**だけ `#general` を使い続けてもよい。専用が多すぎる場合は、まず **`ai-leader`・`ai-sns`・`ai-writer`** から作るとよい。

## 作成後（Cursor / MCP）

チャンネル作成後、MCP の **`slack_search_channels`** で名前を検索し、**`channel_id`** を把握してから **`slack_send_message`** する（`~/ai-company/config/slack-roles.md` 参照）。

## 発言の型（再掲）

どの専用チャンネルでも、投稿先頭は **`【役職フォルダ名】`**（例: `【writer】`）を推奨。
