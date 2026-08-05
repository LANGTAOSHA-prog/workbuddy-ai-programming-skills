---
name: ai-diagram
description: >-
  Generate architecture and flow diagrams (Mermaid) from code or a description.
  当用户说「画个架构图」「生成流程图」「把这段逻辑画成图」「类图怎么画」
  「调用关系图」「模块依赖」「ai-diagram」「draw a diagram / flowchart / classDiagram」时触发。
  支持从代码库抽取模块依赖图,以及把步骤/类描述转成 Mermaid(flowchart / classDiagram)。
agent_created: true
---

# ai-diagram — 架构与流程图生成

把「说不清的结构」变成一眼能看懂的图。优先用 Mermaid(可在 GitHub / 多数 Markdown 渲染器直接显示),再按需补充文字说明。

## 何时使用

- 用户要架构图、流程图、类图、时序图、调用关系图
- 要快速理解一个陌生代码库的结构
- 设计新功能前,先用图对齐思路
- 文档/方案里需要可视化

## 工作流程

### 1. 选图类型

| 想表达 | 图类型 | 怎么来 |
|--------|--------|--------|
| 模块/文件依赖 | flowchart(模块图) | 扫描代码库 |
| 业务/逻辑步骤 | flowchart | 步骤描述 |
| 类与字段/方法 | classDiagram | 类描述 |
| 调用顺序/交互 | sequenceDiagram | 交互描述 |

### 2. 生成(优先用脚本)

**从代码库抽模块依赖图(自动识别 Py/JS/TS 的 import):**

```bash
python3 scripts/gen_mermaid.py module PATH [--depth N] [--json]
```

**把步骤串成流程图(支持中文,用 `->` 连接,`;` 分段):**

```bash
python3 scripts/gen_mermaid.py flow "用户请求->鉴权->处理->返回"
```

**把类描述转成类图(字段直接写,方法加 `()`,关系用 `-->`):**

```bash
python3 scripts/gen_mermaid.py class "User: id, name, email, save(); User --> Order"
```

脚本输出标准 Mermaid,可直接贴进 Markdown(用 ```` ```mermaid ```` 包裹)。

### 3. 补充与校验

- 复杂交互(时序、状态机)脚本覆盖不到时,直接手写 Mermaid 并解释。
- 给图配一段文字:每张图回答什么问题、关键节点是什么。
- 若图过大,建议分层(先顶层组件图,再展开关键子图)。

## Mermaid 速记

- 流程图:`flowchart TD` + `A[标签] --> B[标签]`
- 类图:`classDiagram` + `class X { +field; +method() }` + `X --> Y`
- 时序图:`sequenceDiagram` + `A->>B: 消息`
- 节点标签含空格/中文需用引号:`A["用户请求"]`

## 反模式

- 一股脑把所有文件画进一张巨图,反而看不清
- 图与文字脱节,不给任何解释
- 用不可渲染的私有格式(用户没法直接贴)
- 模块图把第三方库和外链噪音都画进来,淹没重点

## 参考

- 随附 `scripts/gen_mermaid.py`(纯标准库,module/flow/class 三种模式)
- 与 `ai-code-explainer` 配合:图看清结构 → 文字讲清意图
- 与 `ai-refactor` 配合:先画图定位耦合热点,再重构
