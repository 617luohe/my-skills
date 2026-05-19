---
name: 6-调试
description: Disciplined diagnosis loop for bugs and performance issues — reproduce → hypothesise → instrument → fix → regression test. Use when encountering a hard-to-reproduce bug or performance regression.
---

# 6-调试 — 结构化调试

六阶段调试流程，适用于难复现的 bug 和性能问题。

## 流程

### 阶段 1 — 构建反馈回路

这是核心技能。一个快速、确定性的 pass/fail 信号是找到根因的前提。

按顺序尝试：
1. **失败测试** — 在合适的接口层面写测试
2. **复现脚本** — 提取最少执行路径
3. **二分脚本** — 如果在两次 commit 之间出现，写 `git bisect run`
4. **差异对比** — 相同输入在旧版 vs 新版上的输出差异

**优化回路**：更快？信号更准？更确定？

**Python 工具**：

| 场景 | 工具 |
|---|---|
| 快速插入断点 | `breakpoint()` |
| 调用追踪 | `python -m trace --trace script.py` |
| 性能分析 | `python -m cProfile -o output.prof script.py` |
| 火焰图 | `py-spy record -o flame.svg --pid <pid>` |
| 内存分析 | `tracemalloc`、`memory-profiler` |

**无法构建回路时** — 停下来，列出你尝试过的方法，请求访问权限或日志。

---

### 阶段 2 — 复现

跑回路，确认 bug 确实出现。
- [ ] 回路产生的失败模式与描述一致
- [ ] 多次运行可复现

---

### 阶段 3 — 假设

先列 **3-5 条假设**再开始验证。不能只有一个（锚定偏见）。

每条必须可证伪：**"如果 X 是原因，那么改 Y 会消除 bug"**

把排行列表展示给你再验证。你可能瞬间重排优先级。

---

### 阶段 4 — 工具验证

每个探测手段对应阶段 3 的一个具体预测。**一次只改一个变量。**

优先用调试器/REPL，其次用精准日志。不要"全部打 log 然后 grep"。

给每个调试日志打唯一标签如 `[DEBUG-a4f2]`，最后 grep 清除。

---

### 阶段 5 — 修复 + 回归测试

1. 把最小化复现变成失败测试
2. 确认失败
3. 实施修复
4. 确认通过
5. 重新跑原始场景确认修复

```python
# test_regression_<issue_number>.py
def test_payment_retry_on_timeout():
    """回归测试: 支付超时后应自动重试一次"""
    service = PaymentService(timeout=0.01)
    result = service.charge(amount=100)
    assert result.status == "completed"
    assert service.retry_count == 1
```

---

### 阶段 6 — 清理

- [ ] 原始场景不再复现
- [ ] 回归测试通过
- [ ] 所有调试标签已清除（`grep [DEBUG-`）
- [ ] 一次性原型删除

然后问：**"什么能防止这个 bug？"** 如果答案涉及架构变更，交给 5-优化。

---

## 什么时候用

- 遇到一个难复现的 bug
- 性能突然下降需要排查根因
- 修复了一个 bug 但不确定会不会再出现

## 案例

```
你：订单支付接口偶尔返回 500，帮我调试
Claude：先构建反馈回路——用 curl 循环调用 100 次看失败率。

       回路: while true; do curl -s -o /dev/null -w "%{http_code}"
             -X POST localhost:8000/payments; sleep 0.1; done

       发现约 5% 返回 500。进入假设阶段...

       3 条假设：
       1. 数据库连接池耗尽 → 增大连接数试试
       2. 第三方支付网关超时 → mock 网关看是否消失
       3. Redis 缓存穿透 → 检查缓存命中率

       开始验证...
```
