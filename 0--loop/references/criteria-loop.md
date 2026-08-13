# Criteria Loop — 明确支（长跑）

目标：从共识自动生成 metrics/AC/切片，再静默推进直至预算或全达标。编排器不写代码；子进程守 `/2-开发` + `tdd`，分支 `loop/<run-id>/<slice-id>`。

前置：`consensus.md` 已确认（`mode=criteria` 或 hybrid 已切换）。

## 入口

| 来源 | 行为 |
| ---- | ---- |
| `mode=criteria` | 从阶段 A Define 开始 |
| `mode=hybrid`（explore 已切换） | 跳过 Define 若 `criteria.md` 已由 explore 写入；否则快速 Define（仍计 1 轮） |

## 反早停 / 静默

- Define 与切片环 **不问用户**  
- 未满 `min_rounds`：即使部分 AC 已过，继续余下切片或加固测试  
- 全 AC 达标且 `rounds_done ≥ min_rounds` → 可收敛  
- blocked：自动剪枝/改范围 1 次；仍失败 → report，不中途问人  

## 阶段 A — Define（自动，计 1 轮）

1. 从 `consensus.md` 抽可验证目标（可复用 grilling 已写 AC）  
2. 写 metrics + AC  
3. 拆切片 → `criteria.md`  
4. 立即进入阶段 B  

`rounds_done += 1`（Define 算一整轮）。

## 阶段 B — 切片环

Orient → Act（子进程）→ Measure → Reflect → CHECKPOINT → `rounds_done += 1`。  
进度写入 **`slice-progress.md`**（勿用 `progress.md`）。  
同切片失败最多再派 **1** 次；然后 blocked 或跳过可独立下一项。

blocker 优先级：**blocked 切片** > 依赖未满足的 pending > 加深已通过切片的测试证据。

## 收敛条件

须 `rounds_done ≥ min_rounds` 或已无 pending 切片，且任一：

- 全部切片 done（**completion_promise** 若定义也应满足）  
- `max_rounds` 触顶  
- 剩余均为不可自动解除的 blocked  

## 报告

终局 `report.md`：AC 表、分支、blocked、建议清单（等级|工作量|下一步技能）。合并授权只在终局问一次。
