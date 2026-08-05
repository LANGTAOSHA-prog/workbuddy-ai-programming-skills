#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 PDF 抽取正文文本,供后续改写成公众号文章。

用法:
  python3 extract_pdf.py input.pdf [--pages 1-5] [--output text.txt] [--json]

特性:
  - 自动选择可用后端: pypdf > PyPDF2 > pdfminer.six
  - 跳过无文本页(扫描件/图片页),给出提示
  - 可选页码范围、输出到文件或 stdout、JSON 元信息

依赖(任选其一,二选一即可):
  pip install pypdf        # 推荐
  pip install PyPDF2
  pip install pdfminer.six
"""
import argparse
import json
import re
import sys
from pathlib import Path


def get_backend():
    """Return a (name, extractor) tuple, or (None, None) if no backend."""
    try:
        from pypdf import PdfReader
        def _extract(path, pages):
            reader = PdfReader(path)
            return reader, [p.extract_text() or "" for p in reader.pages], len(reader.pages)
        return "pypdf", _extract
    except ImportError:
        pass
    try:
        from PyPDF2 import PdfReader
        def _extract(path, pages):
            reader = PdfReader(path)
            return reader, [p.extract_text() or "" for p in reader.pages], len(reader.pages)
        return "PyPDF2", _extract
    except ImportError:
        pass
    try:
        from pdfminer.high_level import extract_text
        def _extract(path, pages):
            import pdfminer
            n = len(pdfminer.pdfparser.PDFParser)  # placeholder; count via pypdf-free path
            # pdfminer 不便于直接数页数,用 extract_text 按需
            text = extract_text(path, maxpages=0)
            return None, [text], 1
        return "pdfminer.six", _extract
    except ImportError:
        pass
    return None, None


def parse_pages(spec, total):
    """Parse '1-5,8,10-12' into 0-based indices."""
    if not spec:
        return list(range(total))
    idx = set()
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            idx.update(range(int(a) - 1, int(b)))
        else:
            idx.add(int(part) - 1)
    return sorted(i for i in idx if 0 <= i < total)


def clean_text(text):
    # collapse excessive blank lines, trim trailing spaces
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def main():
    ap = argparse.ArgumentParser(description="Extract text from a PDF for article rewriting.")
    ap.add_argument("pdf", help="Input PDF path")
    ap.add_argument("--pages", help="Page range, e.g. '1-5,8' (1-based)")
    ap.add_argument("--output", help="Write extracted text to file")
    ap.add_argument("--json", action="store_true", help="Output JSON with metadata")
    args = ap.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"error: file not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    name, extractor = get_backend()
    if extractor is None:
        print("error: no PDF backend installed. Run one of:", file=sys.stderr)
        print("  pip install pypdf", file=sys.stderr)
        print("  pip install PyPDF2", file=sys.stderr)
        print("  pip install pdfminer.six", file=sys.stderr)
        sys.exit(2)

    reader, pages_text, total = extractor(str(pdf_path), args.pages)
    indices = parse_pages(args.pages, total) if args.pages else list(range(total))

    chunks = []
    empty = 0
    for i in indices:
        t = pages_text[i] if i < len(pages_text) else ""
        if not t.strip():
            empty += 1
            continue
        chunks.append(f"<!-- page {i + 1} -->\n{t}")

    full = clean_text("\n\n".join(chunks))
    meta = {
        "backend": name,
        "file": str(pdf_path.resolve()),
        "total_pages": total,
        "selected_pages": len(indices),
        "empty_pages": empty,
        "char_count": len(full),
    }

    if args.json:
        print(json.dumps({"meta": meta, "text": full}, ensure_ascii=False, indent=2))
        return

    if args.output:
        Path(args.output).write_text(full, encoding="utf-8")
        print(f"wrote {args.output} ({meta['char_count']} chars, backend={name})")
    else:
        print(full)


if __name__ == "__main__":
    main()
