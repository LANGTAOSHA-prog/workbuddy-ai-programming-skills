#!/usr/bin/env python3
"""
chat.py — SenseNova Chat Completions (OpenAI compatible).

Usage:
    python chat.py --model sensenova-6.7-flash-lite --prompt "Hello"
    python chat.py --model sensenova-6.7-flash-lite --prompt "看图" --image img.png
    python chat.py --model deepseek-v4-flash --prompt "9.11vs9.8" --reasoning high
    python chat.py --model deepseek-v4-flash --prompt "列三种语言" --json-mode
    python chat.py --model sensenova-6.7-flash-lite --prompt "Hi" --stream
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error

BASE_URL = "https://token.sensenova.cn/v1"
API_KEY_ENV = "SENSENOVA_API_KEY"

DEFAULTS = {
    "sensenova-6.7-flash-lite": {"temperature": 0.6, "max_tokens": 65536},
    "deepseek-v4-flash": {"temperature": 1.0, "max_tokens": 65536},
}


def build_messages(prompt, image_path=None):
    if image_path:
        # Resolve path
        if not os.path.isabs(image_path):
            image_path = os.path.abspath(image_path)

        if image_path.startswith("http"):
            img_item = {
                "type": "image_url",
                "image_url": {"url": image_path},
            }
        else:
            # Read and base64 encode local image
            with open(image_path, "rb") as f:
                import base64
                b64 = base64.b64encode(f.read()).decode()
            # Detect mime type
            ext = os.path.splitext(image_path)[1].lower()
            mime_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif", ".webp": "image/webp"}
            mime = mime_map.get(ext, "image/png")
            img_item = {
                "type": "image_url",
                "image_url": {"url": f"data:{mime};base64,{b64}"},
            }

        return [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                img_item,
            ]
        }]
    else:
        return [{"role": "user", "content": prompt}]


def call_chat(model, messages, stream=False, reasoning_effort=None, json_mode=False, temperature=None, max_tokens=None):
    payload = {"model": model, "messages": messages}
    if stream:
        payload["stream"] = True
    if reasoning_effort:
        payload["reasoning_effort"] = reasoning_effort
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    if temperature is not None:
        payload["temperature"] = temperature
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ[API_KEY_ENV]}",
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}/chat/completions",
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

    if stream:
        print(body)
        return

    result = json.loads(body)
    choice = result.get("choices", [{}])[0]
    msg = choice.get("message", {})
    content = msg.get("content", "")
    reasoning = msg.get("reasoning_content", "")
    finish = choice.get("finish_reason", "")
    usage = result.get("usage", {})

    if reasoning:
        print(f"[Thinking]\n{reasoning}\n")
    print(content)
    if finish != "stop":
        print(f"\n[finish_reason: {finish}]", file=sys.stderr)
    tokens = usage.get("total_tokens", 0)
    print(f"\n[{tokens} tokens]", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="SenseNova Chat Completions")
    parser.add_argument("--model", default="sensenova-6.7-flash-lite", help="Model ID")
    parser.add_argument("--prompt", "-p", required=True, help="User prompt")
    parser.add_argument("--image", "-i", help="Image file path or URL for multimodal input")
    parser.add_argument("--stream", "-s", action="store_true", help="SSE stream output")
    parser.add_argument("--reasoning", "-r", choices=["low", "medium", "high", "none"], help="Reasoning effort (deepseek)")
    parser.add_argument("--json-mode", "-j", action="store_true", help="Force JSON output")
    parser.add_argument("--temperature", "-t", type=float, help="Temperature override")
    parser.add_argument("--max-tokens", "-m", type=int, help="Max output tokens")

    args = parser.parse_args()

    if not os.environ.get(API_KEY_ENV):
        print(f"Error: {API_KEY_ENV} environment variable not set.", file=sys.stderr)
        sys.exit(1)

    defaults = DEFAULTS.get(args.model, {"temperature": 1.0, "max_tokens": 65536})
    temp = args.temperature if args.temperature is not None else defaults["temperature"]
    max_tok = args.max_tokens if args.max_tokens is not None else defaults["max_tokens"]

    messages = build_messages(args.prompt, args.image)

    print(f"Model: {args.model} | Prompt: {args.prompt[:60]}... | Tokens: max={max_tok}", file=sys.stderr)
    call_chat(args.model, messages, args.stream, args.reasoning, args.json_mode, temp, max_tok)


if __name__ == "__main__":
    main()
