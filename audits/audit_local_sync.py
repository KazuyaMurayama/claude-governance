"""
Local-machine sync audit (VSCode環境専用 / CI では実行しない).

Checks the "3箇所同期" invariant this repo exists to protect:
  1. ~/.claude/CLAUDE.md              == global/CLAUDE.md
  2. ~/.claude/deliverables-policy.md == global/deliverables-policy.md
  3. ~/.claude/settings.json          == global/settings.json.template
     (the 8 canonical keys; _personal_local_values are machine-specific)
  4. CHANGELOG drift heuristic: recent commits touching global/, templates/
     or skills/ must have a same-day commit touching CHANGELOG.md.

Exit code: 0 = all in sync, 1 = drift detected.
Usage: PYTHONIOENCODING=utf-8 python audits/audit_local_sync.py
"""
import json
import os
import subprocess
import sys
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
HOME_CLAUDE = os.path.join(os.path.expanduser("~"), ".claude")

CANONICAL_SETTINGS_KEYS = [
    "env", "permissions", "model", "autoUpdatesChannel",
    "skipDangerousModePermissionPrompt", "agentPushNotifEnabled",
    "switchModelsOnFlag", "effortLevel", "hooks",
]

drift = []


def check_file_pair(local_rel, repo_rel):
    local, repo = os.path.join(HOME_CLAUDE, local_rel), os.path.join(REPO, repo_rel)
    if not os.path.exists(local):
        drift.append(f"{local_rel}: 実機に存在しない")
        return
    if not os.path.exists(repo):
        drift.append(f"{repo_rel}: リポに存在しない")
        return
    a = open(local, encoding="utf-8").read().replace("\r\n", "\n")
    b = open(repo, encoding="utf-8").read().replace("\r\n", "\n")
    if a == b:
        print(f"MATCH {local_rel} == {repo_rel}")
    else:
        drift.append(f"{local_rel} と {repo_rel} が不一致（3箇所同期が破れている）")


def check_settings():
    real_path = os.path.join(HOME_CLAUDE, "settings.json")
    tpl_path = os.path.join(REPO, "global", "settings.json.template")
    real = json.load(open(real_path, encoding="utf-8"))
    tpl = json.load(open(tpl_path, encoding="utf-8"))
    for k in CANONICAL_SETTINGS_KEYS:
        if real.get(k) == tpl.get(k):
            print(f"MATCH settings.{k}")
        else:
            drift.append(
                f"settings.{k}: 実機={json.dumps(real.get(k), ensure_ascii=False)[:80]} "
                f"テンプレ={json.dumps(tpl.get(k), ensure_ascii=False)[:80]}"
            )


def check_changelog_drift(days=30):
    """Commits touching canonical dirs must be accompanied by a same-day
    CHANGELOG.md commit (heuristic; catches forgot-to-log changes)."""
    since = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()

    def log_dates(*paths):
        out = subprocess.run(
            ["git", "-C", REPO, "log", f"--since={since}", "--format=%ad", "--date=short", "--", *paths],
            capture_output=True, text=True,
        ).stdout.split()
        return set(out)

    canon_dates = log_dates("global/", "templates/", "skills/")
    changelog_dates = log_dates("CHANGELOG.md")
    missing = sorted(canon_dates - changelog_dates)
    if missing:
        drift.append(
            f"CHANGELOG 乖離: {', '.join(missing)} に global/templates/skills 変更コミットがあるが "
            f"同日の CHANGELOG.md 更新がない"
        )
    else:
        print(f"MATCH CHANGELOG（直近{days}日、正典変更日はすべて CHANGELOG 更新あり）")


def main():
    check_file_pair("CLAUDE.md", os.path.join("global", "CLAUDE.md"))
    check_file_pair("deliverables-policy.md", os.path.join("global", "deliverables-policy.md"))
    check_settings()
    check_changelog_drift()
    print()
    if drift:
        print("## VERDICT: DRIFT")
        for d in drift:
            print(f"- {d}")
        sys.exit(1)
    print("## VERDICT: IN SYNC")
    sys.exit(0)


if __name__ == "__main__":
    main()
