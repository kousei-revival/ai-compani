# 依頼: 案件探索（クラウドワークス・ランサーズ系）

| **依頼ID** | **CASE-SCOUT-2026-04-24** |
| **発行日** | 2026-04-24 |
| **発行者** | leader |

## 目的

**新規案件候補を探し、一覧化・優先度のたたき台**まで出す。応募の送信は人（経営者）が行う前提。

## 正本ツール

`~/Desktop/your-perfect-days/job-scout/`（手順は同リポの `CURSOR.md`・`setup/SETUP-FOR-CURSOR.md`）。

### 実行の目安

```bash
export PATH="/Users/kousei/Desktop/your-perfect-days/tools/_portable_node/node-v22.15.1-darwin-arm64/bin:$PATH"
cd ~/Desktop/your-perfect-days/job-scout
npm install   # 初回のみ
npm run scout:sheet
# または生データ: npm run scout:raw -- --platform=crowdworks,lancers --limit=15
```

※ Google 連携・`.env` が未設定なら、**設定可能になるまで** `scout:raw` のみ or 手動で媒体を見たメモでも可（`researcher/CLAUDE.md` の判断基準に従う）。

## 探索の焦点（今回）

- **主戦場:** CrowdWorks / Lancers  
- **狙いの型:** AI 活用伴走、業務自動化、導入支援、LP/フォーム/Notion/スプレッド整備など**軽め導入**も候補に入れる  
- **成果物:** `members/researcher/projects/2026-04-cw-scout/` に **Markdown**  
  - 候補一覧（**件数・単価レンジ・URL**）  
  - 上位 3〜5 件の**応募優先のたたき台**（コピペ用に短く）  
  - 除外した条件があれば1行

## リーダー返却

- `members/leader/inbox/replies/CASE-SCOUT-2026-04-24-researcher.md` に **要約5行 + 成果物パス**。

## 禁止

- ToS に反するスクレイピング（**job-scout の既存コマンドの範囲**に留める）  
- 応募の**自動送信**

## 合意

媒体の切り替え・大きな除外条件の変更は **leader レビュー後**に確定。
