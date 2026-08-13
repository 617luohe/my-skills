# Explore Loop — 模糊支（长跑）

目标：多轮多角度试探，尽量花完预算，收敛成带证据的推荐，供 `/1-规划` 落地。默认只读；探针用 `loop/<run-id>/probe-<id>`，不合并。

前置：`consensus.md` 已确认。

## 反早停

- `rounds_done < min_rounds` → **禁止**收敛（即使 AC 可勾、已有推荐）  
- 提前可勾的 AC → 继续加深、扫未探索格  
- 仅当 `rounds_done ≥ min_rounds` 且满足收敛条件之一，才写终局 `report.md`

## findings 分级

| 级 | 含义 |
| -- | ---- |
| A | 改变推荐或 AC 的发现 |
| B | 支撑性证据 |
| C | 弱信号 / 待验证 |

每条必须含 card id 或 `文件:行` 证据指针。

## 每轮 5 步

### 1. PLAN

默认 K≤3：

| 类型 | 数量 | 来源 |
| ---- | ---- | ---- |
| 加深 | 1 | 最高价值「有希望」 |
| 探测 | 1–2 | 「未探索」格（优先） |
| wildcard | 0–1 | 相邻域；仅当未探索仍多且剩余轮次 > 2 |

格子不足时减少 K，不重复格。

### 2. FAN-OUT

并行 researcher/explore；长证据 → `cards/`。

### 3. SYNTHESIZE

去重 → 三轴打分 → 更新 map/findings。**不**向用户提问。

### 4. CHECKPOINT

落盘 state/findings/map/PROGRESS（固定字段）。按 `parent_reset` 决定是否停靠（停靠≠收敛）。**必报一行**进度。

### 5. BUDGET

`rounds_done += 1`。剩余轮次紧 → 取消 wildcard。

## 收敛条件（须 `rounds_done ≥ min_rounds`，且任一）

- `max_rounds` 触顶  
- `completion_promise` 已满足（若 consensus 有定义）  
- 连续 2 轮无新 A 级 **且** 无「未探索」关键格（或仅剩死胡同）  
- consensus 覆盖/AC 已满足 **且** 至少一轮「加深」巩固  

禁止：第 1 轮材料刚够写报告就停。

## hybrid 切换（→ criteria，无 HITL）

当 `mode=hybrid` 且 explore 段满足**全部**：

1. `rounds_done ≥ min_rounds`  
2. map 无未探索关键格，或已有明确推荐方案（findings ≥1 A 级）  
3. consensus「预算内加深」方向已至少一轮加深  

→ 写 `criteria.md`（从 findings 抽 AC/切片）→ 切 [criteria-loop.md](criteria-loop.md) 阶段 B，mode 记为 hybrid/criteria。

## 报告

终局才写完整 `report.md`。中途只更新 PROGRESS + 一行进度，不交付终局菜单。
