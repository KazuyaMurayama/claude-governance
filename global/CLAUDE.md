# Global Instructions

## 0. CLAUDE.md 階層と環境別の振る舞い（最重要・最初に読む）

### 環境別の参照ファイル
| 環境 | 本ファイル (`~/.claude/CLAUDE.md`) | リポ内 `CLAUDE.md` |
|---|---|---|
| **VSCode 拡張版 Claude Code** | ✅ 読まれる | ✅ 読まれる |
| **Web版 Claude Code (claude.ai)** | ❌ **読まれない場合あり** | ✅ 読まれる |

### 設計原則
1. **各リポの `CLAUDE.md` は単独完結である必要がある**（Web版でも有効でなければならない）
2. 本グローバルファイルは「VSCode拡張時に上乗せされる個人デフォルト」と位置付ける
3. ブランチ管理／ファイル保存／成果物報告／開発者命名 等の**運用クリティカルルールは各リポ CLAUDE.md にも重複して書く**（重複は「ミス」ではなく「設計要件」）
4. グローバル更新時は、関連する全リポの CLAUDE.md にも同義の更新を反映させる責務がある

### プロジェクト固有ルールの所在
- **NASDAQ 関連ルール**: `KazuyaMurayama/NASDAQ_backtest` リポの `CLAUDE.md` を正典とする（本ファイルには記載しない）
- 他のドメイン特化ルールも同様に、対象リポの `CLAUDE.md` を正典とする

---

## 1. 開発者情報・命名規則（グローバル・全プロジェクト共通）

| 種別 | 表記 | 用途 |
|---|---|---|
| **システム識別子（変更不可）** | `KazuyaMurayama` | GitHub ユーザー名 / URL / `@KazuyaMurayama` 等 |
| **システム識別子（変更不可）** | `kazuya.murayama.21@gmail.com` | git `user.email` / 連絡先 |
| **表記名（人間として記載する場合）** | **男座員也（Kazuya Oza / おざ かずや）** | ドキュメント本文の著者名 / プロフィール / コミット message 中の自己言及 |

### ルール
- ドキュメント・コード・コミットメッセージ本文等で開発者名を**人間として**記載する際は **男座員也 / Kazuya Oza** を使用する
- GitHub URL、リポジトリ名、`@KazuyaMurayama` 等のシステム識別子は**そのまま使う**（変更しない・できない）
- 「Murayama」「村山」「Otokoza」「おとこざ」を表記名として誤用しない（システム識別子としての `KazuyaMurayama` 出現は許容）
- AI が生成するドキュメントでも本ルールを遵守

---

## 2. ツール実行（毎回適用）
- 確認不要・即実行。「Allow ~~ ?」「Should I...?」等の事前確認文を出力しない。即実行→事後報告。
- 権限は `~/.claude/settings.json` と `~/.claude/settings.local.json` の双方で `defaultMode: bypassPermissions` ＋ allow 全主要ツール設定済み。追加設定不要。
- 例外（事前確認必須）: main/master への `git push --force`、`gh repo delete`。

### ルール競合時の優先順位（全プロジェクト共通）
1. `settings.json` の deny → **絶対ブロック**（ルール文言より優先・上書き不可）
2. この CLAUDE.md の「即実行」指示 → `.claude/quality-rules.md` の「確認後 push」より優先
3. ただし **push 前に diff サマリを1行だけ事後報告**する（ユーザー応答待ちはしない）
4. 例外（上記2項目も override して事前確認必須）: main/master への force push、`gh repo delete`
- 長時間処理は積極的に `run_in_background: true`。
- **ファイル操作（編集・検索・読み込み）は Edit/Write/Read/Grep/Glob を直接使用**。Agent ツールは承認ダイアログが発生するため、単純なファイル操作・ローカル編集タスクには使わない。

### Tool Interrupted 発生時の対処（VSCode拡張で頻発）
- `[Request interrupted by user for tool use]` は**権限エラーではなくVSCode UI側のキャンセル信号**。bypassPermissions では防げない。
- 主因はツール実行中のチャット欄クリック・Esc押下・先行入力など。
- ユーザーが「再開」「すすめて」「OK」等と言ったら、**直前と同一のツール呼び出しを確認なしで即再試行**。説明は不要。
- 同一ツールが3回連続で中断された場合のみ「VSCode再起動 or 実行中はパネルを触らず待機」を1行で案内。
- `~/.claude/` 配下の設定ファイル編集時は中断率が高い傾向。1回目で中断されたら無言で2回目を試行する。

## 3. Shell（毎回適用）
- Windows 11 + PowerShell 5.1。`&&` 不可 → `;` + `if ($?)`。Bash tool併用可。
- GitHub操作は Node.js + REST API 直接呼び出しを優先（gh CLI より高速）。
- git作業前: `git branch --show-current` でブランチ確認 → main以外なら `git checkout main && git pull` してから開始。

## 4. ブランチ管理（毎回適用・絶対厳守）
- **デフォルト: mainへ直接コミット**。ブランチ作成はユーザーが明示的に指示した場合のみ。
- ブランチを作成した場合、作業完了前に必ず `main` へマージ → ブランチ削除 → push まで完了させる。
- ブランチにファイルを置いたまま回答を完了することを禁止。「完了 = mainにマージ済み＆push済み」。
- マージ手順: `git checkout main; git pull; git merge <branch>; git push origin main; git branch -d <branch>`
- Claude Code Web版が自動生成したブランチも同様。セッション終了前に必ずmainへマージする。
- ブランチが残存している場合は、次セッション開始時に `git branch -a` で確認し、即マージ・削除する。

## 5. ファイル生成先ルール（毎回適用・絶対厳守）
- **`C:\Users\user\Desktop` へのファイル生成・スクリプト保存は禁止**（ユーザーが「デスクトップに保存して」と明示した場合のみ例外）。
- リポジトリ作業中に生成する成果物・スクリプト・中間ファイルはすべて **対象リポジトリ内**（GitHub API直接 または ローカルclone配下）に保存する。
- 一時スクリプトが必要な場合も、作業リポジトリのディレクトリ内に作成し、作業後に削除またはコミットする。

## 6. Skill 起動ルール（グローバル・全スキル対象）
以下のスキルは **必須・スキップ禁止**。該当シーンでは `~/.claude/skills/<name>/SKILL.md` を読んでから作業を開始すること。

> Web版 Claude Code では `~/.claude/skills/` ではなく、対象リポの `.claude/skills/` 配下を参照すること。リポ側 CLAUDE.md にも同じ Skill 起動ルールを単独完結形式で記載する。

### 計画・実行・品質
| シーン | スキル |
|---|---|
| アイデア出し・選択肢の洗い出し | `~/.claude/skills/sp-brainstorming/SKILL.md` |
| 複雑な多段タスクの計画作成（必ず着手前に） | `~/.claude/skills/sp-writing-plans/SKILL.md` |
| 計画に沿った実行・サブエージェント管理 | `~/.claude/skills/sp-executing-plans/SKILL.md` |
| 並列サブエージェントの起動・分配 | `~/.claude/skills/sp-dispatching-parallel-agents/SKILL.md` |
| サブエージェント主導の開発 | `~/.claude/skills/sp-subagent-driven-development/SKILL.md` |
| 成果物の納品・コミット前チェック（必ず） | `~/.claude/skills/sp-verification-before-completion/SKILL.md` |

### 開発・デバッグ
| シーン | スキル |
|---|---|
| バグ・エラーの体系的調査 | `~/.claude/skills/sp-systematic-debugging/SKILL.md` |
| TDD でテストから実装 | `~/.claude/skills/sp-test-driven-development/SKILL.md` |
| コードレビューを依頼する | `~/.claude/skills/sp-requesting-code-review/SKILL.md` |
| コードレビューを受け取る・反映する | `~/.claude/skills/sp-receiving-code-review/SKILL.md` |
| 開発ブランチの完了・マージ準備 | `~/.claude/skills/sp-finishing-a-development-branch/SKILL.md` |
| git worktree を使った並列開発 | `~/.claude/skills/sp-using-git-worktrees/SKILL.md` |
| 文章・ドキュメントの執筆 | `~/.claude/skills/sp-writing-skills/SKILL.md` |
| スーパーパワー全体の把握・選択迷い時 | `~/.claude/skills/sp-using-superpowers/SKILL.md` |

### リサーチ・調査
| シーン | スキル |
|---|---|
| Web リサーチ・並列調査・レポート生成 | `~/.claude/skills/research-deep/SKILL.md` |
| YouTube 動画のトランスクリプト取得 | `~/.claude/skills/youtube-transcript/SKILL.md` |
| 記事・Web ページの内容抽出 | `~/.claude/skills/article-extractor/SKILL.md` |

### 図表・ビジュアライゼーション
| シーン | スキル |
|---|---|
| フロー図・アーキテクチャ図・シーケンス図 | `~/.claude/skills/mermaid-agents365/SKILL.md` |
| 高度な Mermaid 図（23 図表型） | `~/.claude/skills/mermaid-wh2099/SKILL.md` |
| データビジュアライゼーション設計 | `~/.claude/skills/visualization-builder/SKILL.md` |
| ダッシュボード仕様の定義 | `~/.claude/skills/dashboard-specification/SKILL.md` |

### コンサルティング・戦略
| シーン | スキル |
|---|---|
| 戦略レポート・事業分析・提案書（McKinsey/BCG/Bain 水準） | `~/.claude/skills/management-consulting/SKILL.md` |
| ステークホルダーへの要件ヒアリング | `~/.claude/skills/stakeholder-requirements-gathering/SKILL.md` |
| エグゼクティブサマリー作成 | `~/.claude/skills/executive-summary-generator/SKILL.md` |
| 技術成果をビジネス指標に翻訳 | `~/.claude/skills/technical-to-business-translator/SKILL.md` |
| インパクトの定量化 | `~/.claude/skills/impact-quantification/SKILL.md` |

### データ分析・統計
| シーン | スキル |
|---|---|
| 時系列・トレンド分析 | `~/.claude/skills/time-series-analysis/SKILL.md` |
| A/B テスト・統計検定 | `~/.claude/skills/ab-test-analysis/SKILL.md` |
| コホート分析 | `~/.claude/skills/cohort-analysis/SKILL.md` |
| ファネル分析 | `~/.claude/skills/funnel-analysis/SKILL.md` |
| セグメンテーション分析 | `~/.claude/skills/segmentation-analysis/SKILL.md` |
| ビジネス指標の計算・定義 | `~/.claude/skills/business-metrics-calculator/SKILL.md` |
| 根本原因調査 | `~/.claude/skills/root-cause-investigation/SKILL.md` |
| EDA（探索的データ分析）のプログラム化 | `~/.claude/skills/programmatic-eda/SKILL.md` |
| インサイトの統合・物語化 | `~/.claude/skills/insight-synthesis/SKILL.md` |
| データナラティブ（分析結果のストーリー化） | `~/.claude/skills/data-narrative-builder/SKILL.md` |

### データ品質・ドキュメント
| シーン | スキル |
|---|---|
| データ品質監査 | `~/.claude/skills/data-quality-audit/SKILL.md` |
| SQL → ビジネスロジック変換 | `~/.claude/skills/sql-to-business-logic/SKILL.md` |
| スキーマのマッピング・変換 | `~/.claude/skills/schema-mapper/SKILL.md` |
| クエリの検証・テスト | `~/.claude/skills/query-validation/SKILL.md` |
| 指標の照合・整合確認 | `~/.claude/skills/metric-reconciliation/SKILL.md` |
| セマンティックモデルの構築 | `~/.claude/skills/semantic-model-builder/SKILL.md` |
| データカタログ登録 | `~/.claude/skills/data-catalog-entry/SKILL.md` |

### 分析ワークフロー・品質管理
> ⚠️ 以下は索引ではなく **必須トリガー**。該当シーンになった瞬間に SKILL.md を読んでから作業を開始すること。

| シーン（トリガー条件） | スキル |
|---|---|
| 分析・調査の計画・設計を始める前 | `~/.claude/skills/analysis-planning/SKILL.md` |
| 分析結果のドキュメントを作成する時 | `~/.claude/skills/analysis-documentation/SKILL.md` |
| 分析の仮定・前提を記録する時 | `~/.claude/skills/analysis-assumptions-log/SKILL.md` |
| **分析・戦略結果のQC・品質チェック・レビュー・ステークホルダー共有前** | `~/.claude/skills/analysis-qa-checklist/SKILL.md` |
| 分析の振り返り・レトロスペクティブを行う時 | `~/.claude/skills/analysis-retrospective/SKILL.md` |
| 構造化されたピアレビューを行う時 | `~/.claude/skills/peer-review-template/SKILL.md` |
| セッション引き継ぎ・コンテキスト整理をする時 | `~/.claude/skills/context-packager/SKILL.md` |
| 分析手法を説明・解説する時 | `~/.claude/skills/methodology-explainer/SKILL.md` |
| Ship → Learn → Next サイクルを回す時 | `~/.claude/skills/ship-learn-next/SKILL.md` |

### その他
| シーン | スキル |
|---|---|
| プロンプトエンジニアリング・改善 | `~/.claude/skills/prompt-engineering/SKILL.md` |
| タペストリー（複合コンテンツ生成） | `~/.claude/skills/tapestry/SKILL.md` |

## 7. モデル使い分け
- メイン: **Claude Fable 5（`claude-fable-5`）** を使用。
  計画・中〜高難易度の実装/分析・全体指揮を担当。
- 実行フェーズ（定型実装・ファイル編集・テスト実行）:
  サブエージェントを `model: "sonnet"` で起動して委譲。
- ※難易度ベースの自動メイン切替は不可。Fable の自動切替は安全性ブロック時の
  Opus 4.8 フォールバックのみ。工程別の使い分けはサブエージェント委譲で行う。

## 8. 進捗報告
- 大タスク開始時に全体計画提示 → 進行中は完了/残りを簡潔報告 → サブエージェント結果は都度要約 → エラー即報告。

## 8b. コンテキスト管理（自動圧縮対策 / Compact Instructions）
Claude Code はコンテキスト利用率が高まると自動でテキスト要約圧縮（auto-compact, 約83.5%目安）を行う。圧縮で重要情報を失わないため以下を守る。
- **圧縮時に必ず保持**: 現タスクの目的・前提制約・意思決定 / `tasks.md` の進行中タスク / 正典ファイル参照（各リポ `CURRENT_*.md`・SPEC 等）/ ファイルスコープ・命名規則 / 直近のエラー・制約・回避策。
- **永続層に状態を書き出す（圧縮の影響外）**: `tasks.md` / `file_index.md` / `session.json` / プロジェクト記憶 `~/.claude/projects/.../memory/MEMORY.md`。会話履歴に状態を依存させない。
- **運用**: 重い調査・実装はサブエージェントに委譲し親には要約のみ戻す（コンテキスト分離）。利用率が高まったら警告を待たず `/compact <保持指示>` を能動実行。別タスクへ移る際は `/clear`（CLAUDE.md・tasks.md・MEMORY.md は残る）。`/context` で利用状況を確認。
- ※潜在空間ベクトル圧縮（Codex の `encrypted_content` 方式）は Anthropic 公開 API がトークン入出力であるため本ハーネスでは自前実装**不可**。テキスト要約＋外部メモリ（CLAUDE.md / MEMORY.md / tasks.md / サブエージェント）で代替する。

## 9. 成果物報告ルール（最重要・毎回必須）
ファイルを1つでも作成・更新・pushしたら、**すべての**成果物を以下の形式で報告する。例外なし。

### 必須フォーマット（3列表）
| 成果物 | 説明 | リンク |
|---|---|---|
| ファイル名.md | 1行説明 | [開く](https://github.com/OWNER/REPO/blob/BRANCH/path/to/file.md) |

### 厳守事項（違反＝再提出）
1. **必ずMarkdownリンク `[表示名](URL)` 形式**。plain text URL は禁止。
2. **`/blob/<ブランチ>/<実パス>` 形式**。リポジトリトップURLは禁止。
3. **報告前にURL検証必須**：`gh api repos/OWNER/REPO/contents/PATH?ref=BRANCH` で存在確認してから提示。
4. **ブランチ名は推測禁止**：`git rev-parse --abbrev-ref HEAD` で実値を取得。
5. **push完了後にのみURL生成**：未pushファイルはURL生成しない。
6. 404を出した場合は即座に訂正版を提示し、原因を1行で報告。

### URL生成手順（毎回この順序）
1. `git push` 完了を確認
2. `git rev-parse --abbrev-ref HEAD` でブランチ取得
3. `gh api repos/OWNER/REPO/contents/PATH?ref=BRANCH` で存在確認
4. URL組み立て → Markdownリンク化 → 表に挿入
5. 報告

### 詳細仕様
成果物が1つでもある場合は **必ず** `~/.claude/deliverables-policy.md` を読む。

### 例外シナリオ別の必須対応
#### A. サブエージェント委託時
- サブ起動promptに必ず明記：「~/.claude/deliverables-policy.md 1.1〜1.5を厳守、3列表で報告、URL検証1.3必須」
- サブの報告URLはメインが**再検証**してからユーザー提示。最終責任はメインClaude。

#### B. ローカル限定ファイル（未push）
- リンク列に絶対パスをバッククォート＋「（ローカル）」で記載。
- 「GitHubへpushしますか？」を Next Action に必ず添える（ユーザーが明示拒否した場合を除く）。

#### C. 急ぎ要求時
- URL検証・3列表・ブランチ実値取得は**省略不可**（数秒で完了するため）。
- 省略可なのは説明文の長さのみ。「急ぎだから検証飛ばす」は禁止。

#### D. 複数タスク並行時
- タスクごとに見出し分離 → 各タスクに3列表。
- 報告直前に「着手タスク数 = 報告セクション数」を自己照合。
- 成果物ゼロのタスクも「成果物なし」と明記（無言省略禁止）。

### 自己チェック（報告送信前の最終ゲート）
以下4点を全タスクで確認できなければ送信しない：
1. サブ委託があったか？ → あれば再検証実施
2. ローカル限定ファイルがあるか？ → あれば絶対パス＋「（ローカル）」表記
3. 急ぎ要求でも検証スキップしていないか？
4. タスク数と報告セクション数が一致しているか？

## 10. ファイル特定（編集前）
- ユーザー発話のキーワード全て（例: "warp-guide"）をファイル名と照合してから編集。file_index.mdがあれば参照。
- キーワードが1つでも不完全一致・候補が不確かな場合は確認してから編集（推測で着手しない）。

## 10b. ドキュメント日付・ファイル名ルール（v2.0 / 2026-06-03 改訂）

### H1直下の日付メタデータ（本文表記）
レポート系 .md 新規作成時は H1直下に必ず記載：
```
作成日: YYYY-MM-DD
最終更新日: YYYY-MM-DD
```
- 更新時は **最終更新日のみ** 当日付に書き換え（作成日は固定）
- **本文中の日付表記**は `YYYY-MM-DD`（ハイフン区切り）

### ファイル名の日付サフィックス（新ルール）
- 基本形: `<TOPIC>_YYYYMMDD.md`（**サフィックス・ハイフンなし**）
  - 例: `STRATEGY_COMPARISON_20260603.md`、`MONTHLY_REPORT_20260603.md`
- **同日中の追加更新**: `-v2`、`-v3` を追加（同名ファイルを上書きせず別ファイルとして残す場合）
  - 1回目: `<TOPIC>_20260603.md`
  - 2回目: `<TOPIC>_20260603-v2.md`
  - 3回目: `<TOPIC>_20260603-v3.md`
- **日付が変わったら v サフィックスはリセット**
  - 翌日1回目: `<TOPIC>_20260604.md`（v なし）
  - 翌日2回目: `<TOPIC>_20260604-v2.md`

### 表記の区別（ファイル名 vs 本文）
- **ファイル名**: ハイフン **なし** `YYYYMMDD`（例: `20260603`）
- **本文中の日付表記**: ハイフン **あり** `YYYY-MM-DD`（例: `2026-06-03`）

### 旧形式（廃止・新規禁止）
- ❌ `2026-06-03_<TOPIC>.md`（プレフィックス・ハイフン）
- ❌ `<TOPIC>_2026-06-03.md`（サフィックス・ハイフン）
- ✅ `<TOPIC>_20260603.md`（**現行ルール**）

### 対象外（日付サフィックスを入れない）
- README.md / CLAUDE.md / FILE_INDEX.md / tasks.md / CHANGELOG.md / LICENSE.md / SPEC.md / HYPOTHESES.md
- `CURRENT_*.md`（常に最新で参照される単一ファイル）
- パイプライン自動生成ファイル（例: `REPORT.md`、`outputs/*.md`）

## 11. 回答スタイル
- 回答末尾に「**Next Action:**」でユーザーの次アクションを具体推奨。迷う場面は「**推奨:**」で明示。

## 12. 参照ファイル
- **成果物が1つでもある場合は必読**: `~/.claude/deliverables-policy.md`
- プロフィール参照時: `~/.claude/profile.md`（職歴・資産・目標）
- プロジェクト記憶: `~/.claude/projects/C--Users-user/memory/MEMORY.md`

## 13. プロジェクト固有ルールの所在（正典は各リポ CLAUDE.md）

| ドメイン | 正典の場所 |
|---|---|
| NASDAQ バックテスト・戦略・評価指標・WFA等 | `KazuyaMurayama/NASDAQ_backtest` → `CLAUDE.md` + `docs/rules/` |
| NASDAQ ベスト戦略の最新値 | `KazuyaMurayama/NASDAQ_backtest/CURRENT_BEST_STRATEGY.md` （WebFetch で取得し一次根拠とする） |
| ナレッジベース（RAG）運用 | `KazuyaMurayama/ai-knowledge-base` → `CLAUDE.md` |
| その他リポ固有ルール | 各リポ `CLAUDE.md` を参照 |

「NASDAQ ベスト戦略 / 推奨 / 最終結果」系の質問は、回答前に必ず上記 `CURRENT_BEST_STRATEGY.md` を WebFetch で取得し、その内容を一次根拠とする。memory やCSVや `FINAL_*` ファイル名は二次資料扱い。
