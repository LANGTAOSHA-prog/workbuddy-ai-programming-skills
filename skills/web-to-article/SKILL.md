---
name: web-to-article
description: "Convert any web page into a polished WeChat public account (公众号) style article. Fetches web content, extracts key information, rewrites with engaging copy, generates AI cover images, and outputs paste-ready HTML with embedded base64 images. Use when the user provides a URL and wants to create a 公众号 article, blog post, or shareable content."
triggers:
  - "转成公众号文章"
  - "生成公众号文章"
  - "转成文章"
  - "网页转文章"
  - "convert to article"
  - "make a blog post from"
---

# Web to Article

把任意网页内容转换成公众号风格文章，支持 AI 配图，一键复制粘贴到公众号编辑器。

## Quick Start

用户提供一个 URL，按以下流程生成文章：

```
用户: 帮我把 https://example.com/some-article 转成公众号文章
→ 1. 用 WebFetch 抓取网页内容
→ 2. 提取核心信息，改写成公众号风格
→ 3. 用 Agnes AI / ImageGen 生成封面图
→ 4. 用 HTML 模板排版
→ 5. 用 make_article.py 内嵌图片为 base64
→ 6. 输出 paste-ready HTML 文件
```

## Workflow

### Step 1: Fetch Content

用 WebFetch 工具抓取目标网页：

```
WebFetch(url="https://example.com/article", prompt="Extract the full article content including title, author, date, main text, key points, and any data/statistics. Preserve the structure and important quotes.")
```

如果页面是 SPA 或 WebFetch 抓不到完整内容，尝试：
- 用 `curl` 抓取原始 HTML
- 用 Jina Reader: `curl -s "https://r.jina.ai/https://目标URL"`
- 加载 `web-access` skill 用浏览器抓取

### Step 2: Rewrite for 公众号

公众号文章的写作要点：

1. **标题**：吸引眼球但不标题党，15-25 字最佳
2. **导语**：1-2 段，快速交代背景和看点，用引用框样式
3. **正文**：分段清晰，每段 2-4 句，适当加粗关键词
4. **点评**：每个要点后附简短点评，有态度有观点
5. **总结**：提炼趋势或洞察，不要泛泛而谈

写作风格参考 `references/writing_guide.md`。

### Step 3: Generate Cover Image

用 AI 图片生成工具创建封面图：

- 如果已安装 `agnes-media-gen` skill：用 `generate_image.py` 脚本
- 否则用 `ImageGen` 工具

封面图 Prompt 模板：

```
A dynamic tech illustration for [主题], [关键视觉元素],
[色彩方案], modern flat design with depth, clean composition,
high detail, social media cover art style, 16:9 aspect ratio
```

尺寸建议：2K 16:9（封面）或 1024x576（段落插图）。

### Step 4: Build HTML

用 `references/article_template.html` 作为基础模板，填入内容。

模板特点：
- 内联 CSS（公众号编辑器只认 inline style）
- 最大宽度 680px（适配手机阅读）
- 卡片式布局，圆角，柔和配色
- 支持代码块、引用框、标签、数据统计等组件

### Step 5: Embed Images (Paste-Ready)

运行 `make_article.py` 把图片压缩并内嵌为 base64：

```bash
python scripts/make_article.py \
  --input article.html \
  --output article_paste.html \
  --max-width 1200 \
  --quality 85
```

这会：
1. 读取 HTML 中所有 `<img src="...">` 引用的本地图片
2. 压缩（resize + JPEG 质量调整）
3. 转为 base64 data URI 内嵌
4. 输出一个自包含的 HTML 文件

用户只需在浏览器中打开 → Ctrl+A → Ctrl+C → 粘贴到公众号编辑器。

### Step 6: Present

用 `present_files` 展示最终的 paste-ready HTML 文件。

告知用户复制步骤：
1. 在浏览器中打开 HTML 文件
2. Ctrl+A 全选，Ctrl+C 复制
3. 在公众号编辑器中 Ctrl+V 粘贴

## HTML Components

模板内置以下组件，直接复制使用：

| 组件 | 用途 | 示例 |
|------|------|------|
| `.cover` | 封面图 | `<img class="cover" src="cover.png">` |
| `.intro` | 导语引用框 | `<div class="intro">导语内容</div>` |
| `.card` | 内容卡片 | `<div class="card">...</div>` |
| `.rank` | 排名徽章 | `<span class="rank rank-1">1</span>` |
| `.tag` | 标签 | `<span class="tag tag-lang">Python</span>` |
| `.commentary` | 点评框 | `<div class="commentary">点评内容</div>` |
| `.summary` | 总结框 | `<div class="summary">...</div>` |
| `.section-img` | 段落插图 | `<img class="section-img" src="section.png">` |
| `.divider` | 分隔符 | `<div class="divider">· · ·</div>` |

完整模板和组件代码见 `references/article_template.html`。

## Skill Dependencies

- **WebFetch**：抓取网页内容（内置工具）
- **agnes-media-gen** 或 **ImageGen**：生成配图（可选）
- **Pillow**：图片压缩（`make_article.py` 依赖，需安装到 managed venv）

安装 Pillow：

```bash
"C:/Users/taojiang/.workbuddy/binaries/python/versions/3.13.12/python.exe" -m venv "C:/Users/taojiang/.workbuddy/binaries/python/envs/default"
"C:/Users/taojiang/.workbuddy/binaries/python/envs/default/Scripts/pip.exe" install Pillow
```

## Resources

- `scripts/make_article.py` — 图片压缩 + base64 内嵌脚本
- `references/article_template.html` — 公众号文章 HTML 模板
- `references/writing_guide.md` — 公众号写作风格指南
