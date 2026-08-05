#!/usr/bin/env python3
"""Statically flag common code smells to feed refactor suggestions.

Pure standard library. Python is parsed with `ast`; JS/TS is parsed with a
lightweight regex/brace scanner (good enough to surface smells, not a full parser).

Usage:
  python3 analyze_smells.py PATH [PATH ...] [--json] [--max-lines 60] [--max-params 4] [--max-depth 4]

PATH may be a file or a directory (recursed, skipping venv/.git/node_modules).
"""
import ast
import json
import os
import re
import sys

DEFAULT_MAX_LINES = 60
DEFAULT_MAX_PARAMS = 4
DEFAULT_MAX_DEPTH = 4

SKIP_DIRS = {".git", "node_modules", "__pycache__", "venv", ".venv", "dist", "build"}

PY_EXT = {".py"}
JS_EXT = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}


def _walk(paths):
    files = []
    for p in paths:
        if os.path.isfile(p):
            files.append(p)
        else:
            for root, dirs, names in os.walk(p):
                dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
                for n in names:
                    if os.path.splitext(n)[1] in PY_EXT | JS_EXT:
                        files.append(os.path.join(root, n))
    return files


# ---------- Python analysis ----------
def _analyze_python(src, max_lines, max_params, max_depth):
    findings = []

    def depth_of(node):
        # measure maximum indentation-driven nesting of compound statements
        maxd = 0
        stack = [(node, 0)]
        while stack:
            cur, d = stack.pop()
            for child in ast.iter_child_nodes(cur):
                if isinstance(child, (ast.If, ast.For, ast.While, ast.With,
                                      ast.Try, ast.FunctionDef, ast.AsyncFunctionDef,
                                      ast.AsyncFor, ast.AsyncWith)):
                    maxd = max(maxd, d + 1)
                    stack.append((child, d + 1))
        return maxd

    class V(ast.NodeVisitor):
        def __init__(self):
            self.in_func = 0

        def visit_FunctionDef(self, node):
            self._func(node)
            self.generic_visit(node)

        visit_AsyncFunctionDef = visit_FunctionDef

        def _func(self, node):
            end = getattr(node, "end_lineno", node.lineno)
            nlines = end - node.lineno
            nparams = len(node.args.args) + len(node.args.kwonlyargs)
            if node.args.vararg:
                nparams += 1
            if node.args.kwarg:
                nparams += 1
            d = depth_of(node)
            # cyclomatic-ish: count decision keywords inside the function body
            cc = 1
            for sub in ast.walk(node):
                if isinstance(sub, (ast.If, ast.For, ast.While, ast.And, ast.Or,
                                    ast.ExceptHandler, ast.comprehension, ast.IfExp)):
                    cc += 1
            smells = []
            if nlines > max_lines:
                smells.append(f"函数过长({nlines} 行 > {max_lines})")
            if nparams > max_params:
                smells.append(f"参数过多({nparams} 个 > {max_params})")
            if d > max_depth:
                smells.append(f"嵌套过深(深度 {d} > {max_depth})")
            if cc > 10:
                smells.append(f"圈复杂度偏高(≈{cc})")
            if smells:
                findings.append({
                    "file": None,
                    "line": node.lineno,
                    "name": node.name,
                    "smells": smells,
                    "metrics": {"lines": nlines, "params": nparams,
                                "depth": d, "cyclomatic": cc},
                })

    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return [{"file": None, "line": e.lineno or 0, "name": "<parse-error>",
                 "smells": [f"语法错误: {e.msg}"], "metrics": {}}]
    V().visit(tree)
    return findings


# ---------- JS/TS analysis (regex-based) ----------
JS_FUNC = re.compile(
    r"(?:function\s+(?P<fn>[A-Za-z0-9_$]+)"
    r"|(?P<asn>[A-Za-z0-9_$]+)\s*=\s*(?:async\s+)?function"
    r"|(?P<asn2>[A-Za-z0-9_$]+)\s*=\s*(?:async\s+)?\("
    r"|function\s*\()\s*\("
)
JS_PARAMS = re.compile(r"\(([^)]*)\)")


def _analyze_js(src, max_lines, max_params, max_depth):
    findings = []
    lines = src.splitlines()

    for m in JS_FUNC.finditer(src):
        name = m.group("fn") or m.group("asn") or m.group("asn2") or "<anonymous>"
        start = src[:m.start()].count("\n") + 1
        # count params
        pm = JS_PARAMS.search(src[m.start():m.start() + 120])
        nparams = 0
        if pm:
            body = pm.group(1).strip()
            if body:
                nparams = len([x for x in re.split(r",", body) if x.strip()])
        # count lines until matching brace
        nlines = 0
        depth = 0
        opened = False
        reached = False
        for ch in src[m.start():]:
            if ch == "\n":
                nlines += 1
            if ch == "{":
                opened = True
                depth += 1
            elif ch == "}":
                depth -= 1
                if opened and depth == 0:
                    reached = True
                    break
        if not reached:
            nlines = min(nlines, len(lines) - start + 1)
        # nested depth via indentation heuristic on the body slice
        slice_lines = lines[start - 1:start - 1 + nlines]
        d = 0
        cur = 0
        for ln in slice_lines:
            indent = len(ln) - len(ln.lstrip(" "))
            cur = indent // 2 if indent else cur
            d = max(d, cur)
        smells = []
        if nlines > max_lines:
            smells.append(f"函数过长({nlines} 行 > {max_lines})")
        if nparams > max_params:
            smells.append(f"参数过多({nparams} 个 > {max_params})")
        if d > max_depth:
            smells.append(f"嵌套过深(深度 {d} > {max_depth})")
        if smells:
            findings.append({
                "file": None, "line": start, "name": name,
                "smells": smells,
                "metrics": {"lines": nlines, "params": nparams, "depth": d},
            })
    return findings


def analyze(path, max_lines, max_params, max_depth):
    ext = os.path.splitext(path)[1]
    try:
        src = open(path, encoding="utf-8", errors="replace").read()
    except OSError as e:
        return [{"file": path, "line": 0, "name": "<read-error>",
                 "smells": [f"无法读取: {e}"], "metrics": {}}]
    if ext in PY_EXT:
        res = _analyze_python(src, max_lines, max_params, max_depth)
    elif ext in JS_EXT:
        res = _analyze_js(src, max_lines, max_params, max_depth)
    else:
        return []
    for r in res:
        r["file"] = path
    return res


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    paths, as_json = [], False
    max_lines, max_params, max_depth = DEFAULT_MAX_LINES, DEFAULT_MAX_PARAMS, DEFAULT_MAX_DEPTH
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--json":
            as_json = True
        elif a == "--max-lines":
            max_lines = int(argv[i + 1]); i += 1
        elif a == "--max-params":
            max_params = int(argv[i + 1]); i += 1
        elif a == "--max-depth":
            max_depth = int(argv[i + 1]); i += 1
        else:
            paths.append(a)
        i += 1
    if not paths:
        print("usage: analyze_smells.py PATH [PATH ...] [--json] [--max-lines N] [--max-params N] [--max-depth N]",
              file=sys.stderr)
        return 2
    all_findings = []
    for p in _walk(paths):
        all_findings.extend(analyze(p, max_lines, max_params, max_depth))
    if as_json:
        print(json.dumps(all_findings, ensure_ascii=False, indent=2))
    else:
        if not all_findings:
            print("未检测到明显代码味道。")
        for f in all_findings:
            loc = f"{f['file']}:{f['line']} ({f['name']})"
            print(f"[SMELL] {loc}")
            for s in f["smells"]:
                print(f"    - {s}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
