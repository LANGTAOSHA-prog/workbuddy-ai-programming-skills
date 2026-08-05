#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 git 历史生成 CHANGELOG 片段(遵循 Keep a Changelog + Conventional Commits)。

用法:
  python3 gen_changelog.py [--since TAG] [--range A..B] [--version X.Y.Z]
                          [--date YYYY-MM-DD] [--output FILE] [--json]

功能:
  - 解析 `git log` 提交,按 Conventional Commits 类型分组:
    feat -> Added, fix -> Fixed, perf -> Performance,
    refactor -> Changed, docs -> Documentation, test -> Tests,
    build/ci -> Build, chore -> Chore, revert -> Reverted, 其它 -> Other
  - 自动推断最新版本标签作为起点(--since)
  - 输出可直接粘贴进 CHANGELOG.md 的 markdown 片段
  - 支持写入文件或直接打印

仅使用 Python 标准库(通过 subprocess 调用 git)。
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

# Conventional Commits type -> CHANGELOG 分组标题
TYPE_TO_SECTION = {
    "feat": "Added",
    "fix": "Fixed",
    "perf": "Performance",
    "refactor": "Changed",
    "docs": "Documentation",
    "style": "Changed",
    "test": "Tests",
    "build": "Build",
    "ci": "Build",
    "chore": "Chore",
    "revert": "Reverted",
}

SECTION_ORDER = [
    "Added", "Changed", "Fixed", "Performance",
    "Documentation", "Tests", "Build", "Chore", "Reverted", "Other",
]


def run(args, cwd=None):
    try:
        out = subprocess.run(
            ["git"] + args, cwd=cwd, capture_output=True, text=True, check=True
        )
        return out.stdout.strip()
    except subprocess.CalledProcessError:
        return ""


def latest_tag(cwd):
    tags = run(["tag", "--sort=-creatordate"], cwd)
    if not tags:
        return None
    return tags.splitlines()[0].strip()


def collect_commits(rng, cwd):
    # subject only: <hash> <subject>
    out = run(["log", rng, "--no-merges", "--pretty=format:%H %s"], cwd)
    if not out:
        return []
    items = []
    for ln in out.splitlines():
        ln = ln.strip()
        if not ln:
            continue
        h, _, subj = ln.partition(" ")
        items.append((h[:8], subj.strip()))
    return items


def clean_subject(subj):
    # strip conventional prefix "type(scope): " or "type: "
    subj = re.sub(r'^\w+(?:\([^)]*\))?!?:\s*', '', subj)
    # strip issue refs for readability but keep them optionally
    return subj.strip()


def group(commits):
    sections = {s: [] for s in SECTION_ORDER}
    for h, subj in commits:
        m = re.match(r'(\w+)(?:\([^)]*\))?!?:\s', subj)
        t = m.group(1).lower() if m else None
        section = TYPE_TO_SECTION.get(t, "Other")
        text = clean_subject(subj)
        if text:
            sections[section].append(f"{text} (`{h}`)")
    return sections


def render(version, dt, sections):
    lines = [f"## [{version}] - {dt}", ""]
    any_entry = False
    for sec in SECTION_ORDER:
        entries = sections.get(sec)
        if not entries:
            continue
        any_entry = True
        lines.append(f"### {sec}")
        for e in entries:
            lines.append(f"- {e}")
        lines.append("")
    if not any_entry:
        lines.append("_No notable changes._")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main():
    ap = argparse.ArgumentParser(description="Generate a CHANGELOG section from git history.")
    ap.add_argument("--since", help="Tag/ref to start from (default: latest tag)")
    ap.add_argument("--range", help="Explicit git range, e.g. v1.0.0..v1.1.0")
    ap.add_argument("--version", help="Version label for the section (e.g. 1.2.0)")
    ap.add_argument("--date", help="Date YYYY-MM-DD (default: today)")
    ap.add_argument("--output", help="Write to file instead of stdout")
    ap.add_argument("--json", action="store_true", help="Output grouped JSON")
    ap.add_argument("path", nargs="?", default=".", help="Repo directory (default: cwd)")
    args = ap.parse_args()

    cwd = str(Path(args.path).resolve())
    if not (Path(cwd) / ".git").exists():
        print("error: not a git repository", file=sys.stderr)
        sys.exit(1)

    if args.range:
        rng = args.range
    else:
        since = args.since or latest_tag(cwd)
        rng = f"{since}..HEAD" if since else "HEAD"

    commits = collect_commits(rng, cwd)
    sections = group(commits)

    if args.json:
        print(json.dumps({
            "range": rng,
            "version": args.version or "Unreleased",
            "sections": {k: v for k, v in sections.items() if v},
        }, ensure_ascii=False, indent=2))
        return

    version = args.version or ("Unreleased" if (args.since or latest_tag(cwd)) else "0.1.0")
    dt = args.date or date.today().isoformat()
    text = render(version, dt, sections)

    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"wrote {args.output} ({len(commits)} commits)")
    else:
        print(text)


if __name__ == "__main__":
    main()
