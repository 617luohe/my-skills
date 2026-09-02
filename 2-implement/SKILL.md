---
name: 2-implement
description: 按 TDD 把 spec 或任务清单实现出来：理解任务、逐垂直切片红-绿-重构、最终合流门禁、交 /3-review 验收后交 /5-git 提交。纯串行编排。
---

# 2-implement — 实现编排壳

输入任务清单（`docs/plans/<feature>/tasks.md`，`/1-plan` 产出）、issue，或 `docs/plans/<feature>/PRD.md`（`/to-spec` 产出；无 tasks 时按 PRD 的 User Stories 与 Implementation Decisions 自切垂直切片），按 `/tdd` 的纪律**串行**实现，自检后交 `/3-review` 验收，验收通过后交 `/5-git` 提交。纪律（红-绿、一次一片、seam 前置）只存在 `/tdd`，本文件只写编排。

对齐原版 `implement` 的流程：理解 → 按 `/tdd` 在预商定 seam 上实现 → 最终全量套件验证 → `/code-review` 审查 → 提交到当前分支。本体系将「审查」落到 `/3-review`、「提交」落到 `/5-git`（需用户授权），中间不做并行调度，一律在主上下文串行推进。

## 流程

1. **理解任务** — 提取功能切片、验收标准、AFK/HITL 标记、前置依赖与 Write Set。`[HITL]` 任务在首个需决策或不可逆动作前暂停。
2. **TDD 实现** — 按 `docs/plans/<feature>/tasks.md` 的 DAG 拓扑顺序，每次一片：Call the Skill tool with "tdd" 完成 RED → GREEN → 下一片。串行执行，不做并行调度。
3. **验证** — 用项目原生 test/type/lint/build 命令跑全量门禁；开发中定期跑单个测试文件与 typecheck。
4. **自检 + 交接审查** — 自检是轻量门禁（全量门禁过 + 快速扫重复与命名），然后带**未提交改动** Call the Skill tool with "3-review"，显式传：审查基点（探测 `git symbolic-ref refs/remotes/origin/HEAD`，不写死 `main`）+ 实际 diff 范围、需求来源路径、diff 审查意图。
5. **提交** — `/3-review` 通过（PASS 或 PASS WITH WARNINGS）后，Call the Skill tool with "5-git" 提交到当前分支；提交范围与动作需用户授权。

## 边界

- 本阶段串行实现，不做条件式并行调度；并行能力交由用户在其他场景按需要求。
- `/3-review` 裁决 FAIL 时逐条修复后复评（回环规则见 `/3-review`）。
- 提交动作交由 `/5-git` 承接并需用户授权，本阶段不直接 `git commit`。

## 完成标准

- 按 `/tdd` 串行完成每片红-绿-重构，最终合流态通过完整 test/type/lint/build 门禁。
- 改动已交 `/3-review` 验收、通过后已交 `/5-git` 提交当前分支。

## 详细规则参考

- `tdd`（canonical `vocabulary/tdd`）：红-绿-重构循环与测试纪律
- `/3-review`：双轴审查与裁决
- `/5-git`：提交、回滚、分支与远程同步（需授权）
