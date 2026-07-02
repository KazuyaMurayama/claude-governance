# CHANGELOG — claude-governance 変更履歴

作成日: 2026-06-23
最終更新日: 2026-07-02

> 変更の **WHAT** より **WHY** を残すことを優先する。何を変えたかは git log で追えるが、なぜそうしたかは記録しないと失われる。

---

## 2026-07-02 (2) — ルール遵守率改善: 絶対ルールTop10＋決定論的hooks＋HR/EH監査軸（rule-enforcement パッケージ）

### What
- **⛔絶対ルール Top10 ブロック**（`templates/hard-rules-block.md`、`HARD_RULES_START v1` マーカー）を、ガバナンス対象42リポ＋本リポ＋グローバル `~/.claude/CLAUDE.md`（`global/CLAUDE.md` 同期）＋テンプレの **CLAUDE.md 最上部（H1直後）** に一括配置。
- **決定論的 hooks 3種**（`templates/hooks/`→各リポ `.claude/hooks/`）: ①`pre_write_guard.py`=Desktop生成をPreToolUseで拒否 ②`post_bash_guard.py`=`git push` 直後に成果物報告ルールをリマインド注入 ③`session_guard.py`=Stop時に非mainブランチ/未pushを検査し終了を1回ブロック（stop_hook_activeでループ不可・全hook fail-open）。
- **`.claude/settings.json` へのマージ配線**: 既存 permissions / 既存 hooks を保持したまま追記（oogiri・deep-research で保全実証）。ローカル `~/.claude/settings.json` にも絶対パスで配線（テンプレ同期・`audit_local_sync` の正典キーに `hooks` 追加）。
- **監査に HR / EH 軸を追加**: Top10ブロック存在・hooks配線を月次監査が継続検証。happiness-system は既存除外の帰結として両軸除外。
- **展開スクリプト** `audits/deploy_rule_enforcement.py`（冪等・マーカー比較で正典へ自動更新・42リポ成功/失敗ゼロ）。
- 分析・設計・期待効果・留意点の詳細 = `RULE_ENFORCEMENT_20260702.md`。

### Why
ユーザー報告「記載済みのルールが守られず、指摘すると『見逃しました』と返る」。分析の結論は、(1) ルールがフラットに多すぎて1本あたりの注意が希釈（各リポ195〜324行・23〜39節）、(2) ルールを読む時点（開始時）と使う時点（終了時・ツール実行時）のミスマッチ、(3) 全てが助言テキストで強制力ゼロ（branch-cleanup トリガー配布済みでも4本のブランチ放置が再発した実証あり）、(4) 完了宣言前の機械ゲート不在。**散文の遵守は確率的、hooks は決定論的**。頻出違反3類型（ブランチ・報告・保存先）を機械ガード化し、残りは「Top10だけ最上部」で注意を集中させる。

### How to apply
- 正典ブロック/hooks を変えたら `python audits/deploy_rule_enforcement.py` で全リポ再展開（冪等）。
- Web版 hooks 発火は次回 Web セッションで実地確認（`git checkout -b test` → 終了時に完了前チェックが出るか）。層1のTop10ブロックは hooks 非依存で Web版でも確実に効く。
- ローカル hooks は次セッション起動から有効。

---

## 2026-07-02 — 監査体制の敵対的レビュー＋頑強化（自動発見・自動実行・偽適合排除）

### What
- **残存ブランチ4本を是正**: shopping_product_search ×2（toddler-undershirt / review-search-rules、各1固有コミット）と deep-research ×2（research-cfd-leverage-sbi 8固有コミット / loving-gauss 0）を main へ `--no-ff` マージ後、REST API DELETE（204）。deep-research の tasks.md コンフリクトは日付降順ユニオンで解決。
- **リポ一覧のハードコード廃止**（`audit_43repos.py` v2）: 認証付き `/user/repos` で毎回自動発見（private 含む・default branch も API 値）。トークン欠如時は fail loud（無認証 60req/h での偽結果を防止）。
- **偽適合の排除**: `ls-remote` / Contents API の失敗を「?」（判定不可＝FAIL要因）として記録。従来は失敗が「余分ブランチなし」等の偽 ✓ に化けていた。
- **audit_summary.py v2**: 監査日ハードコード（2026-06-25 固定）を撤廃し JSON meta から取得 / XB・判定不可・期限切れ除外を問題集計と **VERDICT: PASS/FAIL** に反映（従来は4本ブランチ残存でも「不適合ゼロ」表示だった）/ exit code で CI ゲート可能に / **private リポ名をデフォルトでマスク**（本リポは public のため。実名調査は `--no-mask`）。
- **governance link 陳腐化検知（GC軸）新設**: 正典を `templates/governance-link-block.md` に単一化し、各リポのマーカー間内容と比較。`add_governance_link.py` v2 に `--update`（正典への一括更新）を追加。GV 除外リポは GC も自動除外（含意）。
- **EXCLUSIONS v2**: ```yaml フェンス内のみパース（書式例のファントム登録を排除）/ `review_after` 期限切れを警告＋FAIL要因として実装（従来は文書に「警告する」とあるだけで未実装だった）。
- **月次自動監査**（`.github/workflows/governance-audit.yml`）: 毎月1日 05:00 JST に監査 → `audits/AUDIT_LATEST.md` 自動コミット → FAIL 時に Issue 自動起票（重複起票ガード付き）。private リポ監査には secret `GOVERNANCE_PAT` の登録が必要（未登録時は「判定不可」として表面化）。
- **ローカル同期監査**（`audits/audit_local_sync.py`）新設: 実機 `~/.claude/`（CLAUDE.md / deliverables-policy.md / settings.json 8キー）と本リポ正典の一致、および「正典変更コミットに同日 CHANGELOG 更新があるか」のドリフト検知。
- **settings.json.template を実機に再同期**: `model: opus[1m]` → **`claude-fable-5[1m]`**、`effortLevel: xhigh` → **`max`**（ユーザー確定）。
- **再監査結果**: 従来43リポは全軸適合。新カバー3リポ（Soulful-Content ＋ private 2リポ）の不適合17件と private 1リポの残存ブランチ2本（固有コミットあり）を新規検出 → 是正は次セッションのタスク。

### Why
**問題1: 「不適合ゼロ」は偽りの安心だった**
06-25 の「不適合ゼロ」達成から7日間で余分ブランチが1本→4本に増殖していたが、誰も監査を実行していなかった（実行者不在）。さらにダッシュボードの問題集計に XB が含まれず、4本残存でも「（なし）」と表示される構造だった。「いつでも実行できる」と「実行される」は別物であり、cron による強制実行と、集計の正直化（VERDICT）で「守られている状態」を機械的に維持する。

**問題2: 監査対象リスト自体が最初から不完全だった**
ハードコードされた43リポは public のみで、private 2リポ（2025-10 / 2026-04 作成）は初回監査から一度も対象になっていなかった。新リポ（07-01 作成）も手動追記されるまで永久に対象外。「REPOS リストに追加するだけ」という運用は追加する主体が不在なら機能しない。自動発見に切り替え、逆に意図的な除外だけを EXCLUSIONS.md で明示管理する（allowlist→denylist の反転）。

**問題3: 本リポは public であり、private リポの情報を書けない**
private リポも監査対象に含める以上、コミットされる成果物（ダッシュボード・Issue）に実名を載せると存在自体が漏れる。ユーザー判断で「public 維持・private も監査・名前はマスク」を採択。

**問題4: 文書と実装の乖離（review_after 警告・監査日・旧スクリプト名）**
EXCLUSIONS.md は「review_after が過ぎたら監査スクリプトが警告」と約束していたが未実装だった。監査日は 2026-06-25 にハードコードされ、再実行しても常に同日と表示された。ドキュメントが約束する挙動は実装されているか、このセッションのような敵対的レビューで定期検証する。

### How to apply
- 月次監査は自動実行される。**ユーザー作業: fine-grained PAT（Contents/Metadata: Read、全リポ）を発行し、claude-governance の Settings → Secrets → Actions に `GOVERNANCE_PAT` として登録**（未登録でも動くが private リポが「判定不可」として FAIL 表示される）。
- 手動監査: `PYTHONIOENCODING=utf-8 python audits/audit_43repos.py > /tmp/r.json && python audits/audit_summary.py /tmp/r.json`（実名は `--no-mask`）。
- governance link ブロックの文言を変える時は `templates/governance-link-block.md` を更新 → `python audits/add_governance_link.py --update` で全リポ一括反映 → GC 軸が自動で追従検証。
- 未是正の残タスク: Soulful-Content / private 2リポへのガバナンス展開（独自設計の可能性があるため EXCLUSIONS 登録か標準化かはユーザー判断）、private リポ1つの残存ブランチ2本（固有コミットあり・要マージ）。

---

## 2026-06-25 — 43リポ監査＋上位ガバナンス参照を42リポへ自動追加＋EXCLUSIONS導入

### What
- **監査スクリプト新設**（`audits/audit_43repos.py` + `audit_summary.py`）：12軸×43リポでガバナンス適合性を機械検査。EXCLUSIONS.md で部分除外をサポート。
- **EXCLUSIONS 機構導入**（`audits/EXCLUSIONS.md`）：「ガバナンス違反」と「意図的独自設計」を区別。partial 除外で特定軸のみスキップ可能。
- **happiness-system を partial 除外で登録**：default branch が `claude/flourish-forge-setup-wpvm3n` の独自憲法形式リポ。2026-06-23 作成・毎日活発に使用中で、無理に標準化すると独自設計の良さが壊れるため例外扱い。3か月後（2026-09-25）に再評価。
- **42リポへ「上位ガバナンスへの参照」ブロックを一括追加**（`<!-- GOVERNANCE_LINK_START/END -->` マーカー付き）：GitHub Contents API 直接 PUT で42リポすべて成功・失敗ゼロ。happiness-system のみ EXCLUSIONS に従いスキップ。
- **NASDAQ_backtest の取り残しブランチ削除**：`claude/sbi-click-365-nasdaq-guide-hfw748`（main と identical / ahead 0・behind 0）を REST API DELETE で削除。
- **監査スクリプトのキャッシュ問題を修正**：raw.githubusercontent.com は CDN キャッシュで古い内容を返すことが判明。Contents API + token 認証へ切り替え（5000/h レート）。
- **検証結果**：再監査で「不適合ゼロ」達成（全12軸でゼロ件）。

### Why
**問題1: 整備の経緯がセッション会話履歴にしか残らず、新セッションで再現困難**
→ 前日 `claude-governance` リポを新設したが、43リポへの「参照リンク」が無いため、新セッションの Claude（特に Web版）は本リポの存在を知らずに作業を始めてしまう。ガバナンス機能が半分しか発揮されていなかった。

**問題2: 監査機構が無く、ガバナンスドリフトを検知できない**
→ 「ルールを書く」と「ルールが守られている」は別。機械的監査が無いと、リポを足したり手動編集したりするうちに無自覚に逸脱する。今回の機械検査で実際に2件の見落としを検出できた（NASDAQの残骸ブランチ・shopping_product_search の進行中ブランチ）。

**問題3: 独自設計のリポを「違反」と扱う乱暴さ**
→ happiness-system は 2026-06-23 作成・現役で活発に使われている独自設計プロジェクト。機械監査が「不適合」と騒ぐと、価値ある独自設計が壊れる方向に圧力がかかる。EXCLUSIONS 機構で「意図的設計」を保護する。

**問題4: ガバナンスドリフトを継続検知できる仕組みが無い**
→ 監査を一度回すだけでは効果は限定的。再現可能スクリプトを本リポにコミットすることで、いつでも `python audits/audit_43repos.py` で現状確認できる。

### How to apply
- 新セッションの Claude は本リポを `BOOTSTRAP.md` 経由で読むだけでなく、各リポ末尾の「上位ガバナンスへの参照」セクションを通じて自然に辿れる。
- 監査の継続実行：`cd claude-governance/audits && python audit_43repos.py > _result.json && python audit_summary.py _result.json`
- 新リポ追加時：`audit_43repos.py` の `REPOS` リストに追加するだけで自動的に監査対象になる。
- 独自設計リポを保護したい場合：`EXCLUSIONS.md` に partial 除外エントリを追加（`scope: partial` + `exempt_dims`）。ユーザー承認後の追加が原則。

---

## 2026-06-24 — branch-cleanup スキルを全43リポへ一括展開＋ゴミブランチ実削除

### What
- 前日新設した `branch-cleanup` スキルを **全43リポへ展開**：各リポに `.claude/skills/branch-cleanup/SKILL.md`（手順全文）を配置し、各リポ `CLAUDE.md` の「ブランチ管理」セクション末尾に `<!-- BRANCH_CLEANUP_START/END -->` トリガーブロックを追記（CLAUDE.md 構成が異なる場合は末尾に新セクション）。
- 同時に **ゴミブランチ（`claude/*` 等）を実削除**。削除した9本：
  - deep-research ×1、career_dev ×1、enterprise-ai-strategy-advisor ×1、NASDAQ_backtest ×2、shopping_product_search ×4（うち固有コミット有りは取り込み後削除）
  - 固有コミットが有ったブランチは `git merge --no-ff` で main に取り込んでから削除（取りこぼしゼロ）。例：career_dev（大学講師リサーチmd）、NASDAQ_backtest（Bond ETF 2255 追記）、shopping_product_search（ルールD＋ホエイプロテインレポート在庫確認）。
- 削除はすべて **段階A（`git push origin --delete`）で成功**。REST直接（段階B）・Actions フォールバック（段階C）は不要だった＝Web版でも段階Aで十分削除可能であることを実証。

### Why
ユーザー報告：Web版 Claude Code がブランチ削除を「自分にはできない」と誤認し、ユーザー任せにする問題。スキルを各リポに置くだけでなく、**実際に溜まっていたゴミブランチを今回まとめて掃除**し、全リポを「default branch 1本のみ」のクリーンな状態に揃えた。今後は各リポの自主起動トリガーが機能して、ブランチが溜まる前に整理されるはず。

### How to apply / 検証
- 展開はローカル clone 経由（git push は credential manager 認証、未認証 REST API のレート制限とは別系統）。ブランチ一覧は `git ls-remote --heads`（APIコスト0）で取得し、レート枯渇を回避。
- 6サブエージェント並列（model: sonnet）＋パイロット1で実行。
- **独立検証**：サブエージェント報告を鵜呑みにせず、`git ls-remote --heads`（ブランチ数）＋ raw.githubusercontent（スキル実在）で全43リポを機械再検証。結果 **43/43 OK**（単一 default branch ＋ skill 実在）。
  - この再検証で shopping_product_search の残ブランチ1本（サブの報告漏れ）を検出・是正できた。**「報告でなく実在で検証」が効いた事例**。
- default branch 注意：`academic-research-agent_v1` のみ `master`、他42は `main`。

---

## 2026-06-23 — branch-cleanup スキル新設（Web版でも自走でmain集約・ブランチ削除）

### What
- 正典スキル `skills/branch-cleanup/SKILL.md` を新設（手順全文：作業ツリー確認 → 固有コミットの取り込み → 3段階削除 → ローカル整理 → main のみであることの最終確認）。
- `templates/repo-CLAUDE.md.template` に §9「ブランチ整理（自主起動）」をトリガー1ブロックのみ追記（`<!-- BRANCH_CLEANUP_START/END -->` マーカー方式）。上位ガバナンス参照は §10 へ繰り下げ。
- 削除手段は **3段階**：① `git push origin --delete` → ② REST API 直接 DELETE（`gh api` / token curl）→ ③ Actions ワークフロー フォールバック（使用後は削除してリポを汚さない）。

### Why
ユーザー報告：**Web版 Claude Code（claude.ai/code）でブランチ削除を依頼しても「利用できる機能が限られている／ユーザー自身で対応してください」と誤って回答するケースが頻発**。実際には Web版でも `git push origin --delete` / REST API / Actions 経由で削除は実行可能であることは確認済み。AI 側が「自分にはできない」と誤認しているのが原因。

これを防ぐため：
1. **手順を Skill 形式で各リポに置く** → Web版が「これは実行可能な手順だ」と認識しやすく、単なる md より起動率が高い。
2. **CLAUDE.md は肥大化させない** → 本体は SKILL.md に集約し、CLAUDE.md にはトリガー数行のみ。
3. **自主起動** → トリガーに「ユーザー指示」だけでなく「main 以外のブランチ残存の状態検知」を含め、Claude 自身が気づいて起動できるようにした。
4. SKILL.md と CLAUDE.md の双方に **「Web版でも実行可能。ユーザー任せにしない」** を明記し、誤認を直接打ち消す。

### How to apply
- 全43リポへ展開：各リポに `.claude/skills/branch-cleanup/SKILL.md`（手順全文）を配置し、各リポ `CLAUDE.md` にトリガーブロックを追記。
- 既存の SKILLS_RULES ブロックや章番号と衝突しないよう、各リポの実構成に合わせて挿入位置・節番号を調整（マーカー `<!-- BRANCH_CLEANUP_START/END -->` で将来の一括更新を可能にする）。
- self-contained 原則：SKILL.md は Web版が単独で読んで完結できるよう、全コマンドとフォールバック YAML を内包する。

---

## 2026-06-23 — settings.json テンプレを実機と再同期（model=opus[1m] 正典化・behavior flags 追加）

### What
- `global/settings.json.template` を実機 `~/.claude/settings.json` と再同期：
  - `model`: `claude-fable-5[1m]` → **`opus[1m]`**（ユーザー指示で opus を正典化）
  - `switchModelsOnFlag: true`、`effortLevel: "xhigh"` を**追加**（実機にあったがテンプレに欠落していた）
  - `_comment` を実態に合わせて改稿（`autoUpdatesChannel` は placeholder ではなく正典値である旨を明確化、deny 安全装置も正典の一部と明記）
- 本リポ `CLAUDE.md` §7 を改稿：起動モデル（settings.json の `model`）と役割分担方針（メイン指揮 vs Sonnet委譲）が**別レイヤー**であることを明示し、`opus[1m]` 正典との矛盾を解消。

### Why
新セッションで `claude-governance` の整備状態を点検した際、テンプレと実機 settings.json の間に乖離が見つかった：
1. テンプレの `model` が `claude-fable-5[1m]` のままで、実機の `opus[1m]` と不一致 → PC故障時にテンプレから復元すると意図しないモデルになる
2. `switchModelsOnFlag` / `effortLevel` がテンプレに無く、復元時に欠落する
3. CLAUDE.md §7「メイン=Fable 5」と settings.json `model=opus[1m]` が読み手に矛盾と映る

**「PC破損時に settings.json を正しく復元できる」ことがこのリポの中核的存在意義**であり、テンプレが実機からずれていると復元自体が壊れる。ユーザー判断で「`opus[1m]` を正典」と確定したため、テンプレ・CLAUDE.md の双方をこれに揃えた。

### How to apply
- PC復元時は本テンプレから `_personal_local_values` の3キー（enabledPlugins / extraKnownMarketplaces / mcpServers）以外を `~/.claude/settings.json` へ verbatim でコピーすればよい。
- 検証は `_personal_local_values` 以外の8キー（env / permissions / model / autoUpdatesChannel / skipDangerousModePermissionPrompt / agentPushNotifEnabled / switchModelsOnFlag / effortLevel）が実機と一致するかを `Compare-Object`/`ConvertFrom-Json` で確認する。
- ※ `global/CLAUDE.md`（実機グローバルの正典コピー）の §7 文面は今回未変更。Fable/Opus どちらをグローバル正典 §7 に書くかは別途判断（変更すると 3箇所同期義務が発生するため保留）。

---

## 2026-06-23 — リポジトリ新設・初期コミット

### What
- 新規リポ `KazuyaMurayama/claude-governance` を作成
- グローバル正典 3ファイルをコピー
  - `global/CLAUDE.md` ← `~/.claude/CLAUDE.md`
  - `global/deliverables-policy.md` ← `~/.claude/deliverables-policy.md`
  - `global/settings.json.template` ← `~/.claude/settings.json` から機密項目を除去してテンプレート化
- 43リポ共通テンプレート `templates/repo-CLAUDE.md.template` を新設
- `BOOTSTRAP.md` / `README.md` / `CLAUDE.md` / 本ファイルを新規作成

### Why
ユーザー（男座員也 / KazuyaMurayama）の問題提起：
> 「整備のルール自体は新セッションで再現したり呼び出ししたりするのが難しくなる恐れがあります」

これまでグローバル `~/.claude/CLAUDE.md` / `settings.json` / `deliverables-policy.md` がローカル単独保存だったため：
1. **PCが壊れたら失われる**（バックアップ不在）
2. **Web版 Claude Code（claude.ai/code）から `~/.claude/` を読めない** → グローバルルールが効かない別環境がある
3. **整備の経緯がセッション会話履歴にしか残らない** → 新セッションで再現不可

この3点を解決するため、上位ガバナンスを集約する独立リポを新設。

### How to apply
- 新セッション開始時、Claude は本リポを参照して `global/CLAUDE.md` を最初に読み込む（特に Web版）
- グローバルルール変更時は「3箇所同期」（`~/.claude/CLAUDE.md` ↔ 本リポ `global/CLAUDE.md` ↔ 関連各リポ `CLAUDE.md`）を守る
- 大きな整備をしたら `retros/RETRO_YYYYMMDD.md` を残す

---

## 過去の整備履歴（2026-06-23 以前、本リポ作成前の経緯を遡及記録）

### 2026-06-23 — 全43リポからhaikuモデル指定行を削除
**What**: 各リポ CLAUDE.md および グローバル CLAUDE.md から「- 軽量大量処理（grep集計・単純変換）: `model: "haiku"` 可。」の1行を削除。

**Why**: ユーザー指示「軽量大量処理（grep集計・単純変換）: `model: "haiku"` は、消しておいて。」。Fable 5 メイン + Sonnet 委譲の二段構造に統一し、haiku 並列処理路線を取らない方針に変更。

---

### 2026-06-22 — §7 モデル使い分けセクションを新設し、全43リポへ反映
**What**: グローバル CLAUDE.md および 43リポ CLAUDE.md に「モデル使い分け」セクションを追加。
```
- メイン: Claude Fable 5（claude-fable-5）を使用。
- 実行フェーズ: サブエージェントを model: "sonnet" で起動して委譲。
- ※難易度ベースの自動メイン切替は不可。Fable の自動切替は安全性ブロック時の Opus 4.8 フォールバックのみ。
```

**Why**: Fable 5 は難易度ベースで Opus 4.8 / Sonnet 4.6 へ自動切り替えしないモデル。工程別の使い分けはサブエージェント明示委譲で行う必要があるため、その運用ルールを明文化。

---

### 2026-06-22 — settings.json に rate limit 緩和の env ブロック追加
**What**: `~/.claude/settings.json` のトップレベルに以下を追加。
```json
"env": {
  "CLAUDE_CODE_MAX_TOOL_USE_CONCURRENCY": "3",
  "CLAUDE_CODE_MAX_RETRIES": "15",
  "API_TIMEOUT_MS": "900000"
}
```

**Why**: 「API Error: Server is temporarily limiting requests (not your usage limit) · Rate limited」エラーが連日発生。これは Anthropic の **acceleration limit**（バースト検知）であり、quotaではない。ユーザーの大量並列操作スタイル（43リポ一括変更等）が引き金。並列ツール呼び出しを3に絞ることでバースト解消を狙う。

**How to apply**: 1ファイルの settings.json を変更するだけで全プロジェクトに適用される（リポごとの設定は不要）。

---

### 2026-06-22 — Dependabot自動PR停止（MypageAppTest）
**What**: `MypageAppTest/.github/dependabot.yml` を削除し、既存のdependabot/* ブランチ10本を削除。

**Why**: 毎週dependabotが自動でPRを作成しブランチを増やしていた。MypageAppTestはプロトタイプ用途であり、依存自動更新の継続運用負荷が利益を上回ると判断。

---

### 2026-06-22 — ブランチに残存していたファイルを main へ統合
**What**: 5リポにわたって claude/* ブランチ上にしか存在しなかった11ファイルをmainにマージ、その後7本のブランチを削除。

対応リポ：NASDAQ_backtest, shopping_product_search, facility-search, deep-research, academic-research-agent_v1

**Why**: 「ブランチ作成は明示指示時のみ、作成した場合は完了前にmainマージ→削除」ルールに過去のセッションが従わずブランチを残したため、整合性を回復。

---

### 2026-06-21 — ファイル名命名規則 v2.0（YYYYMMDD サフィックス・ハイフンなし）
**What**: ファイル名の日付サフィックスを `_2026-06-03.md` から `_20260603.md` に変更。同日複数回更新時は `-v2`、`-v3` を追加（翌日リセット）。本文中の日付表記は `YYYY-MM-DD` のまま（ハイフンあり）。

**Why**: ユーザー要望。`_2026-06-03.md` 形式は「ハイフンが日付内に1つ、ハイフンが日付とTOPICの境界に1つ」で視覚的混乱がある。`_20260603.md` は境界が明確で、ファイル名ソートでも自然順序になる。本文表記とファイル名表記を別ルールにすることで、人間可読性とソート性を両立。

**How to apply**: グローバル CLAUDE.md §10b、43リポすべての CLAUDE.md、`deliverables-policy.md` に反映。新規ファイルは v2.0、既存ファイルはリネーム不要（ハイフン形式と新形式が共存可）。

**対象外**: README / CLAUDE.md / FILE_INDEX / tasks.md / CHANGELOG / LICENSE / SPEC / `CURRENT_*` / パイプライン自動生成。

---

### 2026-06-21 — README 5リポ整備
**What**: README が欠落していた5リポに README.md を作成（Doctor, FX-backtest, share-diary, AI_monetize_v2, navigator）。

**Why**: GitHub Repo一覧表示でREADMEが無いと用途が不明、検索性も落ちる。

---

### 2026-06-21 — 「VSCode版 vs Web版」二環境設計の確立
**What**: グローバル CLAUDE.md §0 に「CLAUDE.md 階層と環境別の振る舞い」セクションを追加。各リポの CLAUDE.md は **単独完結** が原則で、グローバルルールも必要なら各リポに重複記載する。

**Why**: ユーザーから「VS Codeとウェブ版でグローバルを参照するかどうかが異なる。ウェブ版はリポジトリだけを参照してプロジェクトが始まるケースも多数ある。よって、グローバルとリポジトリの一つ一つがそれぞれ完結している必要がある」との指摘。

**How to apply**: 43リポ全てのCLAUDE.mdを「Web版だけでも動作する」自己完結形式に書き換え。重複は「ミス」ではなく「設計要件」と位置付ける。

---


### 2026-06-01 — SKILLS_RULES v2.1 → v2.2: ブランチ管理ルール強制（全42リポ）
**What**: 全42リポの CLAUDE.md にブランチ管理の強制ルールを追加し、SKILLS_RULES を v2.2 に更新。
- Pattern A（27リポ）: 既存の `Git・ブランチ管理` セクション見出しを「絶対厳守」に変更し、強制ルール4項目を追記
- Pattern B（15リポ）: SKILLS_RULES ブロック内に `### ブランチ管理（絶対厳守）` セクションを新規挿入

**Why**: Claude Code Web版が自動でブランチを生成し、ファイルをブランチに置いたまま回答完了するケースが発生（2026-06-22 のブランチ残存ファイル統合はこのルール不在が原因）。「完了 = mainにマージ済み＆push済み」を全リポで明示的に強制するため。

**How to apply**: 各リポの CLAUDE.md に `デフォルト: mainへ直接コミット` / `ブランチ作成した場合は必ずマージ→削除→push完了で完了` / `ブランチに置いたまま完了禁止` の3ルールが記述されていることを確認。

---

### 2026-05-29 — SKILLS_RULES v2.0 → v2.1: スキルトリガー拡張（全42リポ）
**What**: スキルが起動しない問題を修正。全42リポの SKILLS_RULES を v2.1 に更新。
1. sp-verification-before-completion: 「コミット前のみ」→「コミット前またはQC・レビューフェーズに入る時」に条件拡張
2. analysis-qa-checklist トリガー新規追加（A/C/D型リポ対象）
3. data-quality-audit トリガー新規追加（A/D型リポ対象）
4. peer-review-template トリガー新規追加（C型リポ対象）

**Why**: NASDAQセッションで「データ分析・ファクトの見直し・レポーティングの品質チェック・レビュー」を依頼した際、スキルが1件も起動しなかった。原因は sp-verification のトリガー条件が「コミット前」限定でQC・レビューシーン非対応だったこと、analysis-qa-checklist 等が全リポに未配置だったこと。リポタイプ別分類（A=リサーチ, B=アプリ, C=コンサルティング, D=データ分析）で必要なスキルを振り分けて追加。

**How to apply**: QC・レビューを依頼した際に sp-verification-before-completion と analysis-qa-checklist が両方起動することを確認（NASDAQセッション等）。

---

### 2026-05-29 — Desktop禁止ルール追加 + 14リポのボイラープレート削減
**What**:
1. グローバル CLAUDE.md と全42リポ CLAUDE.md に「`C:\Users\user\Desktop` への無断ファイル生成・保存禁止」ルールを追加
2. 長文CLAUDE.mdを持つ14リポのSKILLS_RULES外の重複記述を削減（平均182行→99行）

**Why**: VSCodeセッション中にClaudeがデスクトップへ一時ファイル（実行ログ `g14_run_log.txt`、コミットメッセージ用 `.commit_msg_tmp.txt` 等）を生成するケースが複数発生。GitHubリポジトリを単一の真実とする方針に反するため禁止ルールを全リポへ一括展開。ボイラープレート削減は可読性向上のため併せて実施。

**How to apply**: 成果物・スクリプト類はすべて対象GitHubリポジトリ内に保存。デバッグ用捨てスクリプトは `C:\Users\user\AppData\Local\Temp\` へ。コミットメッセージ複数行は PowerShell here-string（`@'...'@`）変数経由で渡す（ファイル経由禁止）。

---
## 今後の更新時のルール

1. 新しいエントリは **上に追加**（最新が上）
2. 各エントリは `## YYYY-MM-DD — 1行サマリ` で始める
3. `### What` `### Why` `### How to apply` の3節構成を推奨
4. **WHY を最重視**。WHAT は git log で追えるが WHY は失われる
