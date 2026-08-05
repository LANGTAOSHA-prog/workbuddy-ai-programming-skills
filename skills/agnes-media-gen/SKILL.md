---
name: agnes-media-gen
description: "Generate images and videos via the Agnes AI API (agnes-image-2.0-flash, agnes-image-2.1-flash, agnes-video-v2.0). This skill should be used when the user asks to generate, create, or edit images using Agnes AI models, or to generate videos from text prompts or images. Supports text-to-image, image-to-image, multi-image composition, text-to-video, image-to-video, and keyframe animation workflows. Requires an Agnes AI API key."
agent_created: true
---

# Agnes Media Gen

Generate images and videos through the Agnes AI API. Covers three models:

| Model | Type | Endpoint |
|-------|------|----------|
| `agnes-image-2.0-flash` | Image generation & editing | `POST /v1/images/generations` |
| `agnes-image-2.1-flash` | Image generation (upgraded, high-density) | `POST /v1/images/generations` |
| `agnes-video-v2.0` | Video generation (async) | `POST /v1/videos` + `GET /agnesapi` |

## Prerequisites

- **API Key**: Obtain from the Agnes AI developer dashboard at
  `https://platform.agnes-ai.com`. Store it in the environment variable
  `AGNES_API_KEY`.
- **Base URL**: `https://apihub.agnes-ai.com/v1`
- **Auth Header**: `Authorization: Bearer $AGNES_API_KEY`

If `AGNES_API_KEY` is not set, ask the user to provide it or direct them to the
dashboard at `https://platform.agnes-ai.com`.

## Quick Start

Use the bundled scripts for reliable, repeatable generation:

```bash
# Image generation (text-to-image)
python scripts/generate_image.py \
  --prompt "A glass cube on a white studio background, soft shadows" \
  --size 1024x768 \
  --output image.png

# Image generation (image-to-image)
python scripts/generate_image.py \
  --prompt "Transform into cinematic cyberpunk style" \
  --size 1024x768 \
  --image https://example.com/input.png \
  --output edited.png

# Video generation (text-to-video)
python scripts/generate_video.py \
  --prompt "A cat walking on the beach at sunset" \
  --output video.mp4

# Video generation (image-to-video)
python scripts/generate_video.py \
  --prompt "The woman slowly turns around and looks at the camera" \
  --image https://example.com/portrait.png \
  --output video.mp4
```

All scripts read the API key from `AGNES_API_KEY`. Set it before running:

```bash
export AGNES_API_KEY="your_key_here"
```

## Image Generation

### Choosing a Model

| Model | Best For |
|-------|----------|
| `agnes-image-2.0-flash` | General-purpose generation and editing. Fast, production-grade. |
| `agnes-image-2.1-flash` | High-information-density images, complex compositions, rich details. Supports tier-based sizing (`1K`/`2K`/`3K`/`4K`) with `ratio`. |

### Key Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `model` | Yes | `agnes-image-2.0-flash` or `agnes-image-2.1-flash` |
| `prompt` | Yes | Text description or editing instruction |
| `size` | Yes | `1024x768` etc. (2.0); `1K`/`2K`/`3K`/`4K` (2.1 recommended) |
| `ratio` | 2.1 only | `1:1`, `3:4`, `4:3`, `16:9`, `9:16`, `2:3`, `3:2`, `21:9` |
| `extra_body.image` | img2img | Array of image URLs or Data URI Base64 |
| `extra_body.response_format` | No | `url` or `b64_json` |
| `return_base64` | No | `true` for Base64 output in text-to-image |

### Critical Rules

1. **Never** place `response_format` at the top level. Always nest it inside
   `extra_body`.
2. **Never** pass `tags: ["img2img"]` for image-to-image. Use `extra_body.image`
   instead.
3. For image-to-image, provide input images via `extra_body.image` as an array.
4. Client timeout should be 60s-360s; generation may take tens of seconds.

### Workflows

- **Text-to-image**: Only `model`, `prompt`, `size` required. Omit `image`.
- **Image-to-image**: Add `extra_body.image` with one or more image URLs.
- **Multi-image composition**: Pass multiple URLs in `extra_body.image`.

For full parameter tables, size/ratio references, and curl examples, see
`references/image_api.md`.

## Video Generation

Video generation is **asynchronous**: create a task, then poll for the result.

### Key Parameters (Create Task)

| Parameter | Required | Description |
|-----------|----------|-------------|
| `model` | Yes | `agnes-video-v2.0` |
| `prompt` | Yes | Video content description |
| `image` | No | Image URL for image-to-video |
| `width` / `height` | No | Default 1152x768. May be normalized to 480p/720p/1080p. |
| `num_frames` | No | Must be <= 441 and follow `8n + 1` rule (e.g. 121) |
| `frame_rate` | No | 1-60. Default 24. |
| `negative_prompt` | No | Content to avoid |
| `seed` | No | For reproducible results |
| `extra_body.image` | No | Array of keyframe image URLs |
| `extra_body.mode` | No | `keyframes` for keyframe animation |

### Duration Control

`seconds = num_frames / frame_rate`

| Duration | num_frames | frame_rate |
|----------|------------|------------|
| ~3s | 81 | 24 |
| ~5s | 121 | 24 |
| ~10s | 241 | 24 |
| ~18s | 441 | 24 |

### Task Flow

1. **Create**: `POST /v1/videos` → returns `video_id` and `task_id`.
2. **Poll**: `GET /agnesapi?video_id=<VIDEO_ID>` → check `status`.
3. **Download**: When `status` is `completed`, get the video URL from
   `metadata.url`.

Status values: `queued` → `in_progress` → `completed` (or `failed`).

For full parameter tables, response formats, and curl examples, see
`references/video_api.md`.

## Pricing (Current)

| Type | Standard | Current (Free) |
|------|----------|----------------|
| Image generation | $0.003/image | **$0/image** |
| Video duration | $0.005/second | **$0/second** |

For RPM limits and token plan details, see `references/pricing_and_limits.md`.

## Prompt Best Practices

### Image Prompts

Structure: `[Subject] + [Scene] + [Style] + [Lighting] + [Composition] + [Quality]`

### Video Prompts

Structure: `[Subject] + [Action] + [Scene] + [Camera Movement] + [Lighting] + [Style]`

For image-to-video, describe what should move and what should stay stable.

## Error Handling

| Status | Meaning | Action |
|--------|---------|--------|
| 400 | Invalid request | Check parameters, especially `extra_body` nesting |
| 401 | Unauthorized | Verify API key |
| 404 | Task not found | Check `video_id` / `task_id` |
| 500 | Server error | Retry after a short wait |
| 503 | Service busy | Retry later |

## Resources

- `scripts/generate_image.py` — Image generation script (text-to-image, image-to-image, multi-image)
- `scripts/generate_video.py` — Video generation script (create task, poll, download)
- `references/image_api.md` — Full image API reference (both models)
- `references/video_api.md` — Full video API reference
- `references/pricing_and_limits.md` — Pricing, RPM limits, token plans
