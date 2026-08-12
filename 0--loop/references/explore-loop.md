# Explore Loop — 模糊支（长跑）

目标：多轮多角度试探，尽量花完预算，收敛成带证据的推荐，供 `/1-规划` 落地。默认只读；探针用 `loop/<run-id>/probe-<id>`，不合并。

前置：`consensus.md` 已确认。

## 反早停

- `rounds_done < min_rounds` → **禁止**收敛（即使 AC 可勾、已有推荐方案）  
- 提前可勾的 AC → 继续加深证据、扫未探索格、压低残余假设  
- 仅当 `rounds_done ≥ min_rounds` 且满足下方收敛条件之一，才写终局 `report.md`

## 每轮 5 步

### 1. PLAN

默认 K≤3：

| 类型 | 数量 | 来源 |
| ---- | ---- | ---- |
| 加深 | 1 | 最高价值「有希望」 |
| 探测 | 1–2 | 「未探索」格（优先） |
| wildcard | 0–1 | 相邻域；仅当未探索格仍多且剩余轮次 > 2 |

格子不足时减少 K，不重复格。

### 2. FAN-OUT

并行 researcher/explore；长证据 → `cards/`。

### 3. SYNTHESIZE

去重 → 三轴打分 → 更新 map/findings。**不**在此步向用户提问。

### 4. CHECKPOINT

落盘 state/findings/map/PROGRESS。按 `parent_reset` 决定是否停靠（停靠≠收敛）。

### 5. BUDGET

`rounds_done += 1`。剩余轮次紧 → 取消 wildcard，只加深 + 补未探索。

## 收敛条件（须同时：已满 min_rounds，且任一）

- `max_rounds` 触顶  
- 连续 2 轮无新 A 级 **且** 地图无「未探索」关键格（或仅剩明确死胡同）  
- consensus 写明的覆盖/AC 已满足 **且** 已做至少一轮「加深」巩固证据  

禁止：第 1 轮材料刚够写报告就停。

## 报告

终局才写完整 `report.md`。中途可用 `PROGRESS.md` 一行记进度，不交付终局菜单。
