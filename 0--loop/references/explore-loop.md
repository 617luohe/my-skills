# Explore Loop — 模糊支（长跑）

目标：多轮多角度试探，收敛成带证据的推荐，供 `/1-规划` 落地。默认只读；探针用 `loop/<run-id>/probe-<id>`，不合并。

前置：`consensus.md` 已确认。

## 停止门禁

- 共识中的探索问题或 AC 已有充分证据回答 → 当轮 checkpoint 后停止。
- 连续两轮没有新增 A 级发现或关闭关键未知 → 停止。
- `max_rounds` 触顶或剩余方向均 blocked → 停止。
- 任何新用户消息 → 只在 PROGRESS checkpoint 标记 superseded，不写 report，立即停止旧主环。
- 先探测宿主隔离与 fresh-context 能力；无并行能力则顺序执行，无等价隔离则以 `capability-unavailable` 安全停止。

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

使用宿主已探测到的只读隔离执行单元；候选名称只在该宿主确实提供时使用。支持并行则并行，不支持则每张卡顺序 fresh-context；长证据 → `cards/`。

### 3. SYNTHESIZE

去重 → 三轴打分 → 更新 map/findings。**不**向用户提问。

### 4. CHECKPOINT

落盘 state/findings/map/PROGRESS（固定字段），更新 `no_high_value_rounds`。按 `parent_reset` 决定是否停靠（停靠≠收敛）。

### 5. STOP CHECK

`rounds_done += 1`。依次检查新用户消息、AC/探索问题、连续两轮无高价值发现、blocked 和 `max_rounds`；命中即停止。

## 停止条件

- 共识 AC 或探索问题已满足。
- 连续两轮无新 A 级发现或关键未知关闭。
- `max_rounds` 触顶。
- 剩余方向不可解除 blocked。
- 宿主缺少等价隔离与 fresh-context 能力。

新用户消息覆盖属于 superseded 分支，不是正常停止原因。

## hybrid 切换（→ criteria，无 HITL）

当 `mode=hybrid` 且 explore 段满足**全部**：

1. 已有明确推荐方案（findings ≥1 A 级）。
2. 推荐可转换为可检查 AC 与切片。
3. 尚未命中连续两轮无高价值发现或其他停止条件。

→ 写 `criteria.md`（从 findings 抽 AC/切片）→ 切 [criteria-loop.md](criteria-loop.md) 阶段 B，mode 记为 hybrid/criteria。

## 报告

正常终局才写完整 `report.md`。中途只更新 PROGRESS + 一行进度，不交付终局菜单；superseded 不写 report。
