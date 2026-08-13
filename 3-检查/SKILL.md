---
name: 3-检查
description: 正式审查指定 diff，核对项目规范与需求并给出 PASS、PASS WITH WARNINGS 或 FAIL。触发：审查改动、review diff、代码验收。
disable-model-invocation: false
---

# 3-检查 — 正式 Diff Review

本技能只审查指定 diff。问题建单由 `/issue-reporting` 负责；根因调查由 `/4-调试` 负责；架构调查走 `/0-询问luohe` 的只读调查路由。

## 输入契约

在 fresh context 中接收且只接收：

1. **fixed point/base**：审查基点、提交列表与 `git diff <fixed-point>...HEAD` 提交差异。
2. **spec**：PRD、任务、issue、验收标准或用户明确需求。
3. **workspace diff**：`git diff --cached`、`git diff`，以及 `git ls-files --others --exclude-standard` 返回的未跟踪文件列表与内容。
4. **证据**：开发方已运行的项目原生 test/type/lint/build 命令及结果。

无意纳入的用户文件必须逐项显式排除并说明理由。缺少任何一项时只询问缺失项；不得用规划或开发聊天记忆补齐。四项可定位后，输入契约完成。

## 流程

1. 固定并记录基点、提交列表、spec、规范来源、diff 范围和验证证据。
2. 按 [review-rules.md](references/review-rules.md) 选择审查深度，并保持 Standards 与 Spec 两轴独立。
3. 功能、性能、可靠性或资源门禁能自动验证则运行；不能验证则记录“需手动验证”并至少给出 warning。
4. 输出可追踪意见：ID、轴、严重级别、`文件:行`、证据与最小修复建议。
5. 给出唯一裁决：**PASS**、**PASS WITH WARNINGS** 或 **FAIL**。

## 裁决

- **FAIL**：至少一个阻断问题，包括核心功能缺失、严重需求不符或严重违反项目规范。
- **PASS WITH WARNINGS**：无阻断，但存在警告或未自动验证的门禁。
- **PASS**：无阻断和警告。

报告必须包含输入契约四项、Standards、Spec、意见清单、未验证项和裁决。详细 reviewer 边界见 [standards-reviewer.md](references/standards-reviewer.md) 与 [spec-reviewer.md](references/spec-reviewer.md)。

## 交接

- FAIL：把全部阻断意见回传 `/2-开发` 或 `/4-调试`，修复后使用同一基点与 spec 复评。
- PASS WITH WARNINGS：默认完成审查；交接时保留 warning ID 与未修复理由。
- PASS：可交接。

任何裁决都不自动 commit。只有 PASS 或 PASS WITH WARNINGS 且用户明确授权，才进入 `/5-版本管理`。
