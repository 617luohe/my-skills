---
name: code-review
layer: vocabulary
description: 审查自一个固定点（commit、branch、tag 或 merge-base）以来的改动，沿两个轴：Standards（代码遵循本仓库记录的编码标准吗？）与 Spec（代码匹配来源 issue/spec 的要求吗？）。在并行 sub-agent 里跑两个审查并并列报告。用户想 review 分支、PR、进行中改动、或要求 "review since X" 时用。
---

对 `HEAD` 与用户给的固定点之间的 diff 做双轴审查：

- **Standards**：代码符合本仓库记录的编码标准吗？
- **Spec**：代码忠实实现了来源 issue / spec 吗？

两轴各在**并行 sub-agent** 里跑，互不污染彼此的上下文，再由本技能汇总它们的发现。

issue tracker 应该已经提供给你。若 `docs/agents/issue-tracker.md` 缺失，让用户先跑 tracker 配置（本体系适配：spec 来源即 `docs/plans/` 下的 PRD/tasks）。

## 流程

### 1. 固定基点

用户所说的就是固定点（commit SHA、branch 名、tag、`main`、`HEAD~5` 等）。没说就问。

一次捕获 diff 命令：`git diff <fixed-point>...HEAD`（三点，对 merge-base 比较）。也记下 commit 列表：`git log <fixed-point>..HEAD --oneline`。

继续之前，确认固定点可解析（`git rev-parse <fixed-point>`）且 diff 非空。坏 ref 或空 diff 应在此失败，而非进两个并行 sub-agent 才失败。

### 2. 定位 spec 来源

按序找来源 spec：

1. commit message 里的 issue 引用（`#123`、`Closes #45`、GitLab `!67` 等），经 issue tracker 工作流取回。
2. 用户作为参数传的路径。
3. `docs/`、`specs/` 或 `.scratch/` 下匹配分支名或 feature 的 spec 文件。
4. 都没有就问用户 spec 在哪。他们说没有时，**Spec** sub-agent 跳过并在报告注明 "no spec available"。

### 3. 定位 standards 来源

仓库里记录"代码应怎么写"的任何东西，如 `CODING_STANDARDS.md` 或 `CONTRIBUTING.md`。

在仓库记录的之外，Standards 轴**始终**携带下面的**味道基线**：一组固定的 Fowler code smells（_Refactoring_ ch.3），即便仓库什么都没记录也适用。两条规则约束它：

- **仓库覆盖一切。** 已记录的仓库标准永远赢；它背书基线会 flag 的东西时，压制该 smell。
- **永远是判断。** 每个 smell 是带标签的启发（"possible Feature Envy"），不是硬违规。和这里的任何标准一样，跳过工具已强制的事项。

每个 smell 读作 *是什么* → *怎么修*；对着 diff 匹配：

- **Mysterious Name**：函数、变量或类型的名字不揭示它做什么或持有谁。→ 重命名；想不出诚实的名字，设计就含糊。
- **Duplicated Code**：同一逻辑形状出现在改动中的多个 hunk 或文件。→ 提取共享形状，两处调用。
- **Feature Envy**：方法伸手进另一对象的数据多过自己的。→ 把方法搬到它羡慕的数据上。
- **Data Clumps**：同一组字段或参数总是一起旅行（一个想出生的类型）。→ 捆成一个类型，传它。
- **Primitive Obsession**：原始类型或字符串顶替一个该有自己的类型的领域概念。→ 给概念它自己的小类型。
- **Repeated Switches**：同一类型上的同一 `switch`/`if` 级联在改动中反复。→ 换成多态，或两处共享一张 map。
- **Shotgun Surgery**：一个逻辑改动逼出多个文件的散改动。→ 把一起变的东西收进一个模块。
- **Divergent Change**：一个文件或模块因多个无关原因被改。→ 拆开，让每个模块只为一个原因变。
- **Speculative Generality**：为 spec 没有的需求加的抽象、参数或钩子。→ 删掉；内联回去直到真实需要出现。
- **Message Chains**：调用者不该依赖的长 `a.b().c().d()` 导航。→ 把行走藏在第一个对象的一个方法后面。
- **Middle Man**：一个类或函数大多只是转发。→ 砍掉，直接调真目标。
- **Refused Bequest**：子类或实现忽略或覆盖继承的大部分。→ 丢掉继承，用组合。

### 4. 并行派生两个 sub-agent

**Standards sub-agent prompt** 应包含：

- 完整 diff 命令与 commit 列表。
- 第 3 步找到的标准源文件清单，**加第 3 步的味道基线全文**（sub-agent 无其它途径拿到它）。
- 任务："按 file/hunk 报告 (a) diff 违反已记录标准的每一处——引用标准（文件 + 规则）；(b) 你发现的任何基线 smell——命名并引用 hunk。区分硬违规与判断项：已记录标准的违反可以是硬的，基线 smell 永远是判断项，且已记录的仓库标准覆盖基线。跳过工具已强制事项。400 词内。"

**Spec sub-agent prompt** 应包含：

- diff 命令与 commit 列表。
- spec 的路径或取回内容。
- 任务："报告 (a) spec 要求但缺失或部分实现的需求；(b) diff 中出现但 spec 未要求的行为（scope creep）；(c) 看似已实现但实现有错的需求。每条引用 spec 行。400 词内。"

spec 缺失时跳过 Spec sub-agent，并在终报告注明。

### 5. 汇总

在 `## Standards` 与 `## Spec` 标题下逐字或轻清理呈现两份报告。**不要**合并或重排发现，因为两轴刻意分开（见 _为何两条轴_）。

末尾一行总结：每轴发现总数，以及每轴内最严重问题（如有）。不要跨轴选单一赢家：这正是这种分离要防止的重排。

## 为何两条轴

一个改动可能过一轴挂另一轴：

- 代码遵循所有标准却实现错事 → **Standards 过，Spec 挂。**
- 代码做了 issue 要求的事却破坏项目惯例 → **Spec 过，Standards 挂。**

分开报告，一轴才不会掩盖另一轴。
