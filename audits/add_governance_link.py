"""
Append (or refresh) the "上位ガバナンスへの参照" block in each repo's CLAUDE.md
via GitHub Contents API.

v2 (2026-07-02):
  - Repo list comes from audit_43repos.discover_repos() (dynamic, incl. private).
  - Block text is loaded from templates/governance-link-block.md (single source
    of truth, shared with the audit's staleness check).
  - --update: when a marker block exists but its content differs from the
    canonical template, replace the content between markers in place.
    Without --update, repos that already have the marker are skipped.

Skips:
  - repos in EXCLUSIONS.md exempting governance_link (or scope: full)
  - repos without CLAUDE.md
  - repos already up to date
"""
import json
import os
import re
import sys
import urllib.request
import base64

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from audit_43repos import (  # noqa: E402
    OWNER, EXCLUSIONS, _TOKEN, discover_repos, fetch_raw, _norm, CANONICAL_LINK_BLOCK,
)

UPDATE_MODE = "--update" in sys.argv

with open(os.path.join(HERE, "..", "templates", "governance-link-block.md"), "r", encoding="utf-8") as f:
    CANONICAL_BLOCK_RAW = f.read().strip()

APPEND_BLOCK = f"""
---

## 上位ガバナンスへの参照

{CANONICAL_BLOCK_RAW}
"""

MARKER_RE = re.compile(r"<!-- GOVERNANCE_LINK_START -->\n.*?<!-- GOVERNANCE_LINK_END -->", re.DOTALL)


def get_file(repo, branch, path):
    url = f"https://api.github.com/repos/{OWNER}/{repo}/contents/{path}?ref={branch}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"token {_TOKEN}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "governance-link-script",
        "Cache-Control": "no-cache",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def put_file(repo, branch, path, new_content_b64, sha, message):
    url = f"https://api.github.com/repos/{OWNER}/{repo}/contents/{path}"
    body = json.dumps({
        "message": message,
        "content": new_content_b64,
        "sha": sha,
        "branch": branch,
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="PUT", headers={
        "Authorization": f"token {_TOKEN}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "governance-link-script",
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, json.loads(r.read().decode("utf-8"))


def main():
    repos = discover_repos()
    results = {"appended": [], "refreshed": [], "up_to_date": [], "skipped_excluded": [],
               "skipped_has_marker": [], "skipped_mention_only": [], "skipped_no_claude_md": [], "failed": []}
    for i, meta in enumerate(repos, 1):
        repo, branch = meta["name"], meta["default_branch"]
        print(f"[{i}/{len(repos)}] {repo}", file=sys.stderr)
        ex = EXCLUSIONS.get(repo)
        if ex and ("governance_link" in (ex.get("exempt_dims") or []) or ex.get("scope") == "full"):
            results["skipped_excluded"].append(repo)
            print("  SKIP (excluded)", file=sys.stderr)
            continue
        try:
            f = get_file(repo, branch, "CLAUDE.md")
        except Exception as e:
            results["failed"].append((repo, f"fetch: {e}"))
            print(f"  FAIL fetch: {e}", file=sys.stderr)
            continue
        if f is None:
            results["skipped_no_claude_md"].append(repo)
            print("  SKIP (no CLAUDE.md)", file=sys.stderr)
            continue
        sha = f["sha"]
        content = base64.b64decode(f["content"]).decode("utf-8")

        has_marker = "<!-- GOVERNANCE_LINK_START -->" in content
        if has_marker:
            m = re.search(r"<!-- GOVERNANCE_LINK_START -->\n(.*?)<!-- GOVERNANCE_LINK_END -->", content, re.DOTALL)
            if m and _norm(m.group(1)) == CANONICAL_LINK_BLOCK:
                results["up_to_date"].append(repo)
                print("  OK (up to date)", file=sys.stderr)
                continue
            if not UPDATE_MODE:
                results["skipped_has_marker"].append(repo)
                print("  SKIP (marker exists but stale; rerun with --update)", file=sys.stderr)
                continue
            new_content = MARKER_RE.sub(CANONICAL_BLOCK_RAW, content, count=1)
            action, message = "refreshed", "docs(governance): refresh upstream governance reference block to canonical"
        else:
            if "claude-governance" in content:
                # mention without marker: appending would duplicate; needs manual review
                results["skipped_mention_only"].append(repo)
                print("  SKIP (mentions claude-governance without marker; review manually)", file=sys.stderr)
                continue
            new_content = content + ("" if content.endswith("\n") else "\n") + APPEND_BLOCK
            action, message = "appended", "docs(governance): add upstream governance reference block (claude-governance)"

        new_b64 = base64.b64encode(new_content.encode("utf-8")).decode("ascii")
        try:
            status, resp = put_file(repo, branch, "CLAUDE.md", new_b64, sha, message)
            results[action].append(repo)
            print(f"  OK {action} status={status} sha={resp.get('commit', {}).get('sha', '')[:7]}", file=sys.stderr)
        except Exception as e:
            results["failed"].append((repo, f"put: {e}"))
            print(f"  FAIL put: {e}", file=sys.stderr)

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
