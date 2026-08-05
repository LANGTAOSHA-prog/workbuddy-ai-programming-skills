# WorkBuddy AI Programming & Content Skills

一套面向 AI 辅助编程与内容创作的 WorkBuddy 开源技能集。覆盖代码审查、提交信息、文档注释、测试生成、代码解释五大编程场景，以及图片/视频生成、网页与短视频转公众号文章、图片内嵌、去 AI 味等内容创作场景。

## 技能列表

### 编程类

| 技能 | 功能 | 触发词 |
|------|------|--------|
| [ai-code-review](./skills/ai-code-review/) | 智能代码审查：Bug检测、安全审计、性能分析、最佳实践 | "review this code", "代码审查", "检查代码" |
| [ai-commit-msg](./skills/ai-commit-msg/) | 根据 git diff 自动生成规范 commit message | "generate commit", "帮我写commit", "生成commit信息" |
| [ai-docstring](./skills/ai-docstring/) | 自动生成代码文档注释（JSDoc/pydoc/JavaDoc/GoDoc等） | "add docs", "写注释", "生成文档" |
| [ai-test-gen](./skills/ai-test-gen/) | 智能生成单元测试（Jest/pytest/JUnit/Go test等） | "write tests", "生成测试", "写测试用例" |
| [ai-code-explainer](./skills/ai-code-explainer/) | 逐段解释复杂代码，生成结构化说明 | "explain this code", "这段代码是什么意思" |

### 内容创作类

| 技能 | 功能 | 触发词 |
|------|------|--------|
| [agnes-media-gen](./skills/agnes-media-gen/) | 调用 Agnes AI 生成图片与视频（agnes-image-2.0/2.1-flash, agnes-video-v2.0） | "用 Agnes 生成图片", "用 Agnes 生成视频", "Agnes Image" |
| [sensenova-api](./skills/sensenova-api/) | 调用 SenseNova（日日新）多模态对话与图片生成 API | "用 SenseNova 分析图片", "用 SenseNova 生成图片", "日日新" |
| [web-to-article](./skills/web-to-article/) | 把任意网页转换为公众号风格文章，含 AI 配图与图片内嵌 | "转成公众号文章", "网页转文章", "convert to article" |
| [wechat-img-embed](./skills/wechat-img-embed/) | 把文章 HTML 中的本地图片压缩并内嵌为 base64，便于复制粘贴到公众号 | "复制到公众号", "图片内嵌", "发布到公众号" |
| [video-to-article](./skills/video-to-article/) | 读取短视频内容（平台链接/字幕文件）并改写成公众号图文 | "短视频转文章", "视频转公众号", "提取视频字幕写文章" |
| [humanizer](./skills/humanizer/) | 去除 AI 写作痕迹，让文本更自然、更像人写 | "去AI味", "humanize", "去掉AI痕迹" |

## 安装

### 方式一：WorkBuddy 市场安装（推荐）

1. 在 WorkBuddy 中打开技能市场
2. 搜索技能名称（如 `ai-code-review`）
3. 点击安装

### 方式二：手动安装

```bash
# 克隆仓库
git clone https://github.com/LANGTAOSHA-prog/workbuddy-ai-programming-skills.git

# 复制技能到 WorkBuddy 技能目录
cp -r workbuddy-ai-programming-skills/skills/* ~/.workbuddy/skills/
```

## 技能详解

### ai-code-review — 智能代码审查

多维度代码审查，覆盖：
- **Bug 检测**：逻辑错误、空指针、竞态条件、资源泄漏
- **安全审计**：OWASP Top 10、注入、XSS、敏感数据、SSRF
- **性能分析**：N+1查询、复杂度分析、缓存策略
- **代码质量**：SOLID、DRY、命名规范、测试覆盖

支持 JavaScript/TypeScript、Python、Go、Java、Rust、C/C++ 等主流语言。

### ai-commit-msg — 智能提交信息

- 遵循 Conventional Commits 规范
- 自动检测变更范围和类型
- 支持多语言（中/英）
- 智能拆分建议多commit场景

### ai-docstring — 文档注释生成

- 自动识别语言和文档标准
- 覆盖函数、类、模块级别
- 解释 WHAT 和 WHY，不止 HOW
- 支持 Google/NumPy/Sphinx/JSDoc/JavaDoc/GoDoc/Doxygen

### ai-test-gen — 测试用例生成

- AAA 模式（Arrange-Act-Assert）
- 覆盖正常路径、边界值、异常路径
- 自动 mock 外部依赖
- 适配项目现有测试框架和风格

### ai-code-explainer — 代码解释

- 由浅入深的多层次解释
- 数据流、控制流、架构图
- 根据受众水平自适应调整
- 揭示设计意图和潜在问题

### agnes-media-gen — Agnes AI 图片与视频生成

- 支持 `agnes-image-2.0-flash`（文生图/图生图/多图合成）与 `agnes-image-2.1-flash`（高清升级）
- 支持 `agnes-video-v2.0`（文生视频/图生视频/关键帧动画，异步轮询）
- Base URL：`https://apihub.agnes-ai.com/v1`，认证 `Authorization: Bearer $AGNES_API_KEY`
- 当前图片与视频生成均免费
- 含 `generate_image.py` / `generate_video.py` 脚本与完整 API 参考

### sensenova-api —  SenseNova（日日新）API

- 多模态对话 `sensenova-6.7-flash-lite`（256K 上下文，支持图像输入）
- 高性能推理 `deepseek-v4-flash`（1M 上下文）
- 图片生成 `sensenova-u1-fast`（11 种尺寸）
- Base URL：`https://token.sensenova.cn/v1`（OpenAI 兼容 + Anthropic `/v1/messages` 兼容）
- 含 `chat.py` / `image_gen.py` 脚本与 API 参考

### web-to-article — 网页转公众号文章

- 输入任意 URL → 抓取网页 → 改写成公众号风格 → AI 配图 → 图片 base64 内嵌 → 输出可粘贴 HTML
- 复用 `wechat-img-embed` 的图片内嵌逻辑
- 改写保留核心事实与观点，重排表达与结构（二次创作，非逐字搬运）

### wechat-img-embed — 公众号图片压缩并内嵌 base64

- 扫描 HTML 中所有 `<img src>`，跳过外链，本地图压缩 + 透明底合成白底转 JPEG + 内嵌 base64
- 输出自包含 HTML，浏览器全选复制即可粘贴到公众号编辑器，无需逐张上传
- 含 `embed_images.py`（`embed` / `convert` 子命令）

### video-to-article — 短视频转公众号文章

- 读取短视频内容：平台链接（浏览器抓文案/字幕）、用户直给文案/字幕文件、本地视频 ASR（可选增强）
- 改写 + AI 配图 + 图片内嵌，产出公众号图文
- 抓不到内容时绝不编造，提示用户提供文案/字幕

### humanizer — 去 AI 味

- 识别并消除 AI 写作常见模式（套话、空洞赞美、八股结构等）
- 让文本更自然、有观点、像人写
- 适用于改写、润色、降 AI 检测率

## 技能结构

每个技能遵循标准结构：

```
skill-name/
├── SKILL.md            # 技能定义和指令（必含）
├── scripts/            # 可选：可执行的 Python/Bash 脚本
└── references/         # 可选：API 参考、写作指南等文档
```

## 贡献

欢迎提交 Issue 和 Pull Request：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/new-skill`)
3. 提交更改 (`git commit -m 'feat: add new skill'`)
4. 推送到分支 (`git push origin feature/new-skill`)
5. 创建 Pull Request

## 许可证

MIT License
