# Diff Review Rules

本文件只保留 3-review 编排层独有的规则，两侧正文都不在此重复：

- 双轴审查纪律（固定基点、定位 spec/standards、Fowler 味道基线、并行 sub-agent、汇总不重排）在 `vocabulary/code-review`。
- 风险路由在 `SKILL.md`「风险路由（本文件专属）」；调整路由只改 `SKILL.md`。

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
