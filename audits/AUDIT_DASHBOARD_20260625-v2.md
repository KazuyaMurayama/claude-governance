# 43リポ ガバナンス適合性 監査結果

対象: 43リポ / 監査日: 2026-06-25

## 凡例
- ✓=適合 / ✗=不適合 / ⚪=`EXCLUSIONS.md` で除外 / ?=判定不可（CLAUDE.md欠落等）
- **CL**=CLAUDE.md存在 / **SC**=単独完結 / **N2**=命名v2.0 / **MD**=モデル§ / **BM**=branch-cleanupトリガー / **BS**=branch-cleanup SKILL / **GV**=governance参照 / **NO**=男座員也 / **NE**=Kazuya Oza / **RM**=README / **HL**=haiku旧記述(✓=削除済)
- **XB**=デフォ以外の余分ブランチ数

## マトリクス

| # | リポ | def | CL | SC | N2 | MD | BM | BS | GV | NO | NE | RM | HL | XB |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | academic-research-agent_v1 | master | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |
| 2 | add-to-nasdaq | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |
| 3 | AI-Architect-forge_v1 | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |
| 4 | ai-knowledge-base | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |
| 5 | AI-News-Collection-Bot_v1 | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |
| 6 | AI-News-Collection-Bot_v2 | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |
| 7 | AI-ROI-simulator_v1 | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |
| 8 | AI-teams-v1 | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |
| 9 | AI-Transformation-Architect | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |
| 10 | AI-Transformation-Architect-monetize | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |
| 11 | AI_monetize_v2 | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |
| 12 | beauty-research-agents_v1 | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |
| 13 | career_dev | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |
| 14 | claude-code-prompt | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |
| 15 | concentration-research-v1 | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |
| 16 | creativity-research-v1 | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |
| 17 | creativity-research-v2 | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |
| 18 | customer_segment_analysis | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |
| 19 | deep-research | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |
| 20 | Doctor | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |
| 21 | enterprise-ai-strategy-advisor | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |
| 22 | facility-search | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |
| 23 | freelance-compass | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |
| 24 | freelance-sales-pipeline | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |
| 25 | FX-backtest | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |
| 26 | Google-Pixel | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |
| 27 | grid_research_v1 | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |
| 28 | happiness-system | claude/flourish.. | ✓ | ⚪ | ⚪ | ⚪ | ⚪ | ⚪ | ⚪ | ✓ | ✓ | ✓ | ✓ | 0 |
| 29 | insider-oracle | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |
| 30 | intent-forge | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |
| 31 | Kanon_Shiraume_Diary | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |
| 32 | MachineLearning_App | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |
| 33 | MypageAppTest | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |
| 34 | NASDAQ-strategy-gas | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |
| 35 | NASDAQ-strategy-monetize | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |
| 36 | NASDAQ_backtest | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |
| 37 | navigator | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |
| 38 | oogiri | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |
| 39 | personal-brand-publisher_v1 | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |
| 40 | PPT-creater | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |
| 41 | share-diary | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |
| 42 | shopping_product_search | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 1 |
| 43 | streamlit-sales-dashboard | main | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 0 |

## 問題集計

| 不適合項目 | 件数 | 該当リポ |
|---|---|---|
| （なし） | 0 | — |

## 余分なブランチが残存しているリポ

| リポ | デフォルト | 余分ブランチ |
|---|---|---|
| shopping_product_search | main | claude/toddler-undershirt-heat-rash-u9e1mu |

## default branch 異常

（なし）

## EXCLUSIONS.md による除外

- **happiness-system** (partial): 除外軸 = ['default_branch_main', 'single_complete', 'naming_v2', 'model_section', 'branch_cleanup_marker', 'branch_cleanup_skill', 'governance_link']
