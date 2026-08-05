#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""收集 Pull Request 所需的 git 上下文,输出结构化摘要。

用法:
  python3 gen_pr_context.py [--base BRANCH] [--json]

收集内容:
  - 当前分支名
  - 自动推断的 base 分支(main / master / develop / 指定)
  - base..HEAD 的提交列表(oneline)
  - base...HEAD 的 diff stat(变更文件与增删行)
  - 提交信息中关联的 issue(#123 / Closes #456)
  - Conventional Commits 类型分布(feat/fix/...)

仅使用 Python 标准库(通过 subprocess 调用 git)。
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

CANDIDATE_BASES = ["main", "master", "develop", "trunk"]


def run(args, cwd=None):
    try:
        out = subprocess.run(
            ["git"] + args, cwd=cwd, capture_output=True, text=True, check=True
        )
        return out.stdout.strip()
    except subprocess.CalledProcessError as e:
        # Return stderr so callers can surface it; empty for "no output"
        return ""


def current_branch(cwd):
    return run(["rev-parse", "--abbrev-ref", "HEAD"], cwd)


def branch_exists(name, cwd):
    return bool(run(["rev-parse", "--verify", name], cwd))


def detect_base(cwd, explicit=None):
    if explicit:
        return explicit if branch_exists(explicit, cwd) else None
    for b in CANDIDATE_BASES:
        if branch_exists(b, cwd):
            return b
    return None


def list_commits(base, cwd):
    rng = f"{base}..HEAD" if base else "HEAD"
    out = run(["log", rng, "--oneline", "--no-merges"], cwd)
    if not out:
        return []
    return [ln.strip() for ln in out.splitlines() if ln.strip()]


def diff_stat(base, cwd):
    rng = f"{base}..." if base else "HEAD"
    out = run(["diff", "--stat", rng], cwd)
    if not out:
        return []
    # Skip trailing summary line if present
    lines = [ln for ln in out.splitlines() if ln.strip()]
    files = []
    for ln in lines:
        m = re.match(r"^(.*?)\s*\|\s*(\d+)\s*([+-]*)$", ln)
        if m:
            files.append({
                "file": m.group(1).strip(),
                "changes": int(m.group(2)),
                "marker": m.group(3),
            })
    return files


def linked_issues(commits):
    issues = set()
    for c in commits:
        for m in re.findall(r'(?:#|close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+#(\d+)',
                            c, re.IGNORECASE):
            issues.add(int(m))
    return sorted(issues)


def classify(commits):
    types = {}
    for c in commits:
        m = re.match(r'\S+\s+(\w+)(?:\([^)]*\))?!?:\s', c)
        if m:
            t = m.group(1).lower()
            types[t] = types.get(t, 0) + 1
    return types


def main():
    ap = argparse.ArgumentParser(description="Gather git context for a PR description.")
    ap.add_argument("--base", help="Base branch (default: auto-detect)")
    ap.add_argument("--json", action="store_true", help="Output raw JSON")
    ap.add_argument("path", nargs="?", default=".", help="Repo directory (default: cwd)")
    args = ap.parse_args()

    cwd = str(Path(args.path).resolve())

    if not (Path(cwd) / ".git").exists():
        print("error: not a git repository", file=sys.stderr)
        sys.exit(1)

    branch = current_branch(cwd)
    base = detect_base(cwd, args.base)
    commits = list_commits(base, cwd)
    files = diff_stat(base, cwd)
    issues = linked_issues(commits)
    types = classify(commits)

    result = {
        "current_branch": branch,
        "base_branch": base,
        "commit_count": len(commits),
        "commits": commits,
        "changed_files": files,
        "linked_issues": issues,
        "commit_types": types,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    print(f"# PR context")
    print(f"Branch : {branch or '(detached)'}")
    print(f"Base   : {base or '(none detected)'}")
    print(f"Commits: {len(commits)}")
    if types:
        print(f"Types  : {', '.join(f'{k}:{v}' for k, v in types.items())}")
    if issues:
        print(f"Issues : {', '.join('#' + str(i) for i in issues)}")
    if commits:
        print("\n## Commits")
        for c in commits:
            print(f"  - {c}")
    if files:
        print("\n## Changed files")
        for f in files:
            print(f"  {f['changes']:>5}  {f['file']}")


if __name__ == "__main__":
    main()
