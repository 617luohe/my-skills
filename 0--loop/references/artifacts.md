# Artifacts — `docs/loop/<run-id>/`

## 目录

```text
docs/loop/<run-id>/
├── state.md          # 共识状态、模式、parent_reset、轮次
├── consensus.md      # grilling 后的共享理解摘要（主环边界）
├── PROGRESS.md       # 续跑入口（下一步动作）
├── report.md         # 收敛后交付
├── cards/            # 可选：长证据原文
├── map.md            # explore
├── findings.md       # explore
├── criteria.md       # criteria
└── progress.md       # criteria 切片进度
```

## consensus.md

grilling 退出并经用户确认后写入，主环只认此文件为需求边界：

```markdown
# Consensus — <run-id>

- 目标：
- 范围：
- 范围外：
- 关键决策：
- mode: explore | criteria | hybrid
- parent_reset: on_pressure | per_round
- max_rounds: 8
- min_rounds: 3
- 成功标准 / AC：
- 残余假设 / 风险：
- 确认：用户已确认（日期）— 确认后主环静默长跑
```

## state.md 最小字段

```markdown
- run-id:
- seed:
- consensus: pending | confirmed
- mode: explore | criteria | hybrid | unset
- parent_reset: on_pressure | per_round
- max_rounds: 8
- min_rounds: 3
- max_parent_rounds_per_session: 5
- rounds_done: 0
- branch_prefix: loop/<run-id>
- status: grilling | running | parked | converged
```
## PROGRESS.md

```markdown
# PROGRESS — <run-id>

- 种子：
- 共识：pending | confirmed（指针：consensus.md）
- 模式：
- parent_reset：
- 当前轮次：
- 状态摘要：
- 下一步动作：<一条可执行指令，如「继续 grilling frontier」或「新会话 /0--loop run-id=… 从 criteria 切片 S-03 Act」>
- 停靠原因：none | grilling | pressure | per_round | converged
```

## map.md（explore）

格子表：ID | 维度 | 状态（未探索/已探测/有希望/深入/死胡同） | 备注

## findings.md（explore）

按 A/B/C 分级；每条含证据指针（卡片 id 或 `文件:行`）。

## criteria.md（criteria）

- metrics 列表  
- AC 列表（id + 可检查条件）  
- slices：id | 目标 | AC | 范围 | 依赖 | status（pending/running/done/blocked）

## progress.md（criteria）

每切片一行：结果、证据、branch、轮次。

## report.md

- 执行摘要（≤10 行）  
- 模式与停止原因  
- 关键发现或 AC 表  
- 分支与未合并说明  
- 下一步推荐（技能名）  
