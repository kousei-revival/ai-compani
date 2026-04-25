# Slack 上で「各役職（AI 社員）」が発言するルール

Slack には**AI 社員 1 人＝1 アカウント**は無い想定。次の**どれか**で「誰の発言か」を分かるようにする。

## 1. 推奨: 1 行目に役職ラベル（#general でも専用チャンネルでも）

すべての「役職からの返信」は、**先頭**に次の形式を付ける（スペース1つ可）。

```text
【役職フォルダ名】本文
```

**例（フォルダ名＝`sns` のとき）:**  
`【sns】今週の X 案は inbox のドラフト 3 本、欠損なし。`

- **理由:** 1 人の Slack アカウント＋MCP でも、読み手が役割を区別できる。  
- **禁止にしないが避ける:** 役職名のない雑多な文だけ（集約のとき困るため）。

## 2. 上級: 役職ごと専用チャンネル（会話の「部屋」が分かれる）

**チャンネル名の正と、手動作成の手順**は **`~/ai-company/config/slack-channels-setup.md`**（MCP ではチャンネル作成不可のため、Slack 上で作成する）。

| `members/` フォルダ | チャンネル名（本採用） |
|----------------------|----------------------|
| `writer` | `#ai-writer` |
| `designer` | `#ai-designer` |
| `sns` | `#ai-sns` |
| `academic` | `#ai-academic` |
| `customer_success` | `#ai-cs` |
| `operations` | `#ai-ops` |
| `researcher` | `#ai-researcher` |
| `web` | `#ai-web` |
| `video` | `#ai-video` |
| `leader` | `#ai-leader` |

- **#general** … 全員向け速報、横断。役職ラベル付き 1 行。  
- **#ai-*** … その役の**長めのやり取り**・中間案（ラベルは同じ型で揃えてもよい）。

Cursor の Slack MCP で投げるときは、**`slack_search_channels`** で上記チャンネルの **channel_id** を解決してから `slack_send_message` する。

## 3. 正（依頼の本体）は常にリポ

Slack は**速報と合意表示**。**約束付き依頼の中身**は `members/<役>/inbox/INSTRUCTION-*.md` と、リーダー発行の**依頼ID**で揃える（`config` と `dispatch/README.md` 参照）。
