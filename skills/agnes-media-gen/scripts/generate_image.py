#!/usr/bin/env python3
"""Agnes AI Image Generation Script.

Supports text-to-image, image-to-image, and multi-image composition
using agnes-image-2.0-flash or agnes-image-2.1-flash.

Usage:
    # Text-to-image (URL output, downloaded to local file)
    python generate_image.py --prompt "A glass cube on white background" --size 1024x768 --output out.png

    # Text-to-image with 2.1 model (tier-based sizing)
    python generate_image.py --prompt "A floating city" --model agnes-image-2.1-flash --size 2K --ratio 16:9 --output out.png

    # Image-to-image
    python generate_image.py --prompt "Make it cyberpunk style" --image https://example.com/input.png --output edited.png

    # Multi-image composition
    python generate_image.py --prompt "Combine both characters in a battle scene" --image https://a.com/1.png --image https://b.com/2.png --output composed.png

    # Base64 output (no download)
    python generate_image.py --prompt "A sunset" --size 1024x1024 --b64 --output out.png

Environment:
    AGNES_API_KEY: Required. API key from https://platform.agnes-ai.com
"""

import argparse
import base64
import json
import os
import sys
import urllib.request
import urllib.error


BASE_URL = "https://apihub.agnes-ai.com/v1/images/generations"


def get_api_key():
    key = os.environ.get("AGNES_API_KEY")
    if not key:
        print("ERROR: AGNES_API_KEY environment variable is not set.", file=sys.stderr)
        print("Get your API key from https://platform.agnes-ai.com", file=sys.stderr)
        sys.exit(1)
    return key


def generate_image(args):
    api_key = get_api_key()

    # Build request body
    body = {
        "model": args.model,
        "prompt": args.prompt,
        "size": args.size,
    }

    # Add ratio for 2.1 model
    if args.ratio:
        body["ratio"] = args.ratio

    # Build extra_body
    extra_body = {}

    if args.image:
        extra_body["image"] = args.image

    if args.b64:
        body["return_base64"] = True
        extra_body["response_format"] = "b64_json"
    else:
        extra_body["response_format"] = "url"

    if extra_body:
        body["extra_body"] = extra_body

    # Send request
    payload = json.dumps(body).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    print(f"Model: {args.model}")
    print(f"Size: {args.size}")
    if args.ratio:
        print(f"Ratio: {args.ratio}")
    if args.image:
        print(f"Input images: {len(args.image)}")
    print("Generating image...")

    req = urllib.request.Request(BASE_URL, data=payload, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=360) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        print(f"HTTP Error {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Network Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Parse response
    if not result.get("data"):
        print("ERROR: No image data in response.", file=sys.stderr)
        print(json.dumps(result, indent=2), file=sys.stderr)
        sys.exit(1)

    item = result["data"][0]

    # Handle output
    if item.get("b64_json"):
        # Base64 output
        img_data = base64.b64decode(item["b64_json"])
        with open(args.output, "wb") as f:
            f.write(img_data)
        print(f"Image saved to: {args.output}")
    elif item.get("url"):
        # URL output - download the image
        img_url = item["url"]
        print(f"Image URL: {img_url}")
        if args.output:
            print("Downloading...")
            req = urllib.request.Request(img_url)
            with urllib.request.urlopen(req, timeout=120) as resp:
                img_data = resp.read()
            with open(args.output, "wb") as f:
                f.write(img_data)
            print(f"Image saved to: {args.output}")
    else:
        print("ERROR: No image URL or base64 data in response.", file=sys.stderr)
        print(json.dumps(result, indent=2), file=sys.stderr)
        sys.exit(1)

    if item.get("revised_prompt"):
        print(f"Revised prompt: {item['revised_prompt']}")

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Generate images via Agnes AI API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--prompt", "-p", required=True,
        help="Text prompt describing the target image or editing instruction"
    )
    parser.add_argument(
        "--model", "-m", default="agnes-image-2.0-flash",
        choices=["agnes-image-2.0-flash", "agnes-image-2.1-flash"],
        help="Model name (default: agnes-image-2.0-flash)"
    )
    parser.add_argument(
        "--size", "-s", default="1024x1024",
        help="Output size: '1024x768' etc. for 2.0; '1K'/'2K'/'3K'/'4K' for 2.1 (default: 1024x1024)"
    )
    parser.add_argument(
        "--ratio", "-r", default=None,
        help="Aspect ratio for 2.1 model: 1:1, 3:4, 4:3, 16:9, 9:16, 2:3, 3:2, 21:9"
    )
    parser.add_argument(
        "--image", "-i", action="append", default=None,
        help="Input image URL for image-to-image (can be repeated for multi-image)"
    )
    parser.add_argument(
        "--b64", action="store_true",
        help="Return image as Base64 instead of URL"
    )
    parser.add_argument(
        "--output", "-o", default="agnes_output.png",
        help="Output file path (default: agnes_output.png)"
    )

    args = parser.parse_args()
    generate_image(args)


if __name__ == "__main__":
    main()
