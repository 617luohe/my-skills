# Artifacts — `docs/loop/<run-id>/`

## 目录

```text
docs/loop/<run-id>/
├── state.md              # 共识状态、模式、parent_reset、轮次
├── consensus.md          # grilling 后的共享理解摘要（主环边界）
├── PROGRESS.md           # 续跑入口（下一步动作）— 大写，唯一
├── report.md             # 收敛后交付
├── cards/                # 长证据原文
├── map.md                # explore
├── findings.md           # explore
├── criteria.md           # criteria
└── slice-progress.md     # criteria 切片进度（勿与 PROGRESS.md 混淆）
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
- 最少交付（地板 / AC）：
- 预算内加深（天花板方向）：
- completion_promise: <可选，精确字符串；criteria 可省略，以 AC 全勾为准>
- 残余假设 / 风险：
- 确认：用户已确认（日期）— 确认后主环静默长跑
```

`completion_promise` 与 `max_rounds` 为**双安全阀**；触顶或 promise 满足均可收敛（须已满 min_rounds）。

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

每轮 CHECKPOINT **必须**更新：

```markdown
# PROGRESS — <run-id>

- 种子：
- 共识：pending | confirmed（指针：consensus.md）
- 模式：
- parent_reset：
- 当前轮次：<rounds_done> / <max_rounds>
- top_finding：<一句>
- blocked：<无 | 简述>
- 状态摘要：
- 下一步动作：<一条，如「新会话 /0--loop 续跑 run-id=… 从 criteria 切片 S-03 Act」>
- 停靠原因：none | grilling | pressure | per_round | converged
```

父会话对用户**必输出一行**（从上述字段抽取）：`R<n>/<max> · <top_finding> · 剩余 <k> 轮 · <停靠|继续>`

## map.md（explore）

格子表：ID | 维度 | 状态（未探索/已探测/有希望/深入/死胡同） | 备注

## findings.md（explore）

按 A/B/C 分级；**每条必须**含证据指针（卡片 id 或 `文件:行`）。

| 级 | 含义 |
| -- | ---- |
| A | 可改变推荐或 AC 的发现 |
| B | 支撑性证据 |
| C | 弱信号 / 待验证 |

## criteria.md（criteria）

- metrics 列表  
- AC 列表（id + 可检查条件）  
- slices：id | 目标 | AC | 范围 | 依赖 | status（pending/running/done/blocked）

## slice-progress.md（criteria）

每切片一行：结果、证据、branch、轮次。**禁止**命名为 `progress.md`（与 PROGRESS.md 冲突）。

## report.md

- 执行摘要（≤10 行）  
- 模式与停止原因（含触顶：max_rounds / promise / AC / explore 收敛）  
- 关键发现或 AC 表  
- 分支与未合并说明  
- 建议清单：等级（S/A/B）| 工作量 | 下一步技能 | 可选「建议改动的路径」  
- 纯 explore：默认**一条**下一步（如 `/1-规划` 或 `/writing-for-agents`），不列菜单  
