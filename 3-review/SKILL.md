---
name: 3-review
description: 对固定基点以来的改动做双轴正式审查：编排风险路由后调 code-review 核心，产出可追踪裁决。
---

# 3-review — 审查编排壳

对 `HEAD` 与用户给定 fixed point 之间的 diff 做双轴审查。去哪里的判定（Review / 只建单 / 查根因 / 架构评估）由 `/0-router` 排一次；本技能只承接「Review」这条路。双轴审查纪律（固定基点、定位 spec/standards、Fowler 味道基线、并行 sub-agent、汇总不重排）只存在 `code-review`（canonical `vocabulary/code-review`），本文件只写风险路由与裁决。

## 风险路由（本文件专属）

- **单 reviewer**：机械性、纯文档或极小且低风险的 diff。跑一个 reviewer 分别检查适用的 Standards 与 Spec，并说明未启用的独立轴。
- **双轴并行**：行为变化、高风险改动，或 spec 复杂且存在明显取舍，且宿主提供独立只读上下文时，独立运行 Standards 与 Spec reviewer。
- **双轴串行**：宿主缺少独立只读上下文，或 diff 很大、上下文可能超限时使用；先 Standards 再 Spec，并在报告中说明原因。

高风险信号包括数据迁移、权限/安全、公共 API、并发、持久化、跨模块行为和性能/可靠性门禁。审查深度不由行数单独决定。单/双 reviewer 的输入契约（committed + staged + unstaged + 未跟踪文件逐项排除）见 `references/review-rules.md`。

## 流程

1. 固定并记录审查基点、需求来源、规范来源和 diff 范围（基点先探测 `git symbolic-ref refs/remotes/origin/HEAD`，不写死 `main`）。
2. 按上方风险路由选单 reviewer 或双轴（并行/串行），然后 Call the Skill tool with "code-review" 执行双轴审查。
3. 输出正式裁决：**PASS**、**PASS WITH WARNINGS** 或 **FAIL**。
4. 给出可追踪意见清单：ID、严重级别、定位与修复建议。
5. FAIL 回传修复；PASS 或 PASS WITH WARNINGS 才能作为进入 `/5-git` 的交接产物。

## 架构评估模式

当用户明确要求架构评估、代码腐烂评估或模块臃肿评估时（由 `/0-router` 送到这一步）：

1. 只读调查模块职责、依赖方向、边界和测试 seam。跨多个相对独立模块、调度收益明确且宿主提供独立只读上下文时，可基于同一快照按模块并行调查；否则串行。主流程统一校准跨模块依赖和边界结论。
2. 输出 `docs/analysis/<topic>.md` 与 `docs/plans/<topic>/` 改造任务。
3. 输出文档路径后停止，由用户决定是否进入 `/1-plan`。

## 边界

- 根因定位与修复由 `/4-debug` 承接。
- 版本提交与推送由 `/5-git` 承接，且仍需用户授权。

## 完成标准

- 已固定审查基点并完成 Standards/Spec 双轴审查。
- Review 产出正式裁决和可追踪意见；架构评估产出分析文档路径。

## 详细规则参考

- `code-review`（canonical `vocabulary/code-review`）：双轴审查核心 + Fowler 味道基线 + 并行 sub-agent
- `references/review-rules.md`：风险路由与审查准备（输入契约、双轴边界）
- `references/standards-reviewer.md`：Standards 轴 reviewer 输入输出
- `references/spec-reviewer.md`：Spec 轴 reviewer 输入输出
