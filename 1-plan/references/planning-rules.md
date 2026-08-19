# Planning Rules

## Frontier Algorithm

将未决事项建模为依赖图：节点是决策，边是依赖，frontier 是当前可回答的决策集合。事实从代码、配置和文档自行查证；目标、范围、风险和取舍交用户决定。优先处理阻塞后续工作的边界，直到所有模块的输入输出接口明确，实现细节可延后。

默认批量询问主题相近且互不依赖的 frontier；用户要求逐步时一次只问一个。用具体场景压力测试领域边界，用实际代码交叉验证系统现状。

## Branching And Prototypes

只有存在真实备选方案和需要用户比较的取舍时，才生成多个方案。比较方案应覆盖模块划分、接口定义、关键交互和测试切面，并给出推荐方案与取舍理由。若没有真实取舍，直接给出一个推荐方案，不制造三方案对比。

状态机、算法或 UI 假设无法由代码、文档或用户决策消除时，建立 throwaway prototype。任务定义待验证假设、最小实验、成功/失败判据和停止条件。验证后保留 verdict、证据摘要及必要决策片段；原型提交到 `prototype/<topic>`，主分支只保留决策。

## Document Authority

- `CONTEXT.md` 只保存领域 glossary：术语、关系、避免或有歧义的词及少量场景。
- 架构决策写入 `docs/adr/NNNN-title.md`，使用 `1-plan/references/adr-format.md`。
- 任务状态写入 `docs/plans/` 的任务清单、issue 或 `docs/handoff/`，不写入 `CONTEXT.md`。
