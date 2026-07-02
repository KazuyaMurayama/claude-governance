"""
Deploy the rule-enforcement package to all governed repos:

  1. HARD_RULES block (templates/hard-rules-block.md) inserted at the TOP of
     CLAUDE.md (right after the first H1). Refreshed in place when stale.
  2. .claude/hooks/{session_guard,pre_write_guard,post_bash_guard}.py
     (templates/hooks/*). Updated when content differs.
  3. .claude/settings.json: our hook wiring MERGED into existing settings
     (never overwrites existing keys/hooks; identified by script filename).

Target = repos whose CLAUDE.md contains GOVERNANCE_LINK_START (i.e. governed).
Others (ungoverned/excluded) are skipped and reported.

Usage: PYTHONIOENCODING=utf-8 python audits/deploy_rule_enforcement.py [--pilot repo1,repo2]
"""
import base64
import json
import os
import re
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from audit_43repos import OWNER, _TOKEN, discover_repos, fetch_raw  # noqa: E402

TPL = os.path.join(HERE, "..", "templates")

with open(os.path.join(TPL, "hard-rules-block.md"), encoding="utf-8") as f:
    HARD_RULES_BLOCK = f.read().strip()

HOOK_FILES = {}
for name in ("session_guard.py", "pre_write_guard.py", "post_bash_guard.py"):
    with open(os.path.join(TPL, "hooks", name), encoding="utf-8") as f:
        HOOK_FILES[name] = f.read()

def hook_cmd(script):
    return f"python .claude/hooks/{script} || python3 .claude/hooks/{script} || exit 0"

OUR_HOOKS = {
    "PreToolUse": {"matcher": "Write|Edit",
                   "hooks": [{"type": "command", "command": hook_cmd("pre_write_guard.py")}]},
    "PostToolUse": {"matcher": "Bash|PowerShell",
                    "hooks": [{"type": "command", "command": hook_cmd("post_bash_guard.py")}]},
    "Stop": {"hooks": [{"type": "command", "command": hook_cmd("session_guard.py")}]},
}
HOOK_MARKER = {"PreToolUse": "pre_write_guard.py", "PostToolUse": "post_bash_guard.py", "Stop": "session_guard.py"}

HR_RE = re.compile(r"<!-- HARD_RULES_START.*?-->\n.*?<!-- HARD_RULES_END -->", re.DOTALL)


def api(method, url, body=None):
    req = urllib.request.Request(url, method=method, headers={
        "Authorization": f"token {_TOKEN}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "rule-enforcement-deploy",
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
    }, data=json.dumps(body).encode("utf-8") if body else None)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return 404, None
        raise


def put_file(repo, branch, path, text, sha, message):
    body = {"message": message, "content": base64.b64encode(text.encode("utf-8")).decode("ascii"), "branch": branch}
    if sha:
        body["sha"] = sha
    return api("PUT", f"https://api.github.com/repos/{OWNER}/{repo}/contents/{path}", body)


def upsert_claude_md(repo, branch, log):
    status, content = fetch_raw(repo, branch, "CLAUDE.md")
    if status != 200:
        return "skip_no_claude_md"
    if "GOVERNANCE_LINK_START" not in content:
        return "skip_ungoverned"
    m = HR_RE.search(content)
    if m:
        current = m.group(0).strip()
        if current == HARD_RULES_BLOCK:
            log("CLAUDE.md up to date")
            return "ok"
        new_content = HR_RE.sub(HARD_RULES_BLOCK, content, count=1)
        msg = "docs(rules): refresh HARD_RULES block to canonical"
    else:
        lines = content.splitlines(keepends=True)
        idx = next((i for i, l in enumerate(lines) if l.startswith("# ")), None)
        if idx is None:
            new_content = HARD_RULES_BLOCK + "\n\n" + content
        else:
            lines.insert(idx + 1, "\n" + HARD_RULES_BLOCK + "\n")
            new_content = "".join(lines)
        msg = "docs(rules): add HARD_RULES Top10 block at top of CLAUDE.md"
    st, meta = api("GET", f"https://api.github.com/repos/{OWNER}/{repo}/contents/CLAUDE.md?ref={branch}")
    put_file(repo, branch, "CLAUDE.md", new_content, meta["sha"], msg)
    log("CLAUDE.md updated")
    return "ok"


def upsert_hooks(repo, branch, log):
    for name, text in HOOK_FILES.items():
        path = f".claude/hooks/{name}"
        st, meta = api("GET", f"https://api.github.com/repos/{OWNER}/{repo}/contents/{path}?ref={branch}")
        if st == 200:
            existing = base64.b64decode(meta["content"]).decode("utf-8")
            if existing == text:
                continue
            put_file(repo, branch, path, text, meta["sha"], f"chore(hooks): update {name} to canonical")
            log(f"{name} updated")
        else:
            put_file(repo, branch, path, text, None, f"chore(hooks): add {name} (rule enforcement guard)")
            log(f"{name} added")
        time.sleep(0.3)


def upsert_settings(repo, branch, log):
    path = ".claude/settings.json"
    st, meta = api("GET", f"https://api.github.com/repos/{OWNER}/{repo}/contents/{path}?ref={branch}")
    if st == 200:
        settings = json.loads(base64.b64decode(meta["content"]).decode("utf-8"))
        sha = meta["sha"]
    else:
        settings, sha = {}, None
    hooks = settings.setdefault("hooks", {})
    changed = False
    for event, entry in OUR_HOOKS.items():
        arr = hooks.setdefault(event, [])
        if not any(HOOK_MARKER[event] in json.dumps(e) for e in arr):
            arr.append(entry)
            changed = True
    if not changed:
        log("settings.json up to date")
        return
    text = json.dumps(settings, ensure_ascii=False, indent=2) + "\n"
    put_file(repo, branch, path, text, sha,
             "chore(hooks): wire rule-enforcement guards into settings.json (merge, no overwrite)")
    log("settings.json merged" if sha else "settings.json created")


def main():
    pilot = None
    for a in sys.argv[1:]:
        if a.startswith("--pilot"):
            pilot = sys.argv[sys.argv.index(a) + 1].split(",") if a == "--pilot" else a.split("=", 1)[1].split(",")
    repos = discover_repos()
    if pilot:
        repos = [r for r in repos if r["name"] in pilot]
    results = {"ok": [], "skip_ungoverned": [], "skip_no_claude_md": [], "failed": []}
    for i, meta in enumerate(repos, 1):
        repo, branch = meta["name"], meta["default_branch"]
        msgs = []
        log = lambda m: msgs.append(m)  # noqa: E731
        print(f"[{i}/{len(repos)}] {repo}", file=sys.stderr)
        try:
            state = upsert_claude_md(repo, branch, log)
            if state != "ok":
                results[state].append(repo)
                print(f"  SKIP ({state})", file=sys.stderr)
                continue
            upsert_hooks(repo, branch, log)
            upsert_settings(repo, branch, log)
            results["ok"].append(repo)
            print("  " + "; ".join(msgs), file=sys.stderr)
        except Exception as e:
            results["failed"].append((repo, str(e)))
            print(f"  FAIL: {e}", file=sys.stderr)
        time.sleep(0.3)
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
