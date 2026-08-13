# 注意力隔离 — 父编排 / 子干净窗

目标：每个子进程在最佳专注窗口工作；父会话上下文不随轮次膨胀。

## 角色

| 角色 | 做什么 | 不做什么 |
| ---- | ------ | -------- |
| Orchestrator（父） | 读磁盘状态、写方向卡、Task 派子进程、收卡片、合成、CHECKPOINT | 大范围搜索深挖、写实现、跑长测试、粘贴 worker 全文 |
| Worker（子） | 只领一张卡，在全新上下文执行，回传卡片或写 `cards/` | 领取第二张卡、改父状态文件以外的编排文件 |
| Disk | `docs/loop/<run-id>/` 为唯一共享记忆 | — |

## parent_reset

写在 `state.md`，可切换：

| 值 | 行为 |
| -- | ---- |
| `on_pressure`（默认） | 同会话可多轮；触压 → 写 PROGRESS → 请用户新会话续跑 |
| `per_round` | 每轮 CHECKPOINT 后立刻停靠 |

用户说「每轮换会话」→ `per_round`；说「压力再换」→ `on_pressure`。

默认 `max_parent_rounds_per_session = 5`（仅 `on_pressure`）。

### 触压信号（满足任一即停靠）

1. 本会话父编排已完成 `max_parent_rounds_per_session` 轮 CHECKPOINT  
2. 单轮 FAN-OUT 后工具输出预估 > ~150KB（或回复明显截断/遗忘早期约束）  
3. FAN-OUT ≥3 线程且本轮 SYNTHESIZE 依赖 >10 张卡片摘要  

停靠时只输出：**run-id + 一句续跑命令**（如 `/0--loop 续跑 run-id=…`）。不征求「是否继续 / 加深 / 换模式」。

## Brief 入站

方向卡 ≤ 40 行，只含：

- 问题一句
- 要收集的证据
- 路径白名单（或「只读调研」）
- 回传 schema
- 指针：`state.md` / `map.md` / `criteria.md` 路径（worker 自行 Read）

## 卡片出站

```text
id: D-NN 或 S-NN
finding: ≤120字
evidence: ≤5 条（文件:行 / URL / 命令结果摘要）
confidence: 1-5
dimensions_or_ac: 关联格子或 AC id
tool_calls: 整数
branch: 若有改动则分支名，否则空
status: ok | blocked | empty
```

- 单卡**摘要** ≤ 800 字符；超限 → 摘要压缩，**长文必须**写 `cards/<id>.md`，父读摘要 + 按需 Read 长文（软顶，不拒收长文文件）  
- findings 每条必须指向 card id 或 `path:line`

## 派发

| 模式 | 子进程 | 约束 |
| ---- | ------ | ---- |
| explore | `researcher` / `explore` | 并行 ≤3；格子互斥 |
| criteria | `worker-dev` / `coder` | `/2-开发` + `tdd`；分支 `loop/<run-id>/<slice-id>` |
| 评判 | `reviewer` | 输入 = 本轮 `cards/`，非聊天记录 |

同轮 worker **互不共享上下文**。冲突只在 SYNTHESIZE 去重。

## blocker 优先级（同轮资源不足时）

1. **blocked 切片**（criteria）— 自动重试 1 次后仍 blocked  
2. **未探索关键格**（explore）— map 标「关键」或 consensus 必看维度  
3. wildcard / 加深次要格  

## 父会话每轮对外输出

**必须**一行：`R<n>/<max> · <top_finding> · 剩余 <k> 轮 · <继续|停靠·原因>`  
不复述证据全文、不贴工具日志。

## 干净停靠

1. 写完 `PROGRESS.md`（含固定字段）与本轮 artifacts  
2. 告知 run-id、停靠原因（pressure / per_round）、续跑：`/0--loop 续跑 run-id=<id>`  
3. 不在膨胀上下文硬开下一轮  
