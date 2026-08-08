# 预算规则 — 估算账本 + 探针校准

## ledger.json 结构

```json
{
  "run_id": "2026-08-08-explore-001",
  "total": 1000,
  "reserve_pct": 0.15,
  "reserved": 150,
  "explorable": 850,
  "factor": 15,
  "spent_estimate": 0,
  "rounds": 0,
  "threads_dispatched": 0,
  "pruned_directions": []
}
```

- `total`：硬上限（用户输入，默认 1000），**任何时点不可让估算消耗超过它**
- `reserved`：留给最终合成 + 报告的钱，`total × reserve_pct`，轮次中**不动**
- `explorable`：可探索预算 = total - reserved，轮次中消耗
- `factor`：每线程估算成本（API 调用数），探针校准

## 探针校准（阶段 0 后、第 1 轮前）

1. 派 **1 个探针线程**（选一个最浅的"未探索"格子），brief 末尾要求"自报工具调用数"。
2. 取探针线程自报的工具调用数 `n`，设 `factor = max(5, n × 1.3)`（1.3 为安全系数，覆盖合成与重试）。
3. 探针线程的发现正常进入 SYNTHESIZE，不浪费。
4. 若探针无法自报（如线程异常），**默认 factor = 15**，并在 ledger.json 记 `factor_source: "default"`。

## 每轮记账

```text
spent_estimate += 线程数 × factor + 3   // 3 = PLAN/SYNTHESIZE 的合成开销估计
```

- 线程数含探针轮（探针那轮：`1 × factor + 3`）。
- 主流程自身的 PLAN/CHECKPOINT 等每次交互算在合成开销里（约 1-2 次调用/步），取 3 为安全均值。

## 动态再分配（每轮 BUDGET 步骤执行）

1. **加深**：高价值方向下轮 +1 线程配额（从探测名额匀）。
2. **剪枝**：低价值方向移出活跃集，其配额回收到"未探索"探测。
3. **下轮线程数**：

```text
下轮 = min(K, floor(剩余可探索预算 / factor))
```

4. **转收敛**：`剩余可探索预算 < 1.5 × factor × 2`（不够开 2 线程）。

## 硬上限保护

- 任何时点若 `spent_estimate + 预留 + 下轮最小开销 > total` → 不派新线程，直接转收敛。
- 记账**宁多勿少**：估算口径偏保守，防止超预算；真实消耗由用户侧 dashboard 兜底核对（二期可接真实源）。

## 校准修正

若某轮线程明显比 factor 重（线程返回大量工具调用 / 长时间运行），`factor = max(factor, 该轮平均自报数 × 1.3)` 就地上调，并在 ledger.json 记录调整原因。
