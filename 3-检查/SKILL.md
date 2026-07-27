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

**支持范围**：完整支持已探测到的 GitHub（`gh`）和 GitLab（`glab`）。Jira 仅在仓库没有可靠的 Jira CLI 或配置时降级为本地草稿；不得假装已自动创建。没有远程 tracker 时同样只生成本地草稿。一次报告只能使用探测到的**同一 tracker**完成“探测 → 查重 → 创建 → URL/编号”，绝不跨 tracker 回退。

### 共同准备与只读查重

用户提供现象并明确只记录/建 issue 时：

1. 探测仓库 remote、项目配置和可用 CLI，明确目标为 GitHub、GitLab、Jira 或无远程 tracker；探测不确定时停止并说明无法确定目标，不猜测平台。
2. 采集触发操作、预期、实际结果、复现性和日志；信息不足时只问一个最关键的现象问题。探索相关代码和测试，生成不编造根因的报告。Bug 标题和正文使用领域术语，不写文件路径或行号。
3. 对已确定目标执行该平台的**只读**查重；查重可在用户确认前执行。查重发现已有 issue 时，输出同一 tracker 的 URL/编号并停止，不再创建。
4. 查重未命中后，先显示将要提交的**标题、完整正文和目标 tracker**，明确这是 outward-facing 创建操作；只有取得用户明确确认后才能创建。未确认则停止，不创建。

### GitHub

仅当探测结果为 GitHub 时使用 `gh`：先确认 `gh` 存在且认证可用，再用 `gh issue list`（或等效只读查询）在该 GitHub 仓库查重。获得用户确认后才用 `gh issue create` 创建，并输出该 GitHub issue 的 URL/编号。

- `gh` 缺失、认证失败或查重失败：停止，不执行创建，不改用 `glab` 或其他 tracker；报告具体失败出口。
- 创建失败：停止并报告失败；不得声称已创建，不改用其他 tracker。

### GitLab

仅当探测结果为 GitLab 时使用 `glab`：先确认 `glab` 存在且认证可用，再用 `glab issue list`（或等效只读查询）在该 GitLab 项目查重。获得用户确认后才用 `glab issue create` 创建，并输出该 GitLab issue 的 URL/编号。

- `glab` 缺失、认证失败或查重失败：停止，不执行创建，不改用 `gh` 或其他 tracker；报告具体失败出口。
- 创建失败：停止并报告失败；不得声称已创建，不改用其他 tracker。

### Jira

若探测到 Jira，但仓库没有可靠的 Jira CLI 或明确可用的 Jira 配置，**不执行 `gh`、`glab` 或任何别的平台 CLI**。将标题和完整正文写入 `docs/issues/<slug>.md` 本地草稿，标明目标为 Jira、状态为“未提交”，并明确告知用户未创建远程 issue、不得声称已自动创建。该草稿是普通文档，必须位于 `docs/issues/` 下。

若存在可靠且已验证的 Jira CLI/配置，仍须先在同一 Jira tracker 只读查重，并在展示标题、正文和目标 Jira tracker、获得用户明确确认后才创建；CLI 缺失、认证失败、查重失败或创建失败均停止，不跨平台回退。

### 无远程 tracker

未探测到远程 tracker 时，将标题和完整正文写入 `docs/issues/<slug>.md` 本地草稿，标明“无远程 tracker；未提交”。普通文档必须位于 `docs/` 下；不得写到仓库根目录或 `docs/` 之外。输出草稿路径和已记录现象，不声称远程 issue 已创建。

除非用户随后要求找根因或立即修复，不转 `/4-调试`。

## 边界

- `/2-开发`：开发、自检并提供 Review 输入契约。
- `/3-检查`：正式 Review 或只建单，不在 Bug 报告中猜测根因。
- `/4-调试`：根因定位与修复，必须从反馈回路开始并补回归测试。
- `/5-版本管理`：仅接收通过 Review 的正式交接产物，且仍须用户明确授权。
