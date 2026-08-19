# ADR Format

## 位置与命名

每个架构决策单独写入：

```text
docs/adr/NNNN-title.md
```

使用下一个四位顺序号。ADR 不写入 `CONTEXT.md`。

## 模板

```markdown
# ADR NNNN: {Title}

**Status:** Proposed | Accepted | Superseded by NNNN | Deprecated

## Context

{Situation, constraints, and decision drivers.}

## Decision

{What was decided.}

## Consequences

{Benefits, costs, risks, and follow-up work.}

## Alternatives considered

- {Alternative}: {why it was not selected}
```

## 规则

1. 仅记录难逆转、非显然且存在真实取舍的决定。
2. 标题简洁描述决定。
3. 写出具体原因和诚实后果。
4. 替换既有决定时保留旧 ADR，并标记 `Superseded by NNNN`。
5. 实现细节与显然选择不建 ADR。
