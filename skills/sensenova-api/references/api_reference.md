# SenseNova API 完整参考

## 基础信息

| 项目 | 值 |
|------|-----|
| Base URL (OpenAI 兼容) | `https://token.sensenova.cn/v1` |
| Base URL (Anthropic 兼容) | `https://token.sensenova.cn/v1/messages` |
| Base URL (图片生成) | `https://token.sensenova.cn/v1/images/generations` |
| 鉴权 | `Authorization: Bearer $SENSENOVA_API_KEY` |
| 内容类型 | `Content-Type: application/json` |
| 响应格式 | JSON (同步) / SSE (流式) |

## 模型列表

### sensenova-6.7-flash-lite

| 属性 | 值 |
|------|-----|
| 类型 | 多模态智能体 |
| 输入模态 | 文本 + 图片 |
| 输出模态 | 文本 |
| 上下文长度 | 256K tokens |
| 最大输出 | 65,536 tokens |
| 量化 | fp8 |
| 调用限制 | 每 5 小时 1500 次 |
| 支持功能 | 工具调用、JSON 输出、流式 |
| 默认温度 | 0.6 |

### deepseek-v4-flash

| 属性 | 值 |
|------|-----|
| 类型 | 高性能推理 |
| 输入模态 | 文本 |
| 输出模态 | 文本 |
| 上下文长度 | 1M tokens |
| 最大输出 | 65,536 tokens |
| 调用限制 | 每 5 小时 500 次 |
| 支持功能 | 工具调用、JSON 输出、流式、思考模式 |
| 默认温度 | 1.0 |

### sensenova-u1-fast

| 属性 | 值 |
|------|-----|
| 类型 | 信息图/图片生成 |
| 输入模态 | 文本 |
| 输出模态 | 图片 |
| 调用限制 | 每 5 小时 1500 次 |

## 端点详情

### 1. Chat Completions (OpenAI 兼容)

```
POST https://token.sensenova.cn/v1/chat/completions
```

**请求体**

| 字段 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `model` | string | ✅ | — | 模型 ID |
| `messages` | array | ✅ | — | 消息列表，role ∈ {system, user, assistant, tool} |
| `stream` | boolean | ❌ | false | SSE 流式 |
| `stream_options` | object | ❌ | `{include_usage: true}` | 流式时包含用量 |
| `temperature` | float | ❌ | 0.6/1.0 | 采样温度 [0, 2] |
| `top_p` | float | ❌ | 0.95/1.0 | 核采样 [0, 1] |
| `max_tokens` | int | ❌ | 65536 | 最大输出 token |
| `n` | int | ❌ | 1 | 生成回复数 1-7 |
| `stop` | str/array | ❌ | — | 停止序列 |
| `frequency_penalty` | float | ❌ | 0 | 频率惩罚 [-2, 2] |
| `presence_penalty` | float | ❌ | 0 | 存在惩罚 [-2, 2] |
| `reasoning_effort` | str | ❌ | medium | 推理力度: low/medium/high/none (deepseek 专用) |
| `tools` | array | ❌ | — | 工具定义列表 |
| `tool_choice` | str/object | ❌ | "auto" | 工具选择策略 |
| `parallel_tool_calls` | boolean | ❌ | true | 并行工具调用 |
| `seed` | int | ❌ | — | 随机种子 |
| `response_format` | object | ❌ | — | `{type: "json_object"}` |

**响应**

```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1713167890,
  "model": "sensenova-6.7-flash-lite",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "回复内容",
      "reasoning_content": "推理内容（deepseek 专用）"
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 12,
    "completion_tokens": 8,
    "total_tokens": 20,
    "prompt_tokens_details": {"cached_tokens": 0}
  }
}
```

**finish_reason**: `stop` / `length` / `tool_calls` / `content_filter`

### 2. Anthropic Messages API

```
POST https://token.sensenova.cn/v1/messages
```

**请求体**

| 字段 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `model` | string | ✅ | — | 模型 ID |
| `messages` | array | ✅ | — | 消息列表 |
| `max_tokens` | int | ✅ | — | 最大输出 token [1, 65536] |
| `system` | str/array | ❌ | — | 系统提示词 |
| `temperature` | number | ❌ | 1 | [0, 2] |
| `top_p` | number | ❌ | 1 | [0, 1] |
| `stop_sequences` | array | ❌ | — | 停止序列 |
| `stream` | boolean | ❌ | false | 流式输出 |
| `metadata` | object | ❌ | — | 请求元数据 |
| `tools` | array | ❌ | — | 工具定义 |
| `tool_choice` | object | ❌ | `{type: "auto"}` | 工具选择 |
| `output_config` | object | ❌ | `{effort: "high"}` | 输出配置 |

**响应**

```json
{
  "id": "msg_<uuid>",
  "type": "message",
  "role": "assistant",
  "content": [
    {"type": "thinking", "thinking": "推理过程"},
    {"type": "text", "text": "最终回复"}
  ],
  "model": "sensenova-6.7-flash-lite",
  "stop_reason": "end_turn",
  "usage": {"input_tokens": 46, "output_tokens": 216}
}
```

**stop_reason**: `end_turn` / `max_tokens` / `stop_sequence` / `tool_use`

**流式事件序列**:
```
event: message_start
event: content_block_start (index, content_block)
event: content_block_delta (index, delta)
event: content_block_stop (index)
event: message_delta (delta, usage)
event: message_stop
```

### 3. 图像生成

```
POST https://token.sensenova.cn/v1/images/generations
```

**请求体**

| 字段 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `model` | string | ✅ | — | 固定 `sensenova-u1-fast` |
| `prompt` | string | ✅ | — | 描述，最大 4096 tokens |
| `size` | string | ❌ | 2752x1536 | 图片尺寸 |
| `n` | int | ❌ | 1 | 生成数量 |

**支持的 11 种尺寸**

| 尺寸 | 比例 | 用途 |
|------|------|------|
| `3072x1376` | 21:9 | 宽屏 |
| `2752x1536` | 16:9 | 标准宽屏 |
| `2496x1664` | 3:2 | 摄影 |
| `2368x1760` | 4:3 | 传统 |
| `2272x1824` | 5:4 | 画册 |
| `2048x2048` | 1:1 | 方形 |
| `1824x2272` | 4:5 | 肖像 |
| `1760x2368` | 3:4 | 竖版肖像 |
| `1664x2496` | 2:3 | 长肖像 |
| `1536x2752` | 9:16 | 竖屏 |
| `1344x3136` | 9:21 | 长竖屏 |

**响应**

```json
{
  "created": 1713167890,
  "data": [{"url": "https://cdn.sensenova.dev/gen/xxx"}]
}
```

⚠️ 返回的图片 URL 为**临时链接**，有效期 **1 小时**，需要及时下载保存。

### 4. 模型列表

```
GET https://token.sensenova.cn/v1/models
```

返回所有可用模型的详细信息，包括 ID、描述、输入输出模态、上下文长度、定价等。

## curl 速查

```bash
# 基础对话
curl https://token.sensenova.cn/v1/chat/completions \
  -H "Authorization: Bearer $SENSENOVA_API_KEY" \
  -d '{"model":"sensenova-6.7-flash-lite","messages":[{"role":"user","content":"Hello"}]}'

# 图像输入
curl https://token.sensenova.cn/v1/chat/completions \
  -H "Authorization: Bearer $SENSENOVA_API_KEY" \
  -d '{"model":"sensenova-6.7-flash-lite","messages":[{"role":"user","content":[{"type":"text","text":"看图"},{"type":"image_url","image_url":{"url":"https://img.png"}}]}]}'

# 工具调用
curl https://token.sensenova.cn/v1/chat/completions \
  -H "Authorization: Bearer $SENSENOVA_API_KEY" \
  -d '{"model":"sensenova-6.7-flash-lite","messages":[{"role":"user","content":"上海天气？"}],"tools":[{"type":"function","function":{"name":"get_weather","parameters":{"type":"object","properties":{"city":{"type":"string"}},"required":["city"]}}}]}'

# 思考模式
curl https://token.sensenova.cn/v1/chat/completions \
  -H "Authorization: Bearer $SENSENOVA_API_KEY" \
  -d '{"model":"deepseek-v4-flash","messages":[{"role":"user","content":"9.11vs9.8"}],"reasoning_effort":"high"}'

# JSON 输出
curl https://token.sensenova.cn/v1/chat/completions \
  -H "Authorization: Bearer $SENSENOVA_API_KEY" \
  -d '{"model":"deepseek-v4-flash","messages":[{"role":"user","content":"列三种语言"}],"response_format":{"type":"json_object"}}'

# 图片生成
curl https://token.sensenova.cn/v1/images/generations \
  -H "Authorization: Bearer $SENSENOVA_API_KEY" \
  -d '{"model":"sensenova-u1-fast","prompt":"信息图：AI应用","size":"2752x1536"}'

# 流式
curl https://token.sensenova.cn/v1/chat/completions \
  -H "Authorization: Bearer $SENSENOVA_API_KEY" \
  -d '{"model":"sensenova-6.7-flash-lite","messages":[{"role":"user","content":"Hello"}],"stream":true}'

# Anthropic 兼容
curl https://token.sensenova.cn/v1/messages \
  -H "Authorization: Bearer $SENSENOVA_API_KEY" \
  -d '{"model":"sensenova-6.7-flash-lite","max_tokens":1024,"messages":[{"role":"user","content":"Hello"}]}'

# 模型列表
curl https://token.sensenova.cn/v1/models \
  -H "Authorization: Bearer $SENSENOVA_API_KEY"
```

## 错误码

| HTTP | 类型 | 说明 |
|------|------|------|
| 400 | `invalid_request_error` | 参数不合法 |
| 400 | `failed_precondition_error` | 前置条件不满足 |
| 403 | `permission_denied_error` | 不支持当前语言 |
| 404 | `not_found_error` | 模型不存在/下线 |
| 408 | `canceled_error` | 客户端取消 |
| 429 | `quota_exceeded_error` | 速率/额度超限 |
| 500 | `internal_server_error` | 服务器错误 |

错误响应格式：
```json
{"error": {"type": "invalid_request_error", "code": "3", "message": "..."}}
```
