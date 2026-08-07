---
name: domain-modeling
layer: vocabulary
description: Build a project's domain model: pin down terminology/ubiquitous language, record architecture decisions. Use when another skill needs to maintain the domain glossary.
disable-model-invocation: false
---

# Domain Modeling — 领域建模

Actively build and sharpen the project's domain model as you design. This is the _active_ discipline — challenging terms, inventing edge-case scenarios, and writing the glossary and decisions down the moment they crystallise.

## File structure

Most repos have a single context:

```
/
├── CONTEXT.md
├── docs/
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

If a `CONTEXT-MAP.md` exists at the root, the repo has multiple contexts. The map points to where each one lives.

Create files lazily — only when you have something to write. If no `CONTEXT.md` exists, create one when the first term is resolved. If no `docs/adr/` exists, create it when the first ADR is needed.

## During the session

> 本技能处理**领域术语/边界**的澄清；计划与方案决策的询问循环由 `/vocabulary/grilling` 承担。

### Challenge against the glossary

When the user uses a term that conflicts with the existing language in `CONTEXT.md`, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account' — do you mean the Customer or the User? Those are different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

### Cross-reference with code

When the user states how something works, check whether the code agrees. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible — which is right?"

### Update CONTEXT.md inline

When a term is resolved, update `CONTEXT.md` right there. Don't batch these up — capture them as they happen.

`CONTEXT.md` should be totally devoid of implementation details. Do not treat `CONTEXT.md` as a spec, a scratch pad, or a repository for implementation decisions. It is a glossary and nothing else.

### Offer ADRs sparingly

Only offer to create an ADR when all three are true:

1. **Hard to reverse** — the cost of changing your mind later is meaningful
2. **Surprising without context** — a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off** — there were genuine alternatives and you picked one for specific reasons

If any of the three is missing, skip the ADR.

## CONTEXT.md format

```markdown
# {项目名称}

{一两句描述}

## Language

**Order**:
A customer's request to purchase products.
_Avoid_: Purchase, transaction

**Invoice**:
A request for payment sent to a customer after delivery.
_Avoid_: Bill, payment request

**Customer** vs **User**:
Customer is the billing entity; User is the person operating the system.
_Previously ambiguous_: "account" referred to both
```

## ADR format

Use this skill's published [ADR template](references/adr-format.md).

ADRs are created only in `docs/adr/NNNN-title.md` with sequential numbering (0001, 0002, ...). Task status belongs in `docs/plans/`, task lists, issues, or `docs/handoff/` — never in `CONTEXT.md`.

## 完成标准

**必须满足**：

- `CONTEXT.md` 中无未标记的歧义术语（所有关键术语已定义或标注 _Avoid_ / _Previously ambiguous_）
- 如果创建了 ADR，必须同时满足三条件：hard to reverse + surprising without context + real trade-off

**交接**：

- 术语澄清完成后，共享理解已建立，可继续上游 skill（如 `/1-规划` 的后续阶段）
- ADR 创建后，决策已记录，可作为实施依据
