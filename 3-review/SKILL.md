---
name: 3-review
description: 对固定基点以来的改动做双轴正式审查：Standards 与 Spec，产出可追踪裁决。
disable-model-invocation: false
---

# 3-review — 正式验收

对 `HEAD` 与用户给定的 fixed point（commit、branch、tag 或 merge-base）之间的 diff 做双轴审查。去哪里的判定（Review / 只建单 / 查根因 / 架构评估）由 `/0-router` 排一次；本技能只承接「Review」这条路。

## 流程

1. 固定并记录审查基点、需求来源、规范来源和 diff 范围（基点先探测 `git symbolic-ref refs/remotes/origin/HEAD`，不写死 `main`）。
2. 按 `references/review-rules.md` 运行 **Standards**（是否符合仓库编码规范）与 **Spec**（是否忠实实现来源 issue/spec）双轴审查。
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
- 只建单由 `/issue-reporting` 承接。

## 完成标准

- 已固定审查基点并完成 Standards/Spec 双轴审查。
- Review 产出正式裁决和可追踪意见；架构评估产出分析文档路径。
