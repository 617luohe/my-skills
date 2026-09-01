---
name: 1-plan
description: 规划中大型功能：按方案确定程度分流到追问/领域建模/接口设计/PRD/任务拆解，产出可交接的规划产物。
---

# 1-plan — 规划编排壳

写代码前按阶段推进。需要用户决策或授权的阶段必须等待；综合整理阶段直接执行。本文件只做**编排与串联**，每一步的具体纪律都在对应的 vocabulary 技能或 references 里，不在此重复。

## 三种深度（先判，再走）

1. **念头未定** — Call the Skill tool with "grill-me" 追问到能拍板。
2. **已想清、只差成文** — Call the Skill tool with "to-spec" 产出 `docs/plans/<feature>/PRD.md`，再 Call the Skill tool with "to-tickets" 拆任务。
3. **纵深规划** — 需要领域建模/接口设计时走下方五阶段流程。

## 核心原则

1. 事实自行查证，目标、偏好、范围、风险和取舍交用户决定；每个决策先给推荐答案和理由。
2. 追问阶段必须由用户显式确认退出；理解确认与开发授权是两件事。
3. 成文与拆解阶段只基于已达成的共识整理，直接产出。

## 五阶段流程（纵深规划）

进入前扫描 `CONTEXT-MAP.md`、`CONTEXT.md`、`docs/adr/`；术语冲突立即指出，已读内容在全程复用。

### 阶段 1 — 方案追问

Call the Skill tool with "grill-me" 建立决策依赖图并推进 frontier。退出前必须确认：

- 所有需求假设已显式化；技术和产品决策完成，frontier 为空且依赖已理清。
- 输出共享理解摘要：目标、已验证事实、关键决策、范围外事项、残余风险。
- 用户确认摘要正确并同意进入阶段 2。

用户指出遗漏时重新加入决策树，回到对应阶段。

### 阶段 2 — 领域术语与 ADR

Call the Skill tool with "domain-modeling" 挑战术语、锐化模糊词、就地更新 `CONTEXT.md`，并按其三项门禁提议 ADR。格式见该技能的 `CONTEXT-FORMAT.md` 与 `ADR-FORMAT.md`（核心层唯一格式源）。

### 阶段 3 — 接口设计与原型验证

只有存在真实备选方案和用户需要比较的取舍时，才生成多个方案；否则直接记录推荐方案及理由。方案比较覆盖模块划分、接口、关键交互和测试切面；接口词汇（module/interfaces/depth/seam）采用 `codebase-design` 的 deep-module 语言。

状态机、算法或 UI 假设无法由代码、文档或用户决策消除时，Call the Skill tool with "prototype" 建立 throwaway prototype（LOGIC/UI 分支与规则见该技能）。结论完成后，把 verdict 与证据摘要写入 `docs/plans/<topic>/`，必要的决策片段内联到 PRD；原型提交到 `prototype/<topic>` 分支留证，主分支只留决策。

### 阶段 4 — 输出 PRD

Call the Skill tool with "to-spec" 综合阶段 1-3 的共识，产出 `docs/plans/<feature>/PRD.md`（Problem Statement、Solution、User Stories、Implementation Decisions、Testing Decisions、Out of Scope、Further Notes）。

### 阶段 5 — 拆解任务

Call the Skill tool with "to-tickets" 把 PRD 拆成 tracer-bullet 垂直切片，写 `docs/plans/<feature>/tasks.md`（每项含 Task ID、Title、Description、Acceptance Criteria、AFK/HITL、Depends On、Write Set；阻塞边、核对话与写作约定见该技能）。

## 最终确认

阶段 5 完成后输出 PRD、任务清单、CONTEXT.md 更新情况和 ADR 情况，然后询问：**是否授权进入原型或开发？** 用户确认后 Call the Skill tool with "2-implement"；指出问题则回到对应阶段。

## 边界

- 本阶段不 `git commit`，不自动进 `/5-git`。
- 规划产物只落 `docs/plans/<feature>/`，术语与 ADR 各自归位 `CONTEXT.md` / `docs/adr/`。

## 完成标准

- 需求假设、关键决策和范围外事项已显式化。
- `CONTEXT.md`、PRD、任务清单和 ADR 情况已落盘或明确说明无需产出。
- 已取得用户对规划结果的确认；未把确认误当成开发授权。

## 详细规则参考

- `grill-me`（canonical `vocabulary/grill-me`）：追问入口，调 grilling
- `grilling`（canonical `vocabulary/grilling`）：询问循环
- `domain-modeling`（canonical `vocabulary/domain-modeling`）：领域建模与 ADR 门禁
- `prototype`（canonical `vocabulary/prototype`）：throwaway prototype
- `to-spec`（canonical `vocabulary/to-spec`）：对话转 PRD
- `to-tickets`（canonical `vocabulary/to-tickets`）：PRD 拆任务
- `references/planning-rules.md`：frontier 与文档权威边界
