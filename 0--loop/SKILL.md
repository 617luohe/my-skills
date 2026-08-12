---
name: 0--loop
description: >
  长时间自主迭代环：开场 grilling 一次对齐需求（含模式/预算），确认后无人打断地多轮探索或验收推进；父编排、子干净窗。
  触发：迭代探索、验收环、模糊需求试方案、标准驱动推进、长时间任务、loop 迭代（非定时 every Nm）。
  续跑：提供 docs/loop/<run-id> 或 PROGRESS.md（不重新 grilling）。
disable-model-invocation: false
---

# 0--loop — 长时间自主迭代环

**一次对齐，长跑交付。** 开场用 `/vocabulary/grilling` 达成共识；用户确认后进入多轮主环，中途不问、不求选、不提前交差。父会话只编排；探索与切片在干净子进程。产出 `docs/loop/<run-id>/`。

与 Cursor 定时 `/loop`（every 5m）不同：本技能是**方法论长跑**，不是时间调度。

## 输入

- `seed`：需求
- 可选（也可在 grilling 里定）：`run-id`、`parent_reset`、`max_rounds`（默认 **8**）、`min_rounds`（默认 **3**）、禁区、必看维度

## 人机门禁（仅两处）

1. **开场共识（grilling）** — 唯一决策窗口：目标/范围/取舍 + **mode** + **parent_reset** + 轮次预算；用户确认 `consensus.md` 后才开跑  
2. **终局交付** — 主环自己跑完后贴 `report.md`；仅此时问「是否授权合并/进规划/检查」（无代码合并则只交付，不追问选项菜单）

主环内：**零 HITL**。不问「是否继续下一轮」「接受报告还是加深」。上下文被迫停靠时只写 `PROGRESS.md` + run-id，等用户一句续跑，不重新决策。

## 铁律

1. **先共识后长跑** — 无确认的 `consensus.md` 不得开主环  
2. **主环静默** — 不中途提问；状态只写磁盘；对外最多一行进度（可选），不摊菜单  
3. **反早停** — 未满 `min_rounds` 不得因「AC 已能勾上」或「已有推荐」而收敛；AC 是地板不是天花板  
4. **花预算** — 优先把 `max_rounds` 用在加深与未探索格上，而不是省轮次  
5. **父禁深潜 / 一卡一窗 / 磁盘即记忆 / 每环必度量** — 同注意力隔离  
6. **硬停止** — 仅：`max_rounds` 触顶 / 满 `min_rounds` 后连续 2 轮无新 A 级（或 criteria 全 AC 达标）/ 共识内不可解除的 blocked  

详规 → [references/attention-isolation.md](references/attention-isolation.md)

## 流程

### 0. 启动 / 续跑

- **新跑**：建目录，`state.md` 中 `consensus: pending`，`status: grilling`  
- **续跑**：读 `PROGRESS.md`；共识已确认 → **跳过 grilling**，静默从下一步续主环  

### 1. 开场 grilling（唯一 HITL 决策）

执行 `/vocabulary/grilling`。frontier **必须覆盖**（可与需求题同一批）：

| 决策 | 默认推荐 |
| ---- | -------- |
| mode | 可验证→criteria；方案未定→explore；先探后做→hybrid |
| parent_reset | `on_pressure` |
| max_rounds / min_rounds | 8 / 3（用户要「长跑」可升到 12 / 4） |
| 成功标准 | 写入 consensus 的 AC 或探索覆盖期望 |

退出后写 `consensus.md`（含 mode、parent_reset、轮次、AC/覆盖期望）→ 用户确认一句 → `consensus: confirmed` → **立即开主环，不再单独问模式**。

### 2. 主环（全自动）

按 `consensus.md` 的 mode：

- explore → [references/explore-loop.md](references/explore-loop.md)  
- criteria → [references/criteria-loop.md](references/criteria-loop.md)（`/2-开发` + `/vocabulary/tdd` 子进程）  
- hybrid：explore 达方案收敛条件后自动切 criteria，**不**再 HITL  

越界 → 记 PROGRESS `blocked`，能剪枝则剪，不问用户。

每轮 CHECKPOINT；`on_pressure` 且会话压力到顶 → 停靠并给出**唯一续跑句**（含 run-id），不征求新决策。

### 3. 终局交付

写 `report.md`，向用户交付路径与摘要。有分支合并或进主流程时才问授权；否则结束。

## 完成标准

- [ ] 开场仅一轮共识确认；mode/预算已写入 `consensus.md`
- [ ] 主环轮次 ≥ `min_rounds`（除非不可解除 blocked）
- [ ] 主环期间无向用户索取决策的菜单式提问
- [ ] `report.md` 已写；停止原因可核对；默认分支未被本技能合并

## 产物

[references/artifacts.md](references/artifacts.md)
