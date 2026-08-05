#!/usr/bin/env python3
"""Parse common stack traces into structured JSON to seed debugging analysis.

Pure standard library. Supports three flavors:
  - Python traceback (``Traceback (most recent call last):`` ... ``ErrorType: msg``)
  - Node / JS (``TypeError: msg`` + ``    at fn (file:line:col)`` frames)
  - Java / JVM (``ExceptionType: msg`` + ``\tat pkg.Class.method(File.java:line)``)

Usage:
  python3 parse_traceback.py TRACE_FILE [--json]
  cat trace.txt | python3 parse_traceback.py - [--json]
"""
import json
import re
import sys

# Python
RE_PY_LINE = re.compile(r'^\s+File "([^"]+)", line (\d+), in (.+)$')
RE_PY_ERR = re.compile(r"^(\w+(?:Error|Exception|Warning))(?::\s*(.*))?$")

# Node / JS:   at func (file:line:col)   OR   at file:line:col
RE_JS_FRAME = re.compile(
    r"^\s*at\s+(?:(.+?)\s+\()?(.+?):(\d+):(\d+)\)?$"
)
RE_JS_ERR = re.compile(r"^([A-Za-z]+Error)(?::\s*(.*))?$")

# Java:   at com.foo.Bar.method(Bar.java:123)
RE_JAVA_FRAME = re.compile(r"^\s*at\s+([\w.$]+(?:\.\w+)*)\(([^):]+):(\d+)\)$")
RE_JAVA_ERR = re.compile(r"^([\w$.]+(?:Error|Exception))(?::\s*(.*))?$")


def _detect_lang(text):
    if "Traceback (most recent call last):" in text:
        return "python"
    # JS: at func (file:line:col)  -- location has TWO colons
    if re.search(r"^\s*at\s+.+\(.+:\d+:\d+\)", text, re.M):
        return "js"
    # Java: at pkg.Class.method(File.java:line)  -- ONE colon, dotted path
    if re.search(r"^\s*at\s+[\w$.]+\([\w/]+\.\w+:\d+\)", text, re.M):
        return "java"
    if re.search(r"[A-Za-z]+Error:", text) or re.search(r"[A-Za-z]+Exception:", text):
        return "js"
    return "unknown"


def _parse_python(text):
    frames = []
    error_type = error_msg = None
    lines = text.splitlines()
    for ln in lines:
        m = RE_PY_LINE.match(ln)
        if m:
            frames.append({"file": m.group(1), "line": int(m.group(2)),
                           "function": m.group(3)})
            continue
        m = RE_PY_ERR.match(ln.strip())
        if m and error_type is None:
            error_type, error_msg = m.group(1), m.group(2) or ""
    frames.reverse()  # store innermost first (matches js/java)
    return frames, error_type, error_msg


def _parse_js(text):
    frames = []
    error_type = error_msg = None
    for ln in text.splitlines():
        m = RE_JS_ERR.match(ln.strip())
        if m and error_type is None:
            error_type, error_msg = m.group(1), m.group(2) or ""
            continue
        m = RE_JS_FRAME.match(ln)
        if m:
            func = (m.group(1) or "<anonymous>").strip()
            frames.append({"function": func, "file": m.group(2),
                           "line": int(m.group(3)), "column": int(m.group(4))})
    return frames, error_type, error_msg


def _parse_java(text):
    frames = []
    error_type = error_msg = None
    for ln in text.splitlines():
        m = RE_JAVA_ERR.match(ln.strip())
        if m and error_type is None:
            error_type, error_msg = m.group(1), m.group(2) or ""
            continue
        m = RE_JAVA_FRAME.match(ln)
        if m:
            frames.append({"function": m.group(1), "file": m.group(2),
                           "line": int(m.group(3))})
    return frames, error_type, error_msg


def parse(text):
    lang = _detect_lang(text)
    if lang == "python":
        frames, et, em = _parse_python(text)
    elif lang == "js":
        frames, et, em = _parse_js(text)
    elif lang == "java":
        frames, et, em = _parse_java(text)
    else:
        return {"lang": "unknown", "error_type": None, "error_message": None,
                "frames": [], "raw": text.strip()[-2000:]}
    return {
        "lang": lang,
        "error_type": et,
        "error_message": em,
        "frames": frames,
        "top_frame": frames[0] if frames else None,
        "frame_count": len(frames),
    }


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    as_json = False
    path = None
    for a in argv:
        if a == "--json":
            as_json = True
        else:
            path = a
    if path == "-":
        text = sys.stdin.read()
    elif path:
        text = open(path, encoding="utf-8", errors="replace").read()
    else:
        print("usage: parse_traceback.py TRACE_FILE|- [--json]", file=sys.stderr)
        return 2
    result = parse(text)
    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"语言: {result['lang']}")
        print(f"错误类型: {result['error_type']}")
        print(f"错误信息: {result['error_message']}")
        print(f"栈帧数: {result['frame_count']}")
        if result["top_frame"]:
            tf = result["top_frame"]
            loc = tf.get("file", "")
            if tf.get("line") is not None:
                loc += f":{tf['line']}"
            print(f"最内层(出错点): {tf.get('function','?')} @ {loc}")
        print("--- 调用栈(由内到外) ---")
        for fr in result["frames"]:
            loc = fr.get("file", "")
            if fr.get("line") is not None:
                loc += f":{fr['line']}"
            print(f"  {fr.get('function','?')}  <-  {loc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
