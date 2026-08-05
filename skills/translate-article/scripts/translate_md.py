#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 Markdown 文章拆成可翻译片段 / 合并翻译结果,便于批量翻译且保留结构。

用法:
  # 1) 拆分:把 markdown 拆成片段,跳过代码块,输出 segments.json
  python3 translate_md.py split --input article.md --output segments.json

  # 2) 模型翻译 segments.json 里 type != "code" 的 src,写回 translations.json:
  #    { "0": "译文的段落0", "2": "译文的标题", ... }   (code 块无需翻译)

  # 3) 合并:用译文重建 markdown
  python3 translate_md.py join --input article.md \
      --translations translations.json --output article.zh.md

设计:
  - 按块(段落/标题/代码块)切分,代码块整体保留不翻译
  - 标题仅翻译文字部分,井号前缀(## )原样保留
  - 片段带稳定 id,join 时按 id 回填,结构与原文一一对应
  - 仅用 Python 标准库
"""
import argparse
import json
import re
import sys
from pathlib import Path


def parse_blocks(text):
    """Yield (id, type, prefix, content).

    type: 'code' | 'heading' | 'text'
    prefix: for headings the '#' run + space; else ''
    content: translatable text (heading without prefix) or full block (code)
    """
    blocks = []
    lines = text.splitlines()
    i = 0
    n = len(lines)
    buf = []
    in_code = False
    code_fence = ""

    def flush(buf, blocks):
        if not buf:
            return
        para = "\n".join(buf).strip("\n")
        if not para.strip():
            return
        # heading?
        m = re.match(r"^(#{1,6})\s+(.*)$", para)
        if m:
            blocks.append((len(blocks), "heading", m.group(1) + " ", m.group(2)))
        else:
            blocks.append((len(blocks), "text", "", para))
        buf.clear()

    while i < n:
        line = lines[i]
        if not in_code:
            if re.match(r"^\s*```", line) or re.match(r"^\s*~~~", line):
                flush(buf, blocks)
                in_code = True
                code_fence = line.strip()[:3]
                code_buf = [line]
                i += 1
                while i < n and not lines[i].strip().startswith(code_fence):
                    code_buf.append(lines[i])
                    i += 1
                if i < n:
                    code_buf.append(lines[i])  # closing fence
                    i += 1
                blocks.append((len(blocks), "code", "", "\n".join(code_buf)))
                in_code = False
                continue
            if line.strip() == "":
                # blank line separates paragraphs
                flush(buf, blocks)
                i += 1
                continue
            buf.append(line)
            i += 1
        else:
            i += 1
    flush(buf, blocks)
    return blocks


def cmd_split(args):
    text = Path(args.input).read_text(encoding="utf-8")
    blocks = parse_blocks(text)
    segments = [
        {"id": b[0], "type": b[1], "src": b[3]}
        for b in blocks
    ]
    Path(args.output).write_text(
        json.dumps(segments, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    n_text = sum(1 for s in segments if s["type"] != "code")
    print(f"wrote {args.output}: {len(segments)} segments ({n_text} translatable)")


def cmd_join(args):
    text = Path(args.input).read_text(encoding="utf-8")
    blocks = parse_blocks(text)
    translations = json.loads(Path(args.translations).read_text(encoding="utf-8"))
    out = []
    for b in blocks:
        bid, btype, prefix, content = b
        key = str(bid)
        if btype == "code":
            out.append(content)
        else:
            translated = translations.get(key)
            if translated is None:
                # 未提供译文则保留原文
                translated = content
            out.append(prefix + translated)
    result = "\n\n".join(out).strip() + "\n"
    Path(args.output).write_text(result, encoding="utf-8")
    print(f"wrote {args.output}: {len(blocks)} blocks rebuilt")


def main():
    ap = argparse.ArgumentParser(description="Split/join markdown for translation.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("split", help="Split markdown into translatable segments")
    sp.add_argument("--input", required=True)
    sp.add_argument("--output", required=True)
    sp.set_defaults(func=cmd_split)

    jp = sub.add_parser("join", help="Rebuild markdown from translations")
    jp.add_argument("--input", required=True)
    jp.add_argument("--translations", required=True)
    jp.add_argument("--output", required=True)
    jp.set_defaults(func=cmd_join)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
