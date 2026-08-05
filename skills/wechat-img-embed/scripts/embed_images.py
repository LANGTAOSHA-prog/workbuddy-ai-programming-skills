#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""公众号文章图片压缩并内嵌为 base64。

子命令:
  embed   把 HTML 中所有本地图片压缩并内嵌为 data URI,输出自包含 HTML
  convert 单张图片压缩并转 base64(输出到文件或 stdout)

仅使用 Python 标准库 + Pillow。
"""
import argparse
import base64
import io
import os
import re
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("缺少依赖 Pillow,请先执行: pip install Pillow")

# 匹配 <img ... src="..." ...>,兼容单/双引号、多行属性
IMG_TAG_RE = re.compile(
    r'(<img\b[^>]*?\bsrc\s*=\s*)(["\'])(.*?)\2([^>]*?>)',
    re.IGNORECASE | re.DOTALL,
)


def compress_to_base64(path, max_width, quality, keep_alpha):
    """读取图片 -> 等比缩放 -> 编码为 base64 data URI。返回 (data_uri, 字节数)。"""
    img = Image.open(path)
    # 多帧 GIF 取首帧(公众号正文不播动画)
    if getattr(img, "is_animated", False):
        img.seek(0)

    if img.width > max_width:
        ratio = max_width / float(img.width)
        new_h = int(img.height * ratio)
        img = img.resize((max_width, new_h), Image.LANCZOS)

    buf = io.BytesIO()
    if keep_alpha:
        img = img.convert("RGBA")
        img.save(buf, format="PNG")
        mime = "image/png"
    else:
        has_alpha = (
            img.mode in ("RGBA", "LA")
            or (img.mode == "P" and "transparency" in img.info)
        )
        if has_alpha:
            # 透明底合成白底,避免转 JPEG 后变黑
            bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
            bg.paste(img, mask=img.split()[-1])
            img = bg.convert("RGB")
        else:
            img = img.convert("RGB")
        img.save(buf, format="JPEG", quality=quality)
        mime = "image/jpeg"

    data = base64.b64encode(buf.getvalue()).decode("ascii")
    return "data:%s;base64,%s" % (mime, data), len(buf.getvalue())


def resolve_path(src, html_dir, base_dir):
    if base_dir:
        return os.path.join(base_dir, src)
    return os.path.join(html_dir, src)


def run_embed(args):
    input_html = args.input
    if not os.path.isfile(input_html):
        sys.exit("输入 HTML 不存在: %s" % input_html)

    output_html = args.output or (os.path.splitext(input_html)[0] + "_paste.html")
    html_dir = os.path.dirname(os.path.abspath(input_html))

    with open(input_html, "r", encoding="utf-8") as f:
        html = f.read()

    count = 0
    total_original = 0
    total_compressed = 0

    def repl(m):
        nonlocal count, total_original, total_compressed
        prefix, quote, src, rest = m.group(1), m.group(2), m.group(3), m.group(4)
        # 跳过外链与已内嵌
        if src.startswith(("http://", "https://", "data:", "//")):
            return m.group(0)
        img_path = resolve_path(src, html_dir, args.base_dir)
        if not os.path.isfile(img_path):
            print("  ! 找不到图片,已跳过: %s" % src, file=sys.stderr)
            return m.group(0)
        data_uri, size = compress_to_base64(
            img_path, args.max_width, args.quality, args.keep_alpha
        )
        count += 1
        total_original += os.path.getsize(img_path)
        total_compressed += size
        return '%s%s%s%s' % (prefix, quote, data_uri, quote) + rest

    new_html = IMG_TAG_RE.sub(repl, html)

    with open(output_html, "w", encoding="utf-8") as f:
        f.write(new_html)

    saved = total_original - total_compressed
    saved_kb = saved / 1024.0
    print("已内嵌 %d 张图片 -> %s" % (count, output_html))
    if count:
        print("原始图片 %.1f KB,内嵌后 %.1f KB,节省 %.1f KB"
              % (total_original / 1024.0, total_compressed / 1024.0, saved_kb))
    print("输出 HTML 总大小 %.1f KB" % (os.path.getsize(output_html) / 1024.0))


def run_convert(args):
    if not os.path.isfile(args.input):
        sys.exit("输入图片不存在: %s" % args.input)
    data_uri, size = compress_to_base64(
        args.input, args.max_width, args.quality, args.keep_alpha
    )
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(data_uri)
        print("已写入 base64 -> %s (%.1f KB)" % (args.output, size / 1024.0))
    else:
        print(data_uri)


def build_parser():
    p = argparse.ArgumentParser(
        description="公众号文章图片压缩并内嵌为 base64"
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("embed", help="HTML 本地图片压缩并内嵌")
    e.add_argument("-i", "--input", required=True, help="源 HTML 文件")
    e.add_argument("-o", "--output", help="输出 HTML(默认 {input}_paste.html)")
    e.add_argument("--base-dir", help="图片查找基准目录(默认 HTML 同级)")
    e.add_argument("-w", "--max-width", type=int, default=1200, help="最大宽度 px")
    e.add_argument("-q", "--quality", type=int, default=85, help="JPEG 质量 1-100")
    e.add_argument("--keep-alpha", action="store_true", help="保留透明通道输出 PNG")
    e.set_defaults(func=run_embed)

    c = sub.add_parser("convert", help="单张图片转 base64")
    c.add_argument("-i", "--input", required=True, help="图片文件")
    c.add_argument("-o", "--output", help="base64 输出文件(省略则打印到 stdout)")
    c.add_argument("-w", "--max-width", type=int, default=1200, help="最大宽度 px")
    c.add_argument("-q", "--quality", type=int, default=85, help="JPEG 质量 1-100")
    c.add_argument("--keep-alpha", action="store_true", help="保留透明通道输出 PNG")
    c.set_defaults(func=run_convert)

    return p


def main():
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
