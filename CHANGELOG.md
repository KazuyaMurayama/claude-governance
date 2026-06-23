# CHANGELOG — claude-governance 変更履歴

作成日: 2026-06-23
最終更新日: 2026-06-23

> 変更の **WHAT** より **WHY** を残すことを優先する。何を変えたかは git log で追えるが、なぜそうしたかは記録しないと失われる。

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

## 今後の更新時のルール

1. 新しいエントリは **上に追加**（最新が上）
2. 各エントリは `## YYYY-MM-DD — 1行サマリ` で始める
3. `### What` `### Why` `### How to apply` の3節構成を推奨
4. **WHY を最重視**。WHAT は git log で追えるが WHY は失われる
