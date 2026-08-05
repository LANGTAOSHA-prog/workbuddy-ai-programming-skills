# 使用说明与排错

## 典型场景

### 场景 A:把生成的文章发到公众号(最常见)

文章 HTML 引用了本地图片 `cover.png`、`section.png`,都在 HTML 同级目录:

```bash
PYTHON="C:/Users/taojiang/.workbuddy/binaries/python/envs/default/Scripts/python.exe"
$PYTHON scripts/embed_images.py embed -i github_trending_article.html
# 生成 github_trending_article_paste.html,图片已内嵌
```

浏览器打开 `*_paste.html` → Ctrl+A → Ctrl+C → 公众号编辑器 Ctrl+V。

### 场景 B:图片在子目录

```bash
$PYTHON scripts/embed_images.py embed -i article.html --base-dir ./assets/images
```

### 场景 C:高质量封面,不要压太狠

```bash
$PYTHON scripts/embed_images.py embed -i article.html -w 1600 -q 92
```

### 场景 D:带透明底的 Logo,想保留透明

默认透明底会合成白底(避免变黑)。若要保留透明,用 `--keep-alpha`(输出体积更大):

```bash
$PYTHON scripts/embed_images.py embed -i article.html --keep-alpha
```

### 场景 E:只要单张图的 base64

```bash
$PYTHON scripts/embed_images.py convert -i cover.png -o cover.b64.txt
# 或直接打印
$PYTHON scripts/embed_images.py convert -i cover.png
```

## 排错

| 现象 | 原因 / 处理 |
|------|------------|
| `缺少依赖 Pillow` | `pip install Pillow`(受管 venv 内) |
| `找不到图片,已跳过` | HTML 里 `src` 路径相对 HTML 文件解析;若图在别处用 `--base-dir` 指定 |
| 粘贴后图片位置错乱 | 公众号编辑器会重写部分样式,手动拖拽调整即可 |
| 粘贴后样式丢失 | 圆角/阴影/hover 被过滤属正常,正文排版结构保留 |
| HTML 过大粘贴卡顿 | 降低 `--max-width` / `--quality`,或拆分多篇文章 |

## 兼容性

- 脚本仅依赖 Python 标准库 + Pillow,跨平台可用。
- 支持 `.png/.jpg/.jpeg/.webp/.gif`;GIF 取首帧静态化。
- 外链(`http(s)://`)与已内嵌(`data:`)图片自动跳过,不重复处理。
