# WorkBuddy AI Programming Skills

一套面向 AI 辅助编程的 WorkBuddy 开源技能集，覆盖代码审查、提交信息生成、文档注释、测试生成和代码解释五大场景。

## 技能列表

| 技能 | 功能 | 触发词 |
|------|------|--------|
| [ai-code-review](./skills/ai-code-review/) | 智能代码审查：Bug检测、安全审计、性能分析、最佳实践 | "review this code", "代码审查", "检查代码" |
| [ai-commit-msg](./skills/ai-commit-msg/) | 根据 git diff 自动生成规范 commit message | "generate commit", "帮我写commit", "生成commit信息" |
| [ai-docstring](./skills/ai-docstring/) | 自动生成代码文档注释（JSDoc/pydoc/JavaDoc/GoDoc等） | "add docs", "写注释", "生成文档" |
| [ai-test-gen](./skills/ai-test-gen/) | 智能生成单元测试（Jest/pytest/JUnit/Go test等） | "write tests", "生成测试", "写测试用例" |
| [ai-code-explainer](./skills/ai-code-explainer/) | 逐段解释复杂代码，生成结构化说明 | "explain this code", "这段代码是什么意思" |

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

## 技能结构

每个技能遵循标准结构：

```
skill-name/
└── SKILL.md          # 技能定义和指令
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
