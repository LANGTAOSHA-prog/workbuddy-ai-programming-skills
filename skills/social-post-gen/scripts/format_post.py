#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把「标题 + 要点」格式化为各平台社媒文案(小红书 / 微博 / 朋友圈)。

用法:
  # 从 brief 文件生成(首行=标题,其余=要点)
  python3 format_post.py --platform xhs --input brief.txt --output post.txt

  # 直接给标题与要点文件(每行一条)
  python3 format_post.py --platform weibo --title "AI 编程真香" \
      --bullets points.txt --hashtags "AI,编程,效率"

  # 关闭 emoji
  python3 format_post.py --platform moments --input brief.txt --no-emoji

平台差异:
  xhs     小红书:emoji 标题钩子 + emoji 要点列表 + 末尾话题标签,偏种草/干货
  weibo   微博:短平快,话题 #词# 内联,可带互动提问
  moments 朋友圈:口语化、第一人称、不加话题标签、更短

仅用 Python 标准库。
"""
import argparse
import sys
from pathlib import Path

EMOJI_ROTATION = ["✨", "🔥", "💡", "🚀", "📌", "🎯", "🧠", "⚡", "🌟", "📚", "🛠️", "👀"]
# 关键词 -> emoji 提示(命中则用,否则轮转)
KEYWORD_EMOJI = {
    "工具": "🛠️", "教程": "📚", "技巧": "💡", "效率": "⚡", "学习": "🧠",
    "注意": "⚠️", "推荐": "🌟", "干货": "📌", "涨": "📈", "省": "💰",
    "坑": "⚠️", "对比": "⚖️", "总结": "🎯", "开始": "🚀", "重要": "🔑",
}

PLATFORMS = {"xhs", "weibo", "moments"}


def load_brief(args):
    title = args.title
    bullets = []
    if args.input:
        lines = [l.strip() for l in Path(args.input).read_text(encoding="utf-8").splitlines()]
        lines = [l for l in lines if l]
        if not title and lines:
            title = lines[0]
            bullets = lines[1:]
        else:
            bullets = lines
    if args.bullets:
        bullets = [l.strip() for l in Path(args.bullets).read_text(encoding="utf-8").splitlines()
                   if l.strip()]
    return title or "", bullets


def pick_emoji(text, idx):
    for kw, em in KEYWORD_EMOJI.items():
        if kw in text:
            return em
    return EMOJI_ROTATION[idx % len(EMOJI_ROTATION)]


def format_post(platform, title, bullets, hashtags, use_emoji):
    tags = [h.strip().lstrip("#") for h in hashtags.split(",")] if hashtags else []

    if platform == "xhs":
        out = []
        hook = f"{'✨ ' if use_emoji else ''}{title}" if title else "✨ 今日分享"
        out.append(hook)
        out.append("")
        for i, b in enumerate(bullets):
            em = f"{pick_emoji(b, i)} " if use_emoji else ""
            out.append(f"{em}{b}")
        out.append("")
        if tags:
            out.append(" ".join(f"#{t}" for t in tags))
        out.append("#干货分享 #日常分享" if not tags else "")
        return "\n".join(l for l in out if l != "")

    if platform == "weibo":
        out = []
        head = f"{title}" if title else "分享一下"
        out.append(head)
        out.append("")
        for i, b in enumerate(bullets):
            em = f"{pick_emoji(b, i)} " if use_emoji else ""
            out.append(f"{em}{b}")
        if tags:
            out.append("")
            out.append(" ".join(f"#{t}#" for t in tags))
        out.append("\n你怎么看?欢迎评论区聊聊👇")
        return "\n".join(out)

    # moments
    out = []
    lead = title if title else "今天想说"
    out.append(f"{lead}")
    out.append("")
    for b in bullets[:5]:  # 朋友圈偏短
        out.append(f"· {b}")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Format social media post copy.")
    ap.add_argument("--platform", required=True, choices=sorted(PLATFORMS))
    ap.add_argument("--input", help="Brief file: first line title, rest bullets")
    ap.add_argument("--title")
    ap.add_argument("--bullets", help="File with one bullet per line")
    ap.add_argument("--hashtags", help="Comma-separated hashtags, e.g. AI,编程")
    ap.add_argument("--no-emoji", action="store_true")
    ap.add_argument("--output")
    args = ap.parse_args()

    title, bullets = load_brief(args)
    if not title and not bullets:
        print("error: provide --title/--input/--bullets", file=sys.stderr)
        sys.exit(1)

    text = format_post(args.platform, title, bullets, args.hashtags or "",
                       use_emoji=not args.no_emoji)

    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
        print(f"wrote {args.output}")
    else:
        print(text)


if __name__ == "__main__":
    main()
