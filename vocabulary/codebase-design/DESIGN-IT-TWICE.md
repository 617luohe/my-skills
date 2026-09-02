# Design It Twice

用户想为选定的加深候选探索替代接口时，用这个并行 sub-agent 模式。基于 "Design It Twice"（Ousterhout）：你的第一个想法不太可能是最好的。

使用 [SKILL.md](SKILL.md) 的词汇：**module**、**interface**、**seam**、**adapter**、**leverage**。

## 流程

### 1. 框定问题空间

派 sub-agent 之前，为选定的候选写一份面向用户的解释，说明问题空间：

- 任何新接口都必须满足的约束
- 它依赖什么，以及这些依赖属于哪个类别（见 [DEEPENING.md](DEEPENING.md)）
- 一份粗略的示意代码草图，把约束钉实——不是提案，只是让约束具体化的方式

展示给用户，然后立即进入第 2 步。用户在 sub-agent 并行工作时阅读和思考。

### 2. 派 sub-agent

并行派 3 个以上 sub-agent。每个必须为加深后的模块产出一个**截然不同**的接口。

给每个 sub-agent 一份独立的技术 brief（文件路径、耦合细节、来自 [DEEPENING.md](DEEPENING.md) 的依赖类别、seam 后面是什么）。brief 与第 1 步面向用户的问题空间解释无关。给每个 agent 不同的设计约束：

- Agent 1: "最小化接口：最多 1–3 个入口点。最大化每个入口点的 leverage。"
- Agent 2: "最大化灵活性：支持大量用例和扩展。"
- Agent 3: "为最常见的调用方优化：让默认场景平凡。"
- Agent 4（如适用）: "围绕 ports & adapters 设计跨 seam 依赖。"

把 [SKILL.md](SKILL.md) 词汇和 CONTEXT.md 词汇都放进 brief，让每个 sub-agent 的命名与架构语言和项目领域语言一致。

每个 sub-agent 输出：

1. 接口（类型、方法、参数，加上不变量、顺序、错误模式）
2. 用法示例，展示调用方怎么用
3. 实现藏在 seam 后面的是什么
4. 依赖策略和 adapters（见 [DEEPENING.md](DEEPENING.md)）
5. 取舍：哪里 leverage 高，哪里薄

### 3. 呈现与比较

逐个顺序呈现设计，让用户能吸收每一个，然后用散文比较。按 **depth**（接口处的 leverage）、**locality**（变更集中在哪里）、**seam 位置**对比。

比较之后给出你自己的推荐：你认为哪个设计最强、为什么。如果不同设计的元素能很好组合，提出混合方案。要有主见：用户要的是强判断，不是菜单。
