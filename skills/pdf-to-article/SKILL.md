---
name: pdf-to-article
description: >-
  将 PDF 文档转换为公众号风格文章。抽取 PDF 正文,改写成公众号排版,配 AI 图并内嵌为可粘贴 HTML。当用户给出
  PDF 文件/论文/报告/电子书章节并希望发到微信公众号、或说"PDF转文章""把这份文档改成公众号图文"时使用。
  复用 wechat-img-embed 完成图片 base64 内嵌。
agent_created: true
---

# PDF 转公众号文章

把一份 PDF（论文、报告、产品文档、电子书章节）变成一篇能直接发公众号的图文。
流程与 `web-to-article` / `video-to-article` 一致：抽取 → 改写 → 配图 → 内嵌。

## 何时使用

- 用户发来一个 `.pdf` 文件,说「转成公众号文章」「把这份文档改写下发公众号」「PDF转文章」
- 用户有现成长篇内容（白皮书、研报、教程）想二次创作成图文
- 任何需要从结构化 PDF 提炼可读文章的场景

## 工作流程

### Step 1: 抽取正文

用配套脚本抽取文本（自动选后端 `pypdf` > `PyPDF2` > `pdfminer.six`）：

```bash
# 抽取全部页到文件
python3 scripts/extract_pdf.py report.pdf --output report.txt

# 只看某几页 / 先看元信息
python3 scripts/extract_pdf.py report.pdf --pages 1-5 --json
```

依赖（任选其一）：`pip install pypdf`。脚本对扫描件/纯图片页会跳过并提示。

### Step 2: 识别内容类型

读抽取出的文本,判断 PDF 是哪一种,决定改写策略：
- **论文/研报**：摘要先行、突出结论与方法、图表转文字描述
- **教程/文档**：保留步骤结构、补充「为什么」
- **产品/宣传**：提炼卖点、加场景化表达
- **书摘**：保留金句、串联主线

### Step 3: 改写成公众号风格

- 保留核心事实与观点,重排表达与结构(二次创作,非逐字搬运)
- 加小标题、分段、重点加粗;开头 2 句抓注意力
- 长文拆成多篇或加目录锚点
- 语言与用户一致(中文为主)

### Step 4: AI 配图 + 内嵌

- 为关键段落生成配图(可调用 agnes-media-gen / sensenova-api 等图像技能)
- 把文章写成 HTML,本地图片用 `wechat-img-embed` 压缩并内嵌 base64：

```bash
python3 ../wechat-img-embed/scripts/embed_images.py embed \
  --input article.html --output article_paste.html --max-width 1200 --quality 85
```

- 输出 `*_paste.html`,浏览器 Ctrl+A / Ctrl+C 全选复制,粘贴进公众号编辑器

### Step 5: 校验与交付

- 打开 `*_paste.html` 预览,确认图片显示、排版不乱
- 提示用户：公众号会过滤部分 CSS(圆角/阴影/hover),粘贴后按需微调

## 注意事项

- **扫描版 PDF**(图片页)抽不到文字：提示用户改用带文本层的 PDF,或提供 OCR 结果
- **版权**：未经授权不要搬运他人受版权保护的内容;改写需注明来源
- **表格/公式**：PDF 抽取易错乱,生成后务必人工核对关键数据与公式

## 参考

- `scripts/extract_pdf.py`：PDF 文本抽取(多后端回退)
- 依赖技能：`wechat-img-embed`(图片内嵌)、`agnes-media-gen` / `sensenova-api`(配图)
