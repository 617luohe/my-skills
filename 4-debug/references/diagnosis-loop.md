# Diagnosis Loop

本文件只保留 4-debug 编排层对诊断循环的指针；六阶段纪律（反馈环 → 复现最小化 → 假设 → 插桩 → 修复+回归 → 清理）及其完成条件、门禁、脱敏要求已下沉到 `vocabulary/diagnosing-bugs`，此处不重复。

## Pointer

- **六阶段诊断纪律** → `vocabulary/diagnosing-bugs`（canonical `vocabulary/diagnosing-bugs`）
- **性能基线** → [performance.md](performance.md)
- **内存问题验收** → [memory.md](memory.md)
- **工具选择** → [tooling.md](tooling.md)
- **偶发/时序/并发** → [intermittent-failures.md](intermittent-failures.md)

## 编排层独有守卫

- 4-debug 在 diagnose-bugs 六阶段之外，负责修复的交接：回归测试按 `tdd` 红-绿流程写，修复代码 + 回归测试保持未提交交 `/3-review`。
- 单行/已定位的直接修复走 CLAUDE.md 小改动路径，不走完整六阶段。
