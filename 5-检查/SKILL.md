---
name: 5-检查
description: Review code on standards and specification compliance, or turn discovered bugs into actionable reports and GitHub issues. Use before merging, after feature completion, for acceptance checks, or when the user asks for review, inspection, quality validation, or bug reporting.
disable-model-invocation: false
---

# 5-检查 — 代码审查与验收

两个模式：**代码审查**（Review）和 **Bug 报告**（QA）。进入时问用户走哪个。

---

## 模式 A — 代码审查

使用 `/vocabulary/code-review` 技能进行双轴审查。

### 快速调用

```
luohe，帮我审查一下当前分支
```

会自动：
1. 确定审查基点（通常是 main）
2. 定位需求来源（commit 消息中的 issue 引用、PRD 文件）
3. 定位规范来源（CLAUDE.md、CONTRIBUTING.md、CONTEXT.md、ADR）
4. 并行运行 Standards 和 Spec 子代理
5. 输出汇总报告

### 详细说明

完整流程见 `/vocabulary/code-review/SKILL.md`：
- 审查准备（确定基点、定位需求和规范来源）
- 并行审查（Standards 子代理 + Spec 子代理）
- 汇总报告（两轴并排展示，不合并）

---

## 模式 B — Bug 报告

你口述问题现象，AI 探索代码并提交 GitHub issue。

### 流程

1. **现象采集** — 你描述观察到的问题：
   - 什么操作触发？
   - 预期行为是什么？
   - 实际发生了什么？
   - 能稳定复现吗？
   - 有错误日志吗？

2. **代码探索** — AI 根据现象：
   - 定位可能相关的代码模块
   - 读取相关代码和测试
   - 尝试理解根因（不一定能找到）

3. **生成 issue** — 使用项目领域术语（CONTEXT.md）描述问题：
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

4. **提交** — 使用 `gh` CLI 提交到 GitHub：
   ```bash
   gh issue create --title "..." --body "..."
   ```

### MUST 规则

- **Bug issue 不包含文件路径和行号。** 使用项目领域术语，不描述代码。
- **现象描述从用户视角出发。** 不假设读者知道代码结构。
- **不编造根因。** 如果没找到，就标记为"待调查"。

---

## 何时使用

- **代码审查** — 合并前、功能完成后、验收检查
- **Bug 报告** — 发现问题时，需要记录并追踪

## 与其他技能的关系

- **输入** — git diff（代码审查）或问题现象（Bug 报告）
- **调用** — `/vocabulary/code-review`（代码审查模式）
- **输出** — 审查报告（代码审查）或 GitHub issue（Bug 报告）
