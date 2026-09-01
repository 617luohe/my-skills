# CONTEXT.md Format

## 结构

```md
# {上下文名称}

{一两句话描述这个上下文是什么、为什么存在。}

## Language

**Order**:
{一两句话描述这个术语}
_Avoid_: Purchase, transaction

**Invoice**:
A request for payment sent to a customer after delivery.
_Avoid_: Bill, payment request

**Customer**:
A person or organization that places orders.
_Avoid_: Client, buyer, account
```

## 规则

- **要有主见。** 多个词表达同一概念时，选出最好的一个，把其余列在 `_Avoid_` 下。
- **定义要紧凑。** 最多一两句话。定义它 **IS** 什么，不是它**做什么**。
- **只收录本项目上下文特有的术语。** 通用编程概念（超时、错误类型、工具模式）不属于此处，即便项目大量使用它们。加词之前先问：这是本上下文独有的概念，还是通用编程概念？只有前者才属于这里。
- **自然成簇时用小标题分组。** 所有术语属于单一内聚领域时，平铺列表即可。

## 单上下文 vs 多上下文仓库

**单上下文（多数仓库）：** 根目录一个 `CONTEXT.md`。

**多上下文：** 根目录的 `CONTEXT-MAP.md` 列出各上下文、它们的位置、以及它们的相互关系：

```md
# Context Map

## Contexts

- Ordering（`./src/ordering/CONTEXT.md`）：receives and tracks customer orders
- Billing（`./src/billing/CONTEXT.md`）：generates invoices and processes payments
- Fulfillment（`./src/fulfillment/CONTEXT.md`）：manages warehouse picking and shipping

## Relationships

- **Ordering → Fulfillment**: Ordering emits `OrderPlaced` events; Fulfillment consumes them to start picking
- **Fulfillment → Billing**: Fulfillment emits `ShipmentDispatched` events; Billing consumes them to generate invoices
- **Ordering ↔ Billing**: Shared types for `CustomerId` and `Money`
```

本技能据此推断适用哪种结构：

- 若存在 `CONTEXT-MAP.md`，读它找到各上下文
- 若只有根目录 `CONTEXT.md`，单上下文
- 若两者都没有，首个术语被解决时惰性创建根目录 `CONTEXT.md`

存在多个上下文时，推断当前话题属于哪个。不清楚就问。
