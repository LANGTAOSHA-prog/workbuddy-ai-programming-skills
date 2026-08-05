---
name: ai-debug
description: >-
  Diagnose errors and stack traces: classify the failure, pinpoint the root cause, and propose a fix.
  当用户说「报错了」「这个异常怎么解」「帮我看下堆栈」「debug 这段」「为什么崩溃」
  「TypeError/NullPointerException/StackOverflow」「ai-debug」「debug this error」时触发。
  支持 Python / Node.js / Java 堆栈,可先用 parse_traceback.py 结构化再给结论。
agent_created: true
---

# ai-debug — 报错与堆栈诊断

把一段报错/堆栈变成「是什么错、为什么、怎么修」。先结构化,再下结论,不瞎猜。

## 何时使用

- 用户贴出报错、异常、崩溃日志求诊断
- 测试/CI 红了,需要定位失败根因
- 复现了一个 bug,想先理解再动手
- Code review 或运行时发现异常堆栈

## 工作流程

### 1. 结构化堆栈(推荐先跑脚本)

```bash
python3 scripts/parse_traceback.py TRACE_FILE [--json]
# 也支持管道:  cat trace.txt | python3 scripts/parse_traceback.py -
```

脚本自动识别 **Python / Node.js / Java** 三种堆栈,输出:

- 语言、错误类型、错误信息
- 栈帧数、最内层(真正出错的那一行)
- 由内到外的调用链

结构化的目的:一眼锁定出错点,而不是在长堆栈里肉眼找。

### 2. 分类与定位

按出错点(`top_frame`)和错误类型,给出:

1. **错误性质**:是空值/越界/类型/并发/资源/配置哪一类?
2. **根因假设**:最可能导致它的 1-3 个原因,按可能性排序(不要只给一个就收手)。
3. **证据**:堆栈里哪一行、哪个变量支撑这个假设。

### 3. 给出修复

- **最小修复**:先给能跑起来的止血方案。
- **根治方案**:为什么会到这步?缺校验、缺初始化、缺边界处理?
- **防复发**:加断言/测试/日志,让同类问题早点暴露。
- 涉及用户文件时,确认后再用 Edit 改,改动最小化。

## 常见错误速查

| 类型 | 常见根因 | 方向 |
|------|----------|------|
| `TypeError` / 属性读取 undefined | 对象未初始化、异步未 await、字段名拼错 | 加空值保护 / 校验返回值 |
| `ZeroDivisionError` / 除零 | 分母可能为 0 未判断 | 卫语句提前返回 |
| `NullPointerException` | 未判空就调用方法 | 早返回 / Optional |
| `IndexError` / 越界 | 循环/切片越界、空集合 | 边界检查 |
| `StackOverflow` / 爆栈 | 递归无终止、相互调用 | 迭代改写 / 终止条件 |
| 连接/超时类 | 配置错、网络、资源耗尽 | 查配置与依赖健康 |

## 反模式

- 没看堆栈就凭「经验」乱猜
- 只给一个原因,忽略其他可能性
- 直接改用户代码而不说明根因
- 止血方案掩盖了真正缺陷(吞异常、盲加 try)
- 把生产敏感信息(密钥、PII)写进回复

## 参考

- 随附 `scripts/parse_traceback.py`(纯标准库,支持 Py/JS/Java)
- 与 `ai-refactor` 配合:debug 定位 → refactor 消除根因
- 与 `ai-test-gen` 配合:修完补测试,防止复发
