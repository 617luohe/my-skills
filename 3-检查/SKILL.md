---
name: 3-检查
description: Review code on standards and specification compliance, or turn discovered bugs into actionable reports and GitHub issues. Use before merging, after feature completion, for acceptance checks, or when the user asks for review, inspection, quality validation, or bug reporting.
disable-model-invocation: false
---

# 3-检查 — 正式验收与质量门禁

**职责**：对 `/2-开发` 完成的代码进行正式验收，确保符合规范和需求。

两个模式：**代码审查**（Review）和 **Bug 报告**（QA）。进入时问用户走哪个。

---

## 模式 A — 代码审查

使用 `/vocabulary/code-review` 技能进行双轴审查，并输出验收裁决。

### 快速调用

```
luohe，帮我审查一下当前分支
```

会自动：
1. 接收 `/2-开发` 传递的审查基点和需求来源；缺失时再确定审查基点（通常是 main）并定位需求来源
2. 定位规范来源（CLAUDE.md、CONTRIBUTING.md、CONTEXT.md、ADR）
3. 并行运行 Standards 和 Spec 子代理
4. 输出汇总报告
5. **输出验收裁决（PASS/FAIL）** — 基于阻断级别问题判定是否可合并
6. 审查通过后保持改动未提交；只有用户明确授权，才进入 `/5-版本管理`

### 验收裁决

审查完成后会根据问题严重程度输出裁决结果：

- **🚫 FAIL** — 存在阻断级别问题（缺失核心功能、严重违反规范），必须修复后才能合并
- **⚠️ PASS WITH WARNINGS** — 无阻断问题，但有警告（建议修复）
- **✅ PASS** — 可以合并

裁决会列出所有阻断和警告问题清单，明确告知功能门禁状态。

### 详细说明

完整流程见 `/vocabulary/code-review/SKILL.md`：
- 审查准备（确定基点、定位需求和规范来源、识别功能目标门禁）
- 并行审查（Standards 子代理 + Spec 子代理）
- 汇总报告（两轴并排展示，不合并）
- 验收裁决（阻断级别定义、裁决规则、功能门禁验证）

---

## 模式 B — Bug 报告

你口述问题现象，AI 探索代码并提交 issue。

### 流程

1. **探测追踪器** — 自动识别项目使用的 issue tracker：
   - 检查 `.github/` 目录 → GitHub Issues
   - 检查 `.gitlab/` 目录 → GitLab Issues
   - 检查 `jira.config` 或 commit 消息中的 JIRA-xxx → Jira
   - 优先使用项目已有的追踪器，避免切换工具

2. **现象采集** — 你描述观察到的问题：
   - 什么操作触发？
   - 预期行为是什么？
   - 实际发生了什么？
   - 能稳定复现吗？
   - 有错误日志吗？

3. **代码探索** — AI 根据现象：
   - 定位可能相关的代码模块
   - 读取相关代码和测试
   - 尝试理解根因（不一定能找到）

4. **查重** — 提交前检查是否已有类似问题：
   ```bash
   gh issue list --state all --search "{关键词}" --limit 20
   ```
   - 如果找到相似 issue → 询问是否需要补充信息到已有 issue
   - 如果未找到 → 继续提交新 issue

5. **生成 issue** — 使用项目领域术语（CONTEXT.md）描述问题：
   ```markdown
   # Bug: {使用领域术语的标题}
   
   ## 现象
   {用户视角的问题描述}
   
   ## 复现步骤
   1. {步骤1}
   2. {步骤2}
   3. {观察到的结果}
   
   ## 预期行为
   {应该发生什么}
   
   ## 相关模块
   {领域层面的模块名，不是文件路径}
   
   ## 可能的根因（如果找到）
   {简短描述，不包含代码片段}
   ```

6. **提交** — 使用对应工具提交 issue：
   ```bash
   # GitHub
   gh issue create --title "..." --body "..."
   
   # GitLab
   glab issue create --title "..." --description "..."
   ```

7. **后续调试（可选）** — 如果需要立即修复：
   - 询问用户是否现在启动调试流程
   - 如果是 → 调用 `4-调试` 技能，传递：
     - Issue 编号（作为追踪标识）
     - 现象描述和复现步骤
     - 已探索的相关模块
   - `4-调试` 会从"构建反馈回路"开始，用测试固化复现步骤

### MUST 规则

- **提交前必须查重。** 使用 issue tracker 的搜索功能检查重复问题。
- **追踪器探测优先。** 自动识别项目已有工具，不主动切换 tracker。
- **Bug issue 不包含文件路径和行号。** 使用项目领域术语，不描述代码。
- **现象描述从用户视角出发。** 不假设读者知道代码结构。
- **不编造根因。** 如果没找到，就标记为"待调查"。
- **建单后询问是否立即调试。** 如果用户需要立即修复，传递上下文给 `4-调试` 技能。

---

## 何时使用

- **代码审查** — `/2-开发` 完成后的正式验收、合并前检查、功能交付前的质量门禁
- **Bug 报告** — 发现问题时，需要记录并追踪

## 与 `/2-开发` 的分工

- **`/2-开发`** — 轻量自检（测试、类型检查、linter、快速扫描）
- **`/3-检查`** — 正式验收（双轴审查：Standards + Spec，深度质量检查）

**交接点**：`/2-开发` 自检通过后，携带审查基点和需求来源调用 `/3-检查` 进行正式验收。审查通过不自动提交；仅在用户明确授权后才进入 `/5-版本管理`。

## 与其他技能的关系

- **输入** — 
  - `/2-开发` 交付的未提交代码、自检结果、审查基点和需求来源
  - git diff（手动代码审查）
  - 问题现象（Bug 报告）
- **调用** — `/vocabulary/code-review`（代码审查模式）
- **输出** — 审查报告（代码审查）或 GitHub/GitLab issue（Bug 报告）
- **审查通过后** — 仅在用户明确授权时 → `/5-版本管理`
- **后续** — Bug 报告后可衔接 `4-调试` 技能进行立即修复
