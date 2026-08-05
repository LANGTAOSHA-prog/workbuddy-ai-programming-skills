#!/usr/bin/env python3
"""
image_gen.py — SenseNova U1 Fast image generation.

Usage:
    python image_gen.py --prompt "生成一个信息图，介绍人工智能应用"
    python image_gen.py --prompt "信息图：AI发展趋势" --size 1664x2496 --output infographic.png

Supported sizes: 1664x2496, 2496x1664, 1760x2368, 2368x1760, 1824x2272,
                2272x1824, 2048x2048, 2752x1536, 1536x2752, 3072x1376, 1344x3136
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error

BASE_URL = "https://token.sensenova.cn/v1"
MODEL = "sensenova-u1-fast"
API_KEY_ENV = "SENSENOVA_API_KEY"

SIZES = [
    "1664x2496", "2496x1664", "1760x2368", "2368x1760",
    "1824x2272", "2272x1824", "2048x2048", "2752x1536",
    "1536x2752", "3072x1376", "1344x3136",
]


def generate_image(prompt, size="2752x1536", n=1, output=None):
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "size": size,
        "n": n,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ[API_KEY_ENV]}",
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}/images/generations",
        data=data,
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        print(f"Error {e.code}: {err_body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Network error: {e.reason}", file=sys.stderr)
        sys.exit(1)

    result = json.loads(body)
    images = result.get("data", [])

    if not images:
        print("No images returned.", file=sys.stderr)
        sys.exit(1)

    if output:
        # Save only first image to output path
        img_url = images[0].get("url", "")
        if not img_url:
            print("Image URL not found in response.", file=sys.stderr)
            sys.exit(1)

        img_req = urllib.request.Request(img_url)
        try:
            with urllib.request.urlopen(img_req, timeout=120) as img_resp:
                img_data = img_resp.read()
            with open(output, "wb") as f:
                f.write(img_data)
            print(f"Image saved to: {output}", file=sys.stderr)
        except Exception as e:
            print(f"Failed to download image: {e}", file=sys.stderr)
            sys.exit(1)

    # Print image URLs
    for i, img in enumerate(images):
        url = img.get("url", "")
        print(f"Image {i + 1}: {url}")
        print(f"(Temporary URL, valid for 1 hour)")

    return [img.get("url", "") for img in images]


def main():
    parser = argparse.ArgumentParser(description="SenseNova U1 Fast Image Generation")
    parser.add_argument("--prompt", "-p", required=True, help="Image description")
    parser.add_argument("--size", "-s", default="2752x1536", help=f"Image size (default: 2752x1536). Options: {', '.join(SIZES)}")
    parser.add_argument("--n", type=int, default=1, help="Number of images to generate (default: 1)")
    parser.add_argument("--output", "-o", help="Output file path (saves first image)")

    args = parser.parse_args()

    if not os.environ.get(API_KEY_ENV):
        print(f"Error: {API_KEY_ENV} environment variable not set.", file=sys.stderr)
        sys.exit(1)

    if args.size not in SIZES:
        print(f"Warning: Size '{args.size}' not in standard list. Using as-is.", file=sys.stderr)

    print(f"Model: {MODEL} | Size: {args.size} | Prompt: {args.prompt[:60]}...", file=sys.stderr)
    generate_image(args.prompt, args.size, args.n, args.output)


if __name__ == "__main__":
    main()
