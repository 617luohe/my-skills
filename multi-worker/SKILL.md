---
name: multi-worker
description: User-invoked orchestration for already confirmed independent tasks in tasks.md.
disable-model-invocation: false
experimental: true
---

# multi-worker — 并行开发编排器

仅可由用户显式调用。它只编排已确认的独立开发任务，不规划、不拆解，也不调用任何仅用户调用的入口。

## 唯一输入与停止条件

输入必须是**已由用户确认的 `tasks.md`**，其权威位置通常为 `docs/plans/<feature>/tasks.md`。文件必须逐项给出 Task ID、目标、允许修改的文件、验收标准及依赖关系。任务分支和 worktree 名不是规划产物；用户确认派发后，编排器根据 Task ID 与任务 slug 确定性生成并展示它们。

1. 找不到 `docs/plans/<feature>/tasks.md`、不能证明其已获用户确认，或字段不完整时：**停止，不得拆解、建分支或派发**；回复“请用户显式运行 `/1-规划`，确认生成的任务清单后再调用 `/multi-worker`。”
2. 任务少于两个、存在依赖、或两个任务允许修改同一文件时：停止并说明不能安全并行。
3. 工作区不干净、Agent 配置缺失，或没有兼容的 `worker-dev`（权限、模型、`isolation: worktree`）时：停止并报告缺口；不得静默降级为通用 Agent。

## 派发前确认

读取 `tasks.md` 后，展示任务、分支、文件和验收标准，并明确询问：“确认按此 `tasks.md` 创建 worktree 并派发 worker 吗？”只有用户明确确认后才继续。确认不替代后续的合并授权或版本管理授权。

## 执行与状态

1. 从干净基线创建集成分支，以及每个任务的独立分支和 worktree。
2. 并行派发配置的 `worker-dev`。worker 只接收任务描述、验收标准和项目约束，必须遵循 TDD，并返回测试结果、修改文件、提交和明确状态。
3. 主 session 对每个 worker 运行任务验收和代码审查。仅 `worker_succeeded` 的任务可进入合并。

状态定义：

| 状态 | 条件 | 必须动作 |
|---|---|---|
| `worker_succeeded` | worker 完成且任务验收、审查通过 | 可候选合并 |
| `worker_failed` | worker 超时、出错、未通过验收或未返回可验证结果 | 停止流程，保留全部 worktree，不得报告完成 |
| `merge_failed` | 任一候选分支冲突或合并命令失败 | 停止流程，保留全部 worktree 和集成分支，不得报告完成 |
| `integration_failed` | 合并后集成验证或最终 review 失败 | 停止流程，保留全部 worktree 和集成分支，不得报告完成 |
| `completed` | 所有任务已合并，且集成验证和最终 review 均通过 | 可报告完成并清理 |

任何失败都报告失败任务、命令输出、保留的 worktree 路径和下一步修复建议；不清理、不隐藏失败，也不得把部分成功说成整体完成。

## 集成门禁与清理

所有候选分支合并到**集成分支**后、清理前，必须在该集成分支依次完成：

1. 运行项目的**完整测试套件**。
2. 运行项目适用的 lint / type check；项目未配置时明确记录“不适用”和依据，不能假装已通过。
3. 对集成 diff 最终 review，确认 `tasks.md` 的所有验收标准、跨任务兼容性及无意外改动。

任一项失败即为 `integration_failed`。只有三项全部通过后才进入 `completed`，并且**全部通过后才清理 worktree**。

## 最终报告

仅在 `completed` 时报告完成，列出集成分支、每个任务状态、完整测试、lint/type check 和最终 review 结果。失败时只报告对应失败状态，绝不使用“完成”。
