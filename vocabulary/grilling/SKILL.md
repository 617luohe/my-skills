---
name: grilling
layer: vocabulary
description: "[内部] 询问循环。由 /1-plan 加载以穷尽决策依赖，不进入模型技能表。"
disable-model-invocation: true
---

# Grilling — 询问循环

Interview me relentlessly about every aspect of this until we reach a shared understanding. Walk down each branch of the decision tree, resolving dependencies one-by-one. For each question, provide your recommended answer.

**批量询问**

- Group independent questions in the same frontier (当前可回答的决策集合)
- Ask them together in one turn, numbered with recommended answers
- If answering one would change another's premise, keep them in separate rounds

If a _fact_ can be found by exploring the environment (filesystem, tools, etc.), dispatch a sub-agent to find it rather than asking me; do not block on it — only the questions downstream of it wait, the rest of the frontier stays open. The _decisions_, though, are mine — put each one to me and wait for my answer.

Do not act on it until I confirm we have reached a shared understanding.

## 完成标准（退出条件）

达成共享理解 = 全部满足，缺一继续问：

1. **决策树已穷尽** — 当前层级的独立决策点都已拿到我的明确答复；已答过的问题按新答案更新，不重复旧结论。
2. **歧义已清零** — 待澄清的前提/边界冲突已全部摆上桌（领域术语歧义交父工作流，见下方分工）。
3. **我明确确认** — 我说理解一致；或连续一轮无新决策提出且我未提出异议。

## 与父工作流领域建模的分工

- 本技能问**计划决策**：方案选择、边界、取舍（"要不要做 X？"）
- `/1-plan` 的领域建模参考处理**领域术语语义**：术语歧义、领域边界（"account 指 Customer 还是 User？"）
- 询问中发现术语歧义 → 交回父工作流处理，在本技能内只指出、由父工作流收尾。
