---
name: wechat-img-embed
description: "将公众号文章 HTML 中的本地图片自动压缩并内嵌为 base64 data URI,生成可直接复制粘贴到微信公众平台编辑器的自包含 HTML。当用户需要把生成的文章或图片发布到微信公众号、需要把本地图片或外链图片打包进单个 HTML、或遇到图片无法直接上传公众号时,使用此 skill。"
---

# 公众号图片压缩并内嵌为 base64

## Overview

微信公众平台编辑器的「复制粘贴」导入对图片兼容性差:外链图片常丢失,本地图片需逐张上传。
本 skill 把 HTML 中引用的**所有本地图片**自动完成:尺寸压缩 → 转 JPEG(透明底合成白底)→ 编码为
`data:image/...;base64,...` 内嵌进 `src`。输出一份**自包含 HTML**,浏览器里 Ctrl+A / Ctrl+C 全选复制,
粘贴进公众号编辑器即可,图片随排版一起带过去,无需单独上传。

同时提供单张图片转 base64 的能力,便于在其它场景手动引用。

## 何时使用

- 用户说「复制到公众号」「发布到公众号」「导出公众号文章」「图片内嵌」时
- 任何生成了带本地图片路径(`.png/.jpg/.jpeg/.webp/.gif`)的 HTML 文章,需要发布到微信时
- 用户想把某张图片转成 base64 字符串直接嵌入页面时

## 快速启动

依赖(Pillow,已在受管 venv 中安装;若缺失执行 `pip install Pillow`):

```bash
# 1) HTML 中所有本地图片压缩 + 内嵌,输出 *_paste.html
PYTHON="C:/Users/taojiang/.workbuddy/binaries/python/envs/default/Scripts/python.exe"
$PYTHON scripts/embed_images.py embed \
  --input article.html \
  --output article_paste.html \
  --max-width 1200 --quality 85

# 2) 单张图片转 base64(输出到文件)
$PYTHON scripts/embed_images.py convert \
  --input cover.png --output cover.b64.txt
```

`--output` 省略时,embed 模式默认在输入文件名后追加 `_paste`。

## 工作流程

1. **确认输入**:拿到要发布的 HTML 文件路径(可由 web-to-article / 其它生成流程产出)。
2. **运行 embed**:脚本扫描 `<img src="...">`,跳过 `http(s)://`、`data:`、`//` 开头的外链,
   仅处理本地文件;图片找不到时打印警告并跳过,不中断。
3. **检查输出**:打开 `*_paste.html` 浏览器预览,确认图片正常显示、排版无大乱。
4. **复制粘贴**:在浏览器中 Ctrl+A 全选 → Ctrl+C 复制 → 公众号编辑器 Ctrl+V 粘贴。
5. **手动微调**:公众号会过滤部分 CSS(圆角/阴影/hover),粘贴后按需调整图片位置与间距。

## 脚本参数

`embed` 子命令:
- `--input, -i` (必填):源 HTML 文件
- `--output, -o` (可选):输出 HTML,默认 `{input}_paste.html`
- `--base-dir` (可选):图片查找基准目录,默认取 HTML 文件同级目录
- `--max-width, -w` (默认 1200):图片缩放上限像素,超出则等比缩小
- `--quality, -q` (默认 85):JPEG 压缩质量 1-100
- `--keep-alpha` (开关):保留透明通道输出 PNG(否则透明底合成白底转 JPEG,体积更小)

`convert` 子命令:
- `--input, -i` (必填):图片文件
- `--output, -o` (可选):base64 文本输出路径,省略则打印到 stdout
- `--max-width / --quality / --keep-alpha`:同上

## 公众号兼容注意事项

- 编辑器会过滤部分 CSS(圆角、阴影、hover 等),粘贴后视觉可能比预览朴素,结构不乱。
- 正文不支持外链跳转,文中链接可用「阅读原文」承载。
- 单图建议控制在 1200px 宽、体积 < 2MB,内嵌后整体 HTML 建议 < 5MB,避免粘贴卡顿。
- GIF 默认取首帧静态化(公众号正文不播动画)。

## 参考

- `references/usage.md`:更详细的使用示例与排错。
- 依赖脚本:`scripts/embed_images.py`(仅用 Python 标准库 + Pillow)。
