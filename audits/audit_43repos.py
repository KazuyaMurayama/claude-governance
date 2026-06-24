"""
Audit all 43 KazuyaMurayama repos for governance rule compliance.
Uses raw.githubusercontent.com (no rate limit) and git ls-remote (no rate limit).
"""
import subprocess
import urllib.request
import json
import sys

OWNER = "KazuyaMurayama"

# 45 repos discovered; exclude self (claude-governance) and profile (KazuyaMurayama)
REPOS = [
    ("academic-research-agent_v1", "master"),
    ("add-to-nasdaq", "main"),
    ("AI-Architect-forge_v1", "main"),
    ("ai-knowledge-base", "main"),
    ("AI-News-Collection-Bot_v1", "main"),
    ("AI-News-Collection-Bot_v2", "main"),
    ("AI-ROI-simulator_v1", "main"),
    ("AI-teams-v1", "main"),
    ("AI-Transformation-Architect", "main"),
    ("AI-Transformation-Architect-monetize", "main"),
    ("AI_monetize_v2", "main"),
    ("beauty-research-agents_v1", "main"),
    ("career_dev", "main"),
    ("claude-code-prompt", "main"),
    ("concentration-research-v1", "main"),
    ("creativity-research-v1", "main"),
    ("creativity-research-v2", "main"),
    ("customer_segment_analysis", "main"),
    ("deep-research", "main"),
    ("Doctor", "main"),
    ("enterprise-ai-strategy-advisor", "main"),
    ("facility-search", "main"),
    ("freelance-compass", "main"),
    ("freelance-sales-pipeline", "main"),
    ("FX-backtest", "main"),
    ("Google-Pixel", "main"),
    ("grid_research_v1", "main"),
    ("happiness-system", "claude/flourish-forge-setup-wpvm3n"),  # ANOMALY: default branch is claude/*
    ("insider-oracle", "main"),
    ("intent-forge", "main"),
    ("Kanon_Shiraume_Diary", "main"),
    ("MachineLearning_App", "main"),
    ("MypageAppTest", "main"),
    ("NASDAQ-strategy-gas", "main"),
    ("NASDAQ-strategy-monetize", "main"),
    ("NASDAQ_backtest", "main"),
    ("navigator", "main"),
    ("oogiri", "main"),
    ("personal-brand-publisher_v1", "main"),
    ("PPT-creater", "main"),
    ("share-diary", "main"),
    ("shopping_product_search", "main"),
    ("streamlit-sales-dashboard", "main"),
]

# Check signals — pattern -> "must contain"
CHECKS_IN_CLAUDE_MD = {
    "single_complete":      ("VSCode版", "Web版"),  # 単独完結マーカー
    "naming_v2":            ("YYYYMMDD",),
    "naming_old_hyphen":    ("2026-06-03",),       # Should be ABSENT or only as example of old format
    "model_section":        ("モデル使い分け", "claude-fable-5"),
    "branch_cleanup_marker": ("BRANCH_CLEANUP_START",),
    "governance_link":      ("claude-governance",),
    "name_oza":             ("男座員也",),
    "name_oza_eng":         ("Kazuya Oza",),
    "haiku_legacy":         ("model: \"haiku\"",),   # Should be ABSENT
}

def fetch_raw(repo, branch, path, timeout=15):
    url = f"https://raw.githubusercontent.com/{OWNER}/{repo}/{branch}/{path}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "audit-script"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return -1, str(e)

def head_raw(repo, branch, path, timeout=10):
    url = f"https://raw.githubusercontent.com/{OWNER}/{repo}/{branch}/{path}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "audit-script"}, method="HEAD")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return -1

def ls_remote_branches(repo, timeout=20):
    try:
        result = subprocess.run(
            ["git", "ls-remote", "--heads", f"https://github.com/{OWNER}/{repo}.git"],
            capture_output=True, text=True, timeout=timeout
        )
        if result.returncode != 0:
            return []
        branches = []
        for line in result.stdout.strip().split("\n"):
            if "\trefs/heads/" in line:
                branches.append(line.split("refs/heads/")[1])
        return branches
    except Exception:
        return []

def audit_one(repo, branch):
    row = {"repo": repo, "default_branch": branch}
    # 1. CLAUDE.md
    status, content = fetch_raw(repo, branch, "CLAUDE.md")
    row["claude_md_exists"] = (status == 200)
    if status == 200:
        for key, patterns in CHECKS_IN_CLAUDE_MD.items():
            row[key] = all(p in content for p in patterns)
        # Special: old hyphen format. Mark as "still uses old" only if the literal "2026-06-03" appears as a real date suffix.
        # Acceptable: "v2.0 / 2026-06-03 改訂" or "❌ <TOPIC>_2026-06-03.md" (as example).
        # Flag only if used as actual filename pattern outside the explanatory block.
        row["naming_old_acceptable"] = ("v2.0" in content) or ("廃止" in content)
    else:
        for key in CHECKS_IN_CLAUDE_MD:
            row[key] = None

    # 2. README.md
    row["readme_exists"] = (head_raw(repo, branch, "README.md") == 200)

    # 3. branch-cleanup SKILL.md
    row["branch_cleanup_skill"] = (head_raw(repo, branch, ".claude/skills/branch-cleanup/SKILL.md") == 200)

    # 4. extra branches
    branches = ls_remote_branches(repo)
    row["all_branches"] = branches
    row["extra_branches"] = [b for b in branches if b != branch]
    return row

def main():
    print(f"Auditing {len(REPOS)} repos...", file=sys.stderr)
    results = []
    for i, (repo, branch) in enumerate(REPOS, 1):
        print(f"[{i}/{len(REPOS)}] {repo}", file=sys.stderr)
        results.append(audit_one(repo, branch))
    print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
