"""Summarize audit result JSON into a per-repo compliance dashboard.

v2 (2026-07-02) changes:
  - Accepts both the new {"meta":..., "rows":...} format and the legacy
    plain-list format.
  - Audit date comes from meta (no more hardcoded date).
  - Extra branches (XB) and check errors ("?") now COUNT AS ISSUES:
    the headline verdict is PASS only when every axis, XB and error count
    is clean. Exit code 1 on FAIL so CI can gate on it.
  - Private repo names are masked by default (the dashboard is committed to
    a PUBLIC repo). Run with --no-mask for local investigation.
  - GC column: governance link block content matches the canonical template.
  - Expired EXCLUSIONS review_after entries are surfaced as warnings.

Usage:
  python audit_summary.py <result.json> [--no-mask]
"""
import json
import os
import sys
import datetime

here = os.path.dirname(os.path.abspath(__file__))
args = [a for a in sys.argv[1:] if not a.startswith("--")]
MASK = "--no-mask" not in sys.argv
result_path = args[0] if args else os.path.join(here, "_audit_result.json")
with open(result_path, "r", encoding="utf-8") as f:
    data = json.load(f)

if isinstance(data, dict):
    rows, meta = data["rows"], data.get("meta", {})
else:  # legacy format
    rows, meta = data, {}
audit_date = meta.get("audit_date", datetime.date.today().isoformat())

# Positive dimensions (True = compliant)
DIMS = [
    ("claude_md_exists",        "CL"),
    ("single_complete",         "SC"),
    ("naming_v2",               "N2"),
    ("model_section",           "MD"),
    ("branch_cleanup_marker",   "BM"),
    ("branch_cleanup_skill",    "BS"),
    ("governance_link",         "GV"),
    ("governance_link_current", "GC"),
    ("hard_rules",              "HR"),
    ("enforce_hooks",           "EH"),
    ("name_oza",                "NO"),
    ("name_oza_eng",            "NE"),
    ("readme_exists",           "RM"),
]
# Negative dimensions (True = violation)
NEG = [
    ("haiku_legacy",            "HL"),
]

_mask_names = {}
def display_name(r):
    if MASK and r.get("private"):
        if r["repo"] not in _mask_names:
            _mask_names[r["repo"]] = f"(private #{len(_mask_names) + 1})"
        return _mask_names[r["repo"]]
    return r["repo"]

def is_exempt(row, key):
    dims = row.get("_exempt_dims") or []
    # governance_link_current is derived from governance_link:
    # a repo exempt from having the link can't be required to keep it current.
    if key == "governance_link_current" and "governance_link" in dims:
        return True
    return key in dims

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

print("# リポ ガバナンス適合性 監査結果")
print("")
print(f"対象: {len(rows)}リポ / 監査日: {audit_date}")
print("")
print("## 凡例")
print("- ✓=適合 / ✗=不適合 / ⚪=`EXCLUSIONS.md` で除外 / ?=判定不可（ネットワーク/権限エラー等。適合扱いにしない）")
print("- **CL**=CLAUDE.md存在 / **SC**=単独完結 / **N2**=命名v2.0 / **MD**=モデル§ / **BM**=branch-cleanupトリガー / **BS**=branch-cleanup SKILL / **GV**=governance参照 / **GC**=governance参照が正典と一致 / **HR**=絶対ルールTop10ブロック / **EH**=rule-enforcement hooks配線 / **NO**=男座員也 / **NE**=Kazuya Oza / **RM**=README / **HL**=haiku旧記述(✓=削除済)")
print("- **XB**=デフォ以外の余分ブランチ数")
if MASK:
    print("- private リポは名前をマスク表示（公開リポにコミットされるため）。実名確認はローカルで `--no-mask` 実行")
print("")
print("## マトリクス")
print("")
print("| # | リポ | def | CL | SC | N2 | MD | BM | BS | GV | GC | HR | EH | NO | NE | RM | HL | XB |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")

issues = {k: [] for k, _ in DIMS + NEG}
issues["extra_branches"] = []
issues["default_anomaly"] = []
errors = []

for i, r in enumerate(rows, 1):
    name = display_name(r)
    cells = []
    full_exempt = (r.get("_exempt_scope") == "full")
    for key, _ in DIMS:
        ex = full_exempt or is_exempt(r, key)
        cells.append(fmt(r.get(key), exempt=ex))
        if (not ex) and (r.get(key) is False):
            issues[key].append(name)
    for key, _ in NEG:
        ex = full_exempt or is_exempt(r, key)
        cells.append(fmt_neg(r.get(key), exempt=ex))
        if (not ex) and (r.get(key) is True):
            issues[key].append(name)

    xb_list = r.get("extra_branches")
    if xb_list is None and not full_exempt:
        xb_show = "?"
    else:
        xb_show = str(len(xb_list or []))
        if (not full_exempt) and (not is_exempt(r, "extra_branches")) and xb_list:
            issues["extra_branches"].append((name, xb_list))
    if (not full_exempt) and (not is_exempt(r, "default_branch_main")) and r["default_branch"].startswith("claude/"):
        issues["default_anomaly"].append((name, r["default_branch"]))
    if r.get("_errors"):
        errors.append((name, r["_errors"]))

    db_show = r["default_branch"][:15] + ".." if len(r["default_branch"]) > 17 else r["default_branch"]
    print(f"| {i} | {name} | {db_show} | " + " | ".join(cells) + f" | {xb_show} |")

print("")
print("## 問題集計")
print("")
print("| 不適合項目 | 件数 | 該当リポ |")
print("|---|---|---|")
n_issues = 0
for key, code in DIMS:
    n = len(issues[key])
    if n > 0:
        n_issues += n
        names = ", ".join(issues[key][:10]) + (f" 他{n-10}" if n > 10 else "")
        print(f"| {code} {key} 欠落 | {n} | {names} |")
for key, code in NEG:
    n = len(issues[key])
    if n > 0:
        n_issues += n
        names = ", ".join(issues[key][:10]) + (f" 他{n-10}" if n > 10 else "")
        print(f"| {code} {key} 残存 | {n} | {names} |")
if issues["extra_branches"]:
    n_issues += len(issues["extra_branches"])
    names = ", ".join(name for name, _ in issues["extra_branches"][:10])
    print(f"| XB 余分ブランチ残存 | {len(issues['extra_branches'])} | {names} |")
if issues["default_anomaly"]:
    n_issues += len(issues["default_anomaly"])
    names = ", ".join(name for name, _ in issues["default_anomaly"])
    print(f"| default branch 異常 | {len(issues['default_anomaly'])} | {names} |")
if n_issues == 0:
    print("| （なし） | 0 | — |")

print("")
print("## 余分なブランチが残存しているリポ")
print("")
if issues["extra_branches"]:
    print("| リポ | 余分ブランチ |")
    print("|---|---|")
    for name, branches in issues["extra_branches"]:
        print(f"| {name} | {', '.join(branches)} |")
else:
    print("（なし）")

print("")
print("## default branch 異常")
print("")
if issues["default_anomaly"]:
    for name, db in issues["default_anomaly"]:
        print(f"- **{name}**: default が `{db}`（claude/* がdefault化されている）")
else:
    print("（なし）")

# Errors are issues too: an unauditable repo is NOT a compliant repo.
if errors:
    print("")
    print("## 判定不可（要調査エラー）")
    print("")
    for name, errs in errors:
        print(f"- **{name}**: {'; '.join(errs)}")

expired = meta.get("expired_reviews") or []
if expired:
    print("")
    print("## ⚠ EXCLUSIONS 再評価期限切れ")
    print("")
    for name, due in expired:
        shown = name
        if MASK:
            row = next((r for r in rows if r["repo"] == name), None)
            if row is not None and row.get("private"):
                shown = display_name(row)
        print(f"- **{shown}**: review_after={due} を経過。除外の妥当性を再評価すること")

exempt_rows = [r for r in rows if r.get("_exempt_scope")]
if exempt_rows:
    print("")
    print("## EXCLUSIONS.md による除外")
    print("")
    for r in exempt_rows:
        print(f"- **{display_name(r)}** ({r['_exempt_scope']}): 除外軸 = {r['_exempt_dims']}")

verdict_fail = n_issues > 0 or bool(errors) or bool(expired)
print("")
print(f"## VERDICT: {'FAIL' if verdict_fail else 'PASS'}")
print("")
print(f"- 不適合 {n_issues} 件 / 判定不可 {len(errors)} 件 / 期限切れ除外 {len(expired)} 件")
sys.exit(1 if verdict_fail else 0)
