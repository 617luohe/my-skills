# Skill mechanics

[`writing-for-agents`](SKILL.md) 的 skill 专属分支：当文档是 skill 时有什么变化（frontmatter、调用方式选择、router 技能）。其余的写作是 `SKILL.md` 里的通用参考。

## Invocation（调用方式）

两种选择，权衡两种负载：

- **model-invoked** skill 保留 `description`，agent 能自主触发它，其它 skill 也能取到它。你仍然可以输入它的名字：model-invocation 永远**包含**人的可达性；一条 description 只会增加 agent 的发现，永不夺走人的。description 是 skill 的顶层 context pointer，被迫一直常驻：以永久 context load 换可发现性。一个内容全是 reference 的 model-invoked skill 也是共享 reference 的一个家：另一个 skill 能调用它，于是多个 skill 都需要的 reference 存在一处。机制：省略 `disable-model-invocation`，写一条面向模型的 description，带上触发分支（`SKILL.md` 的指针写作规则完全适用）。
- **user-invoked** skill 把 description 从 agent 的可达范围里摘掉：只有人输入它的名字才能调用，其它 skill 也不能。零 context load，但花 cognitive load：你是那个必须记得它存在的索引。机制：设 `disable-model-invocation: true`；`description` 变成面向人的：一行摘要，触发列表剥掉。

只有当 agent 必须自己够到这个 skill，或另一个 skill 必须够到它时，才选 model-invocation。如果它只靠手敲触发，就做成 user-invoked，不付 context load。

两个 user-invoked skill 都需要的共享 reference 不能放在任一个里：都没有 description，谁都不能触发谁。把它推到一个 skill 系统之外的普通文件：任何 skill 都能指向的外部 reference。

## Splitting by invocation（按调用方式拆分）

拆分（拆分这个动作）的调用方式一裁（序列裁在 `SKILL.md`）：当你有一个该独立触发它的不同前置词（一个你确实会在 prompt 里用的触发词），或另一个 skill 必须够到它时，拆出一个 model-invoked skill。你为那条新的常驻 description 付 context load，所以那份独立可达性必须值得。

## Router skills

当 user-invoked skill 多到超出你能记住的数量，那份堆积的 cognitive load 由 **router skill（路由技能）** 治愈：一个 user-invoked skill 命名其它技能、何时取哪个，于是人只需记一个技能而不是一堆。它只能提示，永不能触发它们：user-invoked skill 没有 description，所以除了人，谁也够不到它们。

## 加载一个 skill（宿主机制）

技能正文里表达「把这一步交给某个技能」时，统一写作**「加载技能 `<canonical-name>`」**，不在正文写宿主专有 API。含义是：在当前宿主取到该技能的 `SKILL.md` 并按其纪律执行。各宿主的取法：

| 宿主 | 取一个技能的方式 |
| --- | --- |
| Claude Code | 通过其 Skill 工具按运行时名加载（`/<deployment-name>`） |
| Cursor | 直接读该技能的 `SKILL.md`（技能目录已由分发挂载） |
| Codex | 读取 `agents/openai.yaml` 对应的技能文件 |

分发后技能被扁平部署，运行时名是 manifest contract 的 `deployment_name`；正文要指运行时名时用 `/` 前缀（如 `/tdd`），要指权威源时用 canonical name（如 `vocabulary/tdd`）。用户手工输入仍然总是可达的，这一点不随调用方式改变。

## 改 description 之后（trigger eval 约定）

`description` 是路由契约，动了它就要留下可复核的观察记录：

- **重跑受影响的样例**：`tests/fixtures/prompts/router/trigger-evals.json` 中 `expected` 或 `forbidden` 命中该技能的 case；改动 `0-router` 正文时全跑。
- **留痕**：把结果写进 `docs/governance/trigger-eval-results-<YYYY-MM-DD>.md`，头部记宿主、模型、`my-skills` commit；逐 case 记首个触发入口、是否先澄清、是否发生 `allowed_side_effect` 之外的副作用，以及与预期的差异。只记差异与结论，不复制数据集表格。
- **不进阻断式 CI**：数据集结构由 pytest 静态校验（每个 route 必须指向活着的技能），模型观察按日期留痕即可。高副作用 case 的失败结论必须写明「只能进澄清或只读」。
