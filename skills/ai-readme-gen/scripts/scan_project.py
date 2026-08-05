#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""扫描项目目录,输出用于生成 README 的结构化摘要。

子命令/用法:
  python3 scan_project.py [path] [--json] [--depth N] [--max-files N]

功能:
  - 目录树(自动忽略 .git / node_modules / __pycache__ 等)
  - 各语言文件数(按扩展名统计)
  - 识别清单文件(package.json / pyproject.toml / go.mod / Cargo.toml /
    pom.xml / requirements.txt)并抽取名称/版本/描述/关键依赖
  - 推断入口文件(main / index / App / __main__)
  - 是否已有 README
  - 代码行数估计

仅使用 Python 标准库。
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

# 扫描时跳过的目录与文件
SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "env",
    ".idea", ".vscode", "dist", "build", ".tox", ".mypy_cache",
    ".pytest_cache", "target", "bin", "obj", ".svelte-kit",
}
SKIP_FILES = {".DS_Store", "Thumbs.db", "package-lock.json",
              "yarn.lock", "poetry.lock", "pnpm-lock.yaml"}

# 扩展名 -> 语言
LANG_MAP = {
    ".py": "Python", ".js": "JavaScript", ".jsx": "JavaScript",
    ".ts": "TypeScript", ".tsx": "TypeScript", ".go": "Go",
    ".rs": "Rust", ".java": "Java", ".kt": "Kotlin", ".c": "C",
    ".h": "C/C++", ".cpp": "C++", ".cc": "C++", ".hpp": "C++",
    ".cs": "C#", ".rb": "Ruby", ".php": "PHP", ".swift": "Swift",
    ".m": "Objective-C", ".sql": "SQL", ".sh": "Shell",
    ".html": "HTML", ".css": "CSS", ".scss": "SCSS", ".vue": "Vue",
    ".r": "R", ".jl": "Julia", ".lua": "Lua", ".dart": "Dart",
    ".ex": "Elixir", ".exs": "Elixir", ".scala": "Scala",
    ".tf": "Terraform", ".yaml": "YAML", ".yml": "YAML",
}

ENTRY_HINTS = (
    "main.py", "app.py", "__main__.py", "index.js", "main.js",
    "App.tsx", "main.ts", "index.ts", "main.go", "cmd", "main.rs",
    "src/main.rs", "Program.cs", "server.js", "server.py",
)

README_NAMES = {"README.md", "readme.md", "README.rst", "README.txt", "readme.md"}


def iter_files(root: Path, depth: int, max_files: int):
    """Yield (rel_path, depth) for files under root within limits."""
    count = 0
    stack = [(root, 0)]
    while stack:
        d, dep = stack.pop()
        if dep > depth:
            continue
        try:
            entries = sorted(os.scandir(d), key=lambda e: e.name)
        except PermissionError:
            continue
        for e in entries:
            if e.is_dir():
                if e.name in SKIP_DIRS:
                    continue
                stack.append((Path(e.path), dep + 1))
            else:
                if e.name in SKIP_FILES:
                    continue
                count += 1
                if count > max_files:
                    return
                yield Path(e.path), dep


def build_tree(root: Path, depth: int, max_files: int):
    """Return a nested dict tree of directories/files."""
    tree = {}
    for p, dep in iter_files(root, depth, max_files):
        rel = p.relative_to(root)
        parts = rel.parts
        node = tree
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = None  # file marker
    return tree


def count_languages(root: Path, depth: int, max_files: int):
    langs = {}
    for p, _ in iter_files(root, depth, max_files):
        ext = p.suffix.lower()
        lang = LANG_MAP.get(ext)
        if lang:
            langs[lang] = langs.get(lang, 0) + 1
    return dict(sorted(langs.items(), key=lambda kv: -kv[1]))


def read_text(path: Path, limit: int = 4000) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read(limit)
    except OSError:
        return ""


def parse_manifest(root: Path):
    """Detect and parse common manifest files."""
    info = {}
    # package.json
    pj = root / "package.json"
    if pj.exists():
        txt = read_text(pj)
        name = re.search(r'"name"\s*:\s*"([^"]+)"', txt)
        ver = re.search(r'"version"\s*:\s*"([^"]+)"', txt)
        desc = re.search(r'"description"\s*:\s*"([^"]+)"', txt)
        deps = re.findall(r'"(?:dependencies|devDependencies)"\s*:\s*{([^}]*)}', txt)
        dep_pkgs = []
        for block in deps:
            dep_pkgs += re.findall(r'"([^"]+)"\s*:', block)
        info["package.json"] = {
            "name": name.group(1) if name else None,
            "version": ver.group(1) if ver else None,
            "description": desc.group(1) if desc else None,
            "dependencies": dep_pkgs[:30],
        }
    # pyproject.toml
    pt = root / "pyproject.toml"
    if pt.exists():
        txt = read_text(pt)
        name = re.search(r'name\s*=\s*["\']([^"\']+)["\']', txt)
        ver = re.search(r'version\s*=\s*["\']([^"\']+)["\']', txt)
        desc = re.search(r'description\s*=\s*["\']([^"\']+)["\']', txt)
        deps = re.findall(r'(?:dependencies|requires)\s*=\s*\[([^\]]*)\]', txt)
        dep_pkgs = []
        for block in deps:
            dep_pkgs += re.findall(r'["\']([^"\']+)["\']', block)
        info["pyproject.toml"] = {
            "name": name.group(1) if name else None,
            "version": ver.group(1) if ver else None,
            "description": desc.group(1) if desc else None,
            "dependencies": dep_pkgs[:30],
        }
    # go.mod
    gm = root / "go.mod"
    if gm.exists():
        txt = read_text(gm)
        module = re.search(r'module\s+(\S+)', txt)
        gover = re.search(r'go\s+(\S+)', txt)
        reqs = re.findall(r'^\s*([\w./-]+)\s+([\w./+-]+)', txt, re.M)
        info["go.mod"] = {
            "module": module.group(1) if module else None,
            "go": gover.group(1) if gover else None,
            "dependencies": [f"{m} {v}" for m, v in reqs[:30]],
        }
    # Cargo.toml
    cm = root / "Cargo.toml"
    if cm.exists():
        txt = read_text(cm)
        name = re.search(r'name\s*=\s*["\']([^"\']+)["\']', txt)
        ver = re.search(r'version\s*=\s*["\']([^"\']+)["\']', txt)
        info["Cargo.toml"] = {
            "name": name.group(1) if name else None,
            "version": ver.group(1) if ver else None,
        }
    # requirements.txt
    rq = root / "requirements.txt"
    if rq.exists():
        txt = read_text(rq, 8000)
        deps = [l.strip() for l in txt.splitlines()
                if l.strip() and not l.startswith("#")]
        info["requirements.txt"] = {"dependencies": deps[:40]}
    return info


def detect_entry(root: Path):
    found = []
    for hint in ENTRY_HINTS:
        if (root / hint).exists():
            found.append(hint)
    # also look at manifest entry points
    return found


def has_readme(root: Path):
    for n in README_NAMES:
        if (root / n).exists():
            return n
    return None


def estimate_lines(root: Path, depth: int, max_files: int):
    total = 0
    for p, _ in iter_files(root, depth, max_files):
        if p.suffix.lower() in LANG_MAP:
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as f:
                    total += sum(1 for _ in f)
            except OSError:
                pass
    return total


def scan(root: Path, depth: int, max_files: int):
    return {
        "path": str(root.resolve()),
        "has_readme": has_readme(root),
        "languages": count_languages(root, depth, max_files),
        "estimated_code_lines": estimate_lines(root, depth, max_files),
        "manifests": parse_manifest(root),
        "entry_points": detect_entry(root),
        "tree": build_tree(root, depth, max_files),
    }


def main():
    ap = argparse.ArgumentParser(description="Scan a project for README generation.")
    ap.add_argument("path", nargs="?", default=".", help="Project directory (default: cwd)")
    ap.add_argument("--json", action="store_true", help="Output raw JSON")
    ap.add_argument("--depth", type=int, default=3, help="Max tree depth (default 3)")
    ap.add_argument("--max-files", type=int, default=400, help="Max files to scan")
    args = ap.parse_args()

    root = Path(args.path).resolve()
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        sys.exit(1)

    result = scan(root, args.depth, args.max_files)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # Human-readable summary
    print(f"# Project scan: {result['path']}")
    print(f"Existing README : {result['has_readme'] or 'NONE'}")
    print(f"Code lines est. : {result['estimated_code_lines']}")
    if result["entry_points"]:
        print(f"Entry points   : {', '.join(result['entry_points'])}")
    print("\n## Languages")
    for lang, n in result["languages"].items():
        print(f"  {lang:<12} {n} files")
    if result["manifests"]:
        print("\n## Manifests")
        for mf, data in result["manifests"].items():
            print(f"  {mf}: {data}")
    print("\n## Tree")
    def _print(node, prefix=""):
        items = sorted(node.items())
        for i, (k, v) in enumerate(items):
            last = i == len(items) - 1
            conn = "└── " if last else "├── "
            print(prefix + conn + k)
            if v is not None:
                _print(v, prefix + ("    " if last else "│   "))
    _print(result["tree"])


if __name__ == "__main__":
    main()
