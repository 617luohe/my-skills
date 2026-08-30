---
name: 4-debug
description: 对难 bug 与性能回归做纪律化诊断：先建反馈环、最小化、假设、验证、修复加回归测试。
disable-model-invocation: false
---

# 4-debug — 结构化调试编排壳

进入 `references/diagnosis-loop.md` 六阶段循环（观测信号 → 复现 → 假设 → 验证 → 修复+回归 → 清理）。六阶段流程、每阶段完成条件与必守门禁只存在该文件，本文件只写编排与交接。

## 流程

1. 按 `references/diagnosis-loop.md` 走完六阶段，每阶段完成条件以该文件为准。
2. 修复必带回归测试，按 `/tdd` 红-绿流程编写。
3. 带修复代码 + 回归测试（**保持未提交**）交 `/3-review` 验收；审查通过且用户明确授权后 `/5-git`。

## 边界

- 单行/已定位的直接修复走 CLAUDE.md 小改动路径，用户授权即可 `/5-git`。
- 发现架构问题（缺少测试接缝）时记录，交后续迭代重构，不在本流程内解决。

## 完成标准

- 已按 `references/diagnosis-loop.md` 完成六阶段调试。
- 修复带回归测试或等价验证证据。
- 改动保持未提交，已准备交 `/3-review`。

## 详细规则参考

- `references/diagnosis-loop.md`：六阶段诊断循环与门禁
- `/tdd`（canonical `vocabulary/tdd`）：回归测试的红-绿流程
