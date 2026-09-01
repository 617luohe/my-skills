---
name: 4-debug
description: 对难 bug 与性能回归做纪律化诊断：编排后调 diagnosing-bugs 六阶段核心，修复带回归测试交审。
---

# 4-debug — 调试编排壳

对难 bug 与性能回归做纪律化诊断。六阶段纪律（建反馈环 → 复现最小化 → 假设 → 插桩 → 修复+回归 → 清理，每阶段完成条件与必守门禁）只存在 `diagnosing-bugs`（canonical `vocabulary/diagnosing-bugs`），本文件只写编排与交接。

## 流程

1. 按 Call the Skill tool with "diagnosing-bugs" 走完六阶段，每阶段完成条件以该技能为准。
2. 修复必带回归测试，Call the Skill tool with "tdd" 按红-绿流程编写。
3. 带修复代码 + 回归测试（**保持未提交**）Call the Skill tool with "3-review" 验收；审查通过且用户明确授权后 `/5-git`。

## 边界

- 单行/已定位的直接修复走 CLAUDE.md 小改动路径，用户授权即可 `/5-git`。
- 发现架构问题（缺少测试接缝）时记录，交后续迭代重构，不在本流程内解决。

## 完成标准

- 已按 `diagnosing-bugs` 完成六阶段调试。
- 修复带回归测试或等价验证证据。
- 改动保持未提交，已准备交 `/3-review`。

## 详细规则参考

- `diagnosing-bugs`（canonical `vocabulary/diagnosing-bugs`）：六阶段诊断循环与门禁
- `tdd`（canonical `vocabulary/tdd`）：回归测试的红-绿流程
- `references/performance.md`：性能基线建立
- `references/memory.md`：内存问题验收
- `references/tooling.md`：工具选择
- `references/intermittent-failures.md`：偶发/时序/并发问题试验设计
