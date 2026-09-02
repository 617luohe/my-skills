# Deepening

如何安全地加深一个浅模块簇，给定它的依赖。假设已掌握 [SKILL.md](SKILL.md) 的词汇：**module**、**interface**、**seam**、**adapter**。

## 依赖分类

评估加深候选时，给它的依赖分类。类别决定加深后的模块如何跨 seam 测试。

### 1. In-process

纯计算、内存态、无 I/O。总是可加深：合并模块，直接通过新接口测试。不需要 adapter。

### 2. Local-substitutable

有本地测试替身的依赖（Postgres 用 PGLite、内存文件系统）。替身存在即可加深。加深后的模块在测试套件里跑替身来测。seam 是内部的；模块外部接口处没有 port。

### 3. Remote but owned（Ports & Adapters）

你自己的跨网络边界的服务（微服务、内部 API）。在 seam 处定义一个 **port**（接口）。深模块拥有逻辑；传输层作为 **adapter** 注入。测试用内存 adapter。生产用 HTTP/gRPC/queue adapter。

推荐句式：*"在 seam 处定义 port，生产实现 HTTP adapter、测试实现内存 adapter，这样逻辑即使跨网络部署也待在一个深模块里。"*

### 4. True external（Mock）

第三方服务（Stripe、Twilio 等）你无法控制。加深后的模块把外部依赖作为注入的 port 接收；测试提供 mock adapter。

## Seam 纪律

- **一个 adapter 是假设的 seam，两个 adapter 才是真的。** 除非至少两个 adapter 有理由存在（通常是生产 + 测试），否则不要引入 port。单 adapter 的 seam 只是间接层。
- **内部 seam vs 外部 seam。** 深模块可以有内部 seam（实现私有的，供自己的测试用），以及接口处的外部 seam。别因为测试用了内部 seam 就把它们暴露到接口上。

## 测试策略：replace, don't layer

- 加深模块的接口测试存在后，浅模块上的旧单元测试就成了浪费；删掉它们。
- 在加深后模块的接口处写新测试。**接口就是测试面**。
- 测试断言接口处的可观察结果，而非内部状态。
- 测试应扛住内部重构，因为它们描述行为而非实现。如果实现变了测试就得跟着变，那是在测*越过*接口的东西。
