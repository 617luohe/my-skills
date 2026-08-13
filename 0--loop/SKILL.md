---
name: 0--loop
description: >
  实验性、仅用户显式调用的共识长跑：确认模式、AC 与 max_rounds 上限后，多轮探索或验收；满足 AC 或连续两轮无高价值新发现即停。
  不自动承接模糊需求、定时检查、普通开发或单次 PR 循环。
  续跑：/0--loop 续跑 run-id=<id> 或指向 docs/loop/<run-id>/PROGRESS.md。
disable-model-invocation: true
---

# 0--loop — Experimental Consensus Loop

仅由用户显式调用 `/0--loop`。Manifest dependencies 使用 canonical names `vocabulary/grilling`、`vocabulary/tdd`；运行时开场加载 `/grilling`。用户确认 `consensus.md` 后进入主环。父会话只编排，探索与实现切片使用干净上下文。状态写入 `docs/loop/<run-id>/`。

## 定位

- **explore**：方案未定，需要多角度只读调查。
- **criteria**：AC 已锁定，需要分切片推进与验收。
- **hybrid**：先调查形成方案与 AC，再推进切片。

定时/事件调度先使用宿主实际提供的能力（例如仅在宿主确有该命令时使用 `/loop`）；单个实现任务使用 `/2-开发`；普通问题直接对话。本技能不因这些意图自动触发。

## 输入

- `seed`：需求
- 可选：`run-id`、`parent_reset`、`max_rounds`（默认 **8**）、禁区、必看维度
- `mode` 与可检查 AC 在开场共识中确认

`max_rounds` 只是安全上限，不是应当花完的额度。

## 启动 / 续跑

**新跑**：建 `docs/loop/<run-id>/`，`state.md` 设 `consensus: pending`、`status: grilling`。

**续跑**（共识已确认 → 跳过 grilling）：

```text
/0--loop 续跑 run-id=2026-08-13-my-run
```

或粘贴 `docs/loop/<run-id>/PROGRESS.md` 路径。从 PROGRESS「下一步动作」静默继续。

续跑本身必须由用户显式发起。共识确认后 scope 变更使用新 run-id。

## 用户消息优先级

主环运行期间，**任何新用户消息立即覆盖并停止当前主环**：

1. 先把当前安全状态写入 `PROGRESS.md`，`status: superseded`。
2. 不再派发新切片、不合并分支、不继续旧目标。
3. 以最新用户消息为当前请求；只有最新消息明确要求续跑时才恢复。

该规则高于 AC、轮次和既有共识。

## 子进程与卡片（摘要）

主环开始前探测宿主是否提供隔离子进程、fresh context、并行派发和独立评判能力。`researcher`、`explore`、`worker-dev`、`coder`、`reviewer` 仅是可用时的宿主示例名称，不得假设三宿主同名或都存在。

| 模式 | 所需能力 | 分支 |
| ---- | -------- | ---- |
| explore | 只读、隔离的调查执行单元 | 只读；探针 `loop/<run-id>/probe-*` |
| criteria | 隔离的实现执行单元 + 独立评判单元 | `loop/<run-id>/<slice-id>` |
| 共用 | 父 Orchestrator | 不深挖、不写实现 |

无并行能力时，降级为每次只运行一张卡的顺序 fresh-context；无等价隔离或 fresh-context 能力时，写 checkpoint，设正常 `status: stopped` 并以 `capability-unavailable` 安全停止，不在污染上下文中假装隔离。

**Brief**（≤40 行）：问题、证据、路径白名单、回传 schema、磁盘指针。  
**卡片**（≤800 字摘要）：`finding` + `evidence` + `status`；超长正文 → `cards/<id>.md`（软顶，不拒收长文文件）。

详规 → [references/attention-isolation.md](references/attention-isolation.md)

## 主环门禁

1. 无已确认 `consensus.md` 不开主环。
2. 父会话不深潜；一卡一窗；磁盘是唯一共享记忆。
3. 每轮 PLAN → FAN-OUT → SYNTHESIZE → CHECKPOINT，并记录是否产生高价值新发现。
4. 每个 CHECKPOINT 后检查新用户消息，再决定是否继续。
5. 命中任一停止条件立即停止，不追加“加深轮”：
   - criteria/hybrid 的全部 AC 已满足；
   - 连续两轮无高价值新发现或无可验证进展；
   - `max_rounds` 触顶；
   - 剩余工作全部不可解除 blocked。

### rounds_done 语义

- **explore / hybrid 探索段**：每轮 PLAN→CHECKPOINT = +1  
- **criteria Define**：阶段 A = +1；阶段 B 每切片 CHECKPOINT = +1  
- **hybrid 切换**：已有明确推荐且可生成 AC 时切换；条件见 [references/explore-loop.md](references/explore-loop.md)

### parent_reset

| 值 | 行为 |
| -- | ---- |
| `on_pressure`（默认） | 同会话多轮；触压则停靠续跑 |
| `per_round` | 每轮 CHECKPOINT 后停靠 |

触压信号（满足任一）：`parent_rounds ≥ max_parent_rounds_per_session`（默认 5）；或单轮工具输出预估 > ~150KB；或 FAN-OUT ≥3 且上下文明显膨胀。详规 → attention-isolation.md

## 流程

### 1. 开场 grilling

加载 `/grilling`。frontier 必须覆盖：

| 决策 | 默认 |
| ---- | ---- |
| mode | 可验证→criteria；未定→explore；先探后做→hybrid |
| parent_reset | `on_pressure` |
| max_rounds | 8；只作安全上限 |
| 成功标准 | 从 seed 草拟可检查 AC 或探索问题 → 用户确认 |

写 `consensus.md` → 用户确认 → `consensus: confirmed` → **立即开主环**。

### 2. 主环

- explore → [references/explore-loop.md](references/explore-loop.md)  
- criteria → [references/criteria-loop.md](references/criteria-loop.md)（子进程 `/2-开发` + `/tdd`）
- hybrid：explore 达切换条件后自动 criteria，不再 HITL  

每轮：PLAN → FAN-OUT → SYNTHESIZE → CHECKPOINT（更新 PROGRESS 固定字段）→ STOP CHECK。
blocker 优先级：**blocked 切片** > **未探索关键格** > wildcard。

### 3. 终局

命中正常停止条件时写 `report.md`，记录停止原因、AC 状态或关键发现、未完成项和一条推荐下一步。AC 满足设 `status: converged`；停滞、`max_rounds`、blocked 或能力不足设 `status: stopped`。`max_rounds` 触顶不等于成功，必须明确未满足 AC。新用户消息覆盖只写 `PROGRESS.md` 的 `superseded`，不写 `report.md`。

## 完成标准

- [ ] 用户显式调用，且 mode、AC、max_rounds 已写入并确认。
- [ ] 每轮有 checkpoint 与“高价值新发现/进展”判定。
- [ ] AC 达标或连续两轮无高价值新发现时立即停止。
- [ ] 新用户消息出现时旧主环已标记 superseded 并停止。
- [ ] 正常停止已写 `report.md`；superseded 已写 `PROGRESS.md`；默认分支未合并。

## 产物

[references/artifacts.md](references/artifacts.md)

## 术语

| 词 | 含义 |
| -- | ---- |
| HITL | Human-in-the-loop；本技能主环 = 零 HITL（不向你索取决策） |
| FAN-OUT | 并行派发子进程收卡片 |
| CHECKPOINT | 落盘 state/PROGRESS/findings 或 slice-progress |
| parent_reset | 父会话何时停靠换干净窗 |
| on_pressure | 感知上下文膨胀再停靠（默认） |
| per_round | 每轮都停靠，下一会话续跑 |
| seed | 用户原始需求一句话 |
| AC | 可检查验收标准；满足即停止 |
