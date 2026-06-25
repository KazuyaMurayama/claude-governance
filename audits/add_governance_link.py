"""
Append a "上位ガバナンスへの参照" block to each repo's CLAUDE.md via GitHub Contents API.
Skips:
  - repos already containing the marker `<!-- GOVERNANCE_LINK_START -->`
  - repos already mentioning `claude-governance`
  - repos in EXCLUSIONS.md (any partial-exemption including governance_link)
  - repos without CLAUDE.md
"""
import json
import os
import re
import subprocess
import sys
import urllib.request
import base64

OWNER = "KazuyaMurayama"
HERE = os.path.dirname(os.path.abspath(__file__))

# Re-use the same repo list as audit_43repos.py
sys.path.insert(0, HERE)
from audit_43repos import REPOS, EXCLUSIONS  # noqa

GOVERNANCE_BLOCK = """
---

## 上位ガバナンスへの参照

<!-- GOVERNANCE_LINK_START -->
- 本リポの運用は [KazuyaMurayama/claude-governance](https://github.com/KazuyaMurayama/claude-governance) の正典に準拠する
- 競合した場合は本リポの CLAUDE.md が優先（リポ固有ルールが上位ガバナンスに勝つ）
- 上位ガバナンスを変更した際は、本リポの CLAUDE.md にも反映する責務がある
- 監査スクリプト: `claude-governance/audits/audit_43repos.py` を実行することで本リポの適合状況を確認できる
<!-- GOVERNANCE_LINK_END -->
"""

def get_token():
    proc = subprocess.run(
        ["git", "credential", "fill"],
        input="protocol=https\nhost=github.com\n\n",
        capture_output=True, text=True, timeout=15,
    )
    for line in proc.stdout.splitlines():
        if line.startswith("password="):
            return line.split("=", 1)[1]
    raise RuntimeError("token unavailable")

def get_file(repo, branch, path, token):
    url = f"https://api.github.com/repos/{OWNER}/{repo}/contents/{path}?ref={branch}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "governance-link-script",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise

def put_file(repo, branch, path, new_content_b64, sha, message, token):
    url = f"https://api.github.com/repos/{OWNER}/{repo}/contents/{path}"
    body = json.dumps({
        "message": message,
        "content": new_content_b64,
        "sha": sha,
        "branch": branch,
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="PUT", headers={
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "governance-link-script",
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, json.loads(r.read().decode("utf-8"))

def main():
    token = get_token()
    results = {"updated": [], "skipped_excluded": [], "skipped_already_has": [], "skipped_no_claude_md": [], "failed": []}
    for i, (repo, branch) in enumerate(REPOS, 1):
        print(f"[{i}/{len(REPOS)}] {repo}", file=sys.stderr)
        # 1. Excluded?
        ex = EXCLUSIONS.get(repo)
        if ex and ("governance_link" in (ex.get("exempt_dims") or []) or ex.get("scope") == "full"):
            results["skipped_excluded"].append(repo)
            print(f"  SKIP (excluded)", file=sys.stderr)
            continue
        # 2. Fetch CLAUDE.md
        try:
            f = get_file(repo, branch, "CLAUDE.md", token)
        except Exception as e:
            results["failed"].append((repo, f"fetch: {e}"))
            print(f"  FAIL fetch: {e}", file=sys.stderr)
            continue
        if f is None:
            results["skipped_no_claude_md"].append(repo)
            print(f"  SKIP (no CLAUDE.md)", file=sys.stderr)
            continue
        sha = f["sha"]
        content = base64.b64decode(f["content"]).decode("utf-8")
        # 3. Already has marker or mention?
        if "<!-- GOVERNANCE_LINK_START -->" in content:
            results["skipped_already_has"].append(repo)
            print(f"  SKIP (marker exists)", file=sys.stderr)
            continue
        if "claude-governance" in content:
            results["skipped_already_has"].append(repo)
            print(f"  SKIP (claude-governance mentioned)", file=sys.stderr)
            continue
        # 4. Append block. Ensure trailing newline.
        if not content.endswith("\n"):
            content += "\n"
        new_content = content + GOVERNANCE_BLOCK
        # 5. PUT
        new_b64 = base64.b64encode(new_content.encode("utf-8")).decode("ascii")
        try:
            status, resp = put_file(
                repo, branch, "CLAUDE.md", new_b64, sha,
                "docs(governance): add upstream governance reference block (claude-governance)",
                token,
            )
            results["updated"].append(repo)
            print(f"  OK status={status} sha={resp.get('commit',{}).get('sha','')[:7]}", file=sys.stderr)
        except Exception as e:
            results["failed"].append((repo, f"put: {e}"))
            print(f"  FAIL put: {e}", file=sys.stderr)

    print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
