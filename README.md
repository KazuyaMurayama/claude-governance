# claude-governance — Claude Code 運用ガバナンスの正典

KazuyaMurayama（男座員也 / Kazuya Oza）が運用する **43+リポジトリ全体** に対する Claude Code（VSCode拡張版 / Web版 claude.ai）の運用ルール・設定・テンプレート・変更履歴を集約する正典リポジトリ。

> ⚠️ このリポはコードを生むためのものではない。**「Claude Code をどう使うかの上位ルール」を、PC外・セッション外に永続化する**ためのものである。

---

## なぜ存在するのか

これまで以下が **ローカル単独保存** だった：

| 失われると困るもの | 物理的な場所 |
|---|---|
| グローバル運用ルール | `C:\Users\user\.claude\CLAUDE.md` |
| 設定（permissions / env / model） | `C:\Users\user\.claude\settings.json` |
| 成果物報告ルール詳細 | `C:\Users\user\.claude\deliverables-policy.md` |
| 整備の経緯・意図 | セッション会話履歴のみ |

このため:
1. **PCが壊れたら全部消える**
2. **Web版 Claude Code（claude.ai/code）** からは `~/.claude/` が読めない → グローバルルールが効かない
3. **新セッションで再現したい** とき、なぜそうしたのかが辿れない

このリポはこれら3つの問題を解決する。

---

## 構成

```
claude-governance/
├── README.md                              # このファイル
├── CLAUDE.md                              # 本リポ自身の運用ルール（Claude Codeへの指示）
├── BOOTSTRAP.md                           # 新セッション開始時にClaudeに最初に読ませる
├── CHANGELOG.md                           # 全変更履歴（why中心）
├── global/
│   ├── CLAUDE.md                          # ~/.claude/CLAUDE.md の正典コピー
│   ├── settings.json.template             # ~/.claude/settings.json のテンプレート
│   └── deliverables-policy.md             # ~/.claude/deliverables-policy.md の正典コピー
├── templates/
│   ├── repo-CLAUDE.md.template            # 各リポの CLAUDE.md 共通テンプレ
│   └── governance-link-block.md           # 「上位ガバナンスへの参照」ブロックの正典（監査の陳腐化検知が参照）
├── audits/
│   ├── audit_43repos.py                   # 全リポ機械監査（12+軸。リポ一覧は API から自動発見・private 含む）
│   ├── audit_summary.py                   # 監査結果→ダッシュボード（VERDICT付き・private名マスク）
│   ├── audit_local_sync.py                # 実機 ~/.claude/ ↔ 本リポ正典の同期監査（ローカル専用）
│   ├── add_governance_link.py             # 各リポへの参照ブロック追加／--update で正典へ一括更新
│   ├── EXCLUSIONS.md                      # 意図的独自設計リポの部分除外リスト
│   ├── AUDIT_LATEST.md                    # 月次自動監査の最新ダッシュボード（Actions が自動更新）
│   └── AUDIT_YYYYMMDD*.md/json            # 手動監査のスナップショット
├── .github/workflows/
│   └── governance-audit.yml               # 月次自動監査（毎月1日 05:00 JST・不適合時 Issue 起票）
└── retros/
    └── RETRO_YYYYMMDD.md                  # 整備セッション毎のレトロスペクティブ
```

---

## 監査の実行方法

```bash
cd claude-governance
# 全リポ監査（要トークン: git credential helper か GH_TOKEN。無認証は fail loud で中断）
PYTHONIOENCODING=utf-8 python audits/audit_43repos.py > /tmp/result.json
python audits/audit_summary.py /tmp/result.json            # private名マスク（公開用）
python audits/audit_summary.py /tmp/result.json --no-mask  # 実名（ローカル調査用）
# 実機 ~/.claude/ とリポ正典の同期チェック（VSCode環境のみ）
python audits/audit_local_sync.py
```

- 月次自動監査は GitHub Actions（`governance-audit.yml`）が実行。**private リポも監査するには fine-grained PAT を secret `GOVERNANCE_PAT` に登録**（Contents/Metadata: Read、全リポ）。未登録時は private リポが「判定不可(?)」として FAIL 表示される。
- 新リポは**自動的に監査対象**になる（ハードコードリスト廃止済み）。除外は `audits/EXCLUSIONS.md` へ（ユーザー承認必須）。
- ⚠ 本リポは public。private リポの**実名**を EXCLUSIONS.md やコミットする監査レポートに書かないこと（ダッシュボードは自動でマスクされる）。

---

## 新セッション開始時の使い方

### VSCode版 Claude Code（`~/.claude/` を読める環境）
1. グローバル `~/.claude/CLAUDE.md` がそのまま有効。
2. 本リポを定期的に確認し、グローバルとの差分があれば同期する。

### Web版 Claude Code（claude.ai/code、`~/.claude/` を読めない環境）
1. 最初にこのリポを開く: https://github.com/KazuyaMurayama/claude-governance
2. `BOOTSTRAP.md` の指示に従う（このリポの `global/CLAUDE.md` を最初に読ませる）
3. その上で対象リポの作業を開始する

---

## 同期ポリシー

| 変更元 | 同期先 | 責任 |
|---|---|---|
| `~/.claude/CLAUDE.md` 更新 | このリポの `global/CLAUDE.md` | 更新者（このセッションのClaudeまたは人間） |
| このリポの `templates/repo-CLAUDE.md.template` 更新 | 関連する全リポの `CLAUDE.md` | 更新者 |
| 全リポ共通ルールの変更（例：命名規則v2.0） | 全43リポ + グローバル + このリポ全て | 更新セッションのClaude |

**原則**: 「3箇所同期問題」を意識する。グローバル / このリポ / 各リポ の3箇所で乖離が出たら、このリポを正典として復元する。

---

## 関連リポジトリ

- [KazuyaMurayama/claude-code-prompt](https://github.com/KazuyaMurayama/claude-code-prompt) — Claude Code 用プロンプトテンプレート集（本リポとは関心が異なる：プロンプト集 vs 運用ルール）
- [KazuyaMurayama/ai-knowledge-base](https://github.com/KazuyaMurayama/ai-knowledge-base) — AI が管理する知識ベース（RAG 対応）

---

## 開発者情報

**男座員也（Kazuya Oza / おざ かずや）**

| | |
|---|---|
| GitHub | [@KazuyaMurayama](https://github.com/KazuyaMurayama) |
| Email | kazuya.murayama.21@gmail.com |

---

## ライセンス

© 2026 男座員也（Kazuya Oza）. All rights reserved.
