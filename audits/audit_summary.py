"""Summarize audit_result.json into a per-repo compliance dashboard.

Honors per-dimension exemptions: if a row's _exempt_dims includes a dimension key,
that cell is rendered as "⚪" (exempt) and excluded from the issue counts.
"""
import json
import os
import sys

here = os.path.dirname(os.path.abspath(__file__))
result_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "_audit_result.json")
with open(result_path, "r", encoding="utf-8") as f:
    rows = json.load(f)

# Compliance dimensions
DIMS = [
    ("claude_md_exists",      "CL"),
    ("single_complete",       "SC"),
    ("naming_v2",             "N2"),
    ("model_section",         "MD"),
    ("branch_cleanup_marker", "BM"),
    ("branch_cleanup_skill",  "BS"),
    ("governance_link",       "GV"),
    ("name_oza",              "NO"),
    ("name_oza_eng",          "NE"),
    ("readme_exists",         "RM"),
]

# Negative dimensions (should be False/absent)
NEG = [
    ("haiku_legacy",          "HL"),
]

def is_exempt(row, key):
    return key in (row.get("_exempt_dims") or [])

def fmt(v, exempt=False):
    if exempt: return "⚪"
    if v is True: return "✓"
    if v is False: return "✗"
    return "?"

def fmt_neg(v, exempt=False):
    if exempt: return "⚪"
    if v is True: return "✗"
    if v is False: return "✓"
    return "?"

# Header
print("# 43リポ ガバナンス適合性 監査結果")
print("")
print(f"対象: {len(rows)}リポ / 監査日: 2026-06-25")
print("")
print("## 凡例")
print("- ✓=適合 / ✗=不適合 / ⚪=`EXCLUSIONS.md` で除外 / ?=判定不可（CLAUDE.md欠落等）")
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
    full_exempt = (r.get("_exempt_scope") == "full")
    for key, _ in DIMS:
        ex = full_exempt or is_exempt(r, key)
        cells.append(fmt(r.get(key), exempt=ex))
        if (not ex) and (r.get(key) is False):
            issues[key].append(r["repo"])
    for key, _ in NEG:
        ex = full_exempt or is_exempt(r, key)
        cells.append(fmt_neg(r.get(key), exempt=ex))
        if (not ex) and (r.get(key) is True):
            issues[key].append(r["repo"])

    xb_list = r.get("extra_branches") or []
    xb = len(xb_list)
    if (not full_exempt) and (not is_exempt(r, "extra_branches")) and xb > 0:
        issues["extra_branches"].append((r["repo"], xb_list))
    if (not full_exempt) and (not is_exempt(r, "default_branch_main")) and r["default_branch"].startswith("claude/"):
        issues["default_anomaly"].append((r["repo"], r["default_branch"]))

    db_show = r["default_branch"][:15] + ".." if len(r["default_branch"]) > 17 else r["default_branch"]
    print(f"| {i} | {r['repo']} | {db_show} | " + " | ".join(cells) + f" | {xb} |")

print("")
print("## 問題集計")
print("")
print(f"| 不適合項目 | 件数 | 該当リポ |")
print(f"|---|---|---|")
any_issue = False
for key, code in DIMS:
    n = len(issues[key])
    if n > 0:
        any_issue = True
        names = ", ".join(issues[key][:10]) + (f" 他{n-10}" if n > 10 else "")
        print(f"| {code} {key} 欠落 | {n} | {names} |")
for key, code in NEG:
    n = len(issues[key])
    if n > 0:
        any_issue = True
        names = ", ".join(issues[key][:10]) + (f" 他{n-10}" if n > 10 else "")
        print(f"| {code} {key} 残存 | {n} | {names} |")
if not any_issue:
    print(f"| （なし） | 0 | — |")

# Extra branches
print("")
print("## 余分なブランチが残存しているリポ")
print("")
if issues["extra_branches"]:
    print(f"| リポ | デフォルト | 余分ブランチ |")
    print(f"|---|---|---|")
    for repo, branches in issues["extra_branches"]:
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

# Exempt summary
exempt_rows = [r for r in rows if r.get("_exempt_scope")]
if exempt_rows:
    print("")
    print("## EXCLUSIONS.md による除外")
    print("")
    for r in exempt_rows:
        print(f"- **{r['repo']}** ({r['_exempt_scope']}): 除外軸 = {r['_exempt_dims']}")
