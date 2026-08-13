---
name: 0--loop
description: >
  共识长跑（非定时调度、非 shell while、非 Ralph 单 prompt 循环）：开场 grilling 对齐模式/预算，确认后多轮静默探索或验收；父编排、子干净窗。
  触发：模糊需求多轮探索、已共识验收环、标准驱动长跑、长时间自主迭代。
  不触发：every Nm 定时检查、同一 prompt 写到测试绿、单次 PR 合并循环。
  续跑：/0--loop 续跑 run-id=<id> 或指向 docs/loop/<run-id>/PROGRESS.md。
disable-model-invocation: false
---

# 0--loop — 共识长跑

**先对齐范围/预算，再无人打断地跑完。** 开场 `/vocabulary/grilling` 一次；用户确认 `consensus.md` 后进主环。父会话只编排；探索与切片在干净子进程。产物 `docs/loop/<run-id>/`。

**心智入口**：同一 prompt 反复写代码直到测试绿 → Ralph / Cursor 实现环；**要先定 mode/预算/成功标准 → 本技能**。

## 市场定位（三角）

| 能力 | Cursor `/loop` | Ralph Loop | **0--loop** |
| ---- | -------------- | ---------- | ----------- |
| 本质 | 定时/事件**调度** | 同 prompt **实现**循环 | **共识后**方法论长跑 |
| 典型任务 | 每 5m 查部署 | Story 写到 COMPLETE | 模糊探索 / AC 驱动验收 |
| 状态 | shell 唤醒 | scratchpad + promise | `docs/loop/<run-id>/` |
| HITL | 每 tick 可介入 | 极少 | 仅开场 + 终局 |

## 何时用 / 何时不用

```
有清晰 AC、要静默跑切片验收？ ──yes──► criteria（或 hybrid 后半）
方案未定、要多角度试探？     ──yes──► explore
要先探再做的长跑？           ──yes──► hybrid
只是问一句 / 单文件小改？    ──yes──► 不用；走 /2-开发 或对话
要 every Nm 轮询 / 同 prompt 写到绿？ ──yes──► 不用；走 Cursor /loop 或 Ralph
```

| 场景 | mode | 改代码 | 典型轮次 |
| ---- | ---- | ------ | -------- |
| 架构/方案对比、优化清单 | explore | 否（探针分支除外） | 5–8 |
| 共识 AC 已锁定 | criteria | 是（loop 分支） | 3–8 |
| 先调研再实现 | hybrid | 后半改 | 8–12 |

**反例**：修单个 bug、写一份短报告、定时监控 — 均不应触发本技能。

## 输入

- `seed`：需求
- 可选（grilling 可定）：`run-id`、`parent_reset`、`max_rounds`（默认 **8**）、`min_rounds`（默认 **3**）、`completion_promise`、禁区、必看维度

## 启动 / 续跑

**新跑**：建 `docs/loop/<run-id>/`，`state.md` 设 `consensus: pending`、`status: grilling`。

**续跑**（共识已确认 → 跳过 grilling）：

```text
/0--loop 续跑 run-id=2026-08-13-my-run
```

或粘贴 `docs/loop/<run-id>/PROGRESS.md` 路径。从 PROGRESS「下一步动作」静默继续。

**改需求**：共识确认后 scope 变更 → **必须新 run-id**；不得在原 run 上重开 grilling 改边界。

## 人机门禁（仅两处）

1. **开场 grilling** — 目标/范围 + **mode** + **parent_reset** + 轮次 + 成功标准；用户确认 `consensus.md` 后才开主环  
2. **终局交付** — 主环完成后贴 `report.md`；有合并/进主流程时才问授权

主环内 **零 HITL**：不向用户提问、不摊菜单。用户仍可发消息，但编排器不为此暂停主环。上下文被迫停靠 → 写 `PROGRESS.md`，给唯一续跑句。

## 子进程与卡片（摘要）

| 模式 | 子进程 | 分支 |
| ---- | ------ | ---- |
| explore | `researcher` / `explore` | 只读；探针 `loop/<run-id>/probe-*` |
| criteria | `worker-dev` / `coder` + `reviewer` | `loop/<run-id>/<slice-id>` |
| 共用 | 父 Orchestrator | 不深挖、不写实现 |

**Brief**（≤40 行）：问题、证据、路径白名单、回传 schema、磁盘指针。  
**卡片**（≤800 字摘要）：`finding` + `evidence` + `status`；超长正文 → `cards/<id>.md`（软顶，不拒收长文文件）。

详规 → [references/attention-isolation.md](references/attention-isolation.md)

## 铁律

1. **先共识后长跑** — 无确认 `consensus.md` 不得开主环  
2. **主环静默 + 必报一行** — 不中途提问；每轮 CHECKPOINT 后**必须**向用户输出一行进度（轮次 / top 发现 / 剩余 / 是否停靠）  
3. **反早停** — 未满 `min_rounds` 不得收敛；AC 是**地板**（最少交付），预算内仍须**加深**（天花板由轮次与 map 驱动）  
4. **花预算** — 优先加深与未探索格，不省轮次  
5. **父禁深潜 / 一卡一窗 / 磁盘即记忆 / 每环必度量**  
6. **双安全阀停止** — `max_rounds` 触顶；或（满 `min_rounds` 且：`completion_promise` 已满足 / criteria 全 AC 达标 / explore 连续 2 轮无新 A 级且无关键未探索格）；或不可解除 blocked  

### rounds_done 语义

- **explore / hybrid 探索段**：每轮 PLAN→CHECKPOINT = +1  
- **criteria Define**：阶段 A = +1；阶段 B 每切片 CHECKPOINT = +1  
- **hybrid 切换**（探索→criteria，无 HITL）：explore 收敛条件满足且 `rounds_done ≥ min_rounds` 时自动切换；条件见 [references/explore-loop.md](references/explore-loop.md)「hybrid 切换」

### parent_reset

| 值 | 行为 |
| -- | ---- |
| `on_pressure`（默认） | 同会话多轮；触压则停靠续跑 |
| `per_round` | 每轮 CHECKPOINT 后停靠 |

触压信号（满足任一）：`parent_rounds ≥ max_parent_rounds_per_session`（默认 5）；或单轮工具输出预估 > ~150KB；或 FAN-OUT ≥3 且上下文明显膨胀。详规 → attention-isolation.md

## 流程

### 1. 开场 grilling

执行 `/vocabulary/grilling`。frontier **必须覆盖**：

| 决策 | 默认 |
| ---- | ---- |
| mode | 可验证→criteria；未定→explore；先探后做→hybrid |
| parent_reset | `on_pressure` |
| max / min rounds | 8 / 3（长跑可 12 / 4） |
| 成功标准 | 从 seed **草拟 AC/覆盖期望** → 用户改一句确认 |
| completion_promise | 可选；criteria 可省略（以 AC 全勾为准） |

写 `consensus.md` → 用户确认 → `consensus: confirmed` → **立即开主环**。

### 2. 主环

- explore → [references/explore-loop.md](references/explore-loop.md)  
- criteria → [references/criteria-loop.md](references/criteria-loop.md)（子进程 `/2-开发` + `/vocabulary/tdd`）  
- hybrid：explore 达切换条件后自动 criteria，不再 HITL  

每轮：PLAN → FAN-OUT → SYNTHESIZE → CHECKPOINT（更新 PROGRESS 固定字段）→ BUDGET。  
blocker 优先级：**blocked 切片** > **未探索关键格** > wildcard。

### 3. 终局

写 `report.md`（含停止原因、推荐等级、下一步技能）。纯建议型 explore 默认只给**一条**下一步（如 `/1-规划`），不摊菜单。

## 完成标准

- [ ] 仅一轮共识确认；mode/预算/`completion_promise` 在 `consensus.md`
- [ ] 主环轮次 ≥ `min_rounds`（blocked 除外）
- [ ] 主环无菜单式提问；每轮有一行进度
- [ ] `report.md` 已写；默认分支未合并

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
| AC | 可检查验收标准；共识地板，非轮次天花板 |
