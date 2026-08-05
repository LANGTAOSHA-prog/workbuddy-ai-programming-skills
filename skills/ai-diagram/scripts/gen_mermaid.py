#!/usr/bin/env python3
"""Generate Mermaid diagrams from a codebase or a description.

Pure standard library. Two modes:

  module  - scan a directory, build a module/import dependency graph
            (Python via ast; JS/TS via require/import regex). Emits a
            Mermaid flowchart.

  flow    - turn a simple "A -> B; B -> C" step list (or a bullet list from
            stdin) into a Mermaid flowchart.

  class   - turn lightweight "Class: field, field; method()" lines into a
            Mermaid classDiagram.

Usage:
  python3 gen_mermaid.py module PATH [--depth N] [--json]
  python3 gen_mermaid.py flow "A->B;B->C" [--json]
  python3 gen_mermaid.py class "User: id, name; save()" [--json]
"""
import ast
import json
import os
import re
import sys

SKIP_DIRS = {".git", "node_modules", "__pycache__", "venv", ".venv", "dist", "build"}
PY_EXT = {".py"}
JS_EXT = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}


def _node(name):
    # Mermaid node ids must be alphanumeric/underscore; quote labels with spaces
    safe = re.sub(r"\W", "_", name)
    return safe


def _modname(path, root):
    rel = os.path.relpath(path, root)
    rel = rel.replace(os.sep, "/")
    base, _ = os.path.splitext(rel)
    return base


def _scan_python_deps(path):
    try:
        src = open(path, encoding="utf-8", errors="replace").read()
        tree = ast.parse(src)
    except (OSError, SyntaxError):
        return []
    deps = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                deps.append(a.name)  # full dotted: pkg.worker
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                # candidate: the package and each imported submodule
                deps.append(node.module)
                for alias in node.names:
                    deps.append(node.module + "." + alias.name)
    return deps


IMPORT_RE = re.compile(r"(?:require|import\s+[^;]+?\bfrom)\s+['\"]([^'\"]+)['\"]")
DYNAMIC_IMPORT_RE = re.compile(r"import\(\s*['\"]([^'\"]+)['\"]\s*\)")


def _scan_js_deps(path):
    try:
        src = open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return []
    deps = IMPORT_RE.findall(src) + DYNAMIC_IMPORT_RE.findall(src)
    out = []
    for d in deps:
        if d.startswith("."):
            out.append(d)  # relative -> resolvable to a local module
        elif "/" in d or "." in d.split("/")[0]:
            out.append(d.split("/")[0])
    return out


def _local_modules(root):
    mods = {}
    for p in _iter_files(root):
        mods[_modname(p, root)] = p
    return mods


def _iter_files(root):
    for cur, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for n in names:
            if os.path.splitext(n)[1] in PY_EXT | JS_EXT:
                yield os.path.join(cur, n)


def gen_module(root, max_depth=99):
    root = os.path.abspath(root)
    local = _local_modules(root)
    local_set = set(local.keys())
    edges = []
    nodes = set()
    for path in local.values():
        mod = _modname(path, root)
        nodes.add(mod)
        if os.path.splitext(path)[1] in PY_EXT:
            deps = _scan_python_deps(path)
        else:
            deps = _scan_js_deps(path)
        for d in deps:
            # resolve dotted import to a local module path
            cand = d.replace(".", "/")
            target = None
            if cand in local_set:
                target = cand
            elif d in local_set:
                target = d
            if target:
                nodes.add(target)
                edges.append((mod, target))
    # limit depth of displayed graph by dropping farthest leaves if too big
    lines = ["flowchart TD"]
    for n in sorted(nodes):
        lines.append(f"    {_node(n)}[\"{n}\"]")
    for a, b in sorted(set(edges)):
        lines.append(f"    {_node(a)} --> {_node(b)}")
    return "\n".join(lines)


def gen_flow(spec):
    spec = spec.strip()
    chains = [c.strip() for c in re.split(r"[;\n]", spec) if c.strip()]
    lines = ["flowchart TD"]
    counter = 0
    for chain in chains:
        nodes = [n.strip() for n in chain.split("->") if n.strip()]
        ids = []
        for n in nodes:
            nid = f"S{counter}"
            lines.append(f'    {nid}["{n}"]')
            ids.append(nid)
            counter += 1
        for i in range(len(ids) - 1):
            lines.append(f"    {ids[i]} --> {ids[i+1]}")
    return "\n".join(lines)


REL_RE = re.compile(r"^\s*(\w+)\s*(-->|<--|<\|\|--|\*--|o--|--|->|<-)\s*(\w+)\s*$")
REL_MAP = {"->": "-->", "<-": "<--", "--": "--", "<|--": "<|--",
           "*--": "*--", "o--": "o--", "-->": "-->", "<--": "<--"}


def gen_class(spec):
    lines = ["classDiagram"]
    for decl in re.split(r"[;\n]", spec):
        decl = decl.strip()
        if not decl:
            continue
        m = REL_RE.match(decl)
        if m:
            arrow = REL_MAP.get(m.group(2), m.group(2))
            lines.append(f"    {m.group(1)} {arrow} {m.group(3)}")
            continue
        if ":" in decl:
            cls, body = decl.split(":", 1)
            cls = cls.strip()
            lines.append(f"    class {cls} {{")
            for member in body.split(","):
                member = member.strip()
                if not member:
                    continue
                if "(" in member:
                    mm = re.match(r"(\w+)\s*\(([^)]*)\)", member)
                    if mm:
                        lines.append(f"        +{mm.group(1)}()")
                    else:
                        lines.append(f"        +{member}")
                else:
                    lines.append(f"        +{member}")
            lines.append("    }")
        else:
            lines.append(f"    class {decl}")
    return "\n".join(lines)


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    as_json = False
    mode = argv[0] if argv and argv[0] in ("module", "flow", "class") else "module"
    rest = argv[1:] if mode in ("module", "flow", "class") else argv
    out = None
    max_depth = 99
    i = 0
    while i < len(rest):
        a = rest[i]
        if a == "--json":
            as_json = True
        elif a == "--depth":
            max_depth = int(rest[i + 1]); i += 1
        elif a == "--output":
            out = rest[i + 1]; i += 1
        else:
            spec = a
            # for module mode, rest[0] is the path
            break
        i += 1
    else:
        spec = None

    if mode == "module":
        if not spec or not os.path.isdir(spec):
            print("usage: gen_mermaid.py module PATH [--depth N] [--json]", file=sys.stderr)
            return 2
        diagram = gen_module(spec, max_depth)
    elif mode == "flow":
        spec = spec or sys.stdin.read()
        diagram = gen_flow(spec)
    elif mode == "class":
        spec = spec or sys.stdin.read()
        diagram = gen_class(spec)
    else:
        print("unknown mode", file=sys.stderr)
        return 2

    if as_json:
        print(json.dumps({"mode": mode, "diagram": diagram}, ensure_ascii=False, indent=2))
    elif out:
        open(out, "w", encoding="utf-8").write(diagram + "\n")
        print(f"written: {out}")
    else:
        print(diagram)
    return 0


if __name__ == "__main__":
    sys.exit(main())
