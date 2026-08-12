# Criteria Loop — 明确支（长跑）

目标：从共识自动生成 metrics/AC/切片，再静默推进切片直至预算或全达标。编排器不写代码；子进程守 `/2-开发` + `tdd`，分支 `loop/<run-id>/<slice-id>`。

前置：`consensus.md` 已确认（含 mode=criteria|hybrid）。

## 反早停 / 静默

- Define 与切片环 **不问用户**；consensus 已锁边界  
- 未满 `min_rounds` 时：即使部分 AC 已过，继续余下切片或加固测试证据  
- 全 AC 达标且 `rounds_done ≥ min_rounds` → 可收敛  
- blocked：自动剪枝/改切片范围一次；仍失败则记入 report，不中途问人

## 阶段 A — Define（自动，计 1 轮）

1. 从 `consensus.md` 抽可验证目标  
2. 写 metrics + AC（可检查）  
3. 拆切片列表 → `criteria.md`  
4. 立即进入阶段 B（无确认步）

## 阶段 B — 切片环

Orient → Act（子进程）→ Measure → Reflect → CHECKPOINT。  
同切片失败最多自动再派 **1** 次修复；然后 blocked 或跳过依赖允许的下一项。

## 收敛条件

须 `rounds_done ≥ min_rounds` 或已无 pending 切片，且任一：

- 全部切片 done  
- `max_rounds` 触顶  
- 剩余均为不可自动解除的 blocked  

## 报告

终局 `report.md`：AC 表、分支、blocked、建议交接。合并授权只在终局问一次。
