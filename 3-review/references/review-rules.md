# Diff Review Rules

本文件只保留 3-review 编排层独有的规则；双轴审查纪律（固定基点、定位 spec/standards、Fowler 味道基线、并行 sub-agent、汇总不重排）已下沉到 `vocabulary/code-review`，此处不重复。

## 风险路由（编排层专属）

- **单 reviewer**：机械性、纯文档或极小且低风险的 diff。分别检查适用的 Standards 与 Spec，并说明未启用的独立轴。
- **双轴并行**：行为变化、高风险改动，或 spec 复杂且存在明显取舍，且宿主提供独立只读上下文时，独立运行 Standards 与 Spec reviewer。
- **双轴串行**：宿主缺少独立只读上下文，或 diff 很大、上下文可能超限时使用；先 Standards，再 Spec，并在报告中说明原因。

高风险信号包括数据迁移、权限/安全、公共 API、并发、持久化、跨模块行为和性能/可靠性门禁。审查深度不由行数单独决定。

## 输入契约（编排层对核心层的增强）

核心层 `vocabulary/code-review` 只采 `git diff <fixed-point>...HEAD`；编排层额外要求：

1. 记录 `git log <fixed-point>..HEAD --oneline` 与 `git diff <fixed-point>...HEAD`，再采集 `git diff --cached`、`git diff`。
2. 运行 `git ls-files --others --exclude-standard`，记录全部未跟踪文件并审查其内容。无意纳入本次变更的用户文件必须逐项显式排除并说明理由。

## 裁决（编排层专属）

- 主流程唯一汇总，保留 `## Standards` 与 `## Spec`，不合并发现、不改变原严重级别，只给出一个裁决。
- 裁决取值：**PASS**、**PASS WITH WARNINGS**、**FAIL**。
- FAIL 回传修复；PASS 或 PASS WITH WARNINGS 才能作为进入 `/5-git` 的交接产物。

## 完成条件

- fixed point 提交差异、spec、staged/unstaged、未跟踪文件内容，以及已有或审查时新运行的验证证据均已记录。
- 所有排除文件均逐项列出理由。
- 每条发现有轴、严重级别、位置、证据和最小修复建议。
- 未验证门禁已列为 warning。
- 报告只含一个 PASS、PASS WITH WARNINGS 或 FAIL 裁决。
