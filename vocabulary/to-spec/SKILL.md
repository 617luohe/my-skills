---
name: to-spec
layer: vocabulary
description: "把当前对话转成一份 spec，并发布到项目的 issue tracker：不追问，只综合你已经讨论过的东西。"
---

本技能取当前对话上下文与代码库理解，产出一份 spec。**不要**追问用户；只综合你已经知道的东西。

issue tracker 与 triage label 词汇应该已经提供给你。若没有，让用户先跑 issue tracker 配置（本体系中对应任务清单/PRD 的落点约定）。

## 流程

1. 若还没探索过仓库，先探索以理解代码库当前状态。全文使用项目的领域 glossary 词汇，并尊重你所触及区域的任何 ADR。

2. 草拟你将要测试该功能所用的 **seams**。应优先既有 seam 而非新 seam。用尽可能高的 seam。若需要新 seam，在你能做到的最高点提议。整个代码库的 seam 越少越好——理想数量是一个。

和用户核对这些 seam 是否符合他们的预期。

3. 用下面的模板写 spec，然后发布到项目的 issue tracker（本体系适配：写入 `docs/plans/<feature>/PRD.md`）。应用 `ready-for-agent` triage label——不需要额外 triage。

## Problem Statement

用户正面临的问题，从用户的视角。

## Solution

问题的解决方案，从用户的视角。

## User Stories

一长串编号的用户故事。每条用户故事的格式应为：

1. 作为 <actor>，我想要 <feature>，以便 <benefit>

1. 作为手机银行客户，我想要看到账户余额，以便对消费做出更明智的决定

这份用户故事列表应当极其详尽，覆盖功能的所有方面。

## Implementation Decisions

一份已做出的实现决策列表。可以包括：

- 将构建/修改的模块
- 这些模块将被修改的接口
- 来自开发者的技术澄清
- 架构决策
- Schema 变更
- API 契约
- 具体交互

**不要**包含具体文件路径或代码片段。它们可能很快就过时。

例外：若某原型产出的片段比散文更能精确编码一个决策（状态机、reducer、schema、类型形状），把它内联进相关决策，并简短注明它来自原型。裁到决策丰富的部分，不是可运行的 demo，只留重要的那些位。

## Testing Decisions

一份已做出的测试决策列表。包括：

- 一份"什么构成好测试"的描述（只测外部行为，不测实现细节）
- 哪些模块将被测试
- 这些测试的先例（即代码库中类似类型的测试）

## Out of Scope

本 spec 范围之外的事项的描述。

## Further Notes

关于该功能的任何进一步说明。
