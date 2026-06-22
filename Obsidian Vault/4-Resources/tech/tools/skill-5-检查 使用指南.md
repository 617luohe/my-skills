---
title: "skill-5-检查 使用指南"
aliases: ["检查技能指南", "代码审查指南"]
tags:
  - type/resource
  - domain/tech/tools
  - topic/skills-guide
created: 2026-06-18
status: published
confidence: sprout
source: "https://github.com/617luohe/my-skills"
skill: "5-检查"
---

# 5-检查 — 代码审查与验收

> 一句话：双轴并行审查（规范 + 需求符合度），外加交互式 Bug 报告并自动提交 GitHub Issue。

## 什么时候用

| 场景 | 说明 |
|------|------|
| 提 PR 前自审 | 自己检查一遍，减少 reviewer 的负担 |
| 审查队友代码 | 系统性地审查，不遗漏 |
| 合并前把关 | 确保代码符合团队规范 |
| 发现 Bug 想报 issue | 你口述问题，Claude 探索代码并自动建 issue |
| 系统性 QA | 对某个模块做全面验收 |

## 两个模式

```
进入时选择
  │
  ├── 模式 A — 代码审查
  │   双轴并行：Standards 审查 + Spec 审查
  │
  └── 模式 B — Bug 报告
      交互式 QA → 探索代码 → 创建 GitHub Issue
```

## 案例演示

### 案例 1：模式 A——代码审查

```
用户：/5-检查 帮我审查 payment-service 分支

Claude：luohe，走模式 A（代码审查）。

       审查基点：当前分支 vs main。先定位需求和规范...

       [定位需求] commit 消息中引用了 issue #42 "退款原路返回"
       [定位规范] 找到 CLAUDE.md + pyproject.toml（Ruff 120列 + 单引号）

       启动双轴并行审查...

       ═══════════════════════════════════
       ## Standards 审查（规范）
       ═══════════════════════════════════

       ❌ payment/processor.py:45
          processPayment() → 应改为 process_payment()（snake_case）

       ❌ payment/views.py:102
          except Exception: 过宽，应捕获具体的 PaymentError

       ⚠️  payment/utils.py:23,45,67
          3 个函数缺少类型注解

       ⚠️  payment/models.py:12
          import os, sys, json 应分开写（import 组织）

       ─────────────────────────────
       Standards 小计：2 个错误 + 2 个警告
       ─────────────────────────────

       ═══════════════════════════════════
       ## Spec 审查（需求符合度）
       ═══════════════════════════════════

       ❌ 缺失需求：Issue #42 §"退款原路返回"
          refund() 方法调用了支付网关但未传 original_transaction_id

       ❌ 范围蔓延：payment_logger.py
          需求中没要求，代码中出现了——建议确认是否遗漏

       ⚠️  实现问题：payment/processor.py:56
          超时未处理——需求中说"支付超时需要重试"

       ─────────────────────────────
       Spec 小计：2 个错误 + 1 个警告
       ─────────────────────────────

       ── 总结 ──
       Standards: 2 errors, 2 warnings — 最严重：processPayment 命名
       Spec:      2 errors, 1 warning  — 最严重：退款未传原交易号
```

### 案例 2：模式 B——Bug 报告

```
用户：/5-检查 发现一个 Bug：取消订单后，优惠券没有退回

Claude：luohe，走模式 B（Bug 报告）。先澄清一下。

       1. 是所有取消订单都不退券，还是只有部分情况？
       2. 已支付取消和未支付取消，退券逻辑一样吗？

用户：所有取消都不退。应该都要退。

Claude：了解了。让我探索一下代码确认根因。

       [后台探索…]

       找到了：src/services/cancel.py:process()
       取消逻辑只做了三件事：
       1. 更新订单状态
       2. 触发退款（如果已付）
       3. 释放库存
       → 没有退优惠券的步骤

       而 src/services/coupon.py 中有 return_coupon() 方法但没有被调用。

       这是单一根因导致的问题，一个 issue 就够了。

       创建 GitHub Issue...

       $ gh issue create \
         --title "取消订单后优惠券未退回" \
         --body "$(cat <<'EOF'
       ## What happened
       取消订单后，已使用的优惠券不会退回到用户账户。

       ## What I expected
       取消订单时优惠券应恢复到可用状态，用户可在新订单中继续使用。

       ## Steps to reproduce
       1. 使用优惠券下一笔订单
       2. 进入订单详情，点击"取消订单"
       3. 进入优惠券页面
       4. 该优惠券仍显示"已使用"，而非"可用"
       EOF
       )"

       ✅ Issue #56 已创建。
       https://github.com/your-org/payment-service/issues/56

       继续下一个，还是完成了？
```

### 案例 3：模式 B——多 Bug 拆分

```
用户：/5-检查 支付页面有三个问题：
       1. 微信支付按钮点不了
       2. 金额显示的是美元符号 $ 而不是 ¥
       3. 支付成功后跳转到 404 页面

Claude：luohe，三个问题看起来是彼此独立的。

       1. 微信支付按钮 — 前端组件问题
       2. 货币符号 — 前端/后端国际化问题
       3. 支付成功跳转 — 后端重定向 URL 问题

       三者没有共同根因，建议拆成 3 个独立 issue，不同人可并行修复。

       先提交哪个？微信支付按钮（阻塞支付流程）？

用户：嗯，先报微信支付的

Claude：$ gh issue create --title "微信支付按钮点击无响应" ...
       ✅ Issue #57 已创建。

       第二个——金额显示 $ 而非 ¥？

用户：对

Claude：[探索代码…]
       发现 currency_display 函数中 hardcode 了 $ 符号。
       $ gh issue create --title "支付页面货币符号显示 $ 而非 ¥" ...
       ✅ Issue #58 已创建。

       第三个——跳转 404？

用户：对

Claude：[探索代码…]
       路由中 payment_success 拼写成了 payment_sucess。
       $ gh issue create --title "支付成功后跳转到 404 页面" ...
       ✅ Issue #59 已创建。

       三个 issue 已提交：
       - #57 微信支付按钮无响应（阻塞支付流程，建议先修）
       - #58 货币符号显示错误
       - #59 支付成功跳转 404（拼写错误，快速修复）

       继续下一个，还是完成了？
```

## Issue 规则

| ✅ 要做的 | ❌ 不要做的 |
|----------|-----------|
| 使用项目领域术语 | 不包含文件路径和行号（会过期） |
| 描述行为而非代码 | 不写 "在 payment.py:45 处…" |
| 复现步骤必须可执行 | 不写模糊的 "有时会出错" |
| 30 秒内能读完 | 不写长篇背景介绍 |

## 注意事项

- 模式 A 的双轴审查是**并行子代理**——两个审查互相独立，不会交叉污染
- 模式 B 中，拆分还是合并 issue 取决于根因是否相同
- 依赖关系的 issue 先建阻塞项，后建被阻塞项

## 相关技能

- [[skill-4-开发 使用指南]] — 开发完成后进入审查
- [[skill-6-优化 使用指南]] — 审查发现架构问题，进入优化
- [[skill-7-调试 使用指南]] — 审查发现 Bug，进入调试
