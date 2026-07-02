# BOOTSTRAP — 新セッション開始時のブートストラップ

作成日: 2026-06-23
最終更新日: 2026-07-02

新しい Claude Code セッションを開始した際、このリポを参照する Claude が **最初に読むべき手順**。

---

## 1. このリポの目的を理解する

`README.md` を読む。要点：

- 43+ リポ全体に対する Claude Code の運用ルール正典である
- グローバル `~/.claude/CLAUDE.md` / `settings.json` / `deliverables-policy.md` のバックアップ兼正典コピーがある
- Web版 Claude Code（`~/.claude/` を読めない環境）で参照するための入口である

---

## 2. 環境を判定する

### あなたが VSCode 拡張版 Claude Code の場合
- `~/.claude/CLAUDE.md` が既に読み込まれているはず → そちらを優先
- 本リポは「正典のバックアップ」「変更履歴の参照先」として扱う
- 本リポと `~/.claude/` の差分があれば、ユーザーに確認してから同期する

### あなたが Web版 Claude Code（claude.ai/code）の場合
- `~/.claude/CLAUDE.md` は読めない
- 本リポの `global/CLAUDE.md` を **最初に読み込む** → これがグローバル相当のルール
- 本リポの `global/deliverables-policy.md` も合わせて読む
- その後、作業対象リポの `CLAUDE.md` を読む（リポ固有ルールが上書きする）

---

## 3. 作業を開始する前のチェックリスト

- [ ] `global/CLAUDE.md` のルールを把握した
- [ ] 命名規則 v2.0（`<TOPIC>_YYYYMMDD.md`、同日更新は `-v2/-v3`）を把握した
- [ ] 成果物報告ルール（3列表 / Markdownリンク / URL検証）を把握した
- [ ] ブランチ管理（デフォルトmain直接コミット、ブランチ作成時は完了前にマージ→削除）を把握した
- [ ] ファイル保存先（`C:\Users\user\Desktop` 禁止、リポ内のみ）を把握した
- [ ] 開発者表記（システム識別子は `KazuyaMurayama`、表記名は **男座員也 / Kazuya Oza**）を把握した
- [ ] モデル使い分け（メイン Claude Fable 5、実行は Sonnet サブエージェント）を把握した

---

## 4. 全リポを横断する作業をする場合

### グローバルルール変更時の同期手順（3箇所同期）
1. `global/CLAUDE.md` を更新（本リポ）
2. `~/.claude/CLAUDE.md` を更新（VSCode版で実機）
3. 関連する各リポの `CLAUDE.md` を一括更新（43リポすべて、または対象部分集合）
4. `CHANGELOG.md` に何をなぜ変更したかを記録
5. 必要であれば `retros/RETRO_YYYYMMDD.md` でレトロを残す

### 各リポへの一括反映時の注意
- 各リポは「self-contained」が原則。リポ間でルールに差分が出ても、各リポ単独でWeb版から動作可能であること
- リポ固有ルールが上位ガバナンスに勝つ（リポ側で「mainブランチ運用のみ」とあれば、グローバルの「mainへ直接コミット」と整合）

---

## 4b. 適合状況を確認したい場合（監査機構）

- `audits/AUDIT_LATEST.md` → 月次自動監査の最新結果（GitHub Actions が毎月1日に更新・不適合時は Issue 起票）
- 手動監査: `PYTHONIOENCODING=utf-8 python audits/audit_43repos.py > /tmp/r.json && python audits/audit_summary.py /tmp/r.json`
  - リポ一覧は API から自動発見（新リポ追加時のリスト更新は不要）
  - 意図的独自設計リポの除外は `audits/EXCLUSIONS.md`（追加はユーザー承認必須）
- 実機 `~/.claude/` とリポ正典の同期チェック: `python audits/audit_local_sync.py`（VSCode環境のみ）

---

## 5. 過去の経緯を辿りたい場合

- `CHANGELOG.md` を読む → いつ何をなぜ変更したか
- `retros/RETRO_YYYYMMDD.md` を読む → 整備セッションのレトロスペクティブ

---

## 6. このリポ自体を更新する場合

`CLAUDE.md`（本リポ自身の運用ルール）を読んでから着手する。

---

## 7. 上位ガバナンスとの優先順位

```
1. ユーザーの直接指示（最優先）
2. 作業対象リポの CLAUDE.md（リポ固有ルール）
3. 本リポ global/CLAUDE.md（グローバル相当）
4. デフォルトのClaude Code挙動
```

リポ固有ルールが上位ガバナンスに勝つ。グローバル変更時は、各リポへの反映も検討すること。
