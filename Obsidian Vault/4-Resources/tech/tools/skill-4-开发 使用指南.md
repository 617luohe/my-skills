---
title: "skill-4-开发 使用指南"
aliases: ["开发技能指南", "TDD开发指南"]
tags:
  - type/resource
  - domain/tech/tools
  - topic/skills-guide
created: 2026-06-18
status: published
confidence: sprout
source: "https://github.com/617luohe/my-skills"
skill: "4-开发"
---

# 4-开发 — TDD 编码实现

> 一句话：pytest 驱动的红-绿-重构循环，四条编程准则贯穿全程。测试验证行为而非实现细节。

## 什么时候用

| 场景 | 说明 |
|------|------|
| 实现新功能 | 接口已确定（经 1-规划），开始正式编码 |
| 修复 Bug | 先写测试重现 Bug，再写修复代码 |
| 需要高可靠性 | 金融计算、支付流程、核心业务逻辑 |
| 重构后补测试 | 6-优化 提取模块后，补上行为测试 |

**不适用**：一次性脚本、探索性代码（用 3-原型），或者改一个配置常量。

## 四条编程准则

```
准则 1 — 先想后写
  编码前说出假设，列出多种解读，有更简单的方案就说出来
  ❌ "我猜要加个 try-catch"  ✅ "这里可能抛 TimeoutError，两种处理方式：重试 or 降级"

准则 2 — 简单第一
  最少代码解决问题。不需要的功能不加，只用一次的逻辑不抽象
  ❌ 写了一个工厂模式处理两个分支  ✅ if-else 就够了

准则 3 — 手术刀式改动
  只碰必须碰的，不改没坏的东西，匹配现有风格
  ❌ "顺便把旁边的变量名也改了"  ✅ 只动这个函数的实现

准则 4 — 目标驱动
  模糊任务转可验证目标，多步骤先列计划再动手
  ❌ "优化一下代码"  ✅ "将这个函数的循环从 O(n²) 降到 O(n)"
```

## TDD 流程

```
规划 ──→ 示踪弹 ──→ 递增循环 ──→ 重构

规划：确认接口，列出测试行为，等你批准
示踪弹：一个测试 + 最少代码通过，证明路径可行
递增循环：RED（写测试确认失败）→ GREEN（最少代码通过），一次一个
重构：全部变绿后提取重复，绝不在 RED 时重构
```

## 案例演示

### 案例 1：标准 TDD 流程——实现计算器

```
用户：/4-开发 用 TDD 实现一个计算器 add 方法

Claude：luohe，先确认接口。

       接口设计：
       def add(a: int, b: int) -> int

       测试行为列表：
       1. 两个正数相加 → 返回和
       2. 正数加零 → 返回原数
       3. 两个负数相加 → 返回负数和
       4. 大数相加 → 不溢出

       先从行为 1 开始。可以吗？

用户：可以

Claude：[示踪弹]
       
       RED — tests/test_calculator.py：
       def test_add_two_positives():
           assert add(2, 3) == 5
       
       运行：FAILED — NameError: name 'add' is not defined ✅

       GREEN — src/calculator/main.py：
       def add(a: int, b: int) -> int:
           return a + b
       
       运行：PASSED ✅

       示踪弹通过，进入递增循环。

       ---

       RED — 行为 2（正数加零）：
       def test_add_with_zero():
           assert add(5, 0) == 5
       
       运行：PASSED ✅（已有实现直接通过，无需写新代码）

       ---

       RED — 行为 3（负数相加）：
       def test_add_negative_numbers():
           assert add(-2, -3) == -5
       
       运行：PASSED ✅（Python 原生支持）

       ---

       RED — 行为 4（大数）：
       def test_add_large_numbers():
           assert add(10**18, 10**18) == 2 * 10**18
       
       运行：PASSED ✅（Python int 自动处理）

       全部变绿，检查是否需要重构。
       当前实现只有一行 return a + b，不需要重构。

       4 个测试通过，覆盖了所有行为。还要加其他用例吗？
```

### 案例 2：Bug 修复（先写回归测试）

```
用户：/4-开发 用户反馈：订单总金额为 0 时，支付接口抛 500，帮我修

Claude：luohe，先写测试重现 Bug。

       读取现有代码… 发现 payment_service.py:process() 中：
       
       def process(self, order_id: str) -> PaymentResult:
           order = self.repo.get(order_id)
           fee = order.amount * self.rate  # ← 这里没问题？
           return self.gateway.charge(order, fee)

       看网关实现… 找到了：
       
       def charge(self, order, amount):
           if amount <= 0:  # 第三方要求金额 > 0
               raise ValueError("Invalid amount")
       
       问题清楚：amount=0 时网关抛异常，但 payment_service 没有处理这个边界。

       RED — 回归测试：
       def test_process_zero_amount_order():
           """回归: 金额为0的订单应降级处理而非抛500"""
           service = PaymentService(repo=MockRepo(amount=0))
           result = service.process("order-1")
           assert result.status == "completed"
           assert result.amount == 0

       运行：FAILED — ValueError: Invalid amount ✅（Bug 已重现）

       GREEN — 修复：
       def process(self, order_id: str) -> PaymentResult:
           order = self.repo.get(order_id)
           if order.amount <= 0:
               return PaymentResult(status="completed", amount=0)
           fee = order.amount * self.rate
           return self.gateway.charge(order, fee)

       运行：PASSED ✅

       同时确认原有的正常金额测试仍然通过 ✅

       无需重构。修复完成。
```

### 案例 3：垂直切片 vs 水平切片

```
用户：/4-开发 我想实现一个 UserService，有 create、update、delete、find_by_id、find_all

Claude：luohe，5 个方法。

       错误做法（水平切片）：
       RED: 5 个测试一起写
       GREEN: 5 个方法一起实现
       → 中间可能迷失方向

       正确做法（垂直切片）：
       RED→GREEN: test_create → create()
       RED→GREEN: test_find_by_id → find_by_id()
       RED→GREEN: test_update    → update()
       RED→GREEN: test_delete    → delete()
       RED→GREEN: test_find_all  → find_all()
       → 每次都只有一个小目标

       先从 create 开始？

用户：好

Claude：RED — test_create_user：
       def test_create_user():
           service = UserService(MockRepo())
           user = service.create(name="张三", email="zhang@test.com")
           assert user.name == "张三"
           assert user.id is not None
       
       FAILED ✅
       
       GREEN — create() 实现：
       def create(self, name, email):
           user = User(id=uuid4(), name=name, email=email)
           self.repo.save(user)
           return user
       
       PASSED ✅
       
       继续 test_find_by_id？
```

## 每周期自检清单

- [ ] 测试描述行为，不是实现
- [ ] 只用公共接口
- [ ] 重构后测试不变
- [ ] 代码量刚好通过当前测试
- [ ] 没有投机功能（"以后可能需要"的不写）

## 注意事项

- **绝不在 RED 时重构**——先变绿，再优化
- **测试先行**——先看到测试失败（证明测试在检测问题），再写实现
- **接口确认后才开始**——如果你的函数签名还不确定，先回 1-规划 或 3-原型
- 垂直切片：一次只做一个小目标（一个测试 + 一个实现），不要批量

## 相关技能

- [[skill-1-规划 使用指南]] — 接口设计完成后进开发
- [[skill-3-原型 使用指南]] — 验证完成后进开发
- [[skill-5-检查 使用指南]] — 开发完成后代码审查
- [[skill-7-调试 使用指南]] — Bug 修复后走回归测试
