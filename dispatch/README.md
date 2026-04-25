# リーダー配信（dispatch）

Cursor は**別のチャットに文言を自動送信する公式機能を持たない**ため、代わりに次の 2 点で **Linux の「パイプ」に近い**運用にする。

1. **ひな形** — `~/ai-company/templates/role-dispatch-instruction-template.md` を埋める。  
2. **配信スクリプト** — `~/ai-company/scripts/dispatch-instruction.sh` が、指定した `members/<役>/inbox/` に **`INSTRUCTION-` で始まるファイル**としてコピーする。

`dispatch/sent/日付/by-role/<役名>/` には、配信先ファイルへの**シンボリックリンク**が残る。リーダーは「何を誰に送ったか」をここで追える。

## 依頼の入口（leader 先）

**`INSTRUCTION-` で配る約束付き依頼は、leader と内容を決めてから**テンプレを埋め・本スクリプトで配信する運用を正とする。各役チャットは下書きや専門確認まで。詳細は **`~/ai-company/members/leader/CLAUDE.md`** の「依頼の入口（leader 先・採用ルール）」。

## 指示の出し方: Slack「あり / なし」どちらでも使える

| 状況 | やること（**正＝倉庫**） | Slack |
|------|--------------------------|--------|
| **Slack なし** | テンプレを埋め → `dispatch-instruction.sh` で各 `inbox` へ。各役は **Cursor** で当該フォルダを開き `inbox` を最優先。 | 不要。 |
| **Slack あり** | 上に**同じ**。加えて、依頼ID・期限の短い**リマインド**を `#general` や `#ai-役名` へ（MCP または手動）。 | 速報。本文の合意は **必ず in-repo の `INSTRUCTION-`**。 |

- **下から上への返却**は、**基本は常に** `members/leader/inbox/replies/依頼ID-役職名.md`（Slack の有無に依らない）。  
- **Slack にも貼る**場合は、同じ**依頼ID**をメッセージ先頭に書き、**`【役職名】`** を付けて会話上「誰の発言か」が分かるようにする。詳細は **`~/ai-company/config/slack-roles.md`**。

## Slack 上で各「役職」が発言する見せ方

- 実アカウントを増やす必要はなく、**1 行目を `【フォルダ名（役職）】`** に統一すれば、#general でも**役職者ごとの発言**として読める。  
- 量が多い役は、**`#ai-writer` のような専用チャンネル**を切る案も `config/slack-roles.md` にある（作成はワークスペース管理側）。

## 下位（各役職）側の合意

- その役の会話を始めるときは `cd ~/ai-company/members/<役職名>`。  
- 最初に **`inbox/INSTRUCTION-*.md` の最新**を読む。  
- 返却はテンプレの **`members/leader/inbox/replies/`** へ。Slack へも出すなら `config/slack-roles.md` の形式に合わせる。

## 上位（リーダー）側

- 返信を受け、必要なら `meetings/handoffs/YYYY-MM-DD.md` や日次集約に反映する。  

詳細はリポジトリ直下の `README.md` 、`~/ai-company/config/slack-roles.md` も参照。
