#!/usr/bin/env python3
"""
Jules Interactive CLI (Option C - immersive assistant)

Features:
 - REPL with stateful sessions
 - `auto` command: run pytest -> send failures -> apply patch / PR
 - `task "..."` command: arbitrary dev tasks (bugfix, refactor, tests, docs)
 - `session` command: create/list/select sessions
 - `apply` command: apply patch from last result
 - `commit` / `push` / `pr` helpers for GitHub
 - `exit` / `help`

Usage:
  python tools/jules_cli/cli.py
"""

import os
import time
import json
import shlex
import subprocess
from typing import Optional, Dict, Any, List
import requests

# Configuration
JULES_KEY = os.getenv("JULES_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
BASE = "https://jules.googleapis.com/v1alpha"
HEADERS = {"X-Goog-Api-Key": JULES_KEY, "Content-Type": "application/json"}
POLL_INTERVAL = 3
POLL_TIMEOUT = 300

# State
_state = {
    "current_session": None,   # last created session dict
    "last_result": None,       # {"type":"patch"/"pr", ...}
    "repo_source": None,       # source object used
    "repo_owner": None,
    "repo_name": None
}

# ---------- Utilities ----------

def check_env():
    if not JULES_KEY:
        raise RuntimeError("JULES_API_KEY not set in environment. Set it before running.")

def run_cmd(cmd: List[str], capture=True):
    try:
        if capture:
            p = subprocess.run(cmd, capture_output=True, text=True, check=False)
            return p.returncode, p.stdout, p.stderr
        else:
            p = subprocess.run(cmd, check=True)
            return p.returncode, "", ""
    except Exception as e:
        return 1, "", str(e)

def run_pytest() -> (int, str, str):
    print("[+] Running pytest...")
    return run_cmd(["pytest", "-q", "--maxfail=1"])

def _http_request(method: str, path: str, json_data: Optional[dict] = None, params: Optional[dict] = None, timeout=60):
    url = f"{BASE}{path}"
    try:
        resp = requests.request(method, url, headers=HEADERS, json=json_data, params=params, timeout=timeout)
    except Exception as e:
        raise RuntimeError(f"HTTP request failed: {e}")
    if resp.status_code == 401:
        raise RuntimeError(f"401 UNAUTHENTICATED from Jules API. Check API key.\nBody: {resp.text}")
    if resp.status_code >= 400:
        raise RuntimeError(f"Jules API returned {resp.status_code}:\n{resp.text}")
    try:
        return resp.json()
    except ValueError:
        raise RuntimeError(f"Invalid JSON response: {resp.text[:2000]}")

# ---------- Jules API helpers ----------

def list_sources() -> List[dict]:
    return _http_request("GET", "/sources").get("sources", [])

def pick_source_for_repo(repo_name: str) -> Optional[dict]:
    for s in list_sources():
        gr = s.get("githubRepo") or {}
        if gr.get("repo") == repo_name:
            return s
    for s in list_sources():
        if repo_name in (s.get("name") or ""):
            return s
    return None

def create_session(prompt: str, source_name: str, starting_branch="main", title="Jules CLI session", automation_mode=None) -> dict:
    payload = {
        "prompt": prompt,
        "sourceContext": {"source": source_name, "githubRepoContext": {"startingBranch": starting_branch}},
        "title": title
    }
    if automation_mode:
        payload["automationMode"] = automation_mode
    return _http_request("POST", "/sessions", json_data=payload)

def list_sessions(page_size=20):
    return _http_request("GET", "/sessions", params={"pageSize": page_size})

def get_session(session_id: str):
    return _http_request("GET", f"/sessions/{session_id}")

def list_activities(session_id: str, page_size=50):
    return _http_request("GET", f"/sessions/{session_id}/activities", params={"pageSize": page_size})

def send_message(session_id: str, prompt: str):
    return _http_request("POST", f"/sessions/{session_id}:sendMessage", json_data={"prompt": prompt})

# ---------- Polling / extraction ----------

def poll_for_result(session_id: str, timeout=POLL_TIMEOUT):
    t0 = time.time()
    print(f"[+] Polling session {session_id} for up to {timeout}s...")
    while True:
        activities = list_activities(session_id).get("activities", [])
        # newest-first
        for act in reversed(activities):
            for art in act.get("artifacts", []):
                cs = art.get("changeSet")
                if cs:
                    gp = cs.get("gitPatch") or {}
                    patch = gp.get("unidiffPatch")
                    if patch:
                        return {"type": "patch", "patch": patch, "activity": act}
                pr = art.get("pullRequest")
                if pr:
                    return {"type": "pr", "pr": pr, "activity": act}
        # check session outputs
        sess = get_session(session_id)
        if sess.get("outputs"):
            for out in sess["outputs"]:
                if out.get("pullRequest"):
                    return {"type": "pr", "pr": out["pullRequest"], "session": sess}
        if time.time() - t0 > timeout:
            raise TimeoutError("Timed out waiting for Jules outputs.")
        time.sleep(POLL_INTERVAL)

# ---------- Patch application & git helpers ----------

def apply_patch_text(patch_text: str):
    tmp = "tmp_patch.diff"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(patch_text)
    print("[+] Applying patch via 'patch -p1 -i tmp_patch.diff' ...")
    code, out, err = run_cmd(["patch", "-p1", "-i", tmp])
    os.remove(tmp)
    if code != 0:
        print("[!] Patch failed; stdout/stderr:")
        print(out)
        print(err)
        raise RuntimeError("patch failed")
    print("[+] Patch applied successfully.")

def git_current_branch() -> str:
    code, out, _ = run_cmd(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    return out.strip() if code == 0 else "main"

def git_create_branch_and_commit(branch_name: str, commit_message: str = "jules: automated fix"):
    run_cmd(["git", "checkout", "-b", branch_name], capture=False)
    run_cmd(["git", "add", "-A"], capture=False)
    run_cmd(["git", "commit", "-m", commit_message], capture=False)

def git_push_branch(branch_name: str):
    run_cmd(["git", "push", "-u", "origin", branch_name], capture=False)

def github_create_pr(owner: str, repo: str, head: str, base: str = "main", title: str = None, body: str = None):
    if not GITHUB_TOKEN:
        raise RuntimeError("GITHUB_TOKEN not set; cannot create PR automatically.")
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    data = {"head": head, "base": base, "title": title or "Automated fix from Jules CLI", "body": body or ""}
    resp = requests.post(url, headers=headers, json=data, timeout=30)
    if resp.status_code >= 400:
        raise RuntimeError(f"GitHub PR creation failed {resp.status_code}: {resp.text}")
    return resp.json()

# ---------- High-level flows ----------

def auto_fix_command(repo_dir_name="bot_platform"):
    # run pytest first
    code, out, err = run_pytest()
    if code == 0:
        print("🎉 All tests passed. Nothing to do.")
        return
    failure_text = out + "\n" + err
    run_task(prompt_from_failure(failure_text), repo_dir_name=repo_dir_name, auto=True)

def prompt_from_failure(failure_text: str) -> str:
    return (
        "You are Jules, an automated debugging assistant. I will paste pytest output. "
        "Produce a minimal, correct fix and include any new tests required. "
        "Return changes as changeSet.gitPatch.unidiffPatch or create a PR artifact. "
        "Pytest output:\n" + failure_text
    )

def run_task(user_prompt: str, repo_dir_name: str = "bot_platform", automation_mode: Optional[str] = "AUTO_CREATE_PR"):
    # pick source
    source_obj = pick_source_for_repo(repo_dir_name)
    if not source_obj:
        available = [s.get("name") for s in list_sources()]
        raise RuntimeError(f"No source matched repo '{repo_dir_name}'. Available: {available}")
    source_name = source_obj["name"]
    owner = source_obj["githubRepo"]["owner"]
    repo = source_obj["githubRepo"]["repo"]
    print(f"[+] Using Jules source: {source_name} (repo {owner}/{repo})")

    # create session
    print("[+] Creating Jules session...")
    sess = create_session(prompt=user_prompt, source_name=source_name, starting_branch="main",
                          title="Jules CLI interactive", automation_mode=automation_mode)
    _state["current_session"] = sess
    sid = sess.get("id")
    if not sid:
        raise RuntimeError(f"Failed to create session: {sess}")
    print(f"[+] Session created: {sid}. Polling for result...")
    result = poll_for_result(sid)
    _state["last_result"] = result
    _state["repo_source"] = source_name
    _state["repo_owner"] = owner
    _state["repo_name"] = repo
    print("[+] Result received:", result["type"])
    if result["type"] == "patch":
        print("[+] Patch available in last_result['patch']. Use `apply` to apply locally.")
    elif result["type"] == "pr":
        pr = result.get("pr")
        print("[+] PR artifact:", json.dumps(pr, indent=2))
    return result

# ---------- Interactive REPL ----------

WELCOME = """
Jules Interactive CLI — fully immersive developer assistant.

Commands:
  auto                      Run pytest and auto-fix failures
  task "your instruction"    Ask Jules to perform arbitrary dev task (bugfix/refactor/tests/docs)
  session list              List sessions
  session show <SESSION_ID> Show session details
  apply                     Apply last patch received
  commit                    Commit & create branch after apply (if patch applied locally)
  push                      Push branch to origin
  pr create                 Create a GitHub PR from last branch (requires GITHUB_TOKEN)
  last                      Show last result/session
  help                      Show this help
  exit                      Quit
"""

def cmd_session_list():
    j = list_sessions()
    print(json.dumps(j, indent=2))

def cmd_session_show(session_id: str):
    s = get_session(session_id)
    print(json.dumps(s, indent=2))

def cmd_apply():
    res = _state.get("last_result")
    if not res:
        print("No last result to apply.")
        return
    if res["type"] != "patch":
        print("Last result is not a patch. It may be a PR artifact.")
        return
    patch = res["patch"]
    apply_patch_text(patch)

def cmd_commit_and_push():
    # create branch with timestamp
    ts = int(time.time())
    branch = f"jules/auto-{ts}"
    try:
        git_create_branch_and_commit(branch, commit_message="chore: automated changes from Jules")
    except Exception as e:
        print("Failed to commit:", e)
        return
    try:
        git_push_branch(branch)
        print(f"Pushed branch {branch}")
    except Exception as e:
        print("Failed to push automatically:", e)
        print(f"Run: git push origin {branch}")

def cmd_create_pr():
    if not GITHUB_TOKEN:
        print("GITHUB_TOKEN not set; cannot create PR.")
        return
    owner = _state.get("repo_owner"); repo = _state.get("repo_name")
    if not owner or not repo:
        print("No repo detected in state. Run a task first.")
        return
    # determine current branch to use as head
    head = git_current_branch()
    try:
        pr = github_create_pr(owner, repo, head=head, base="main", title="Automated fix from Jules CLI", body="Auto PR")
        print("Created PR:", pr.get("html_url"))
    except Exception as e:
        print("Failed to create PR:", e)

def repl():
    print(WELCOME)
    while True:
        try:
            raw = input("jules> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        if not raw:
            continue
        parts = shlex.split(raw)
        cmd = parts[0].lower()
        args = parts[1:]
        try:
            if cmd in ("exit", "quit"):
                break
            elif cmd == "help":
                print(WELCOME)
            elif cmd == "auto":
                auto_fix_command()
            elif cmd == "task":
                # join remainder as the prompt
                prompt = raw[len("task"):].strip()
                if not prompt:
                    print("Usage: task \"Your description here\"")
                    continue
                # if user wraps with quotes, strip them
                if (prompt.startswith('"') and prompt.endswith('"')) or (prompt.startswith("'") and prompt.endswith("'")):
                    prompt = prompt[1:-1]
                run_task(prompt)
            elif cmd == "session" and args and args[0] == "list":
                cmd_session_list()
            elif cmd == "session" and args and args[0] == "show" and len(args) > 1:
                cmd_session_show(args[1])
            elif cmd == "apply":
                cmd_apply()
            elif cmd == "commit":
                cmd_commit_and_push()
            elif cmd == "push":
                # assume last created branch is current; push current branch
                branch = git_current_branch()
                try:
                    git_push_branch(branch)
                except Exception as e:
                    print("Push failed:", e)
            elif cmd == "pr" and args and args[0] == "create":
                cmd_create_pr()
            elif cmd == "last":
                print("current_session:", json.dumps(_state.get("current_session"), indent=2))
                print("last_result:", json.dumps(_state.get("last_result"), indent=2))
            else:
                print("Unknown command. Type 'help' for commands.")
        except Exception as e:
            print("[!] Error during command:", e)

# ---------- Main ----------

def main():
    check_env()
    print("Jules CLI starting. JULES_API_KEY detected.")
    repl()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Fatal error:", e)
        raise