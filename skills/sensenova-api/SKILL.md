---
name: sensenova-api
description: "Access SenseNova (日日新) API for text chat, image generation, and multimodal understanding. Supports four models: sensenova-6.8-flash-lite (multimodal agent, text+image→text, 256K context), sensenova-u1-fast (infographic/image generation), deepseek-v4-flash (reasoning, 1M context), and glm-5.2 (flagship text model, 1M context, 128K output). Uses OpenAI-compatible Chat Completions, Anthropic-compatible Messages API, and a dedicated Images endpoint. Requires SENSENOVA_API_KEY environment variable."
triggers:
  - "用日日新"
  - "用SenseNova"
  - "调用商汤API"
  - "SenseNova 对话"
  - "SenseNova 图片生成"
  - "sensenova"
---

# SenseNova API

通过 SenseNova（日日新）平台调用商汤大模型 API，包括文本对话、图像生成和多模态理解。

## Quick Start

用户想要使用 SenseNova 进行对话、生成图片或调用工具时触发。

```
用户: 用SenseNova帮我分析这张图片：xxx
→ 用 chat.py 调用 sensenova-6.8-flash-lite（支持图像输入）

用户: 用SenseNova生成一张信息图
→ 用 image_gen.py 调用 sensenova-u1-fast

用户: 用SenseNova思考一下这个数学题
→ 用 chat.py 调用 deepseek-v4-flash，开启 reasoning_effort

用户: 用SenseNova写一份长文分析
→ 用 chat.py 调用 glm-5.2（1M 上下文，128K 输出）
```

## Prerequisites

- **API Key**: 在 SenseNova 平台申请，存储在环境变量 `SENSENOVA_API_KEY`
- **Base URLs**:
  - OpenAI 兼容: `https://token.sensenova.cn/v1`
  - Anthropic 兼容: `https://token.sensenova.cn/v1/messages`
  - 图片生成: `https://token.sensenova.cn/v1/images/generations`
- **Auth**: `Authorization: Bearer $SENSENOVA_API_KEY`

## Available Models

| Model ID | 类型 | 输入 | 输出 | 上下文 | 特性 |
|----------|------|------|------|--------|------|
| `sensenova-6.8-flash-lite` | 多模态智能体 | 文本 + 图片 | 文本 | 256K | 工具调用、JSON 输出、流式 |
| `sensenova-u1-fast` | 信息图生成 | 文本 | 图片 | — | 11 种尺寸比例 |
| `deepseek-v4-flash` | 高性能推理 | 文本 | 文本 | 1M | 思考模式、工具调用、JSON |
| `glm-5.2` | 旗舰文本模型 | 文本 | 文本 | 1M | 128K 最大输出、长文写作 |

## Endpoints

| 端点 | 方法 | 模型 | 说明 |
|------|------|------|------|
| `/v1/chat/completions` | POST | 6.8 Flash-Lite, DeepSeek, GLM-5.2 | OpenAI 兼容对话 |
| `/v1/messages` | POST | 6.8 Flash-Lite, DeepSeek, GLM-5.2 | Anthropic 兼容对话 |
| `/v1/images/generations` | POST | U1 Fast | 图像生成 |
| `/v1/models` | GET | 所有 | 模型列表查询 |

## Scripts

### Chat Completion

```bash
python scripts/chat.py \
  --model sensenova-6.8-flash-lite \
  --prompt "介绍一下商汤科技"

# 图像输入
python scripts/chat.py \
  --model sensenova-6.8-flash-lite \
  --prompt "图片里面有什么" \
  --image https://example.com/image.png

# 思考模式
python scripts/chat.py \
  --model deepseek-v4-flash \
  --prompt "9.11和9.8哪个更大" \
  --reasoning high

# JSON 输出
python scripts/chat.py \
  --model deepseek-v4-flash \
  --prompt "列出三种编程语言及其特点" \
  --json-mode
```

### Image Generation

```bash
python scripts/image_gen.py \
  --prompt "生成一个信息图，介绍人工智能应用" \
  --size 2752x1536 \
  --output infographic.png
```

## Key Parameters

### Chat (OpenAI compatible)

| 参数 | 必填 | 说明 |
|------|------|------|
| `model` | ✅ | 模型 ID |
| `messages` | ✅ | 消息列表 |
| `stream` | ❌ | 流式输出 |
| `temperature` | ❌ | 0-2，默认 0.6 (6.8 Flash-Lite) / 1 (DeepSeek, GLM-5.2) |
| `max_tokens` | ❌ | 最大输出 token 数 |
| `reasoning_effort` | ❌ | deepseek 专用：low/medium/high/none |
| `response_format` | ❌ | `{"type":"json_object"}` 启用 JSON |
| `tools` | ❌ | 工具调用定义 |

### Image Generation

| 参数 | 必填 | 说明 |
|------|------|------|
| `model` | ✅ | 固定 `sensenova-u1-fast` |
| `prompt` | ✅ | 描述文本，最大 4096 tokens |
| `size` | ❌ | 默认 `2752x1536`，11 种比例 |
| `n` | ❌ | 生成数量，默认 1 |

### 支持的图片尺寸

`1664x2496` (2:3) · `2496x1664` (3:2) · `1760x2368` (3:4) · `2368x1760` (4:3) · `1824x2272` (4:5) · `2272x1824` (5:4) · `2048x2048` (1:1) · `2752x1536` (16:9) · `1536x2752` (9:16) · `3072x1376` (21:9) · `1344x3136` (9:21)

## Rate Limits

| Model | 限制 |
|-------|------|
| `sensenova-6.8-flash-lite` | 每 5 小时 1500 次 |
| `sensenova-u1-fast` | 每 5 小时 1500 次 |
| `deepseek-v4-flash` | 每 5 小时 500 次 |
| `glm-5.2` | 每 5 小时 500 次 |

## Error Handling

| HTTP | 类型 | 含义 |
|------|------|------|
| 400 | `invalid_request_error` | 参数不合法 |
| 403 | `permission_denied_error` | 不支持当前语言请求 |
| 404 | `not_found_error` | 模型不存在或已下线 |
| 429 | `quota_exceeded_error` | 速率/额度超限 |
| 500 | `internal_server_error` | 服务器内部错误 |

## Resources

- `scripts/chat.py` — 文本对话脚本（支持图像输入、工具调用、流式）
- `scripts/image_gen.py` — 图像生成脚本
- `references/api_reference.md` — 完整 API 参考
- `references/pricing_and_limits.md` — 定价与限制详情
