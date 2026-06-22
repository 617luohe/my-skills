---
title: "skill-7-调试 使用指南"
aliases: ["调试技能指南", "结构化调试指南"]
tags:
  - type/resource
  - domain/tech/tools
  - topic/skills-guide
created: 2026-06-18
status: published
confidence: sprout
source: "https://github.com/617luohe/my-skills"
skill: "7-调试"
---

# 7-调试 — 结构化调试

> 一句话：六阶段系统化排查难复现的 Bug 和性能问题。最核心的是阶段 1——构建快速反馈回路。

## 什么时候用

| 场景 | 说明 |
|------|------|
| 间歇性 Bug | "偶尔返回 500，不知道什么时候触发" |
| 性能突然下降 | "上周还能用，这周慢了 10 倍" |
| 难复现的问题 | "只有生产环境出现，本地跑就正常" |
| 排查根因而非修复 | 不只是"打个补丁"，要找到真正的根因 |

**不适用**：一眼就能看出来的 bug（typo、明显逻辑错误），或者你需要的是修复而非诊断。

## 六阶段流程

```
阶段 1 ★★★ 构建反馈回路 ──→ 快速 pass/fail 信号（最重要的阶段）
阶段 2     复现           ──→ 确认回路产生的失败模式与描述一致
阶段 3     假设           ──→ 列出 3-5 条可证伪假设（不能只有 1 个）
阶段 4     工具验证       ──→ 一次改一个变量，验证每条假设
阶段 5     修复+回归      ──→ 失败测试 → 修复 → 回归测试
阶段 6     清理           ──→ 确认不复现、回归通过、调试标签清除
```

## 反馈回路优先级

| 优先级 | 方法 | Python 实现 |
|--------|------|------------|
| 1 | 失败测试 | `pytest` 写一个能用 assert 抓到症状的测试 |
| 2 | HTTP 脚本 | `curl` / `httpx` 循环调用，diff 响应 |
| 3 | CLI 复现 | 用 fixture 输入调用脚本，diff stdout |
| 4 | 回放捕获 | 保存真实请求到文件，隔离重放 |
| 5 | 一次性 harness | 最小子集 mock 依赖，单函数调用触发 bug |
| 6 | 模糊循环 | 1000 个随机输入找失败模式 |
| 7 | 二分 harness | `git bisect run` 脚本 |
| 8 | 差异对比 | 相同输入在新旧版本下的输出差异 |

## 案例演示

### 案例 1：间歇性 500（完整 6 阶段）

```
用户：/7-调试 订单支付接口偶尔返回 500，帮我排查

Claude：luohe。

       === 阶段 1：构建反馈回路 ===

       需要一个快速、确定性的信号。从优先级 2 开始：HTTP 脚本。

       while true; do
         curl -s -o /dev/null -w "%{http_code}\n" \
           -X POST http://localhost:8000/api/payments \
           -H "Content-Type: application/json" \
           -d '{"order_id":"test-001","amount":100}'
         sleep 0.1
       done | sort | uniq -c

       运行 200 次：
       189 200
        11 500    ← 约 5.5% 失败率

       回路已建立。5.5% 的复现率可以调试。

       === 阶段 2：复现 ===

       再跑 3 轮各 200 次：
       Round 1: 8/200  (4.0%)
       Round 2: 13/200 (6.5%)
       Round 3: 10/200 (5.0%)
       平均：5.2% — 复现确认 ✅

       === 阶段 3：假设 ===

       3 条可证伪假设（按概率排序）：

       1. 数据库连接池耗尽 → 增大 pool_size，失败率应下降
       2. 第三方支付网关超时 → mock 网关返回固定响应，失败率应归零
       3. Redis 缓存穿透 → 检查缓存命中率，miss 率应与失败率正相关

       你瞬间排一下优先级？

用户：按这个顺序来

Claude：=== 阶段 4：工具验证 ===

       验证假设 1：数据库连接池耗尽？

       [DEBUG-a4f2] 当前配置：pool_size=5, max_overflow=10
       改为：pool_size=20, max_overflow=30
       
       重新跑 200 次：成功 200 次，失败 0 次 ✅

       失败率从 5.2% → 0%。
       假设 1 被证实：连接池太小是根因。

       不需要验证假设 2 和 3 了——假设 1 已经解释了全部失败。

       === 阶段 5：修复 + 回归 ===

       失败测试：
       def test_payment_concurrent_under_load():
           """回归: 并发 50 笔支付请求不应因连接池耗尽而失败"""
           service = PaymentService(pool_size=20)
           with ThreadPoolExecutor(max_workers=50) as executor:
               futures = [executor.submit(service.process, f"order-{i}") 
                         for i in range(50)]
               results = [f.result() for f in futures]
           failures = [r for r in results if r.status != "completed"]
           assert len(failures) == 0, f"{len(failures)} 笔失败"

       修复前：FAILED — 3 笔失败
       修复后：PASSED ✅

       原始回路确认：200 次全部 200 ✅

       === 阶段 6：清理 ===

       ✅ 原始场景不再复现
       ✅ 回归测试通过
       ✅ 调试标签已清除（无 [DEBUG- 残留）
       
       什么能防止这个 Bug？
       → 将连接池配置从硬编码改为基于并发量的动态计算。
       如果需要，可以进 6-优化 讨论。
```

### 案例 2：无回路时的处理

```
用户：/7-调试 生产环境偶尔出现 "Order not found" 错误，但我查了数据库明明有

Claude：luohe，先构建回路。

       本地能复现吗？

用户：不能，只有生产环境出现

Claude：需要捕获生产数据。试试优先级 4（回放捕获）。

       建议：在生产环境加临时日志，捕获出错的请求参数：
       
       @app.exception_handler(OrderNotFoundError)
       async def capture(e, request):
           logger.error(f"OrderNotFound: {request.body}", 
                        extra={"request_body": await request.body()})
       
       部署后等一天，把捕获到的请求参数给我，我们在本地回放。

用户：这是捕获到的
     {"order_id": "ORD-2026-00123", "user_id": "U-456"}

Claude：在本地用这个数据回放：

       import json
       data = json.loads('{"order_id": "ORD-2026-00123", "user_id": "U-456"}')
       result = OrderService().get_order(data["order_id"])
       → Order found ✅（本地能找到）
       
       再查生产数据库：
       SELECT * FROM orders WHERE id = 'ORD-2026-00123';
       → 确实存在
       
       那问题不在数据库。查一下请求的到达时间…
       发现错误时间集中在每天 03:00-03:05
       
       → 怀疑：数据库备份期间的短暂不可用？
       
       验证：查数据库备份计划——确实是每天 03:00，备份期间
       read replica 有 30 秒的切换窗口。
       
       根因确认：备份切换窗口内的查询路由到旧 replica，返回空结果。
       
       修复：重试逻辑 + 备份窗口期间的只读查询走主库。
```

### 案例 3：假设过多的问题

```
用户：/7-调试 这个函数返回的结果有时候不对

Claude：luohe，先看代码。

       def calculate_discount(price, user_type, coupon_code=None):
           ...

       构建回路：
       assert calculate_discount(100, "vip", "SAVE10") == 80
       

       先列假设。不要只列一条——

       ❌ 只列一条："可能是 coupon_code 解析有问题"
          → 锚定偏见，你会下意识筛选"支持这条假设"的证据

       ✅ 列 3-5 条，每条必须可证伪：
       1. user_type 匹配用了 == 而非 in → 部分用户类型未命中
          验证：传入 "vip" 看返回值
       2. coupon_code 的折扣计算顺序问题 → VIP 折扣覆盖了优惠券
          验证：对比 VIP only vs 优惠券 only 的结果
       3. price 类型是 str 而非 int → 比较时行为异常
          验证：type(price) 检查
       
       从假设 1 开始验证。
```

## Python 调试工具速查

| 场景 | 工具 |
|------|------|
| 快速插入断点 | `breakpoint()` |
| 调用追踪 | `python -m trace --trace script.py` |
| 性能分析 | `python -m cProfile -o output.prof script.py` |
| 火焰图 | `py-spy record -o flame.svg --pid <pid>` |
| 内存分析 | `tracemalloc`、`memory-profiler` |
| 模糊测试 | `pytest --randomly`、`hypothesis` |

## 注意事项

- **没有回路，不准进假设阶段**——盯着代码猜的命中率太低
- **一次只改一个变量**——同时改两个因素，你不知道哪个起效
- 假设必须**可证伪**——"如果 X 是原因，那么改 Y 会消除 bug"
- 非确定性 bug 的目标不是完美复现，而是**提高复现率**到可调试水平（≥5%）
- 调试日志打唯一标签 `[DEBUG-x]`，最后 grep 确认全部清除

## 相关技能

- [[skill-4-开发 使用指南]] — 阶段 5 修复时进去 TDD 实现
- [[skill-5-检查 使用指南]] — 修复后审查
- [[skill-6-优化 使用指南]] — 根因涉及架构问题时进去重构
- [[skill-2-分析 使用指南]] — 排查前先理解模块结构
