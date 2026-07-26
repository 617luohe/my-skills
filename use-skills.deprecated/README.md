# use-skills 已废弃

**废弃日期**: 2026-07-26

**原因**: 被 `/0-询问luohe` 路由器替代。

**迁移指南**:
- 原来用 `/use-skills <需求>` → 现在用 `/0-询问luohe`
- 原来自动匹配技能 → 现在查看主流程图 + 快速判断表，更清晰

**新路由器优势**:
1. 中文版 ask-matt，包含完整流程图
2. 主流程 + 上游 + 支撑层，层次清晰
3. 快速判断表（15 种常见情况）
4. 明确 multi-worker 的实验性定位

**如需恢复**:
```bash
mv use-skills.deprecated use-skills
```

**参考**: `0-询问luohe/SKILL.md`
