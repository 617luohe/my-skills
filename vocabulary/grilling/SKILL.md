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

If a *fact* can be found by exploring the environment (filesystem, tools, etc.), look it up rather than asking me. The *decisions*, though, are mine — put each one to me and wait for my answer.

Do not act on it until I confirm we have reached a shared understanding.
