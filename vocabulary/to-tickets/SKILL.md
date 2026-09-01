---
name: to-tickets
layer: vocabulary
description: 把 plan、spec 或当前对话拆成一组 tracer-bullet ticket，每个声明它的阻塞边，发布到已配置的 tracker（本地每个 ticket 一个文件、边写成文本，或在真 tracker 上用原生阻塞链接）。
---

# To Tickets

把 plan、spec 或对话拆成一组 **ticket**：tracer-bullet 垂直切片，每个声明**阻塞**它的 ticket。

issue tracker 与 triage label 词汇应该已经提供给你。若没有，让用户先跑 issue tracker 配置（本体系适配：落点 `docs/plans/<feature>/tasks.md`）。

## 流程

### 1. 收集上下文

从对话上下文已有的内容出发。用户传引用（spec 路径、issue 号或 URL）作参数时，取来读它的全文与评论。

### 2. 探索代码库（可选）

若尚未探索过代码库，就先探索以理解代码当前状态。ticket 的标题与描述应使用项目领域 glossary 词汇，并尊重你所触及区域的 ADR。

寻找 prefactor 的机会，让实现更容易。"先让改动变容易，再做那个容易的改动。"

### 3. 起草垂直切片

把工作拆成 **tracer bullet** ticket。

- 每个切片切一条窄而**完整**、贯穿每一层（schema、API、UI、测试）的路径：垂直，**不是**只切一层水平切片
- 完成的切片自身可 demo 或可验证
- 每个切片大小适配单个 fresh context window
- 任何 prefactor 都应先做

给每个 ticket 声明它的**阻塞边**：必须先完成、它才能开始的其它 ticket。无阻塞的 ticket 可立即开始。

**宽重构是垂直切片的例外。** 宽重构是一个机械改动（改列名、重定共享符号类型）其**爆炸半径**横扫整个代码库，单次编辑同时破坏上千调用点、没有垂直切片能落绿。别硬塞进 tracer bullet；按 **expand–contract** 排序。先 expand：新旧并存加新形式，什么都不破坏。再按爆炸半径分批（按 package、按目录）迁移调用点，每批一个 ticket、被 expand 阻塞，旧形式仍在所以批间 CI 常绿。最后 contract：无调用者后删旧形式，一个 ticket、被每个迁移批阻塞。连批内都无法单独常绿时，保持顺序但让它们共享一个 integration branch，全部阻塞一个最终的 integrate-and-verify ticket；只有那里承诺常绿。

### 4. 向用户核对

把提议的拆解呈作编号列表。每个 ticket 展示：

- **Title**：简短描述名
- **Blocked by**：必须先完成的其它 ticket（如有）
- **What it delivers**：这个 ticket 使之工作的端到端行为

问用户：

- 粒度合适吗？（太粗 / 太细）
- 阻塞边对吗：每个 ticket 只依赖真正门控它的 ticket？
- 有 ticket 要合并或再拆吗？

迭代到用户认可拆解。

### 5. 把 ticket 发布到已配置的 tracker（本体系适配：写入 `docs/plans/<feature>/tasks.md`）

发布已认可的 ticket。**怎么做**取决于你体系的落点约定；ticket 本身不变，唯一变的是阻塞边的形状：

- **本体系 tasks.md** → 写 `docs/plans/<feature>/tasks.md`，按依赖序（阻塞者在前）编号。每项包含 Task ID、Title、Description、Acceptance Criteria、AFK/HITL、Depends On、Write Set。
- **真 issue tracker（GitHub、Linear、…）** → 按依赖序（阻塞者在前）每个 ticket 发布一个 issue，让每条阻塞边能引用真标识符。平台有原生阻塞 / sub-issue 关系就用它；否则把每个 ticket 的 "Blocked by" 设为阻塞它的 issue。除非另有指示，应用 `ready-for-agent` triage label；ticket 按构造即可被 agent 抓取。

按 **frontier** 推进：任何阻塞者都已完成的 ticket。纯线性链就是自上而下。

**不要**关闭或修改任何父 issue。

〔模板：local-ticket-template〕

# <NN>: <Ticket title>

**要构建什么：** 这个 ticket 使之工作的端到端行为，从用户视角，而非逐层实现清单。

**被谁阻塞：** 门控本 ticket 的 ticket 编号/标题，或 "无（可立即开始）"。

**状态：** ready-for-agent

- [ ] 验收标准 1
- [ ] 验收标准 2

〔模板结束〕

〔模板：issue-template〕

## 父级

对 tracker 上父 issue 的引用（若来源是既有 issue；否则省略本节）。

## 要构建什么

这个 ticket 使之工作的端到端行为，从用户视角，而非逐层实现。

## 验收标准

- [ ] 标准 1
- [ ] 标准 2

## 被谁阻塞

- 对每个阻塞 ticket 的引用，或 "无（可立即开始）"。

〔模板结束〕

任何形式都避免具体文件路径或代码片段：它们很快过时。例外：若某原型产出的片段比散文更能精确编码一个决策（状态机、reducer、schema、类型形状），内联它，并简短注明它来自原型。裁到决策丰富的部分，不是可运行的 demo，只留重要的那些位。
