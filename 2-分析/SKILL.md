---
name: 2-分析
description: Read unfamiliar code and output a high-level map — modules, data flow, entry points, architecture context. Use when you don't understand a section of code, need architecture overview, or want to see the big picture. 触发词：分析、理解、概览、地图、看不懂、结构、模块、代码结构、overview。
disable-model-invocation: true
---

# 2-分析 — 代码理解与概览

面对一段不熟悉的代码时，让 Claude 跳出细节，给你一张"地图"，而不是钻进代码行。

## MUST 规则

1. **立刻往上一层抽象。** 不进代码行细节，给地图不给实现。
2. **四部分缺一不可。** 模块地图 + 数据流 + 关键入口 + 与整体架构的关系。
3. **全程使用项目领域术语。** 不泛称"这个模块""那个类"。
4. **如检测到 graphify 产出，优先利用其分析线索。** 读取 Suggested Questions 作为分析切入点。

## 前置检查

**如果检测到 `graphify-out/GRAPH_REPORT.md` 存在**：
1. 读取其中的 **Suggested Questions** 节（通常在文档末尾）
2. 从中筛选与当前分析目标相关的问题
   - 如用户说"分析 auth 模块" → 筛选含 "auth" 的问题
   - 如用户说"看不懂整个项目" → 选择最能揭示架构的 3-5 个问题
3. 将这些问题作为分析线索，在输出的"关键入口"和"架构关系"节中回答
4. 在输出末尾标注：`基于 graphify 索引的分析线索：[问题1][问题2]...`

**如果不存在**：跳过，按常规流程分析。

## 工作方式

立刻往上一层抽象，输出以下四部分：

### 1. 模块地图

当前区域涉及哪些模块/文件，各自职责是什么。

### 2. 数据流

数据在这些模块之间如何流转：谁调谁、输入输出是什么。

### 3. 关键入口

从哪里开始读最有效率，推荐阅读顺序。

### 4. 与整体架构的关系

这片代码在整个项目中处于什么位置，上下游分别是谁。

全程使用项目领域术语描述，不用泛称。

## 什么时候用

- 接手一个你不熟悉的模块的 issue
- 看 PR 之前想先了解改动区域的全貌
- 新加入项目，需要快速建立代码心智模型

## 案例

```
你：这个 views.py 我完全看不懂，帮我分析一下
Claude：这是订单模块的视图层，整体结构如下：

        User → OrderViewSet (views.py:15)
                ├── list()     → OrderSerializer → OrderRepository
                ├── create()   → validate → PaymentService.process()
                └── retrieve() → OrderSerializer → OrderRepository

        数据流：request → 认证中间件 → ViewSet → Service → Repository → DB
        返回：Serializer → JSON

        这片代码主要负责订单的 CRUD 和支付状态变更，上游是 API 网关，
        下游是 OrderService 和 PaymentService。
        建议从 OrderViewSet.create() (views.py:42) 开始读。
```

## 完成后 — 自动推进

分析只给地图，不改代码。给出地图后按用户的原始意图自动衔接，无需重新点名：

- **原意图是"看懂就行"** → 停在这里，不擅自往下。
- **原意图是"分析完帮我改/优化/修"** → 按需求进环：要动结构 → `/6-优化`；要加功能 → `/1-规划`；要修 bug → `/7-调试`。
- **接手陌生项目场景** → 分析是 `/0--graphify` 之后的第二步，给完地图即进上面对应的环。

推进前一句话报出下一步 skill，再执行。
