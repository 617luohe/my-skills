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
| `on_pressure`（默认） | 同会话可多轮；感知膨胀（多轮 FAN-OUT 后工具输出堆积、或满 `max_parent_rounds_per_session`）→ 写 PROGRESS → 请用户新会话续跑 |
| `per_round` | 每轮 CHECKPOINT 后立刻停靠；下一步必须在新会话用 run-id 续跑 |

用户说「每轮换会话」→ 写成 `per_round`；说「压力再换」→ `on_pressure`。

默认 `max_parent_rounds_per_session = 5`（仅 `on_pressure`；拉长同会话静默跑，少打断用户）。

停靠时只输出：**run-id + 一句续跑命令**。不征求「是否继续 / 加深 / 换模式」。

## Brief 入站（硬顶）

方向卡 ≤ 40 行，只含：

- 问题一句
- 要收集的证据
- 路径白名单（或「只读调研」）
- 回传 schema
- 指针：相关 `state.md` / `map.md` / `criteria.md` 路径（worker 自行 Read，不把全文塞进 prompt）

## 卡片出站（硬顶）

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

单卡正文 ≤ 800 字符。超限 → 拒收，令 worker 重交摘要。原始长文写 `cards/<id>.md`，父只读卡片摘要。

## 派发

- 模糊探测：并行 `researcher` / `explore`，默认每轮 ≤ 3 线程；格子互斥  
- 明确切片：串行或文件不重叠时并行 `worker-dev` / `coder`；遵守 `/2-开发` + `tdd` 纪律；分支 `loop/<run-id>/<slice-id>`  
- 需要独立评判时另派 `reviewer`，输入 = 本轮卡片目录，不是聊天记录  

同轮 worker **互不共享上下文**。冲突只在 SYNTHESIZE 用卡片去重。

## 父会话每轮对外输出

只报：轮次、top 发现或 AC 差距、剩余轮次、下一步、是否停靠。不复述证据全文、不贴工具日志。

## 干净停靠

1. 写完 `PROGRESS.md`（含下一步动作）与本轮 artifacts  
2. 告知 run-id、停靠原因（pressure / per_round）、续跑方式：`/0--loop` + run-id  
3. 不在膨胀上下文硬开下一轮  
