# claude-governance — Claude Code 運用ルール

KazuyaMurayama（男座員也 / Kazuya Oza）が運用する43+リポジトリ全体に対する Claude Code の上位ガバナンス正典リポジトリ。**このリポはコードを生むためのものではなく、運用ルール・設定・変更履歴を永続化するためのもの**。

> **本ファイルは VSCode版 / Web版 Claude Code（claude.ai）の両方で本リポジトリの単独完結ガイド**。
> Web版はグローバル `~/.claude/CLAUDE.md` を参照しない前提で、本リポの運用に必要な全ルールをここに集約。

---

## 0. このリポの特殊性
本リポは「Claude Code の運用ルールを管理するメタリポ」である。**通常のリポと違い、ここでの変更は他の42リポへの同期義務を伴うことがある**。

### 変更の影響範囲を必ず判定する
| 変更内容 | 同期義務 |
|---|---|
| `global/CLAUDE.md` の変更 | `~/.claude/CLAUDE.md` を更新し、必要なら全43リポ `CLAUDE.md` へも反映 |
| `global/settings.json.template` の変更 | `~/.claude/settings.json` を更新（個人情報項目は手動で再設定） |
| `templates/repo-CLAUDE.md.template` の変更 | 影響を受ける各リポの `CLAUDE.md` を一括更新 |
| `CHANGELOG.md` の変更 | 同期義務なし（本リポ単独） |
| `BOOTSTRAP.md` / `README.md` の変更 | 同期義務なし（本リポ単独） |

---

## 1. セッション開始時の参照順序
1. `BOOTSTRAP.md` — 新セッション開始時の手順（特にWeb版から開いた場合）
2. `CHANGELOG.md` — 直近の変更履歴
3. このCLAUDE.md — ルール入口

---

## 2. 開発者情報・命名ルール

| 種別 | 表記 | 用途 |
|---|---|---|
| **システム識別子（変更不可）** | `KazuyaMurayama` | GitHub ユーザー名 / URL / `@KazuyaMurayama` |
| **システム識別子（変更不可）** | `kazuya.murayama.21@gmail.com` | git `user.email` / 連絡先 |
| **表記名（人間として記載する場合）** | **男座員也（Kazuya Oza / おざ かずや）** | ドキュメント本文の著者名 / コミット message 中の自己言及 |

---

## 3. ツール実行・Git・ファイル保存
- 確認不要・即実行（事前確認文を出力しない）
- 例外（事前確認必須）: main への `git push --force`、`gh repo delete`、**および全43リポへの一括反映**
- **ブランチ管理**: mainへ直接コミット。ブランチ作成禁止
- **ファイル保存**: 本リポ内のみ。`C:\Users\user\Desktop` への出力禁止
- **機密情報**: settings.json の `mcpServers` / `enabledPlugins` 等の個人固有値はテンプレ化して保存し、実値はコミットしない

### 一括反映時の注意
全43リポへの一括反映は **影響が大きい**。以下の手順を守る：
1. 変更内容を CHANGELOG.md に **先に記録**
2. ユーザーに「全リポへ反映してよいか」確認
3. 反映実行
4. 完了後、reトロを `retros/RETRO_YYYYMMDD.md` に残す

---

## 4. 成果物報告ルール

| 成果物 | 説明 | リンク |
|---|---|---|
| file.md | 1行説明 | [開く](https://github.com/KazuyaMurayama/claude-governance/blob/main/path/to/file.md) |

- Markdownリンク `[表示名](URL)` 形式必須 / `/blob/main/<実パス>` 形式
- 報告前にURL存在確認
- push完了後のみURL生成

---

## 5. このリポでやってはいけないこと
- 通常のソフトウェア開発タスク（コード書き、デバッグ等）→ 別リポで実施
- 個人固有の機密値（API token、MCP server PATH、enabledPlugins 個別値）を `global/settings.json.template` にコミット → テンプレ化して placeholder にする
- 「整備セッションが終わったのに CHANGELOG を更新しない」→ **CHANGELOG が無いと本リポの存在意義が失われる**

---

## 6. ドキュメント命名・日付ルール（v2.0 / 2026-06-03 改訂）

### ファイル名
- `<TOPIC>_YYYYMMDD.md` 形式（**サフィックス・ハイフンなし**）
- **同日中の追加更新**: `-v2`、`-v3` を追加
- **翌日1回目**: v サフィックスをリセット

### 表記の区別
- **ファイル名**: ハイフン**なし** `YYYYMMDD`
- **本文中の日付表記**: ハイフン**あり** `YYYY-MM-DD`

### 対象外（日付サフィックスを入れない）
- README / CLAUDE.md / FILE_INDEX / tasks.md / CHANGELOG / LICENSE / SPEC.md
- `BOOTSTRAP.md`（本リポ固有・常に最新）
- `global/*.md`（正典コピーであり、ファイル名固定）
- `templates/*`（テンプレ）

### 本リポで日付サフィックスを使うファイル
- `retros/RETRO_YYYYMMDD.md` — 整備セッションのレトロ

---

## 7. モデル使い分け
- メイン: **Claude Fable 5（`claude-fable-5`）** を使用。
- 実行フェーズ（定型実装・ファイル編集・テスト実行）: サブエージェントを `model: "sonnet"` で起動して委譲。
- ※難易度ベースの自動メイン切替は不可。Fable の自動切替は安全性ブロック時の Opus 4.8 フォールバックのみ。

---

## 8. 上位ガバナンスとの優先順位
このリポ自体が上位ガバナンスである。よって本ファイル `CLAUDE.md` は本リポ作業の最終権威。ただしユーザーの直接指示はこれを上書きする。
