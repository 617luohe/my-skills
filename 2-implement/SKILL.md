---
name: 2-implement
description: 按 TDD 把 spec 或任务清单实现出来：红-绿-重构，自检后交 /3-review 验收、保持未提交。
---

# 2-implement — 实现编排壳

输入任务清单（`docs/plans/<feature>/tasks.md`，`/1-plan` 产出）、issue，或 `docs/plans/<feature>/PRD.md`（`/to-spec` 产出；无 tasks 时按 PRD 的 User Stories 与 Implementation Decisions 自切垂直切片），按 `/tdd` 的纪律实现，自检后带未提交改动交 `/3-review`。纪律（红-绿、一次一片、seam 前置）只存在 `/tdd`，本文件只写编排。

## 流程

1. **理解任务** — 提取功能切片、验收标准、AFK/HITL 标记、前置依赖与 Write Set。`[HITL]` 任务在首个需决策或不可逆动作前暂停；所有受该决策影响的任务以它为依赖门。
2. **条件式并行调度** — 执行前分别探测宿主是否提供 fresh context，以及基于同一冻结基点的隔离可写上下文和可回传变更包。仅当至少两个切片的依赖已验收、Write Set 互斥、共享接口与唯一 owner 已固定、HITL 无未决影响、运行资源可隔离，且收益高于调度成本时并行；并行能力不足时按同一 DAG 顺序 fresh context 执行，fresh context 也不可用时在主上下文顺序执行。

   每个 worker 只修改其 Write Set，独立运行验收标准对应的局部验证，仅返回变更包与验证证据，不 commit、不 merge。主流程是唯一合流者，按 DAG 拓扑顺序把变更包应用到未提交工作区；**冲突即停止**：发现写集重叠、越界修改、工作区漂移、变更包无法应用或接口不兼容时，报告受影响任务，不自动解决，重新划分边界或降级为串行。全部合入后只在**最终合流态**运行完整门禁。
3. **TDD 实现** — Call the Skill tool with "tdd" 逐片完成：规划 → RED → GREEN → 下一片。
4. **验证** — 用项目原生 test/type/lint/build 命令在最终合流态跑完整套件。
5. **自检 + 交接** — 自检是轻量门禁（项目配置的完整 test/type/lint/build 门禁过 + 快速扫重复与命名），然后带**未提交改动** Call the Skill tool with "3-review"，显式传：审查基点（探测 `git symbolic-ref refs/remotes/origin/HEAD`，不写死 `main`）+ 实际 diff 范围、需求来源路径、diff 审查意图。

## 边界

- 本阶段不 `git commit`，不自动进 `/5-git`。
- `/3-review` 裁决 FAIL 时逐条修复后复评（回环规则见 `/3-review`）。

## 完成标准

- 按 `/tdd` 完成红-绿-重构，最终合流态通过完整 test/type/lint/build 门禁。
- 改动未提交，已带审查基点、需求来源、diff 意图交 `/3-review`。

## 详细规则参考

- `/tdd`（canonical `vocabulary/tdd`）：红-绿-重构循环与测试纪律
