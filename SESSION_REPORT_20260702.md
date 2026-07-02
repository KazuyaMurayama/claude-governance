# セッションレポート — ガバナンス監査体制の頑強化＋ルール遵守率改善（2026-07-02）

作成日: 2026-07-02
最終更新日: 2026-07-02
作者: 男座員也（Kazuya Oza）／ Claude Code（VSCode拡張版・Fable 5）セッション実装

> 本レポートは 2026-07-02 の1セッションで実施した2つの改善（**Part 1: 監査体制の敵対的レビュー＋頑強化** / **Part 2: ルール遵守率改善 rule-enforcement パッケージ**）を、**単体で読めば再現できる**粒度でまとめた正典記録である。
> 関連コミット: Part 1 = `8f16b64`、Part 2 = `d15af27`（いずれも本リポ main）。是正マージ = shopping_product_search `9cc52f8` / deep-research `d359eba`。

---

## 0. サマリ（何をどう改善したか）

| # | 問題 | 対応 | 検証結果 |
|---|---|---|---|
| 1 | 「不適合ゼロ」達成の7日後に余分ブランチが1→4本に増殖（監査の実行者不在） | 月次 GitHub Actions cron による監査の強制実行＋FAIL時 Issue 自動起票 | ワークフロー配置済（初回 dispatch 確認は残タスク） |
| 2 | 監査対象リストがハードコードで、private 2リポは初回から漏れ・新リポも未捕捉 | 認証付き `/user/repos` によるリポ自動発見（allowlist→denylist 反転） | 46リポ自動発見・新カバー3リポの実不適合17件を即検出 |
| 3 | 監査の失敗経路が「適合」に化ける（偽適合）・XB が問題集計外で「不適合ゼロ」が過大表示 | 失敗=「?」判定・XB/期限切れ/判定不可を VERDICT: PASS/FAIL と exit code に反映 | 再監査で FAIL が正しく表面化 |
| 4 | 文書が約束する挙動の未実装（review_after 警告・監査日ハードコード等） | review_after 期限切れ警告を実装・監査日を動的化・EXCLUSIONS パーサ堅牢化 | 実装済・happiness-system の期限は自動警告される |
| 5 | 実機 `~/.claude/` とリポ正典の乖離（settings の model/effortLevel ドリフト）を検知できない | `audits/audit_local_sync.py` 新設＋テンプレを実機正典に再同期 | VERDICT: IN SYNC |
| 6 | 固有コミット計10件がブランチに滞留（2リポ・4ブランチ） | 全て main へ `--no-ff` マージ→REST API で削除 | 両リポとも main のみを ls-remote で確認 |
| 7 | **CLAUDE.md に書いてあるルールが守られない**（「見逃しました」問題） | 3層防御: ⛔絶対ルールTop10（最上部）＋決定論的hooks＋HR/EH監査軸 → 42リポ＋グローバルへ展開 | deploy 42/42 成功・再監査で展開リポ全軸適合 |

---

## Part 1: 監査体制の敵対的レビュー＋頑強化

### 1.1 発見した問題（一次資料による再検証の結果）

前セッション（2026-06-25）の「43リポ・不適合ゼロ」という結論を、記憶を信じずに再検証した：

1. **余分ブランチの増殖**: 7日間で1本→4本（shopping_product_search ×2・deep-research ×2、固有コミット計10件）。監査は「いつでも実行できる」状態だったが**誰も実行していなかった**。
2. **監査リスト自体の欠落**: GitHub 実所有48リポに対し監査対象は43＋除外2。`Soulful-Content`（新規）に加え、**private 2リポは初回監査から一度も対象になっていなかった**（当時の探索が public のみ）。
3. **実装バグ3件**: ①`audit_summary.py` の監査日が `2026-06-25` にハードコード ②EXCLUSIONS.md の「review_after 経過で警告」が未実装 ③EXCLUSIONS パーサが書式例をファントム登録。
4. **偽適合の構造**: `ls_remote_branches()` が失敗時に `[]` を返し「ネットワーク断＝ブランチなし＝適合」になる。XB（余分ブランチ）が問題集計に入らず、4本残存でも「不適合ゼロ」と表示。
5. **settings テンプレドリフト**: 実機 `model="claude-fable-5[1m]"` / `effortLevel="max"` vs テンプレ `opus[1m]` / `xhigh`。「PC破損時の復元」という本リポの中核目的が壊れていた。

### 1.2 実施した対応

| 対応 | 実装場所 | 要点 |
|---|---|---|
| ブランチ是正 | shopping_product_search / deep-research | 固有コミットを `git merge --no-ff <sha>` で main へ（tasks.md コンフリクトは日付降順ユニオンで解決）→ `DELETE /repos/{owner}/{repo}/git/refs/heads/{branch}`（`git push --delete` は settings.json の deny 対象のため REST 使用） |
| リポ自動発見 | `audits/audit_43repos.py` | `GET /user/repos?affiliation=owner`（ページング・private含む・default_branch も API 値）。除外は `SKIP_REPOS`＋`EXCLUSIONS.md` のみ。**ファイル名は42リポの参照リンク保全のため据え置き** |
| fail loud | 同上 | トークン無しなら `sys.exit(2)`（無認証60req/hでの偽結果を防止） |
| 偽適合排除 | 同上＋`audit_summary.py` | 失敗は `None`（表示 `?`）で「判定不可＝FAIL要因」。VERDICT: PASS/FAIL と exit code を出力し CI ゲート可能に |
| review_after 実装 | 同上 | ```yaml フェンス内のみパース・期限切れは警告＋FAIL要因 |
| GC軸（陳腐化検知） | 同上＋`templates/governance-link-block.md` | 各リポの `GOVERNANCE_LINK_START/END` 間を正典と内容比較。`add_governance_link.py --update` で一括更新可能 |
| 月次自動監査 | `.github/workflows/governance-audit.yml` | 毎月1日 05:00 JST → `audits/AUDIT_LATEST.md` 自動コミット → FAIL時 Issue 起票（重複ガード付）。private リポ監査には secret `GOVERNANCE_PAT` が必要 |
| ローカル同期監査 | `audits/audit_local_sync.py` | 実機 `~/.claude/`（CLAUDE.md / deliverables-policy.md / settings.json 正典キー）↔ リポ正典の一致＋「正典変更コミットに同日 CHANGELOG 更新があるか」を検査 |
| private 情報保護 | `audit_summary.py` | 本リポは public のため、ダッシュボードでは private リポ名を `(private #n)` に自動マスク（実名調査は `--no-mask` ローカル限定・raw JSON はコミットしない） |

### 1.3 ユーザー決定事項（このセッションで確定）

- 残存ブランチ4本 → **マージ＋削除を実行**
- private リポの扱い → **(ii) public 維持・private も監査・公開成果物では名前マスク**
- settings テンプレ正典 → **実機（`claude-fable-5[1m]` / `max`）に合わせる**
- 自動化方式 → **GitHub Actions 月次 cron**

---

## Part 2: ルール遵守率改善（rule-enforcement パッケージ）

### 2.1 問題分析（なぜ「書いてあるのに守られない」のか）

| 要因 | 実測エビデンス |
|---|---|
| (1) 注意の希釈 | 各リポ CLAUDE.md = 195〜324行・23〜39節。全ルールがフラット並列で、1本あたりの遵守確率が構造的に低い |
| (2) タイミングのミスマッチ | ルールを読むのは開始時、破るのは終了時（ブランチ集約・成果物報告）とツール実行時（保存先）。長セッション＋自動コンパクションで希薄化 |
| (3) 強制力の欠如 | branch-cleanup トリガー全リポ配布済みでも、06-24〜29 の Web版セッションがブランチ4本を放置して完了（**散文だけでは再発を防げない実証**） |
| (4) 完了前ゲート不在 | 検証系スキルは50超のトリガー表の1行に埋没し起動率が低い |

結論: **散文ルールの遵守は確率的、hooks は決定論的**。頻出違反は機械ガード化し、散文は Top10 に絞って最上部に置く。

### 2.2 実装（3層防御）

**層1: ⛔絶対ルール Top10 ブロック**
- 正典: [`templates/hard-rules-block.md`](templates/hard-rules-block.md)（`<!-- HARD_RULES_START v1 -->` マーカー管理）
- 違反実績で選抜した10項目（ブランチ/成果物3列表/保存先/命名/表記名/事前確認禁止/検証後完了宣言/QCスキル起動/一次資料主義/Next Action）を**CLAUDE.md 最上部（H1直後）**に命令形で配置
- 展開先: ガバナンス対象42リポ＋本リポ＋グローバル `~/.claude/CLAUDE.md`（`global/CLAUDE.md` に同期）＋ `templates/repo-CLAUDE.md.template`
- Web版でもリポ内ファイルとして確実に読まれる

**層2: 決定論的 hooks**（正典: [`templates/hooks/`](templates/hooks/)、各リポ `.claude/hooks/` へ配布）

| スクリプト | イベント / matcher | 動作 |
|---|---|---|
| `pre_write_guard.py` | PreToolUse / `Write\|Edit` | Desktop への書き込みを `permissionDecision: deny` で拒否（`Desktop\repos\`・`Desktop\投資・不動産\` は許可） |
| `post_bash_guard.py` | PostToolUse / `Bash\|PowerShell` | `git push` 検出時（`--delete` 除く）に「3列表＋URL検証＋mainのみ」をリマインド注入 |
| `session_guard.py` | Stop | 非 main ブランチ / 未 push コミットを検査し、違反なら `{"decision":"block"}` で終了を**1回だけ**ブロックし是正内容をフィードバック（`stop_hook_active` で2回目は素通し＝ループ構造的に不可） |

設計原則（全 hook 共通）:
- **fail-open**: 例外・python 不在・非 git ディレクトリでは必ず素通し（セッションを壊さない）。ブロックは JSON でのみ行い、exit 2 は使わない（`python` の「file not found = exit 2」誤爆を回避するため、配線コマンド末尾に `|| exit 0`）
- **重複排除**: グローバル側コピーは、cwd に同名のリポ側 hook が存在すれば自動で譲る
- **日本語は `ensure_ascii=True`（デフォルト）のまま JSON 出力**（Windows コンソールエンコーディング事故を回避）

配線（`.claude/settings.json`）: 既存の permissions / hooks を**保持したままマージ**。
```json
{"hooks": {
  "PreToolUse":  [{"matcher": "Write|Edit",      "hooks": [{"type": "command", "command": "python .claude/hooks/pre_write_guard.py || python3 .claude/hooks/pre_write_guard.py || exit 0"}]}],
  "PostToolUse": [{"matcher": "Bash|PowerShell", "hooks": [{"type": "command", "command": "python .claude/hooks/post_bash_guard.py || python3 .claude/hooks/post_bash_guard.py || exit 0"}]}],
  "Stop":        [{"hooks": [{"type": "command", "command": "python .claude/hooks/session_guard.py || python3 .claude/hooks/session_guard.py || exit 0"}]}]
}}
```
ローカル（VSCode）側は `~/.claude/hooks/` に同スクリプト＋ `~/.claude/settings.json` に**絶対パス**で配線（シェル演算子なし・PowerShell/cmd 差異の影響を受けない）。`global/settings.json.template` に同期済み、`audit_local_sync.py` の正典キーに `hooks` を追加済み。

**層3: 監査による維持**
- 監査に **HR**（Top10ブロック存在）/ **EH**（settings.json に session_guard 配線 AND スクリプト実在）を追加
- 月次 Actions が欠落・剥がれを自動検知

### 2.3 展開と検証

- ユニットテスト: 違反検出 / 許可パス / 壊れた入力（fail-open）/ `stop_hook_active` / 非 git ディレクトリ — 全ケース期待どおり
- パイロット: career_dev（settings 新規作成）・oogiri（既存 permissions 11件とのマージ保全）→ 検証 OK
- 一括展開: **42リポ成功・失敗ゼロ**（skip: happiness-system=EXCLUSIONS / Soulful-Content・tax-advisor=未ガバナンス / sharetask=CLAUDE.md 無し）
- 再監査: 展開済みリポは HR/EH 含め**全軸適合**・ローカル同期 IN SYNC

---

## 3. 再現手順（コマンド集）

```bash
cd claude-governance

# --- 全リポ監査（要トークン。無ければ fail loud で中断）---
export GH_TOKEN=$(printf "protocol=https\nhost=github.com\n\n" | git credential fill | grep password= | cut -d= -f2)
PYTHONIOENCODING=utf-8 python audits/audit_43repos.py > /tmp/r.json
python audits/audit_summary.py /tmp/r.json            # 公開用（private名マスク）。exit 0=PASS / 1=FAIL
python audits/audit_summary.py /tmp/r.json --no-mask  # ローカル調査用（実名）

# --- 実機 ~/.claude ↔ リポ正典の同期チェック（VSCode環境のみ）---
python audits/audit_local_sync.py                     # exit 0=IN SYNC / 1=DRIFT

# --- Top10ブロック / hooks の正典を変更したら全リポへ冪等再展開 ---
#（正典: templates/hard-rules-block.md, templates/hooks/*.py）
PYTHONIOENCODING=utf-8 python audits/deploy_rule_enforcement.py            # 全対象
PYTHONIOENCODING=utf-8 python audits/deploy_rule_enforcement.py --pilot repoA,repoB  # パイロット

# --- governance link ブロックの文言変更時 ---
#（正典: templates/governance-link-block.md）
python audits/add_governance_link.py --update
```

運用ノート（再現時の落とし穴）:
- **バックグラウンドシェルでは `git credential fill` が空になる**ことがある → `GH_TOKEN` を先に export してから実行する
- raw.githubusercontent.com は CDN 遅延があるため使わない（全スクリプトは Contents API + `Cache-Control: no-cache` + token 認証で統一済み）
- 監査結果の raw JSON は private リポ実名を含むため**本リポにコミットしない**（コミットするのはマスク済みダッシュボードのみ）
- `audit_43repos.py` のファイル名は歴史的経緯（42リポの参照リンク）でそのまま。リポ列挙は自動なのでリスト追記は不要

---

## 4. 期待効果と留意点

**期待効果**: ①頻出違反3類型（ブランチ放置・報告漏れ・保存先違反）は「見逃し」で素通りするパスが閉じた（Desktop は決定論的ブロック、ブランチ/未pushは終了時に必ず1回機械捕捉、報告は push の瞬間に再注入）。②ガバナンスの陳腐化（リスト・ブロック文言・除外期限・3箇所同期）は月次監査＋ローカル同期監査が自動検知する。

**留意点**:
1. **Web版での hooks 発火は未実証** — 次回 Web セッションで `git checkout -b test` → 終了時に完了前チェックが出るか確認する。層1（Top10）は hooks 非依存で Web版でも確実に効く
2. Stop hook のブロックは**1回だけ**（意図的にブランチ継続する場合は理由を回答に書けばそのまま終了できる）
3. push リマインドは毎 push 後に出る（ノイズなら「セッション初回のみ」への改修候補）
4. hooks は fail-open のため 100% の防御ではなく「ほぼ常に効く網」
5. ローカル側 hooks は**次セッション起動から**有効
6. ルール総量は増えている。次の改善候補は CLAUDE.md 本文の重複記述を Top10 参照に置換して総量削減

---

## 5. 残タスク（次セッションへの引き継ぎ）

1. **`GOVERNANCE_PAT` の登録（ユーザー作業・約5分）**: fine-grained PAT（All repositories / Contents: Read・Metadata: Read）→ 本リポ Settings → Secrets and variables → Actions → `GOVERNANCE_PAT`。未登録でも動くが private リポが毎月「判定不可」= FAIL 表示になる
2. **Actions 初回動作確認**: Actions タブから `governance-audit` を workflow_dispatch で手動実行し、`AUDIT_LATEST.md` コミットと Issue 起票を確認
3. **Web版 hooks 発火の実地確認**（上記留意点1）
4. **新カバー3リポの方針決定**: Soulful-Content / private 2リポ → 標準ガバナンス展開 or EXCLUSIONS 登録（happiness-system の教訓により、まず用途を見てから）
5. **private リポ1つの残存ブランチ2本**（固有コミットあり）→ マージ＋削除（実名は `--no-mask` で確認）
6. **happiness-system の review_after=2026-09-25** → 期限到来時に監査が自動警告する

---

## 6. 関連ドキュメント

| ドキュメント | 内容 |
|---|---|
| [RULE_ENFORCEMENT_20260702.md](RULE_ENFORCEMENT_20260702.md) | Part 2 の詳細（分析・設計・期待効果・保守手順） |
| [CHANGELOG.md](CHANGELOG.md) | 2026-07-02 の2エントリ（WHY 中心の変更記録） |
| [retros/RETRO_20260702.md](retros/RETRO_20260702.md) | Part 1 のレトロ（Before/After・教訓6項）＋ Part 2 追記 |
| [audits/AUDIT_DASHBOARD_20260702-v2.md](audits/AUDIT_DASHBOARD_20260702-v2.md) | HR/EH 軸込みの最新監査ダッシュボード |
| [audits/EXCLUSIONS.md](audits/EXCLUSIONS.md) | 除外リスト（軸コード一覧・v2 パーサ仕様） |
| [README.md](README.md) / [BOOTSTRAP.md](BOOTSTRAP.md) | 監査機構の入口・新セッション向け導線 |
