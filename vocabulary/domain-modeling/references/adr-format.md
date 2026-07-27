# ADR Format Reference

## File location and naming

Create each architecture decision record as its own file:

```
docs/adr/NNNN-title.md
```

Use the next zero-padded sequential number, for example `0001-use-postgres.md`. ADRs never live in `CONTEXT.md`.

## Standard template

```markdown
# ADR NNNN: {Title}

**Status:** Proposed | Accepted | Superseded by NNNN | Deprecated

## Context

{The situation, constraints, and decision drivers.}

## Decision

{What was decided.}

## Consequences

{Benefits, costs, risks, and follow-up work accepted by this choice.}

## Alternatives considered

- {Alternative}: {why it was not selected}
```

## Writing guidelines

1. Create an ADR only for a hard-to-reverse, non-obvious decision with a genuine trade-off.
2. Give the title a concise imperative form, such as "Use PostgreSQL for the write model".
3. State concrete reasons and honest consequences.
4. When replacing an accepted decision, retain the old ADR and mark its status `Superseded by NNNN`.
5. Do not use ADRs for implementation details or obvious choices.
