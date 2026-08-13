# Diff Review Rules

## 风险路由

- **单 reviewer**：机械性、纯文档或极小且低风险的 diff。分别检查适用的 Standards 与 Spec，并说明未启用的独立轴。
- **双轴并行**：行为变化、高风险改动，或 spec 复杂且存在明显取舍时，独立运行 Standards 与 Spec reviewer。
- **双轴串行**：仅在 diff 很大、上下文可能超限时使用；先 Standards，再 Spec，并在报告中说明原因。

高风险信号包括数据迁移、权限/安全、公共 API、并发、持久化、跨模块行为和性能/可靠性门禁。审查深度不由行数单独决定。

## 审查准备

1. 记录 `git log <fixed-point>..HEAD --oneline` 与 `git diff <fixed-point>...HEAD`，再采集 `git diff --cached`、`git diff`。
2. 运行 `git ls-files --others --exclude-standard`，记录全部未跟踪文件并审查其内容。无意纳入本次变更的用户文件必须逐项显式排除并说明理由。
3. 优先使用输入契约提供的任务、issue、PRD 或 spec；commit 引用和路径参数仅作后备。没有可用 spec 时，该缺口本身阻断正式裁决。
4. 从项目规则、贡献指南、领域上下文、ADR 及项目原生 linter/formatter/type 配置派生 Standards。
5. 从 spec 提取功能门禁。性能、可靠性、资源和覆盖率等指标必须自动验证，或标注“需手动验证”并降级为 warning。

## 双轴边界

- Standards 只按已定位的项目规范和技术栈审查命名、类型、异常、依赖、公共 API 文档及其他明确门禁。
- Spec 只核对缺失或部分实现、范围蔓延、意图不符和功能目标门禁。
- 汇总保留 `## Standards` 与 `## Spec`，不合并发现、不改变原严重级别。

## 完成条件

- fixed point 提交差异、spec、staged/unstaged、未跟踪文件内容与验证证据均已记录。
- 所有排除文件均逐项列出理由。
- 每条发现有轴、严重级别、位置、证据和最小修复建议。
- 未验证门禁已列为 warning。
- 报告只含一个 PASS、PASS WITH WARNINGS 或 FAIL 裁决。
