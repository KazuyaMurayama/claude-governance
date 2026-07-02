"""
Audit all KazuyaMurayama-owned repos for governance rule compliance.

NOTE: The filename keeps the historical "43repos" name because 40+ repos'
CLAUDE.md governance blocks reference `audits/audit_43repos.py` — renaming
would orphan those links. The repo list itself is discovered dynamically.

v2 (2026-07-02) changes:
  - REPOS hardcode removed: repos are discovered via authenticated
    GET /user/repos (includes private repos; default_branch comes from API).
  - Token is REQUIRED (fail loud). Unauthenticated runs would hit the 60/h
    rate limit mid-audit and report rate-limit 403s as false "missing file".
  - Network / rate-limit failures are recorded as errors ("?"), never as
    a silent pass or a false fail.
  - EXCLUSIONS.md: only ```yaml fenced blocks are parsed (the format example
    in the doc is no longer picked up as a phantom entry); review_after is
    parsed and expired entries are flagged.
  - governance_link_current: content between GOVERNANCE_LINK_START/END is
    compared against templates/governance-link-block.md (staleness check).

Output: JSON {"meta": {...}, "rows": [...]} on stdout.
"""
import subprocess
import urllib.request
import urllib.error
import json
import os
import re
import sys
import datetime

OWNER = "KazuyaMurayama"
HERE = os.path.dirname(os.path.abspath(__file__))

# Repos that are never audited (the governance repo itself and the profile repo).
SKIP_REPOS = {"claude-governance", OWNER}


def _get_token():
    """Fetch GitHub token from git credential helper, or GH_TOKEN/GITHUB_TOKEN env."""
    try:
        proc = subprocess.run(
            ["git", "credential", "fill"],
            input="protocol=https\nhost=github.com\n\n",
            capture_output=True, text=True, timeout=10,
        )
        for line in proc.stdout.splitlines():
            if line.startswith("password="):
                return line.split("=", 1)[1]
    except Exception:
        pass
    return os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")


_TOKEN = _get_token()
if not _TOKEN:
    print(
        "FATAL: no GitHub token (git credential helper empty and GH_TOKEN/GITHUB_TOKEN unset).\n"
        "Unauthenticated audits exceed the 60 req/h rate limit and produce false results. Aborting.",
        file=sys.stderr,
    )
    sys.exit(2)


def _auth_headers(accept="application/vnd.github+json"):
    return {
        "User-Agent": "audit-script",
        "Cache-Control": "no-cache",
        "Authorization": f"token {_TOKEN}",
        "Accept": accept,
    }


def api_get(url, accept="application/vnd.github+json", timeout=30):
    """GET with auth. Returns (status, body_str). status=-1 on network error."""
    try:
        req = urllib.request.Request(url, headers=_auth_headers(accept))
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")
    except Exception as e:
        return -1, str(e)


def discover_repos():
    """All owned repos via /user/repos (paginated, includes private)."""
    repos, page = [], 1
    while True:
        status, body = api_get(
            f"https://api.github.com/user/repos?per_page=100&page={page}&affiliation=owner"
        )
        if status != 200:
            print(f"FATAL: /user/repos page {page} -> HTTP {status}: {body[:200]}", file=sys.stderr)
            sys.exit(2)
        batch = json.loads(body)
        if not batch:
            break
        repos.extend(batch)
        page += 1
    out = []
    for r in repos:
        if r["name"] in SKIP_REPOS:
            continue
        out.append({
            "name": r["name"],
            "default_branch": r["default_branch"],
            "private": bool(r["private"]),
            "archived": bool(r.get("archived", False)),
        })
    return sorted(out, key=lambda x: x["name"].lower())


# ---------------------------------------------------------------- exclusions
def load_exclusions():
    """Parse EXCLUSIONS.md. Only ```yaml fenced blocks are parsed, so the
    format example (plain ``` fence) can't create phantom entries."""
    path = os.path.join(HERE, "EXCLUSIONS.md")
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        txt = f.read()
    exclusions = {}
    for block in re.findall(r"```yaml\n(.*?)```", txt, re.DOTALL):
        for entry in re.split(r"\n- repo:\s*", "\n" + block)[1:]:
            name = entry.splitlines()[0].strip()
            if not name or "<" in name:
                continue
            scope_m = re.search(r"^\s*scope:\s*(\w+)", entry, re.MULTILINE)
            review_m = re.search(r"^\s*review_after:\s*(\d{4}-\d{2}-\d{2})", entry, re.MULTILINE)
            dims = []
            dims_m = re.search(r"exempt_dims:\s*\n((?:\s*-\s*\w+\s*(?:#.*)?\n)+)", entry)
            if dims_m:
                for line in dims_m.group(1).splitlines():
                    m = re.match(r"\s*-\s*(\w+)", line)
                    if m:
                        dims.append(m.group(1))
            exclusions[name] = {
                "scope": scope_m.group(1) if scope_m else "partial",
                "exempt_dims": dims,
                "review_after": review_m.group(1) if review_m else None,
            }
    return exclusions


EXCLUSIONS = load_exclusions()


# ------------------------------------------------------- governance link 正典
def load_canonical_link_block():
    path = os.path.join(HERE, "..", "templates", "governance-link-block.md")
    with open(path, "r", encoding="utf-8") as f:
        txt = f.read()
    m = re.search(r"<!-- GOVERNANCE_LINK_START -->\n(.*?)<!-- GOVERNANCE_LINK_END -->", txt, re.DOTALL)
    return _norm(m.group(1)) if m else None


def _norm(s):
    """Whitespace-insensitive normalization for block comparison."""
    return "\n".join(line.strip() for line in s.strip().splitlines() if line.strip())


CANONICAL_LINK_BLOCK = load_canonical_link_block()

# Check signals — key -> tuple of "must contain" strings in CLAUDE.md
CHECKS_IN_CLAUDE_MD = {
    "single_complete":       ("VSCode版", "Web版"),
    "naming_v2":             ("YYYYMMDD",),
    "model_section":         ("モデル使い分け", "claude-fable-5"),
    "branch_cleanup_marker": ("BRANCH_CLEANUP_START",),
    "governance_link":       ("claude-governance",),
    "name_oza":              ("男座員也",),
    "name_oza_eng":          ("Kazuya Oza",),
    "haiku_legacy":          ('model: "haiku"',),   # should be ABSENT
}


def fetch_raw(repo, branch, path, timeout=30):
    """Fetch file via Contents API (no CDN lag). Returns (status, content)."""
    url = f"https://api.github.com/repos/{OWNER}/{repo}/contents/{path}?ref={branch}"
    return api_get(url, accept="application/vnd.github.raw", timeout=timeout)


def head_exists(repo, branch, path):
    """Existence check. Returns True / False / None (network or rate-limit error)."""
    status, body = fetch_raw(repo, branch, path)
    if status == 200:
        return True
    if status == 404:
        return False
    return None  # 403 rate limit, 5xx, network error → unknown, NOT a pass/fail


def ls_remote_branches(repo, timeout=30):
    """List remote heads. Returns list of branch names, or None on failure.
    Token is embedded in the URL so private repos work; output is captured
    so the token is never printed."""
    url = f"https://x-access-token:{_TOKEN}@github.com/{OWNER}/{repo}.git"
    try:
        result = subprocess.run(
            ["git", "ls-remote", "--heads", url],
            capture_output=True, text=True, timeout=timeout,
        )
        if result.returncode != 0:
            return None
        branches = []
        for line in result.stdout.strip().splitlines():
            if "\trefs/heads/" in line:
                branches.append(line.split("refs/heads/")[1])
        return branches
    except Exception:
        return None


def audit_one(meta):
    repo, branch = meta["name"], meta["default_branch"]
    row = {
        "repo": repo,
        "default_branch": branch,
        "private": meta["private"],
        "archived": meta["archived"],
        "_errors": [],
    }
    exemption = EXCLUSIONS.get(repo)
    row["_exempt_scope"] = exemption["scope"] if exemption else None
    row["_exempt_dims"] = exemption["exempt_dims"] if exemption else []
    row["_review_after"] = exemption["review_after"] if exemption else None

    if exemption and exemption["scope"] == "full":
        return row

    # 1. CLAUDE.md content checks
    status, content = fetch_raw(repo, branch, "CLAUDE.md")
    if status == 200:
        row["claude_md_exists"] = True
        for key, patterns in CHECKS_IN_CLAUDE_MD.items():
            row[key] = all(p in content for p in patterns)
        # governance link staleness: compare marker-delimited block to canonical
        m = re.search(r"<!-- GOVERNANCE_LINK_START -->\n(.*?)<!-- GOVERNANCE_LINK_END -->", content, re.DOTALL)
        if m and CANONICAL_LINK_BLOCK:
            row["governance_link_current"] = (_norm(m.group(1)) == CANONICAL_LINK_BLOCK)
        else:
            row["governance_link_current"] = False  # no marker block → can't bulk-update → stale
    elif status == 404:
        row["claude_md_exists"] = False
        for key in CHECKS_IN_CLAUDE_MD:
            row[key] = None
        row["governance_link_current"] = None
    else:
        row["claude_md_exists"] = None
        for key in CHECKS_IN_CLAUDE_MD:
            row[key] = None
        row["governance_link_current"] = None
        row["_errors"].append(f"CLAUDE.md fetch HTTP {status}")

    # 2. README.md
    row["readme_exists"] = head_exists(repo, branch, "README.md")
    if row["readme_exists"] is None:
        row["_errors"].append("README.md check failed")

    # 3. branch-cleanup SKILL.md
    row["branch_cleanup_skill"] = head_exists(repo, branch, ".claude/skills/branch-cleanup/SKILL.md")
    if row["branch_cleanup_skill"] is None:
        row["_errors"].append("branch-cleanup SKILL check failed")

    # 4. extra branches (None = could not determine, rendered as "?")
    branches = ls_remote_branches(repo)
    if branches is None:
        row["all_branches"] = None
        row["extra_branches"] = None
        row["_errors"].append("ls-remote failed")
    else:
        row["all_branches"] = branches
        row["extra_branches"] = [b for b in branches if b != branch]
    return row


def main():
    today = datetime.date.today().isoformat()
    repos = discover_repos()
    print(f"Discovered {len(repos)} repos (private: {sum(1 for r in repos if r['private'])}). Auditing...", file=sys.stderr)
    if EXCLUSIONS:
        print(f"  Loaded EXCLUSIONS for: {list(EXCLUSIONS.keys())}", file=sys.stderr)
    rows = []
    for i, meta in enumerate(repos, 1):
        print(f"[{i}/{len(repos)}] {meta['name']}", file=sys.stderr)
        rows.append(audit_one(meta))
    expired = [
        (name, ex["review_after"]) for name, ex in EXCLUSIONS.items()
        if ex.get("review_after") and ex["review_after"] < today
    ]
    out = {
        "meta": {
            "audit_date": today,
            "repo_count": len(repos),
            "private_count": sum(1 for r in repos if r["private"]),
            "exclusions": {k: v for k, v in EXCLUSIONS.items()},
            "expired_reviews": expired,
        },
        "rows": rows,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
