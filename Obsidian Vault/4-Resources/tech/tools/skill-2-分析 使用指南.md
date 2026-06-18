---
title: "skill-2-分析 使用指南"
aliases: ["分析技能指南", "代码分析指南"]
tags:
  - type/resource
  - domain/tech/tools
  - topic/skills-guide
created: 2026-06-18
status: published
confidence: sprout
source: "https://github.com/617luohe/my-skills"
skill: "2-分析"
---

# 2-分析 — 代码理解与概览

> 一句话：面对不熟悉的代码，跳出细节，输出一张"模块地图 + 数据流 + 关键入口 + 架构位置"。先看地图，再读代码。

## 什么时候用

| 场景 | 说明 |
|------|------|
| 接手一个不熟悉的模块 | 拿到一个 issue 但完全不知道代码在哪 |
| 看 PR 之前 | 先了解改动区域的全貌，再看 diff |
| 新加入项目 | 快速建立代码心智模型，知道什么在哪 |
| 重构前的侦察 | 6-优化 之前先走 2-分析 了解全貌 |
| 排查问题前定位 | 7-调试 之前先用 2-分析 找到可疑模块 |

**不适用**：你只想知道一个函数是干什么的（直接读代码更快），或者你已经对这个模块很熟悉。

## 输出四部分

```
1. 模块地图 ── 涉及哪些文件/模块，各自职责
2. 数据流   ── 谁调谁、输入输出是什么
3. 关键入口 ── 从哪里开始读最有效率
4. 架构位置 ── 这片代码在整个项目中的上下游
```

## 案例演示

### 案例 1：看懂一个复杂文件

```
用户：/2-分析 这个 views.py 我完全看不懂，帮我分析一下

Claude：luohe，我来看看。

       这是订单模块的视图层，整体结构如下：

       ┌── 模块地图 ──────────────────────┐
       │                                  │
       │ User (HTTP Request)              │
       │   │                              │
       │   ▼                              │
       │ OrderViewSet (views.py:15)       │
       │   ├── list()     — 订单列表      │
       │   │   └── OrderSerializer        │
       │   │       └── OrderRepository    │
       │   │                              │
       │   ├── create()   — 创建订单      │
       │   │   └── validate()             │
       │   │       └── PaymentService     │
       │   │           └── .process()     │
       │   │                              │
       │   ├── retrieve() — 订单详情      │
       │   │   └── OrderSerializer        │
       │   │                              │
       │   └── cancel()   — 取消订单      │
       │       └── CancelService          │
       │           └── RefundService      │
       │                                  │
       └──────────────────────────────────┘

       ┌── 数据流 ──────────────────────────┐
       │                                  │
       │ request → 认证中间件              │
       │   → ViewSet.dispatch()           │
       │   → ViewSet.create()             │
       │   → OrderSerializer.validate()   │
       │   → OrderService.create_order()  │
       │   → OrderRepository.save() → DB  │
       │   → PaymentService.process()     │
       │   → Response (JSON)              │
       │                                  │
       └──────────────────────────────────┘

       上游：API 网关 / 认证中间件
       下游：OrderService、PaymentService、OrderRepository

       📖 推荐阅读顺序：
       1. views.py:42 — OrderViewSet.create()（创建订单是核心流程）
       2. serializers.py:18 — OrderSerializer（理解数据结构）
       3. services/order.py:30 — OrderService.create_order()（业务逻辑）
```

### 案例 2：接手一个新项目

```
用户：/2-分析 我刚 clone 了这个项目，帮我快速理解整个代码结构

Claude：luohe，帮你扫一遍。

       ┌── 项目结构 ───────────────────────┐
       │                                  │
       │ payment-service/                 │
       │ ├── src/                         │
       │ │   ├── api/          — HTTP 层  │
       │ │   │   ├── routes/   — 路由注册 │
       │ │   │   └── middleware/ — 认证/日志│
       │ │   ├── services/     — 业务逻辑 │
       │ │   │   ├── payment.py   — ★核心 │
       │ │   │   ├── refund.py    — 退款  │
       │ │   │   └── reconcile.py — 对账  │
       │ │   ├── models/        — 数据模型 │
       │ │   ├── repository/    — 数据库层 │
       │ │   └── config.py      — 配置    │
       │ └── tests/                        │
       │                                  │
       └──────────────────────────────────┘

       ┌── 数据流（主链路） ────────────────┐
       │                                  │
       │ 外部请求 → API Gateway           │
       │   → routes/payment.py            │
       │   → middleware/auth.py (JWT验证) │
       │   → services/payment.py          │
       │       ├── 查费率 (config.py)     │
       │       ├── 调第三方 (gateway.py)  │
       │       └── 写库 (repository/)     │
       │   → 返回 JSON                    │
       │                                  │
       └──────────────────────────────────┘

       📖 上手路径（30 分钟了解全貌）：
       1. README.md + config.py — 了解项目是做什么的（5min）
       2. api/routes/payment.py — 看入口，理解有哪些接口（10min）
       3. services/payment.py — 看核心业务逻辑（10min）
       4. models/ — 看数据结构（5min）

       这个项目最复杂的部分是 services/payment.py 的 process()，
       建议从这里开始深度阅读。
```

### 案例 3：排查前定位

```
用户：/2-分析 用户反馈订单支付后状态没更新，帮我定位可能是哪里的问题

Claude：luohe，先看涉及"支付→状态更新"这条链路的所有模块。

       支付完成 → 状态更新 的数据流：

       第三方回调 → webhook/payment.py:callback()
         → services/payment.py:confirm_payment()    ← 验证签名 + 更新状态
            → repository/order.py:update_status()    ← 写数据库
            → services/notification.py:notify()      ← 通知用户

       可能出问题的点（按概率排序）：
       1. webhook 没有被调 — 检查第三方平台的回调日志
       2. confirm_payment() 抛了异常 — 检查 error 日志，特别是签名验证
       3. update_status() 条件不匹配 — 状态机限制了转换路径

       建议从 services/payment.py:confirm_payment() 开始排查。
       如果需要深入调试，可以走 7-调试。
```

## 注意事项

- 这个技能是**纯分析**，不修改代码，不提出修改建议
- 全程使用**项目领域术语**描述，不用泛称（说"OrderViewSet"不说"那个视图类"）
- 如果代码量很大，输出会聚焦在关键路径上，不会展开所有细节
- 技能标注了 `disable-model-invocation: true`，意味着它不通过 Skill 工具调用，而是直接作为提示词嵌入

## 相关技能

- [[skill-6-优化 使用指南]] — 分析后发现问题，进入重构
- [[skill-7-调试 使用指南]] — 分析定位后，进入结构化排查
- [[skill-1-规划 使用指南]] — 分析现有代码后，规划新功能
