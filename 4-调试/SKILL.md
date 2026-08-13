---
name: 4-调试
description: Diagnose hard-to-reproduce bugs, unknown root causes, and performance regressions via a structured six-phase loop. 已定位的小修复不触发。
disable-model-invocation: false
---

# 4-调试 — 结构化调试

按 [references/diagnosis-loop.md](references/diagnosis-loop.md) 执行六阶段调试流程：观测信号 → 复现 → 假设 → 验证 → 修复与回归 → 清理。

## 何时使用

- Bug 难复现、偶发
- 性能突然下降
- 回归：之前正常，现在失败
- 多次尝试修复仍未解决

## 快速调用

```
luohe，订单支付接口偶尔返回 500，帮我调试
```

核心纪律：先建立可比较观测信号、用工具验证不靠猜、一次只改一个变量、修复带回归测试、展示先脱敏。

## 与其他技能的关系

- **输入** — Bug 现象描述、错误日志、性能指标
- **流程** — `references/diagnosis-loop.md`；manifest dependency 为 `vocabulary/tdd`，行为修复运行时按 `/tdd` 建立回归保护
- **输出** — 修复代码 + 回归测试 + 项目原生验证证据，**保持未提交** → `/3-检查` 验收；审查通过且用户明确授权后 `/5-版本管理`
- **小修复例外** — 单行/已定位的直接修复走 CLAUDE.md 小改动路径，用户授权即可 `/5-版本管理`
- **后续** — 如果发现架构问题（缺少测试接缝），需在后续迭代中重构
