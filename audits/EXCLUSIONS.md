# 監査除外リスト（EXCLUSIONS）

作成日: 2026-06-25
最終更新日: 2026-06-25

監査スクリプト（`audit_43repos.py` / `audit_summary.py`）が **意図的にチェックをスキップ** するリポジトリと、その理由・例外範囲を管理する。

## 設計思想

- 「ガバナンス違反」と「意図的な独自設計」は区別する
- 独自設計が確立し活発に運用されているリポを、機械的監査で「不適合」として騒ぐのは害悪
- ただし **完全に監査対象外** にすると将来の変化を見逃すため、**部分除外**（特定の軸だけスキップ）の概念を持つ

## 除外フォーマット

各エントリは以下のYAMLライクなブロックで管理：

```
- repo: <リポ名>
  scope: <full | partial>
  exempt_dims: [<除外する軸コード>, ...]    # partial の場合のみ
  reason: <なぜ除外するか>
  registered_at: <YYYY-MM-DD>
  review_after: <YYYY-MM-DD>                # 再評価予定日（任意）
```

### scope の定義
- **full**: 監査対象から完全除外（リポ自体スキップ）
- **partial**: 特定の軸のみ除外し、その他は通常監査

### 除外可能な軸コード（`audit_43repos.py` の `CHECKS_IN_CLAUDE_MD` に対応）
| コード | 軸 |
|---|---|
| `default_branch_main` | default branch が main/master であること |
| `single_complete` | 単独完結マーカー |
| `naming_v2` | 命名規則 v2.0 |
| `model_section` | モデル使い分け§ |
| `branch_cleanup_marker` | branch-cleanup トリガー |
| `branch_cleanup_skill` | branch-cleanup SKILL.md |
| `governance_link` | 上位ガバナンス参照 |
| `name_oza` | 男座員也 表記 |
| `name_oza_eng` | Kazuya Oza 表記 |
| `readme_exists` | README.md |
| `haiku_legacy` | haiku 旧記述削除 |
| `extra_branches` | 余分ブランチなし |

---

## 現在の除外エントリ

### 1. happiness-system（partial 除外）

```yaml
- repo: happiness-system
  scope: partial
  exempt_dims:
    - default_branch_main          # main 不在で claude/* が default
    - single_complete              # 独自憲法形式のため標準マーカー無し
    - naming_v2                    # 標準命名規則を適用しない独自設計
    - model_section                # 独自エージェント構成のため §7 標準フォーマット不適用
    - branch_cleanup_marker        # main 不在＝branch-cleanup の前提が成立しない
    - branch_cleanup_skill         # 同上
    - governance_link              # 独自設計の自律性を尊重しリンク強制しない
  reason: |
    flourish-forge 独自運用憲法（50行以内）形式の現役プロジェクト。
    2026-06-23 作成、2026-06-24 まで毎日活発に push（実運用中）。
    4エージェント逐次パイプライン＋独自スラッシュコマンド（/savor /scan /recall /morning /reflect /continue）
    で構成され、本リポ標準ガバナンスとは設計思想が異なる。
    無理に標準化するとこの独自設計の良さが壊れるため、partial 除外で扱う。
    ただし name_oza / name_oza_eng / readme_exists / haiku_legacy / extra_branches は
    本人運用ルールとして共通であり、これらは監査対象に残す。
  registered_at: 2026-06-25
  review_after: 2026-09-25  # 3か月後に運用状況を再評価
```

---

## エントリ追加・削除のルール

1. **追加時**: ユーザー判断を経てから登録（Claude 単独で追加しない）
2. **削除時**: 該当リポが標準ガバナンスに完全準拠したことを確認してから削除
3. **review_after が過ぎたら**: 監査スクリプトが警告し、再評価を促す
4. **変更履歴**: `CHANGELOG.md` に「除外エントリの追加・削除」を記録

---

## 監査スクリプトとの連携

`audit_43repos.py` は本ファイルを読み込み：
- `scope: full` のリポはスキップ
- `scope: partial` のリポは `exempt_dims` の軸のみ "✓" 扱いに（実際の値とは無関係）
- 除外されている事実はダッシュボードに「⚪ (exempt)」マークで明示
