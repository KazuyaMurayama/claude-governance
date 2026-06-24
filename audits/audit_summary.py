"""Summarize audit_result.json into a per-repo compliance dashboard."""
import json

with open("_audit_result.json", "r", encoding="utf-8") as f:
    rows = json.load(f)

# Compliance dimensions
DIMS = [
    ("claude_md_exists",      "CL"),  # CLAUDE.md exists
    ("single_complete",       "SC"),  # 単独完結マーカー
    ("naming_v2",             "N2"),  # 命名規則 v2.0
    ("model_section",         "MD"),  # モデル使い分け
    ("branch_cleanup_marker", "BM"),  # CLAUDE.md内トリガー
    ("branch_cleanup_skill",  "BS"),  # SKILL.md実在
    ("governance_link",       "GV"),  # claude-governance参照
    ("name_oza",              "NO"),  # 男座員也
    ("name_oza_eng",          "NE"),  # Kazuya Oza
    ("readme_exists",         "RM"),  # README.md
]

# Negative dimensions (should be False/absent)
NEG = [
    ("haiku_legacy",          "HL"),  # haiku旧記述残存
]

def fmt(v):
    if v is True: return "✓"
    if v is False: return "✗"
    return "?"

def fmt_neg(v):
    if v is True: return "✗"  # has legacy → bad
    if v is False: return "✓"  # absent → good
    return "?"

# Header
print("# 43リポ ガバナンス適合性 監査結果")
print("")
print(f"対象: {len(rows)}リポ / 監査日: 2026-06-25")
print("")
print("## 凡例")
print("- ✓=適合 / ✗=不適合 / ?=判定不可（CLAUDE.md欠落等）")
print("- **CL**=CLAUDE.md存在 / **SC**=単独完結 / **N2**=命名v2.0 / **MD**=モデル§ / **BM**=branch-cleanupトリガー / **BS**=branch-cleanup SKILL / **GV**=governance参照 / **NO**=男座員也 / **NE**=Kazuya Oza / **RM**=README / **HL**=haiku旧記述(✓=削除済)")
print("- **XB**=デフォ以外の余分ブランチ数")
print("")
print("## マトリクス")
print("")
print("| # | リポ | def | CL | SC | N2 | MD | BM | BS | GV | NO | NE | RM | HL | XB |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")

issues = {k: [] for k, _ in DIMS + NEG}
issues["extra_branches"] = []
issues["default_anomaly"] = []

for i, r in enumerate(rows, 1):
    cells = []
    for key, _ in DIMS:
        cells.append(fmt(r.get(key)))
        if r.get(key) is False:
            issues[key].append(r["repo"])
    for key, _ in NEG:
        cells.append(fmt_neg(r.get(key)))
        if r.get(key) is True:
            issues[key].append(r["repo"])
    xb = len(r["extra_branches"])
    if xb > 0:
        issues["extra_branches"].append((r["repo"], r["extra_branches"]))
    if r["default_branch"].startswith("claude/"):
        issues["default_anomaly"].append((r["repo"], r["default_branch"]))
    db_show = r["default_branch"][:15] + ".." if len(r["default_branch"]) > 17 else r["default_branch"]
    print(f"| {i} | {r['repo']} | {db_show} | " + " | ".join(cells) + f" | {xb} |")

print("")
print("## 問題集計")
print("")
print(f"| 不適合項目 | 件数 | 該当リポ |")
print(f"|---|---|---|")
for key, code in DIMS:
    n = len(issues[key])
    if n > 0:
        names = ", ".join(issues[key][:10]) + (f" 他{n-10}" if n > 10 else "")
        print(f"| {code} {key} 欠落 | {n} | {names} |")
for key, code in NEG:
    n = len(issues[key])
    if n > 0:
        names = ", ".join(issues[key][:10]) + (f" 他{n-10}" if n > 10 else "")
        print(f"| {code} {key} 残存 | {n} | {names} |")

# Extra branches
print("")
print("## 余分なブランチが残存しているリポ")
print("")
if issues["extra_branches"]:
    print(f"| リポ | デフォルト | 余分ブランチ |")
    print(f"|---|---|---|")
    for repo, branches in issues["extra_branches"]:
        # find default
        db = next(r["default_branch"] for r in rows if r["repo"] == repo)
        print(f"| {repo} | {db} | {', '.join(branches)} |")
else:
    print("（なし）")

print("")
print("## default branch 異常")
print("")
if issues["default_anomaly"]:
    for repo, db in issues["default_anomaly"]:
        print(f"- **{repo}**: default が `{db}`（claude/* がdefault化されている）")
else:
    print("（なし）")
