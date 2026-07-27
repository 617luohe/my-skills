---
name: 3-检查
description: Route review, issue-only reporting, or root-cause repair from the supplied input contract. Review code against standards and specification; turn observed problems into actionable tracker reports.
disable-model-invocation: false
---

# 3-检查 — 正式验收与问题建单

**职责**：根据输入契约选择 Review、Bug 报告或 `/4-调试`，不把已足够的信息再变成模式选择题。

## 输入契约路由

按以下优先级路由：

1. **根因修复**：用户要求“找根因”“排查原因”“立即修复”或同等意图时，直接进入 **`/4-调试`**；传递已有现象、复现步骤、issue 编号和相关模块。不要先建单，也不要做 Review。
2. **Review**：来自 `/2-开发` 或 `multi-worker`，且带有 **fixed point/base（审查基点）**、**spec/需求来源** 和 **diff 审查意图**时，强制进入 Review，**不再询问模式**。用户独立请求审查、验收、检查 diff，且已提供或可明确定位这些审查输入时，也进入 Review。
3. **Bug 报告**：用户明确要求“记录”“建 issue”或“只建单”，并提供问题现象时，进入 Bug 报告；只记录和追踪，不启动根因分析或修复。
4. **确实模糊**：仅在输入确实模糊时，即以上输入契约都不成立，问**一个澄清问题**：`你要审查改动、只记录为 Bug，还是查根因并立即修复？`

## Review — 正式验收

使用 `/vocabulary/code-review` 执行 Standards 和 Spec 双轴审查。

### 交接输入

- `/2-开发` 的未提交改动、自检结果、审查基点和需求来源。
- `multi-worker` 集成分支的 fixed point/base、`tasks.md` 或其他 spec/需求来源，以及集成 diff 审查意图。
- 独立 Review 的 fixed point/base、spec/需求来源和 diff；若其中一项不能明确定位，才使用上面的一个澄清问题。

### 流程

1. 固定并记录审查基点、需求来源、规范来源和 diff 范围。
2. 按 `/vocabulary/code-review` 的规则运行 Standards 与 Spec 审查。
3. 输出完整审查报告和唯一正式验收裁决：**PASS**、**PASS WITH WARNINGS** 或 **FAIL**。
4. 该裁决及报告是可选进入 `/5-版本管理` 的**正式交接产物**。审查通过（PASS 或 PASS WITH WARNINGS）也保持改动未提交；只有用户明确授权才可进入 `/5-版本管理`。FAIL 不得作为版本管理交接。

## Bug 报告 — 只建单

用户提供现象并明确只记录/建 issue 时：

1. 探测项目已有 issue tracker。
2. 采集触发操作、预期、实际结果、复现性和日志；信息不足时只问一个最关键的现象问题。
3. 探索相关代码和测试，查重后生成问题报告；不编造根因。
4. 使用项目既有 tracker 建单。Bug issue 使用领域术语，不写文件路径或行号。
5. 输出 issue 链接/编号和已记录现象。除非用户随后要求找根因或立即修复，不转 `/4-调试`。

## 边界

- `/2-开发`：开发、自检并提供 Review 输入契约。
- `/3-检查`：正式 Review 或只建单，不在 Bug 报告中猜测根因。
- `/4-调试`：根因定位与修复，必须从反馈回路开始并补回归测试。
- `/5-版本管理`：仅接收通过 Review 的正式交接产物，且仍须用户明确授权。
