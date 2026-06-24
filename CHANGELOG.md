# CHANGELOG — claude-governance 変更履歴

作成日: 2026-06-23
最終更新日: 2026-06-23

> 変更の **WHAT** より **WHY** を残すことを優先する。何を変えたかは git log で追えるが、なぜそうしたかは記録しないと失われる。

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
