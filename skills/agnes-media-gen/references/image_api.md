# Agnes AI Image Generation API Reference

## Base URL

```
https://apihub.agnes-ai.com/v1/images/generations
```

## Authentication

```
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

## Models

### agnes-image-2.0-flash

High-performance image generation and editing model. Supports text-to-image,
image-to-image, and multi-image composition. ELO score 1,184 on Artificial
Analysis image editing leaderboard (Top 20).

- **Pricing**: $0.003/image standard, **$0/image current**
- **Client timeout**: 60s-360s recommended

### agnes-image-2.1-flash

Upgraded model optimized for high-information-density visuals, complex
compositions, and detail-rich scenes. Better composition preservation during
image-to-image editing. Supports tier-based sizing with `ratio`.

- **Pricing**: $0.003/image standard, **$0/image current**
- **Client timeout**: 60s-360s recommended

## Request Parameters

### Common Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `model` | string | Yes | `agnes-image-2.0-flash` or `agnes-image-2.1-flash` |
| `prompt` | string | Yes | Text prompt for generation or editing instruction |
| `size` | string | Yes | Output size (see model-specific formats below) |
| `return_base64` | boolean | No | Set `true` for Base64 output in text-to-image |
| `extra_body.response_format` | string | No | `url` or `b64_json` |
| `extra_body.image` | string[] | img2img | Input image URLs or Data URI Base64 |

### agnes-image-2.0-flash Specifics

- `size`: Exact dimensions like `1024x768`, `1024x1024`, `768x1024`
- No `ratio` parameter

### agnes-image-2.1-flash Specifics

- `size`: Tier-based — `1K`, `2K`, `3K`, `4K` (recommended) or legacy exact sizes
- `ratio`: Aspect ratio — `1:1`, `3:4`, `4:3`, `16:9`, `9:16`, `2:3`, `3:2`, `21:9` (default: `1:1`)

### Size + Ratio Output Dimensions (2.1 Flash)

| Ratio | 1K | 2K | 3K | 4K |
|-------|-----|-----|-----|-----|
| `1:1` | 1024x1024 | 2048x2048 | 3072x3072 | 4096x4096 |
| `3:4` | 864x1152 | 1728x2304 | 2592x3456 | 3456x4608 |
| `4:3` | 1152x864 | 2304x1728 | 3456x2592 | 4608x3456 |
| `16:9` | 1312x736 | 2624x1472 | 3936x2208 | 5248x2944 |
| `9:16` | 736x1312 | 1472x2624 | 2208x3936 | 2944x5248 |
| `2:3` | 832x1248 | 1664x2496 | 2496x3744 | 3328x4992 |
| `3:2` | 1248x832 | 2496x1664 | 3744x2496 | 4996x3328 |
| `21:9` | 1568x672 | 3136x1344 | 4704x2016 | 6272x2688 |

## Critical Rules

1. **`response_format` must be inside `extra_body`**, never at top level.
   Placing it at top level causes a 400 error.
2. **No `tags` needed** for image-to-image. Do not pass `tags: ["img2img"]`.
3. **Image-to-image** uses `extra_body.image` (array), not top-level `image`.
4. Input images must be publicly accessible HTTPS URLs or Data URI Base64.

## Request Examples

### Text-to-image (URL output)

```bash
curl https://apihub.agnes-ai.com/v1/images/generations \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agnes-image-2.0-flash",
    "prompt": "A clean product photo of a glass cube on a white studio background",
    "size": "1024x768",
    "extra_body": {
      "response_format": "url"
    }
  }'
```

### Text-to-image (Base64 output)

```bash
curl https://apihub.agnes-ai.com/v1/images/generations \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agnes-image-2.0-flash",
    "prompt": "A glass cube on white background",
    "size": "1024x768",
    "return_base64": true
  }'
```

### Image-to-image (URL input + URL output)

```bash
curl https://apihub.agnes-ai.com/v1/images/generations \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agnes-image-2.0-flash",
    "prompt": "Transform into cinematic cyberpunk style",
    "size": "1024x768",
    "extra_body": {
      "image": ["https://example.com/input.png"],
      "response_format": "url"
    }
  }'
```

### Multi-image composition

```bash
curl https://apihub.agnes-ai.com/v1/images/generations \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agnes-image-2.0-flash",
    "prompt": "Combine the two characters into a fantasy battle scene",
    "size": "1024x768",
    "extra_body": {
      "image": [
        "https://example.com/char1.png",
        "https://example.com/char2.png"
      ],
      "response_format": "url"
    }
  }'
```

### 2.1 Flash with tier-based sizing

```bash
curl https://apihub.agnes-ai.com/v1/images/generations \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agnes-image-2.1-flash",
    "prompt": "A cinematic floating city above a misty canyon at sunrise",
    "size": "2K",
    "ratio": "16:9",
    "extra_body": {
      "response_format": "url"
    }
  }'
```

### Data URI Base64 input

```bash
curl https://apihub.agnes-ai.com/v1/images/generations \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agnes-image-2.1-flash",
    "prompt": "Make the object matte black",
    "size": "1024x768",
    "extra_body": {
      "image": ["data:image/png;base64,BASE64_HERE"],
      "response_format": "b64_json"
    }
  }'
```

## Response Format

### URL output

```json
{
  "created": 1780000000,
  "data": [
    {
      "url": "https://storage.googleapis.com/agnes-aigc/xxx.png",
      "b64_json": null,
      "revised_prompt": null
    }
  ]
}
```

### Base64 output

```json
{
  "created": 1780000000,
  "data": [
    {
      "url": null,
      "b64_json": "iVBORw0KGgoAAAANSUhEUgAA...",
      "revised_prompt": null
    }
  ]
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `created` | integer | Request creation timestamp |
| `data` | array | List of generated image results |
| `data[].url` | string/null | Generated image URL (null for Base64 output) |
| `data[].b64_json` | string/null | Base64 image data (null for URL output) |
| `data[].revised_prompt` | string/null | Revised prompt if available |

## Prompt Best Practices

### Text-to-image structure

```
[Subject] + [Scene / Background] + [Style] + [Lighting] + [Composition] + [Quality]
```

Example: `A professional product photo of a wireless headphone on a clean white background, soft studio lighting, sharp details, commercial photography style`

### Image-to-image structure

```
[Editing Instruction] + [Elements to Preserve] + [Target Style / Scene] + [Lighting] + [Composition]
```

Example: `Change the background to a futuristic city at night while keeping the person's face, outfit, and pose unchanged`

### Multi-image composition structure

```
[Reference roles] + [Target scene] + [Relationship between images] + [Style / Lighting]
```

Example: `Place the person from the first image beside the robot from the second image in a cinematic sci-fi battle scene`
