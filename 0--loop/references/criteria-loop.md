# Criteria Loop — 明确支（长跑）

目标：从共识生成 metrics/AC/切片，再推进至 AC 达标或停止条件命中。编排器不写代码；隔离实现单元守 `/2-开发` + `/tdd`，分支 `loop/<run-id>/<slice-id>`。

前置：`consensus.md` 已确认（`mode=criteria` 或 hybrid 已切换）。

## 入口

| 来源 | 行为 |
| ---- | ---- |
| `mode=criteria` | 从阶段 A Define 开始 |
| `mode=hybrid`（explore 已切换） | 跳过 Define 若 `criteria.md` 已由 explore 写入；否则快速 Define（仍计 1 轮） |

## 运行门禁

- Define 与切片环 **不问用户**  
- 全 AC 达标 → 当轮 checkpoint 后立即停止
- 连续两轮没有关闭 AC、产生关键证据或解除 blocker → 停止
- blocked：自动剪枝/改范围 1 次；仍失败 → report，不中途问人  
- 任何新用户消息 → 只在 PROGRESS checkpoint 标记 superseded，不写 report，立即停止旧主环
- 先探测宿主隔离与 fresh-context 能力；无并行能力则顺序执行，无等价隔离则以 `capability-unavailable` 安全停止

## 阶段 A — Define（自动，计 1 轮）

1. 从 `consensus.md` 抽可验证目标（可复用 grilling 已写 AC）  
2. 写 metrics + AC  
3. 拆切片 → `criteria.md`  
4. 立即进入阶段 B  

`rounds_done += 1`（Define 算一整轮）。

## 阶段 B — 切片环

Orient → Act（隔离执行单元，或顺序 fresh-context 降级）→ Measure → Reflect → CHECKPOINT → `rounds_done += 1`。
进度写入 **`slice-progress.md`**（勿用 `progress.md`）。  
同切片失败最多再派 **1** 次；然后 blocked 或跳过可独立下一项。

blocker 优先级：**blocked 切片** > 依赖未满足的 pending > 加深已通过切片的测试证据。

## 停止条件

命中任一即停止：

- 全部 AC 达标。
- 连续两轮无高价值进展。
- `max_rounds` 触顶。
- 剩余均为不可自动解除的 blocked。
- 宿主缺少等价隔离与 fresh-context 能力。

新用户消息覆盖属于 superseded 分支，不是正常停止原因。

## 报告

正常终局 `report.md`：停止原因、AC 表、分支、blocked 和一条下一步。`max_rounds`、停滞或能力不足停止时明确未满足 AC；合并授权只在成功终局问一次。superseded 不写 report。
