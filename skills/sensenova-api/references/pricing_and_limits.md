# SenseNova 定价与限制

## 调用限制

| Model | 限制 | 备注 |
|-------|------|------|
| `sensenova-6.7-flash-lite` | 每 5 小时 1500 次 | 多模态智能体 |
| `deepseek-v4-flash` | 每 5 小时 500 次 | 高性能推理 |
| `sensenova-u1-fast` | 每 5 小时 1500 次 | 图片生成 |

当超过限制时，API 返回 HTTP 429 `quota_exceeded_error`。

## 定价

当前文档显示各模型 pricing 均为 0（可能为免费额度或示例数据）。实际定价请以 SenseNova 控制台为准。

```json
"pricing": {
  "prompt": "0",
  "completion": "0",
  "image": "0",
  "request": "0",
  "input_cache_read": "0"
}
```

## 限制说明

- 上下文长度：sensenova-6.7-flash-lite 256K tokens，deepseek-v4-flash 1M tokens
- 最大输出：两者均为 65,536 tokens
- 单次并发请求数：未明确限制，超出配额返回 429
- 图片 URL 有效期：1 小时，到期后链接失效

## 支持的图片输入格式

- `image/png`
- `image/jpeg`
- `image/gif`
- `image/webp`

## 支持的输出格式

- 文本对话：纯文本 / JSON（通过 `response_format`）
- 图像生成：PNG（临时 URL）

## 数据地域

所有模型的数据中心位于中国大陆（`datacenters: [{country_code: "CN"}]`），适合中文场景和国内合规要求。
