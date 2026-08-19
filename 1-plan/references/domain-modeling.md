# Domain Modeling

规划期间主动锐化领域语言，并在术语确认时立即更新项目 glossary。计划取舍由 `/grilling` 处理；本参考只处理术语语义与领域边界。

## 文件边界

- 单一上下文默认使用根目录 `CONTEXT.md`。
- 已有 `CONTEXT-MAP.md` 时按其指针维护多个上下文。
- 首个术语确认后才创建缺失的 `CONTEXT.md`；首个合格架构决策出现后才创建 `docs/adr/`。

## 过程

1. 用户用词与现有 glossary 冲突时，指出旧定义与当前含义并要求二选一。
2. 模糊或过载词出现时，提出精确规范词，例如区分 Customer 与 User。
3. 用具体边界场景压力测试关系和例外。
4. 用户陈述系统行为时，用代码和现有测试交叉验证；矛盾必须显式解决。
5. 术语一经确认就更新 `CONTEXT.md`，不积攒到会话末尾。

`CONTEXT.md` 只保存术语、关系、少量领域场景和已标记歧义。实现细节、技术栈、模块地图、任务状态、历史记录和 ADR 均写入各自权威位置。

## ADR 门禁

只有决策同时满足以下三项才提议 ADR：

1. 改变决定的成本显著。
2. 缺少上下文时未来读者会疑惑。
3. 存在真实备选与明确取舍。

合格 ADR 使用 [adr-format.md](adr-format.md)，写入 `docs/adr/NNNN-title.md`。

## 完成条件

- 关键术语均已定义，或明确标记 Avoid / Previously ambiguous / Flagged ambiguity。
- glossary 与已验证代码行为无未处理冲突。
- 新 ADR 均通过三项门禁，任务状态未写入 `CONTEXT.md`。
