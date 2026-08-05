#!/usr/bin/env python3
"""
make_article.py - Embed images as compressed base64 in HTML for WeChat paste.

Usage:
    python make_article.py --input article.html --output article_paste.html
    python make_article.py -i article.html -o article_paste.html --max-width 1200 --quality 85

Requires: Pillow (pip install Pillow)
"""

import argparse
import base64
import io
import os
import re
import sys


def compress_image(image_path, max_width=1200, quality=85):
    """Compress an image and return base64-encoded JPEG data."""
    try:
        from PIL import Image
    except ImportError:
        print("Error: Pillow is required. Install with: pip install Pillow", file=sys.stderr)
        sys.exit(1)

    img = Image.open(image_path)

    # Convert to RGB (strip alpha for JPEG)
    if img.mode in ("RGBA", "P", "LA"):
        img = img.convert("RGB")
    elif img.mode != "RGB":
        img = img.convert("RGB")

    # Resize if wider than max_width
    if img.width > max_width:
        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        img = img.resize((max_width, new_height), Image.LANCZOS)

    # Compress to JPEG
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    data = buf.getvalue()

    b64 = base64.b64encode(data).decode("ascii")
    return f"data:image/jpeg;base64,{b64}"


def process_html(html_path, output_path, max_width, quality):
    """Read HTML, find local image references, embed as base64."""
    html_dir = os.path.dirname(os.path.abspath(html_path))

    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Match <img ... src="..." ...> with local file paths
    # Matches: src="image.png", src="./images/foo.jpg", src="C:/path/to/img.png"
    pattern = re.compile(
        r"""(<img\s+[^>]*src=["'])(?!data:|https?://|//)([^"']+)(["'])""",
        re.IGNORECASE,
    )

    replacements = []

    def replace_src(match):
        prefix = match.group(1)
        img_path = match.group(2)
        suffix = match.group(3)

        # Resolve path
        if os.path.isabs(img_path):
            full_path = img_path
        else:
            full_path = os.path.join(html_dir, img_path)

        full_path = os.path.normpath(full_path)

        if not os.path.exists(full_path):
            print(f"  Warning: Image not found: {full_path}", file=sys.stderr)
            return match.group(0)

        original_size = os.path.getsize(full_path)
        data_uri = compress_image(full_path, max_width, quality)
        compressed_size = len(data_uri) * 3 // 4  # base64 overhead

        replacements.append(
            f"  {img_path} -> base64 "
            f"({original_size // 1024}KB -> {compressed_size // 1024}KB)"
        )

        return f"{prefix}{data_uri}{suffix}"

    html = pattern.sub(replace_src, html)

    # Write output
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Processed {len(replacements)} image(s):")
    for r in replacements:
        print(r)
    print(f"\nOutput: {output_path} ({os.path.getsize(output_path) // 1024} KB)")


def main():
    parser = argparse.ArgumentParser(
        description="Embed images as compressed base64 in HTML for WeChat paste."
    )
    parser.add_argument(
        "-i", "--input", required=True, help="Input HTML file path"
    )
    parser.add_argument(
        "-o", "--output", required=True, help="Output HTML file path"
    )
    parser.add_argument(
        "--max-width", type=int, default=1200,
        help="Max image width in pixels (default: 1200)"
    )
    parser.add_argument(
        "--quality", type=int, default=85,
        help="JPEG quality 1-100 (default: 85)"
    )

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    print(f"Input:  {args.input}")
    print(f"Output: {args.output}")
    print(f"Max width: {args.max_width}px | JPEG quality: {args.quality}")
    print()

    process_html(args.input, args.output, args.max_width, args.quality)


if __name__ == "__main__":
    main()
