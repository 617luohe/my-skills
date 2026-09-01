---
name: domain-modeling
layer: vocabulary
description: 构建并锐化项目的领域模型。讨论代码术语、写或编辑 CONTEXT.md、记录或编辑 ADR 时用。
---

# Domain Modeling

积极主动地构建并锐化项目的领域模型，贯穿设计全程。这是*主动*纪律：挑战术语、发明边界场景，并在术语与决策一结晶的当下写下来。（仅仅*阅读* `CONTEXT.md` 获取词汇不是本技能：那是任何技能都能做的一行习惯。本技能用于**改变**模型，而非只是消费它。）

## 文件结构

多数仓库只有一个上下文：

```
/
├── CONTEXT.md
├── docs/
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

若根目录存在 `CONTEXT-MAP.md`，仓库就有多个上下文。map 指向每个上下文的所在：

```
/
├── CONTEXT-MAP.md
├── docs/
│   └── adr/                          ← 系统级决策
├── src/
│   ├── ordering/
│   │   ├── CONTEXT.md
│   │   └── docs/adr/                 ← 该上下文的决策
│   └── billing/
│       ├── CONTEXT.md
│       └── docs/adr/
```

惰性创建文件：只有当你有了要写的东西才建。没有 `CONTEXT.md` 时，首个术语被解决时才创建；没有 `docs/adr/` 时，首个 ADR 需要时才创建。

## 会话中

### 对照 glossary 挑战

用户用词与 `CONTEXT.md` 既有语言冲突时，立即指出。"你的 glossary 把 'cancellation' 定义为 X，但你似乎指的是 Y。是哪个？"

### 锐化模糊语言

用户使用模糊或过载词时，提出精确的规范词。"你说 'account'：你指的是 Customer 还是 User？那是两个不同的东西。"

### 讨论具体场景

讨论领域关系时，用具体场景压力测试它们。发明探测边界情况的场景，迫使用户精确界定概念之间的边界。

### 与代码交叉验证

用户陈述某事的运作方式时，核对代码是否一致。发现矛盾就摆出来："你的代码取消的是整张 Order，但你刚刚说部分取消是可能的。哪个才是对的？"

### 就地更新 CONTEXT.md

术语一经解决就就地更新 `CONTEXT.md`。不要攒成批：一发生就捕获。使用 [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md) 的格式。

`CONTEXT.md` 应完全不含实现细节。别把 `CONTEXT.md` 当 spec、草稿纸或实现决策的仓库。它是 glossary，仅此而已。

### 审慎提议 ADR

只有三项全部成立时才提议创建 ADR：

1. **难逆转**：日后改变主意的成本是有意义的
2. **缺上下文会令人意外**：未来的读者会疑惑"他们为什么这样做？"
3. **真实取舍的结果**：当时存在真实的备选，你为具体理由选了其一

任何一项缺失就跳过 ADR。使用 [ADR-FORMAT.md](./ADR-FORMAT.md) 的格式。
