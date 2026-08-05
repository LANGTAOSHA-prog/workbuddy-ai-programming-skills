# Agnes AI Video Generation API Reference

## Base URL

```
https://apihub.agnes-ai.com
```

## Authentication

```
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

## Model

`agnes-video-v2.0` — Asynchronous video generation supporting text-to-video,
image-to-video, and keyframe animation.

- **Pricing**: $0.005/second standard, **$0/second current**

## Endpoints

| Action | Method | Endpoint |
|--------|--------|----------|
| Create task | POST | `/v1/videos` |
| Get result (recommended) | GET | `/agnesapi?video_id=<VIDEO_ID>` |
| Get result (legacy) | GET | `/v1/videos/<TASK_ID>` |

## Create Task Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `model` | string | Yes | `agnes-video-v2.0` |
| `prompt` | string | Yes | Video content description |
| `image` | string | No | Image URL for image-to-video |
| `mode` | string | No | `ti2vid` or `keyframes` |
| `height` | integer | No | Video height (default: 768) |
| `width` | integer | No | Video width (default: 1152) |
| `num_frames` | integer | No | Total frames, <= 441, must follow `8n + 1` rule |
| `frame_rate` | number | No | 1-60 (default: 24) |
| `num_inference_steps` | integer | No | Number of inference steps |
| `seed` | integer | No | Random seed for reproducible results |
| `negative_prompt` | string | No | Content to avoid |
| `extra_body.image` | array | No | Keyframe image URLs for keyframe mode |
| `extra_body.mode` | string | No | `keyframes` |

## Duration Control

```
seconds = num_frames / frame_rate
```

### Rules

- `num_frames` must be <= 441
- `num_frames` must follow the `8n + 1` rule (e.g., 81, 121, 161, 201, 241, 281, 321, 361, 401, 441)
- `frame_rate` supports 1-60

### Common Duration Presets

| Duration | num_frames | frame_rate |
|----------|------------|------------|
| ~3s | 81 | 24 |
| ~5s | 121 | 24 |
| ~10s | 241 | 24 |
| ~18s | 441 | 24 |

## Resolution Normalization

The model supports three standard tiers: `480p`, `720p`, `1080p`. When
requested `width`/`height` don't match supported specs, the system maps to the
nearest standard configuration.

### Supported Aspect Ratios

| Ratio | Use Case |
|-------|----------|
| `16:9` | Landscape, product demos, YouTube |
| `9:16` | Vertical shorts, TikTok/Reels |
| `1:1` | Square, social media feeds |
| `4:3` | Traditional landscape |
| `3:4` | Vertical presentations |

**Important**: Use the `size` and `seconds` fields from the API response as the
source of truth, not the requested dimensions.

## Create Task Examples

### Text-to-video

```bash
curl -X POST https://apihub.agnes-ai.com/v1/videos \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agnes-video-v2.0",
    "prompt": "A cinematic shot of a cat walking on the beach at sunset, soft ocean waves, warm golden lighting",
    "height": 768,
    "width": 1152,
    "num_frames": 121,
    "frame_rate": 24
  }'
```

### Image-to-video

```bash
curl -X POST https://apihub.agnes-ai.com/v1/videos \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agnes-video-v2.0",
    "prompt": "The woman slowly turns around and looks back at the camera, natural facial expression",
    "image": "https://example.com/image.png",
    "num_frames": 121,
    "frame_rate": 24
  }'
```

### Keyframe animation

```bash
curl -X POST https://apihub.agnes-ai.com/v1/videos \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agnes-video-v2.0",
    "prompt": "Generate a smooth cinematic transition between the keyframes",
    "extra_body": {
      "image": [
        "https://example.com/keyframe1.png",
        "https://example.com/keyframe2.png"
      ],
      "mode": "keyframes"
    },
    "num_frames": 121,
    "frame_rate": 24
  }'
```

## Create Task Response

```json
{
  "id": "task_YOUR_TASK_ID",
  "task_id": "task_YOUR_TASK_ID",
  "video_id": "video_YOUR_VIDEO_ID",
  "object": "video",
  "model": "agnes-video-v2.0",
  "status": "queued",
  "progress": 0,
  "created_at": 1780457477,
  "seconds": "10.0",
  "size": "1280x768"
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Task ID |
| `task_id` | string | Task ID (same as `id`) |
| `video_id` | string | Video ID (recommended for retrieval) |
| `object` | string | Usually `video` |
| `model` | string | Model name |
| `status` | string | `queued`, `in_progress`, `completed`, `failed` |
| `progress` | integer | Progress percentage |
| `created_at` | integer | Creation timestamp |
| `seconds` | string | Video duration |
| `size` | string | Video resolution |

## Get Video Result

### By video_id (recommended)

```bash
curl -X GET 'https://apihub.agnes-ai.com/agnesapi?video_id=<VIDEO_ID>' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```

### By video_id + model_name

```bash
curl -X GET 'https://apihub.agnes-ai.com/agnesapi?video_id=<VIDEO_ID>&model_name=agnes-video-v2.0' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```

### Legacy: By task_id

```bash
curl -X GET 'https://apihub.agnes-ai.com/v1/videos/<TASK_ID>' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```

## Final Result Response

```json
{
  "id": "task_YOUR_TASK_ID",
  "video_id": "task_YOUR_TASK_ID",
  "task_id": "task_YOUR_TASK_ID",
  "object": "video",
  "model": "agnes-video-v2.0",
  "status": "completed",
  "progress": 100,
  "created_at": 1784530473,
  "completed_at": 1784530510,
  "seconds": "1.0",
  "size": "832x448",
  "metadata": {
    "size_mapping": {
      "adjusted": true,
      "height": 448,
      "message": "Input size 1024x576 was mapped to nearest preset 480p/16:9 (832x448)",
      "ratio": "16:9",
      "requested_height": 576,
      "requested_width": 1024,
      "resolution": "480p",
      "width": 832
    },
    "url": "https://platform-outputs.agnes-ai.space/videos/agnes-video-v2.0/task_YOUR_TASK_ID.mp4"
  }
}
```

### Result Fields

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Task status |
| `progress` | integer | Progress percentage |
| `created_at` | integer | Creation timestamp |
| `completed_at` | integer | Completion timestamp |
| `seconds` | string | Video duration |
| `size` | string | Actual output resolution |
| `metadata.url` | string | Final video URL (available when completed) |
| `metadata.size_mapping` | object | Size normalization details |
| `error` | object/null | Error info if failed |

## Task Status Values

| Status | Description |
|--------|-------------|
| `queued` | Task waiting in queue |
| `in_progress` | Video being generated |
| `completed` | Generation successful |
| `failed` | Generation failed |

## Recommended Parameters

| Scenario | Settings |
|----------|----------|
| Standard generation | width: 1152, height: 768, num_frames: 121, frame_rate: 24 |
| Social shorts | num_frames: 81 or 121, frame_rate: 24 |
| Longer videos | Increase num_frames or reduce frame_rate |
| Smoother motion | frame_rate: 24 or 30 |
| Reproducible results | Set fixed seed |
| Keyframe transition | extra_body.mode: "keyframes" |
| Avoid unwanted content | Use negative_prompt |

## Prompt Best Practices

### Text-to-video

```
[Subject] + [Action] + [Scene] + [Camera Movement] + [Lighting] + [Style]
```

Example: `A young astronaut walking across a red desert planet, dust blowing in the wind, slow cinematic tracking shot, dramatic sunset lighting, realistic sci-fi style`

### Image-to-video

Describe what should move and what should stay stable:

`Animate the character with subtle breathing motion, hair moving gently in the wind, background lights flickering softly, while keeping the face and outfit consistent`

### Keyframe animation

`Create a smooth transition from the first keyframe to the second keyframe, maintaining character identity, consistent camera angle, and natural motion`

## Error Codes

| Status | Description |
|--------|-------------|
| 400 | Invalid request parameters |
| 401 | Unauthorized — check API key |
| 404 | Task or video not found |
| 500 | Server error |
| 503 | Service busy, try again later |
