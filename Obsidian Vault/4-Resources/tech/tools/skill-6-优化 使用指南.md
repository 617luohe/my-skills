---
title: "skill-6-优化 使用指南"
aliases: ["优化技能指南", "重构指南"]
tags:
  - type/resource
  - domain/tech/tools
  - topic/skills-guide
created: 2026-06-18
status: published
confidence: sprout
source: "https://github.com/617luohe/my-skills"
skill: "6-优化"
---

# 6-优化 — 重构与架构改进

> 一句话：发现架构摩擦点，制定渐进式重构方案。两个模式：A 发现问题、B 解决问题。

## 什么时候用

| 场景 | 说明 |
|------|------|
| 模块越来越臃肿 | 一个文件 500+ 行，单个函数 100+ 行 |
| 测试越来越难写 | mock 一大堆才能测一个简单逻辑 → 接缝放错了 |
| 改一个地方要改 N 处 | 修改一处逻辑，散落到 5 个文件都要改 |
| 接手遗留代码 | 先用 2-分析 理解，再用 6-优化 改进 |
| 部署频率下降 | 改一行代码要测一天 → 删除测试没过 |

**不适用**：只改一个变量名（直接用 4-开发 更轻量），或者代码本身没问题只是风格偏好。

## 两个模式

```
进入时选择
  │
  ├── 模式 A — 架构分析（发现问题）
  │   探索 → 展示候选问题 → 追问循环
  │
  └── 模式 B — 重构计划（解决问题）
      听取描述 → 检查测试覆盖 → 探讨选项 → 敲定范围 → 拆解提交
```

## 核心概念速查

| 术语 | 含义 | 例 |
|------|------|-----|
| **深度** | 小接口封装大逻辑 = 深模块（好） | `process_payment()` 内部处理了验签/风控/记账/通知 |
| **浅模块** | 接口几乎和实现一样复杂（坏） | `set_name()` 就是 `self.name = name` |
| **接缝** | 不修改原处就能改变行为的接口位置 | 依赖注入的 Service 参数 |
| **删除测试** | 删掉这个模块 → 复杂度消失还是散落？ | 删一个工具函数 → 散落 → 应该保留；删一个浅包装 → 消失 → 应该删 |

## 案例演示

### 案例 1：模式 A——架构分析

```
用户：/6-优化 payment_service.py 800 行了，帮我看看有什么问题

Claude：luohe，走模式 A（架构分析）。

       === 探索代码 ===

       payment_service.py (803 行) 概览：
       
       class PaymentService:
           ├── process_payment()         120行
           ├── refund_order()             95行
           ├── reconcile_transactions()  140行  ← 对账逻辑
           ├── send_notification()        45行  ← 发通知
           ├── validate_payment()         60行
           ├── calculate_fee()            50行
           ├── log_transaction()          40行
           ├── _format_email()            30行  ← 邮件模板
           ├── _format_sms()              25行  ← 短信模板
           ├── _retry_gateway_call()      55行
           └── ...                        6个辅助方法

       === 删除测试 ===

       假设删掉 PaymentService——复杂度不会消失，会散落到所有调用方。
       所以 PaymentService 本身不应该删 → 应该拆分。

       但 `_format_email()` → 删掉它，通知格式化的复杂度从哪里来？
       答案：也应该存在，但不是存在 PaymentService 里——它不该管邮件格式。

       === 展示候选 ===

       候选 1：支付处理 + 退款 + 对账 + 通知 四个关注点耦合在同一类
       问题：改对账逻辑要碰 PaymentService，改通知模板也要碰
       方案：按职责拆成 4 个独立 Service
       收益：各自独立测试、独立部署、独立修改

       候选 2：`_format_email()` 和 `_format_sms()` 在支付服务里
       问题：支付服务不应该知道邮件模板——这是表示层的事
       方案：提取到 NotificationFormatter
       收益：更换邮件模板不需要动支付核心

       候选 3：`_retry_gateway_call()` 混在业务逻辑中
       问题：重试逻辑和支付逻辑缠绕在一起
       方案：提取为独立的重试装饰器或中间件
       收益：其他需要重试的模块复用同一逻辑

       你关注哪个？
```

### 案例 2：模式 B——重构计划

```
用户：/6-优化 帮我制定重构方案，目标是把 PaymentService 拆开

Claude：luohe，走模式 B（重构计划）。

       先检查测试覆盖...

       现有测试：tests/test_payment_service.py (12 个测试)
       覆盖了 process_payment、refund_order、reconcile。
       
       好消息：有测试。坏消息：都是集成测试（连测试数据库）。
       重构过程中需要保持这些测试全绿。
       
       === 探讨选项 ===

       方案 A：一次拆分
       一次提交拆成 4 个 Service → 改动大，风险高

       方案 B：渐进拆分（推荐）
       5 步，每步独立可提交，每步保持所有测试全绿

       选方案 B。

       === 敲定范围 ===
       要改的：PaymentService 拆分为 4 个独立 Service
       不改的：外部接口不变（调用方无感知），数据库不变

       === 拆解为极小提交 ===

       ## Problem Statement
       PaymentService 承载了支付、退款、对账、通知 4 个关注点，803 行难以维护。

       ## Solution
       分 5 步渐进拆分，每步独立可提交可回滚。

       ## Commits
       1. [提取 PaymentStatus 枚举]
          把散落在方法中的状态字符串 "pending"/"paid"/"failed"
          提取为 PaymentStatus 枚举 → 不影响逻辑，纯类型安全
          结果：可工作 ✅

       2. [提取 PaymentProcessor]
          将 process_payment + validate_payment + calculate_fee
          移入 PaymentProcessor → 原 PaymentService 委托调用
          结果：可工作 ✅，外部接口不变

       3. [提取 RefundProcessor]
          将 refund_order + 退款相关验证
          移入 RefundProcessor → 委托调用
          结果：可工作 ✅

       4. [提取 ReconciliationService]
          将 reconcile_transactions + log_transaction
          移入 ReconciliationService → 委托调用
          结果：可工作 ✅

       5. [提取 NotificationService]
          将 send_notification + _format_email/_format_sms
          移入 NotificationService → 委托调用
          结果：可工作 ✅，PaymentService 从 803 行 → 约 50 行

       ## Testing Decisions
       - 每一步前后都跑 `pytest tests/test_payment_service.py` — 12 个测试必须全绿
       - 新增 4 个 Service 的单元测试（mock 依赖，不连数据库）
       - 参考 tests/test_order_service.py 的 mock 风格

       ## Out of Scope
       - 不改变外部 API 签名
       - 不改数据库 schema
       - 不优化性能（那是另一个 PR 的事）
```

### 案例 3：快速架构诊断

```
用户：/6-优化 我总觉得代码越来越难改，但说不出具体问题在哪

Claude：luohe，走模式 A，帮你做一次架构扫描。

       先看几个信号：

       信号 1️⃣：修改成本
       你最近一次加功能，改了几个文件？
       
用户：加一个"导出 CSV"，改了 7 个文件

Claude：这很说明问题。导出一个 CSV 应该只碰：
       - 一个路由注册
       - 一个导出 Service
       - 可能加一个 Serializer
       3 个文件。你改了 7 个→ 耦合超出预期。

       信号 2️⃣：浅模块普查
       我扫描一下… 发现 3 个可疑的"浅模块"：
       
       - user_formatter.py:12 — title_case(name) 只有一行
       - price_utils.py:8   — add_tax(price) 就是 price * 1.13
       - date_utils.py:5    — today_str() 就是 str(date.today())
       
       这些都是接口和实现一样复杂的典型。删掉它们，复杂度不会散落——
       调用方直接写 `price * 1.13` 比 `add_tax(price)` 更清晰。

       信号 3️⃣：删除测试
       逐个过：删掉 `user_formatter.py` → 3 个调用方只需改一行 → 删。
              删掉 `price_utils.py` → 5 个调用方改一行 → 删。
              删掉 `date_utils.py` → 12 个调用方 → 这个可以考虑保留。
       
       初步诊断：你的代码没有重大架构问题，但有积水——多个浅模块增加了间接层
       却不提供抽象价值。建议：删掉 user_formatter 和 price_utils，保留 date_utils。
```

## 注意事项

- 重构计划的每步提交都必须**独立可工作**——任何一步停下来都不会破坏系统
- 模式 B 会先**检查测试覆盖**——如果覆盖不够，会主动提出来
- **不要一边重构一边加功能**——重构和功能开发是两个独立的 PR
- 模式 A 的 ADR 冲突处理：如果候选方案与已有 ADR 矛盾，只有"值得重新审视"时才提出来

## 相关技能

- [[skill-2-分析 使用指南]] — 重构前先理解代码结构
- [[skill-4-开发 使用指南]] — 重构计划中的每步提交用 TDD 实现
- [[skill-5-检查 使用指南]] — 重构完成后代码审查
