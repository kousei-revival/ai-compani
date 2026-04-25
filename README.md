# ai-company

## ディレクトリの意味

| パス | 役割 |
|------|------|
| `~/ai-company/` | **会社共通** — 方針・テンプレ・全員参照の資料など |
| `~/ai-company/templates/` | **雛形** — `member-CLAUDE-template.md` / **`council-handoff-template.md`**（役職者会議→経営者手渡し） / **`role-dispatch-instruction-template.md`**（リーダー→他役の約束付き依頼） |
| `~/ai-company/scripts/dispatch-instruction.sh` | **配信** — 上記テンプレを `members/<役>/inbox/` へ一斉コピー（**別 Cursor チャットへの「自動送付」の代替**） |
| `~/ai-company/dispatch/` | **配信履歴**（`sent/`）と運用メモ `README.md`（**Slack なしで指示**する手順もここ） |
| `~/ai-company/config/slack-roles.md` | **Slack 上**で役職別に会話を分ける（`【役職名】`・`#ai-*`） |
| `~/ai-company/config/slack-channels-setup.md` | **専用チャンネル一覧と手動作成手順**（MCP は作成不可） |
| `~/ai-company/projects/slack-bot/` | **Slack @ボット返信**（Bolt + LLM）。**[README](projects/slack-bot/README.md)** にデプロイと Slack App 設定 |
| `~/ai-company/meetings/handoffs/` | **経営者への日次手渡し**（`YYYY-MM-DD.md`） |
| `~/ai-company/CLAUDE.md` の「CLAUDE.md の育て方」 | 初稿 50 点 OK・運用で追記して AI 社員を育てる方針 |
| 同上「月次メンテ」 | **月 1 回**、ルールの削除・統合・具体化で肥大化を防ぐ |
| `~/ai-company/members/` | **各 AI 社員の部屋** — メンバーごとの作業用フォルダ（人格・ログ・専用メモなど） |
| **Slack** | **日次の共有・速報のハブ**（`members/leader/CLAUDE.md`「連絡のハブ」）。**公式 LINE は主軸にしない。**リポの Markdown が正、Slack は抜粋と割り切る。 |

新しい社員用の部屋を作るときは `members/` の下に、その子の名前でフォルダを切る想定。  
**役職の切り方**（週 3 回以上の作業＝役職候補）は `~/ai-company/CLAUDE.md` の「メンバー（役職）の決め方」を参照。  
**新しい部屋を増やす前**は、同ファイルの「**新役職を作る前に答える5つ**」で解像度を上げる。

### メンバー部屋の構造（例：`leader`）

| パス | 役割 |
|------|------|
| `members/<名前>/CLAUDE.md` | その役の**役割説明** |
| `members/<名前>/inbox/` | **タスク置き場**（依頼・未整理メモ） |
| `members/leader/inbox/replies/` | **他役職からリーダーへ返却**（分析結果・`INSTRUCTION-` への回答） |

### メンバー部屋の構造（例：`designer`）

| パス | 役割 |
|------|------|
| `members/designer/inbox/` | 依頼・メモ |
| `members/designer/projects/<案件名>/` | その案件の成果物（PNG / JPG など）を置く |

### メンバー部屋の構造（例：`writer`）

| パス | 役割 |
|------|------|
| `members/writer/inbox/` | 依頼・ブリーフ |
| `members/writer/projects/<案件名>/` | その案件の成果物（**Markdown**: ブログ・メルマガ・LP コピー等） |
| `members/writer/references/` | note / X 長文用の**参照コピー**（みかみスタイルガイド・こうせい用スキル等）。詳細は `references/README.md` |

### メンバー一覧（フォルダ名＝ CWD 人格名）

| フォルダ | 役割の一言 |
|----------|------------|
| `leader` | 朝 inbox・レビュー・夕方の集約 |
| `writer` | ブログ・メルマガ・note 長文など |
| `designer` | 画像・バナー・ビジュアル |
| `sns` | X 運用・投稿文案・運用メモ |
| `academic` | 学術班オペレーション（症例・スライドまわり） |
| `customer_success` | 伴走クライアント向け資料・日報設計 |
| `operations` | ルーチン確認・週次オペメモ |
| `web` | HP・LP 構成とコピーたたき台 |
| `video` | 動画の台本・構成チェック |
| `researcher` | 案件探索（`job-scout` 連携・候補の整理） |

各フォルダは `inbox/` と `projects/` を持つ（`leader` は運用例として `inbox` 中心）。`cd ~/ai-company/members/<上記>/` で起動すると `~/CLAUDE.md` のルールでその人格になる想定。
