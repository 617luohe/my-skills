# 断点续跑 — 上下文膨胀 / 崩溃后的续跑协议

## 原则

一切可续跑信息都在磁盘，不在对话记忆。任何一轮 CHECKPOINT 之后停掉都不丢已探索成果。

## PROGRESS.md 格式（每轮 CHECKPOINT 更新）

```markdown
# PROGRESS — <run-id>

- 种子：<一句话>
- 预算：<total> / 估算消耗：<spent_estimate> / factor：<n>
- 当前轮次：<N>
- 活跃方向：<D-xx: 状态>
- 已剪枝：<D-xx: 原因>
- 下一步动作：<明确的一条指令，如"继续 PLAN 第 N+1 轮，加深 D-01">
```

## 上下文膨胀时的干净停靠

1. 感知上下文接近极限（对话过长、工具输出堆积）。
2. **先写** `PROGRESS.md`（含下一步动作），再写 `ledger.json` 最终账本。
3. 向用户报告：`run-id`、停靠原因、续跑命令。
4. **不要**在膨胀的上下文里硬撑下一轮。

## 续跑协议（新会话/新上下文）

1. 用户运行 `/0--explore` 并提供 `run-id`（或直接粘贴 PROGRESS.md）。
2. 读 `PROGRESS.md` → `state.md` → `findings.md` → `ledger.json`，恢复全部状态。
3. 按 `PROGRESS.md` 的"下一步动作"继续：从该轮 PLAN（或第 5 步 BUDGET）续起。
4. 更新 PROGRESS.md 后继续正常循环。

## 崩溃保护

- 若在某轮中途崩溃（线程已派、合成未写）：以最新 CHECKPOINT 为准重跑该轮 PLAN。
- 线程重复派发造成的浪费由预算账本吸收（`factor` 含安全系数），不要尝试"恢复半完成线程"。
