#!/usr/bin/env python3
"""Agnes AI Video Generation Script.

Supports text-to-video, image-to-video, and keyframe animation
using agnes-video-v2.0. Video generation is asynchronous: this script
creates a task, polls for completion, and downloads the result.

Usage:
    # Text-to-video (5 seconds, 16:9)
    python generate_video.py --prompt "A cat walking on the beach at sunset" --output out.mp4

    # Image-to-video
    python generate_video.py --prompt "The woman turns around slowly" --image https://example.com/portrait.png --output out.mp4

    # Keyframe animation
    python generate_video.py --prompt "Smooth transition between keyframes" \
        --image https://a.com/kf1.png --image https://b.com/kf2.png --mode keyframes --output out.mp4

    # Custom duration (10 seconds)
    python generate_video.py --prompt "A cityscape at night" --num-frames 241 --frame-rate 24 --output out.mp4

    # Just create task, don't wait for download
    python generate_video.py --prompt "Ocean waves" --no-wait

Environment:
    AGNES_API_KEY: Required. API key from https://platform.agnes-ai.com
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error


BASE_URL = "https://apihub.agnes-ai.com"
CREATE_ENDPOINT = f"{BASE_URL}/v1/videos"
POLL_ENDPOINT = f"{BASE_URL}/agnesapi"


def get_api_key():
    key = os.environ.get("AGNES_API_KEY")
    if not key:
        print("ERROR: AGNES_API_KEY environment variable is not set.", file=sys.stderr)
        print("Get your API key from https://platform.agnes-ai.com", file=sys.stderr)
        sys.exit(1)
    return key


def create_task(args):
    api_key = get_api_key()

    body = {
        "model": "agnes-video-v2.0",
        "prompt": args.prompt,
    }

    if args.image and args.mode != "keyframes":
        # Single image for image-to-video (top-level)
        body["image"] = args.image[0]

    if args.width:
        body["width"] = args.width
    if args.height:
        body["height"] = args.height

    body["num_frames"] = args.num_frames
    body["frame_rate"] = args.frame_rate

    if args.negative_prompt:
        body["negative_prompt"] = args.negative_prompt
    if args.seed is not None:
        body["seed"] = args.seed
    if args.num_inference_steps:
        body["num_inference_steps"] = args.num_inference_steps

    # Keyframe mode uses extra_body
    if args.mode == "keyframes" and args.image:
        body["extra_body"] = {
            "image": args.image,
            "mode": "keyframes",
        }

    payload = json.dumps(body).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    print(f"Model: agnes-video-v2.0")
    print(f"Frames: {args.num_frames} @ {args.frame_rate} fps (~{args.num_frames / args.frame_rate:.1f}s)")
    if args.image:
        print(f"Input images: {len(args.image)}")
    if args.mode == "keyframes":
        print("Mode: keyframes")
    print("Creating video task...")

    req = urllib.request.Request(CREATE_ENDPOINT, data=payload, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        print(f"HTTP Error {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Network Error: {e}", file=sys.stderr)
        sys.exit(1)

    video_id = result.get("video_id") or result.get("task_id")
    if not video_id:
        print("ERROR: No video_id or task_id in response.", file=sys.stderr)
        print(json.dumps(result, indent=2), file=sys.stderr)
        sys.exit(1)

    print(f"Task created successfully!")
    print(f"  video_id: {video_id}")
    print(f"  task_id:  {result.get('task_id', 'N/A')}")
    print(f"  status:   {result.get('status', 'N/A')}")
    if result.get("seconds"):
        print(f"  duration: {result['seconds']}s")
    if result.get("size"):
        print(f"  size:     {result['size']}")

    return api_key, video_id, result


def poll_result(api_key, video_id, max_wait=600, interval=10):
    """Poll for video task completion. Returns the final result dict."""
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"{POLL_ENDPOINT}?video_id={video_id}"

    print(f"\nPolling for result (max {max_wait}s, every {interval}s)...")

    elapsed = 0
    while elapsed < max_wait:
        req = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="replace")
            print(f"  HTTP Error {e.code}: {error_body}", file=sys.stderr)
            time.sleep(interval)
            elapsed += interval
            continue
        except (urllib.error.URLError, json.JSONDecodeError) as e:
            print(f"  Poll error: {e}", file=sys.stderr)
            time.sleep(interval)
            elapsed += interval
            continue

        status = result.get("status", "unknown")
        progress = result.get("progress", 0)
        print(f"  [{elapsed}s] status={status}, progress={progress}%")

        if status == "completed":
            return result
        elif status == "failed":
            print("ERROR: Video generation failed.", file=sys.stderr)
            print(json.dumps(result, indent=2), file=sys.stderr)
            sys.exit(1)

        time.sleep(interval)
        elapsed += interval

    print(f"ERROR: Timed out after {max_wait}s.", file=sys.stderr)
    sys.exit(1)


def download_video(url, output_path):
    """Download video from URL to local file."""
    print(f"Downloading video from: {url}")
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = resp.read()
    with open(output_path, "wb") as f:
        f.write(data)
    size_mb = len(data) / (1024 * 1024)
    print(f"Video saved to: {output_path} ({size_mb:.1f} MB)")


def main():
    parser = argparse.ArgumentParser(
        description="Generate videos via Agnes AI API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--prompt", "-p", required=True,
        help="Text description of the video content"
    )
    parser.add_argument(
        "--image", "-i", action="append", default=None,
        help="Image URL for image-to-video (can be repeated for keyframes)"
    )
    parser.add_argument(
        "--mode", default=None,
        choices=["ti2vid", "keyframes"],
        help="Generation mode: ti2vid (text/image-to-video) or keyframes"
    )
    parser.add_argument(
        "--width", type=int, default=1152,
        help="Video width (default: 1152, may be normalized)"
    )
    parser.add_argument(
        "--height", type=int, default=768,
        help="Video height (default: 768, may be normalized)"
    )
    parser.add_argument(
        "--num-frames", type=int, default=121,
        help="Number of frames, must be <= 441 and follow 8n+1 rule (default: 121 = ~5s)"
    )
    parser.add_argument(
        "--frame-rate", type=int, default=24,
        help="Frame rate 1-60 (default: 24)"
    )
    parser.add_argument(
        "--negative-prompt", default=None,
        help="Negative prompt describing content to avoid"
    )
    parser.add_argument(
        "--seed", type=int, default=None,
        help="Random seed for reproducible results"
    )
    parser.add_argument(
        "--num-inference-steps", type=int, default=None,
        help="Number of inference steps"
    )
    parser.add_argument(
        "--output", "-o", default="agnes_output.mp4",
        help="Output file path (default: agnes_output.mp4)"
    )
    parser.add_argument(
        "--no-wait", action="store_true",
        help="Create task only, don't poll or download"
    )
    parser.add_argument(
        "--max-wait", type=int, default=600,
        help="Maximum wait time in seconds (default: 600)"
    )
    parser.add_argument(
        "--poll-interval", type=int, default=10,
        help="Poll interval in seconds (default: 10)"
    )

    args = parser.parse_args()

    # Validate num_frames (8n + 1 rule)
    if args.num_frames > 441:
        print("ERROR: num_frames must be <= 441.", file=sys.stderr)
        sys.exit(1)
    if (args.num_frames - 1) % 8 != 0:
        print(f"WARNING: num_frames={args.num_frames} does not follow the 8n+1 rule.", file=sys.stderr)
        print(f"Recommended values: 81, 121, 161, 201, 241, 281, 321, 361, 401, 441", file=sys.stderr)

    # Create task
    api_key, video_id, task_result = create_task(args)

    if args.no_wait:
        print(f"\nTask created. Poll manually with:")
        print(f"  curl -H 'Authorization: Bearer $AGNES_API_KEY' \\")
        print(f"    '{POLL_ENDPOINT}?video_id={video_id}'")
        return

    # Poll for result
    final_result = poll_result(api_key, video_id, max_wait=args.max_wait, interval=args.poll_interval)

    # Download video
    video_url = None
    if final_result.get("metadata"):
        video_url = final_result["metadata"].get("url")

    if not video_url:
        print("ERROR: No video URL in completed result.", file=sys.stderr)
        print(json.dumps(final_result, indent=2), file=sys.stderr)
        sys.exit(1)

    download_video(video_url, args.output)

    # Print summary
    print(f"\n--- Video Generation Complete ---")
    print(f"  Duration: {final_result.get('seconds', 'N/A')}s")
    print(f"  Size: {final_result.get('size', 'N/A')}")
    if final_result.get("metadata", {}).get("size_mapping"):
        sm = final_result["metadata"]["size_mapping"]
        print(f"  Resolution: {sm.get('resolution', 'N/A')} ({sm.get('ratio', 'N/A')})")
        print(f"  Actual: {sm.get('width', 'N/A')}x{sm.get('height', 'N/A')}")


if __name__ == "__main__":
    main()
