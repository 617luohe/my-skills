---
name: 1-plan
description: 规划中大型功能：需求澄清、领域术语、接口设计、PRD 和任务拆解。
disable-model-invocation: false
---

# 1-plan — 方案设计与任务拆解

写代码前按阶段推进，不跳跃。需要用户决策或授权的阶段必须等待；综合整理阶段直接执行。

## 核心原则

1. 事实自行查证，目标、偏好、范围、风险和取舍交用户决定；每个决策先给推荐答案和理由。
2. 阶段 1 必须由用户显式确认退出；理解确认不等于开发授权。
3. 阶段 4-5 只基于已达成的共识整理，不追问。

## 五阶段流程

### 阶段 1 — 方案追问

使用 `/grilling` 建立决策依赖图并推进 frontier。进入追问前扫描 `CONTEXT-MAP.md`、`CONTEXT.md`、`docs/adr/`；术语冲突立即指出，已读内容在全程复用。默认批量询问互不依赖的决策；用户要求逐步时一次只问一个。用场景压力测试边界，用代码交叉验证现状。算法细节见 [references/planning-rules.md](references/planning-rules.md)。

退出前必须确认：

- 所有需求假设已显式化；技术和产品决策完成，frontier 为空且依赖已理清。
- 输出共享理解摘要：目标、已验证事实、关键决策、范围外事项、残余风险。
- 用户确认摘要正确并同意进入阶段 2。

用户指出遗漏时重新加入决策树，不进入后续阶段。

### 阶段 2 — 领域术语

使用 `references/domain-modeling.md` 维护 `CONTEXT.md`。标记术语冲突，锐化模糊或过载词，按确认结果实时更新。该文件只保存规范术语、关系、少量场景和已标记歧义；不写 ADR、技术栈、模块地图、任务状态或历史归档。

### 阶段 2.5 — 决策记录（ADR，可选）

仅当决策同时满足难逆转、少见、存在真实取舍时提议 ADR。使用 `references/domain-modeling.md` 的 ADR 模板，写入 `docs/adr/NNNN-title.md`。

### 阶段 3 — 接口设计与原型验证

只有存在真实备选方案和用户需要比较的取舍时，才生成多个方案；否则直接记录推荐方案及理由。方案比较需覆盖模块划分、接口、关键交互和测试切面。

状态机、算法或 UI 假设无法由代码、文档或用户决策消除时，在 `docs/prototypes/<topic>/` 建立 throwaway prototype，定义待验证假设、最小实验、成功/失败判据和停止条件。逻辑/状态机用可直接运行的单文件；UI 用单路由差异化变体；不抛光、不加无关测试、错误处理或持久化。结论完成后，把 verdict 与证据摘要写入 `docs/plans/<topic>/`，必要的状态机、reducer 或 schema 片段内联到 PRD；原型提交到 `prototype/<topic>`，主分支只留决策。

### 阶段 4 — 输出 PRD

基于阶段 1-3 的共识写 `docs/plans/<feature>/PRD.md`，包含 Problem Statement、Solution、User Stories、Implementation Decisions、Testing Decisions、Out of Scope、Further Notes。Implementation Decisions 写模块、接口、技术澄清、架构、Schema 和 API 契约；不写易过期的具体路径或代码，原型决策片段除外。

### 阶段 5 — 拆解任务

将 PRD 拆成可独立执行的垂直切片，写 `docs/plans/<feature>/tasks.md`。每项包含 Task ID、Title、Description、Acceptance Criteria、AFK/HITL 和 Depends On。

## 最终确认

阶段 5 完成后输出 PRD、任务清单、CONTEXT.md 更新情况和 ADR 情况，然后询问：**是否授权进入原型或开发？** 用户确认后才进入 `/2-implement`；指出问题则回到对应阶段。

## 完成标准

- 需求假设、关键决策和范围外事项已显式化。
- `CONTEXT.md`、PRD、任务清单和 ADR 情况已落盘或明确说明无需产出。
- 已取得用户对规划结果的确认；未把确认误当成开发授权。

## 详细规则参考

- `/grilling`（canonical `vocabulary/grilling`）：询问循环
- `references/domain-modeling.md`：领域建模
- `references/planning-rules.md`：frontier、方案分支和文档权威边界
- `references/context-format.md`：CONTEXT.md 格式
- `references/adr-format.md`：ADR 格式（领域建模阶段使用）
