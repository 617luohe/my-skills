---
name: code-review
layer: vocabulary
description: Risk-based review of code changes for project standards and specification compliance.
disable-model-invocation: false
---

# Code Review — 代码审查

按变更风险选择审查深度，审查基点、需求来源和规范来源必须先确认。

## 风险路由

- **单 reviewer**：机械性改动、纯文档改动或极小且低风险的 diff。按适用范围检查 Standards 与 Spec，并说明未启用的独立轴。
- **双轴并行**：高风险改动、行为变化，或需求/spec 复杂、存在明显取舍时，独立运行 Standards 与 Spec reviewer。
- **双轴串行**：仅在 diff 很大、上下文可能超限时使用；先 Standards，再 Spec，并在报告中说明原因。

高风险信号包括数据迁移、权限/安全、公共 API、并发、持久化、跨模块行为和性能/可靠性门禁。不能仅按行数决定并行方式。

## 审查准备

1. 记录 `git diff <fixed-point>...HEAD`，未提交改动再附加 `git diff` 和 `git diff --cached`；同时记录 `git log <fixed-point>..HEAD --oneline`。上游已传 fixed-point 时直接使用，否则先确认。
2. 按优先级定位需求：上游传递的任务/issue 或 PRD/spec；commit 引用和路径参数仅作后备。没有 spec 时标记“无可用 spec”。
3. 从 `CLAUDE.md`、`CONTRIBUTING.md`、`CONTEXT.md`、`CONTEXT-MAP.md`、ADR 及项目 linter/formatter/类型配置派生 Standards。规范随项目技术栈确定；只有识别到项目默认使用 Python 时，才检查 Python 惯用法，不把 Python 规则当作通用标准。
4. 从上游 skill 提取功能门禁。性能、可靠性、资源和覆盖率等指标必须自动验证，或在裁决中标注“需手动验证”并降级为警告。

## Reviewer 任务

Standards reviewer 只按已定位的项目规范和技术栈审查命名、类型、异常、imports、公共 API 文档及其他明确门禁。

Spec reviewer 只按需求来源核对缺失或部分实现、范围蔓延、意图不符和功能目标门禁。

汇总时保留 `## Standards` 与 `## Spec` 两个轴，不合并、不重排优先级。单 reviewer 可在同一报告中分别列出适用轴；所有报告必须给出 PASS、PASS WITH WARNINGS 或 FAIL 裁决。

## 裁决

- **FAIL**：至少一个阻断问题，包括核心功能缺失、严重需求不符或严重违反项目规范。
- **PASS WITH WARNINGS**：无阻断但有警告，或存在未自动验证且需手动验证的功能门禁。
- **PASS**：无阻断和警告。

输出必须包含审查基点、提交列表、需求来源、规范来源、各轴发现和裁决。详细输出模板与 reviewer 角色见 `agents/standards.md`、`agents/spec.md`。

## MUST 规则

1. 基点、需求来源和规范来源先确认再审查。
2. 按风险路由单 reviewer、双轴并行或必要时串行；独立 reviewer 不互相污染上下文。
3. 保留 Standards/Spec 轴边界并明确裁决。
4. 功能门禁必须验证，未验证项降级为警告。
