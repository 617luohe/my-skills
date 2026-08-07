---
name: grilling
layer: vocabulary
description: Grill the user relentlessly about a plan or decision. Use when the user wants to stress-test their thinking.
disable-model-invocation: false
---

# Grilling — 询问循环

Interview me relentlessly about every aspect of this until we reach a shared understanding. Walk down each branch of the decision tree, resolving dependencies one-by-one. For each question, provide your recommended answer.

**默认模式：批量询问**

- Group independent questions in the same frontier (当前可回答的决策集合)
- Ask them together in one turn, numbered with recommended answers
- If answering one would change another's premise, keep them in separate rounds

**逐步模式：一次一问**

- When I say "逐步", "一步一步", "一个一个问", "step by step", or "one at a time"
- Switch to asking one question at a time, waiting for feedback on each

If a _fact_ can be found by exploring the environment (filesystem, tools, etc.), look it up rather than asking me. The _decisions_, though, are mine — put each one to me and wait for my answer.

Do not act on it until I confirm we have reached a shared understanding.

## 完成标准（退出条件）

达成共享理解 = **全部满足**，缺一继续问：

1. **决策树已穷尽** — 当前层级的独立决策点都已拿到你的明确答复；批量轮中已回答的问题不再重复
2. **歧义已清零** — 无待澄清的前提/边界冲突（领域术语歧义不归本技能，见下方分工）
3. **你明确确认** — 你说理解一致；或连续一轮无新决策提出且你未提出异议

## 与 domain-modeling 的分工

- 本技能问**计划决策**：方案选择、边界、取舍（"要不要做 X？"）
- `/vocabulary/domain-modeling` 问**领域术语语义**：术语歧义、领域边界（"account 指 Customer 还是 User？"）
- 询问中发现术语歧义 → 转 domain-modeling 处理，不在本技能内纠缠
