---
name: social-post-gen
description: >-
  从「标题 + 要点」生成各平台社媒文案:小红书(种草干货)、微博(短平快话题)、朋友圈(口语化)。
  当用户要把一篇文章/话题/产品改写成社媒短文、说"写个小红书文案""生成微博""朋友圈文案""social post"时使用。
  配套 format_post.py 按平台套用格式与 emoji / 话题标签。
agent_created: true
---

# 社媒文案生成（小红书 / 微博 / 朋友圈）

把一段内容（文章、产品、观点）改写成适合不同平台的短文案。重点不是「翻译」，
而是**按平台调语气、结构、钩子与标签**。

## 何时使用

- 用户说「写个小红书文案」「生成微博」「朋友圈怎么发」「social post」「种草文案」
- 已有文章/要点,想分发到社媒引流
- 把长文浓缩成一屏可读的短内容

## 工作流程

### Step 1: 提炼要点

从用户给的素材（URL、文章、口述）提炼：
- 一个抓眼球的**标题/钩子**
- 3–5 条**核心要点**（每条一句,有信息量）

若素材是长文,可先用 `web-to-article` / `pdf-to-article` 改写后再浓缩。

### Step 2: 用脚本套格式

```bash
# 小红书:brief 文件首行=标题,其余=要点
python3 scripts/format_post.py --platform xhs \
  --input brief.txt --hashtags "AI,编程,效率"

# 微博:带 #话题#
python3 scripts/format_post.py --platform weibo \
  --title "AI 编程真香" --bullets points.txt --hashtags "AI编程"

# 朋友圈:口语化、无标签
python3 scripts/format_post.py --platform moments --input brief.txt --no-emoji
```

脚本负责：平台专属排版、emoji 钩子（关键词命中优先,否则轮转）、话题标签位置。
文案的**实质内容（标题与要点）由你撰写**,脚本只做格式化。

### Step 3: 润色

- 小红书：开头加痛点/反差钩子,结尾加互动（「收藏起来慢慢看」）
- 微博：控制长度,话题词精准,可抛问题引评论
- 朋友圈：第一人称、更短、像跟朋友聊

## 平台差异速记

| 平台 | 语气 | 结构 | 标签 |
|------|------|------|------|
| 小红书 | 种草/干货 | emoji 标题 + emoji 列表 | 末尾 `#话题` |
| 微博 | 短平快 | 标题 + 列表 + 提问 | 内联 `#话题#` |
| 朋友圈 | 口语/私人 | 简短要点 | 无 |

## 反模式

- 把长文整段照搬,不浓缩
- 语气跨平台雷同（朋友圈发成小红书风）
- 硬塞不相关的话题标签
- 标题空洞无钩子

## 参考

- `scripts/format_post.py`：平台格式化(仅用 Python 标准库,支持 --no-emoji)
