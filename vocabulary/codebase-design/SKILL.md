---
name: codebase-design
layer: vocabulary
description: 设计深模块的共享词汇。用户想设计或改进模块接口、找加深机会、决定 seam 位置、让代码更可测或更易被 AI 导航，或另一个技能需要深模块词汇时用。
---

# Codebase Design

设计**深模块**：小接口后面藏着大量行为，放在干净的 seam 上，能通过该接口测试。在任何设计或重构代码的地方使用这套语言和原则。目标是调用方的 **leverage**、维护方的 **locality**、所有人的可测试性。

## Glossary

精确使用这些词：不要替换成 "component"、"service"、"API" 或 "boundary"。语言一致就是全部意义所在。

**Module**：任何有接口和实现的东西。刻意与规模无关：函数、类、包，或跨层切片。_Avoid_: unit, component, service。

**Interface**：调用方正确使用模块必须知道的一切：类型签名，还有不变量、顺序约束、错误模式、所需配置和性能特征。_Avoid_: API, signature（太窄，它们只指类型层面的表面）。

**Implementation**：模块内部的东西，它的代码主体。与 **Adapter** 区分：一个东西可以是小 adapter + 大 implementation（Postgres repo），也可以是大 adapter + 小 implementation（in-memory fake）。讨论点是 seam 时用 "adapter"，否则用 "implementation"。

**Depth**：接口处的 leverage。调用方（或测试）每学一单位接口就能拿到的行为量。模块**深**，指大量行为藏在小接口后面；**浅**，指接口几乎和实现一样复杂。

**Seam** _(Michael Feathers)_：不改动原地就能改变行为的地方；模块接口所在的*位置*。seam 放哪是独立的设计决策，区别于它后面放什么。_Avoid_: boundary（与 DDD 的 bounded context 过载）。

**Adapter**：在 seam 处满足接口的具体东西。描述*角色*（它填什么槽），不是*实质*（里面是什么）。

**Leverage**：调用方从 depth 得到的东西。每学一单位接口获得更多能力。一份实现回报 N 个调用点和 M 个测试。

**Locality**：维护方从 depth 得到的东西。变更、bug、知识和验证集中在一处，而不是散布到调用方。修一次，处处生效。

## Deep vs shallow

**深模块** = 小接口 + 大量实现：

```
┌─────────────────────┐
│   Small Interface   │  ← 少方法，简单参数
├─────────────────────┤
│                     │
│  Deep Implementation│  ← 复杂逻辑藏在内
│                     │
└─────────────────────┘
```

**浅模块** = 大接口 + 少量实现（避免）：

```
┌─────────────────────────────────┐
│       Large Interface           │  ← 多方法，复杂参数
├─────────────────────────────────┤
│  Thin Implementation            │  ← 只是透传
└─────────────────────────────────┘
```

设计接口时问：

- 能减少方法数吗？
- 能简化参数吗？
- 能把更多复杂度藏进内部吗？

## Principles

- **Depth 是接口的属性，不是实现的属性。** 深模块内部可以由小的、可 mock 的、可替换的部件组成；它们只是不属于接口。模块可以有**内部 seam**（实现私有的，供自己的测试用）以及接口处的**外部 seam**。
- **删除测试。** 想象删掉这个模块。复杂度随之消失，它就是透传；复杂度散布回 N 个调用方，它就在挣它的存在价值。
- **接口就是测试面。** 调用方和测试跨同一个 seam。如果你想测*越过*接口的东西，模块的形状大概不对。
- **一个 adapter 是假设的 seam，两个 adapter 才是真的。** 除非有东西真的跨 seam 变化，否则不要引入 seam。

## Designing for testability

好接口让测试自然：

1. **接受依赖，不要创建依赖。**

   ```typescript
   // 可测
   function processOrder(order, paymentGateway) {}

   // 难测
   function processOrder(order) {
     const gateway = new StripeGateway();
   }
   ```

2. **返回结果，不要产生副作用。**

   ```typescript
   // 可测
   function calculateDiscount(cart): Discount {}

   // 难测
   function applyDiscount(cart): void {
     cart.total -= discount;
   }
   ```

3. **小表面积。** 少方法 = 少测试。少参数 = 简单测试设置。

## Relationships

- 一个 **Module** 恰好有一个 **Interface**（它向调用方和测试呈现的表面）。
- **Depth** 是 **Module** 的属性，对着它的 **Interface** 度量。
- **Seam** 是 **Module** 的 **Interface** 所在之处。
- **Adapter** 坐在 **Seam** 上并满足 **Interface**。
- **Depth** 为调用方产出 **Leverage**，为维护方产出 **Locality**。

## Rejected framings

- **Depth 作为实现行数对接口行数的比率**（Ousterhout）：奖励灌水实现。我们用 depth-as-leverage。
- **"Interface" 作为 TypeScript `interface` 关键字或类的公共方法**：太窄：这里的 interface 包含调用方必须知道的每一个事实。
- **"Boundary"**：与 DDD 的 bounded context 过载。说 **seam** 或 **interface**。

## Going deeper

- **给定依赖加深一个簇**，见 [DEEPENING.md](DEEPENING.md)：依赖分类、seam 纪律、replace-don't-layer 测试。
- **探索替代接口**，见 [DESIGN-IT-TWICE.md](DESIGN-IT-TWICE.md)：并行 sub-agent 用几种截然不同的方式设计接口，然后按 depth、locality 和 seam 位置比较。
