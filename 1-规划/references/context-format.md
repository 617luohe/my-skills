# CONTEXT.md Format Specification

## Purpose

`CONTEXT.md` is the project's domain glossary. It records stable ubiquitous language so people and agents use the same words for the same domain concepts.

It is **not** a project overview, technical-stack record, module map, ADR register, task tracker, or historical archive.

## Structure

```markdown
# {Project name}

{One-sentence domain scope, if useful.}

## Language

**Order**:
A customer's request to purchase products.
_Avoid_: Purchase, transaction

**Customer** vs **User**:
Customer is the billing entity; User is the person operating the system.
_Previously ambiguous_: "account" referred to both.

## Relationships

- An **Order** contains one or more **Order Lines**.
- An **Invoice** requests payment for an **Order**.

## Domain scenarios

- If an Order is partially shipped, only its unshipped Order Lines are cancellable.

## Flagged ambiguities

- "Cancellation" must state whether it applies to the whole Order or an Order Line.
```

## Allowed content

- Canonical terms and concise definitions
- Relationships between domain concepts
- Avoided, overloaded, or previously ambiguous words
- A small number of domain scenarios that clarify a boundary

## Update rules

1. Add a term when its meaning is resolved.
2. Clarify ambiguity beside the relevant term or in **Flagged ambiguities**.
3. Keep examples domain-facing, not implementation-facing.
4. Record architectural decisions only in `docs/adr/NNNN-title.md`.
5. Record task status only in `docs/plans/`, a task list, issue, or `docs/handoff/` document.

## Anti-patterns

- Technical stack, implementation details, or module maps
- Embedded ADRs or a list of ADR decisions
- Current branch, progress checklist, active task, or sprint status
- Historical changelog or session archive
