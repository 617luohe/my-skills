---
name: 3-review
description: 按输入契约在正式审查、只建单和根因修复之间分流，并产出可追踪结果。
disable-model-invocation: false
---

# 3-review — 正式验收与问题建单

根据输入契约，在 Review、Bug 报告和 `/4-debug` 之间做唯一分流。

## 输入契约路由

按优先级判断：

1. **架构评估**：用户明确要求架构评估、代码腐烂评估或模块臃肿评估。
2. **根因修复**：用户要求找根因、排查原因或立即修复 → 直接转 `/4-debug`。
3. **Review**：已给出 fixed point/base、spec/需求来源和 diff 审查意图。
4. **Bug 报告**：用户明确要求只记录、建 issue 或只建单。
5. **确实模糊**：只问一个问题，确认是审查、建单还是查根因。

## Review

使用 `references/review-rules.md` 执行 Standards 和 Spec 双轴审查。

1. 固定并记录审查基点、需求来源、规范来源和 diff 范围。
2. 按 `references/review-rules.md` 的规则运行 Standards 与 Spec 审查。
3. 输出正式裁决：**PASS**、**PASS WITH WARNINGS** 或 **FAIL**。
4. 给出可追踪意见清单：ID、严重级别、定位与修复建议。
5. FAIL 回传修复；PASS 或 PASS WITH WARNINGS 才能作为进入 `/5-git` 的交接产物。

## Bug 报告

1. 先探测唯一 tracker：GitHub、GitLab、Jira 或无远程 tracker。
2. 采集现象、预期、实际结果、复现性和必要日志；不编造根因。
3. 在同一 tracker 内只读查重；若已存在同类 issue，输出链接后停止。
4. 查重未命中时，先展示标题、完整正文和目标 tracker。
5. 只有用户明确确认后才创建 issue；失败时如实停止，不跨平台回退。
6. 没有可靠远程 tracker 时，写 `docs/issues/<slug>.md` 本地草稿并标明未提交。

## 架构评估

1. 只读调查模块职责、依赖方向、边界和测试 seam。
2. 输出 `docs/analysis/<topic>.md` 与 `docs/plans/<topic>/` 改造任务。
3. 输出文档路径后停止，由用户决定是否进入 `/1-plan`。

## 边界

- `/3-review` 只做正式审查、只建单或架构评估。
- 根因定位与修复交给 `/4-debug`。
- 版本提交与推送交给 `/5-git`，且仍需用户授权。

## 完成标准

- 已依据输入契约完成唯一分流。
- Review 产出正式裁决和可追踪意见。
- Bug 报告未编造根因，且创建前已取得用户确认。
