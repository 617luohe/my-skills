---
name: 1-规划
description: Plan non-trivial features through requirements, domain terms, interfaces, PRD, and task breakdown.
disable-model-invocation: true
---

# 1-规划 — 方案设计与任务拆解

写代码前的完整规划流程。按阶段推进，不跳跃。

## 核心原则

1. **按顺序走阶段，不跳跃。** 需要用户决策或授权的阶段必须等待；明确规定不追问的综合整理阶段直接执行。
2. **事实自行查证，决策交给用户。** 代码、配置、文档和工具中有唯一答案的是事实；目标、偏好、范围、风险和取舍是决策。
3. **每个决策先给推荐答案和理由，再让用户选择。** 不做开放题。
4. **阶段 1 必须由用户显式确认退出。** frontier 为空后先输出共享理解摘要；用户确认前不得进入阶段 2 或生成规划产物。
5. **理解确认不等于开发授权。** 进入原型或开发前，用户还需确认 PRD 和任务清单可执行。
6. **阶段 4-5 不追问用户。** 只基于阶段 1-3 已达成的共识综合整理。

## 五阶段流程

### 阶段 1 — 方案追问

使用 `/vocabulary/grilling` 技能进行决策树 grilling：

**文档发现（进入追问前）**
- 扫描 `CONTEXT-MAP.md`、`CONTEXT.md`、`docs/adr/` 了解已有领域文档
- 如果用户输入术语与现有文档冲突 → 立即指出
- 缓存读取的文档内容，整个规划过程复用，不重复读取

**决策树 grilling（默认批量，可切逐步）**
- 把未决事项建模为依赖图：节点是决策，边是依赖，**frontier** 是当前可回答的决策集合
- **事实（Fact）** — 代码、配置、文档中有答案，自行调查
- **决策（Decision）** — 涉及目标、偏好、范围、风险、取舍，必须由用户决定，先给推荐答案和理由
- **默认批量模式** — 每轮集中询问 frontier 中主题相近且互不依赖的决策
- **逐步模式** — 用户说"一步一步"/"逐步完善"/"一个一个问"时，一次只问一个决策
- **场景压力测试** — 用具体场景探测领域边界
- **代码交叉验证** — 用实际代码核实用户描述的系统现状

**阶段 1 退出门禁**
1. [ ] 所有需求假设已显式化并确认
2. [ ] 所有技术和产品决策已完成，frontier 为空
3. [ ] 决策依赖关系已理清
4. [ ] 输出共享理解摘要：目标、已验证事实、关键决策、范围外事项、残余风险
5. [ ] 用户显式确认摘要正确，并同意进入阶段 2

若用户指出遗漏，重新加入决策树，不进入后续阶段。

---

### 阶段 2 — 领域术语

使用 `/vocabulary/domain-modeling` 技能维护 `CONTEXT.md`：

**实时规则（贯穿整个阶段）**
- **术语冲突标记** — 如果用词与已有 CONTEXT.md 冲突，立即指出
- **模糊语言锐化** — 当使用模糊或过载词汇时，提议精确的规范术语
- **场景压力测试** — 用具体场景探测边界
- **内联更新** — 每当一个术语被确认，立即更新 CONTEXT.md

**输出**：`CONTEXT.md` — 项目唯一领域 glossary，只包含规范术语、关系、少量领域场景及已标记歧义；ADR、技术栈/模块地图、任务状态和历史归档不写入其中。

> 如果项目已有 CONTEXT.md，在其基础上更新。如果项目没有 CONTEXT.md，这里按需创建。

---

### 阶段 2.5 — 决策记录（ADR，可选）

在术语体系建立后、接口设计前，回顾整个规划阶段已做出的关键决策。

**仅当以下三个条件全部满足时才提议创建 ADR**：
1. **难逆转** — 事后改主意的成本很高
2. **少见** — 未来的读者看到代码会想"为什么这样做？"
3. **真实取舍** — 有真实的备选方案和取舍理由

使用 `/vocabulary/domain-modeling` 技能拥有的 [ADR 模板](../vocabulary/domain-modeling/references/adr-format.md)，创建在 `docs/adr/NNNN-title.md`。

---

### 阶段 3 — 接口设计与原型验证

并行生成 3 个接口方案对比：
1. **方案 A** — 面向简单场景优化
2. **方案 B** — 面向扩展性优化
3. **方案 C** — 面向测试性优化

每个方案包含：模块划分、接口定义、关键交互、测试切面。

用户选择最优方案，或指出各方案的可取之处后由 AI 合成最终方案。

**不确定假设门禁**：状态机、算法或 UI 假设无法通过代码、文档或用户决策消除时，在 `docs/prototypes/<topic>/` 建立 throwaway prototype 验证任务。任务须定义待验证假设、最小实验、成功/失败判据和停止条件；原型默认不进入生产代码或任务清单。把结论、证据和后续决定回写 `docs/plans/<topic>/`，再继续 PRD 与任务拆解。

---

### 阶段 4 — 输出 PRD

基于阶段 1-3 已达成的共识综合整理，**不追问用户**。

**输出路径**：`docs/plans/<feature>/PRD.md`

**PRD 结构**：
```markdown
## Problem Statement
{用户视角的问题}

## Solution
{用户视角的解决方案}

## User Stories
1. As a <actor>, I want a <feature>, so that <benefit>
{详尽的用户故事列表}

## Implementation Decisions
- 要修改的模块
- 要修改的接口
- 技术澄清
- 架构决策
- Schema 变更
- API 契约

不包含具体文件路径或代码片段（易过期）。
例外：如果原型产出了决策片段（状态机、reducer、schema），内联到相关决策中。

## Testing Decisions
- 什么是好测试（只测外部行为，不测实现细节）
- 要测试哪些模块
- 现有类似测试作为参考

## Out of Scope
{范围外事项}

## Further Notes
{补充说明}
```

---

### 阶段 5 — 拆解任务

将 PRD 拆解为可独立执行的垂直切片（task list）。

**输出路径**：`docs/plans/<feature>/tasks.md`

每个任务包含：
- **Task ID** — T001, T002, ...
- **Title** — 简短标题
- **Description** — 要实现的功能切片
- **Acceptance Criteria** — 验收标准
- **AFK/HITL** — 标记是否需要人工介入
- **Depends On** — 前置任务 ID（如果有）

**输出格式**：
```markdown
## Task List

### T001: {Title}
**Description:** {切片描述}
**Acceptance Criteria:**
- [ ] {标准1}
- [ ] {标准2}
**AFK/HITL:** AFK
**Depends On:** None

### T002: {Title}
...
```

---

## 最终确认

阶段 5 完成后，输出：
1. PRD 文档路径
2. 任务清单路径
3. CONTEXT.md 更新情况
4. ADR 创建情况（如果有）

然后询问用户：**是否授权进入原型或开发？**

- 用户确认 → 可以进入 `/2-开发`
- 用户指出问题 → 回到对应阶段修正

---

## 详细规则参考

完整的决策树算法、frontier 计算规则、CONTEXT.md 格式详见：
- `vocabulary/grilling/SKILL.md` — 询问循环的核心逻辑
- `vocabulary/domain-modeling/SKILL.md` — 领域建模的详细规则
- `references/planning-rules.md` — frontier 算法和文档权威边界
- `references/context-format.md` — CONTEXT.md glossary 格式规范
- `../vocabulary/domain-modeling/references/adr-format.md` — ADR 编写指南
