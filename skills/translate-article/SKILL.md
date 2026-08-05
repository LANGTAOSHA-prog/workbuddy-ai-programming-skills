---
name: translate-article
description: >-
  将 Markdown 文章在中文与英文之间互译,保留代码块、链接、标题结构与专业术语。当用户要把文章/文档/教程翻译
  成另一种语言、说"翻译这篇文章""中英互译""translate this doc""把文档翻成英文"时使用。配套 translate_md.py
  先把长文拆成片段批量翻译,再合并,避免破坏格式。
agent_created: true
---

# 文章翻译（Markdown 中英互译）

把一篇 Markdown 文章从中文译英或英译中,**保留结构、代码与术语**,而不是逐字机翻。
长文用配套脚本拆段翻译,降低上下文压力、避免格式错乱。

## 何时使用

- 用户发来 `.md` / `.markdown` 文章,要求翻译
- "把这篇文档翻成英文" / "translate this to Chinese" / "中英互译"
- 技术博客、README、教程、产品文档的跨语言发布

## 工作流程

### Step 1: 拆分（长文必做）

```bash
python3 scripts/translate_md.py split --input article.md --output segments.json
```

脚本把文章切成片段并标注类型：
- `heading`：仅文字部分翻译,`#` 前缀原样保留
- `text`：正文段落(可翻译)
- `code`：代码块整体保留,**不翻译**

### Step 2: 逐段翻译

读取 `segments.json`,对 `type != "code"` 的 `src` 逐段翻译,输出译文映射：

```json
{ "0": "Introduction", "1": "This is a paragraph about ...", "2": "Setup", "3": "Run the following:", "5": "..." }
```

(code 块 id 4 无需出现在映射里,脚本会自动保留原文)

翻译纪律：
- **代码块、行内代码、变量名、API 名、命令不翻译**
- **链接 URL 不翻译**,链接文字可译
- **专业术语**保持一致(首次出现可附原文,如「持续集成(Continuous Integration)」)
- 保留 Markdown 语法(`**加粗**`、`- 列表`、`> 引用`)
- 语气贴合目标语言习惯,不要生硬直译

### Step 3: 合并

```bash
python3 scripts/translate_md.py join \
  --input article.md --translations translations.json --output article.en.md
```

脚本按 id 回填,结构与原文一一对应;缺译文的片段保留原文。

### Step 4: 校验

- 打开 `article.en.md`,确认标题层级、代码块、列表完好
- 抽查术语一致性;必要时二次润色

## 短文 / 纯文本

若文章很短(单屏内),可跳过拆分,直接翻译并保留格式输出。

## 反模式

- 把代码块、命令、变量名也翻译了
- 破坏 Markdown 结构(标题层级错位、列表断裂)
- 术语前后不一致
- 机翻腔重、不贴合目标语言表达

## 参考

- `scripts/translate_md.py`：Markdown 拆分/合并(仅用 Python 标准库)
