---
name: video-to-article
description: "读取短视频内容并改写成公众号风格文章。通过浏览器抓取视频平台的文案/字幕(抖音/快手/B站/YouTube/小红书等),或读取用户提供的字幕文本与字幕文件,改写成带 AI 配图、可直接复制粘贴到公众号编辑器的美化图文。当用户发来短视频链接、想把视频文案变成文章、或对短视频内容做二次创作成图文时使用此 skill。"
triggers:
  - "短视频转文章"
  - "视频转公众号"
  - "把视频文案改成文章"
  - "提取视频字幕写文章"
  - "video to article"
---

# Video to Article

短视频内容读取 → 改写 → AI 配图 → 图片内嵌,产出可直接发布到公众号的图文。

## 何时使用

- 用户发来一个短视频链接(抖音 / B站 / YouTube / 小红书 / 快手等),想变成公众号文章
- 用户已有视频文案 / 字幕(.srt / .vtt 或纯文本),想改写成图文
- 用户想对短视频内容做"二次创作"成公众号风格

## 工作流程

```
用户: 帮我把这个短视频转成公众号文章 + URL
→ 1. 读取短视频内容(见下,按输入形式分支)
→ 2. 改写成公众号风格(标题 / 导语 / 卡片正文 / 点评 / 总结)
→ 3. 用 Agnes AI / ImageGen 生成封面图 + 段落插图
→ 4. 用 HTML 模板排版(680px 宽,内联 CSS)
→ 5. 图片压缩 + base64 内嵌(paste-ready)
→ 6. 输出 HTML,提示复制步骤
```

## Step 1: 读取短视频内容

按输入形式自动分支:

### A. 平台链接(主力路径)
加载 `web-access` skill,用浏览器打开视频页,提取:
- 标题、作者、发布时间
- 简介 / 文案(很多博主把口播稿放在简介或置顶评论)
- 字幕 / 转录文本(开启 CC 字幕或 transcript 面板的平台)

抓取提示词示例:

```
打开 {url},提取这个视频的:1) 标题 2) 作者 / 账号 3) 简介正文
4) 如果有字幕 / 转录文本请完整提取 5) 置顶评论里的文案。
尽量保留原文案原文,不要概括、不要遗漏要点。
```

各平台可行性见 `references/platforms.md`。
**如果抓取结果为空**(抖音 / 快手等强反爬),礼貌提示用户:把视频文案复制粘贴给我,
或导出 .srt 字幕文件,我照样能改写。绝不要凭空编造视频内容。

### B. 用户直接给文案 / 字幕(最可靠)
- 纯文本:直接作为素材
- .srt / .vtt 文件:解析提取时间轴之外的文本行(跳过序号与时间码)
- 直接进 Step 2

### C. 本地视频文件(可选增强,需配置)
见下方「高级:本地视频 ASR」。当前受管环境默认不可用,除非用户已配 ffmpeg + ASR key。

## Step 2: 改写(公众号风格)

按 `references/writing_guide.md` 改写:
- 标题 15-25 字,有信息量不标题党
- 导语 1-2 段,放引用框,快速交代看点且有观点
- 正文卡片化,每段 2-4 句,关键词加粗
- 每个要点后附 1-2 句点评(有态度、补背景、指局限)
- 结尾总结框提炼 2-4 条洞察

**核心原则:保留原视频的事实、数据、观点骨架;重写表达与结构。** 这是二次创作,
不是逐字搬运——如果用户要"一字不差",走 B 路径且只排版、不加点评。

## Step 3-5: 配图 / 排版 / 内嵌

与 `web-to-article` 完全相同:
- 配图:`agnes-media-gen` 的 `generate_image.py` 或 `ImageGen` 工具
- 模板:复用 `web-to-article` 的 `references/article_template.html`(内联 CSS、680px、卡片布局)
- 内嵌:用 `wechat-img-embed` 的 `embed_images.py`(或本项目同款逻辑)压缩 + base64

封面图 Prompt 模板:

```
A dynamic illustration for [视频主题], [关键视觉元素],
[色彩方案], modern flat design with depth, clean composition,
high detail, social media cover art style, 16:9 aspect ratio
```

尺寸建议:2K 16:9(封面)或 1024x576(段落插图)。

## Step 6: 交付

`present_files` 展示最终 paste-ready HTML;告知用户:
浏览器打开 → Ctrl+A 全选 → Ctrl+C 复制 → 公众号编辑器 Ctrl+V 粘贴。

## 高级:本地视频 ASR(可选增强)

仅当用户已配置 ffmpeg + ASR key 时可用:
1. `ffmpeg -i video.mp4 audio.wav` 提取音频
2. 调 ASR 服务(如 OpenAI Whisper:`openai.Audio.transcribe("whisper-1", audio.wav)`)
3. 得到的文本进 Step 2

当前受管环境未预装 ffmpeg / whisper,需用户自行安装并配置 API key 才启用。

## 依赖

- `web-access`(浏览器抓取,内置)—— Step 1 平台链接路径
- `agnes-media-gen` 或 `ImageGen`(配图)—— Step 3
- `wechat-img-embed` 的 `embed_images.py` / Pillow(图片内嵌)—— Step 5
- 可选:`ffmpeg` + ASR key(本地视频路径)

## Resources

- `references/platforms.md` — 各平台抓取策略与限制
- `references/writing_guide.md` — 公众号改写风格指南
- 文章 HTML 模板逻辑与 `web-to-article` 的 `references/article_template.html` 一致,可直接复用
