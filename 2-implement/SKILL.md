---
name: 2-implement
description: 按 TDD 把 spec 或任务清单实现出来：红-绿-重构，自检后交 /3-review 验收、保持未提交。
disable-model-invocation: false
---

# 2-implement — 实现编排壳

输入任务清单（`docs/plans/<feature>/tasks.md`，`/1-plan` 产出）或 issue，按 `/tdd` 的纪律实现，自检后带未提交改动交 `/3-review`。纪律（红-绿、一次一片、seam 前置）只存在 `/tdd`，本文件只写编排。

## 流程

1. **理解任务** — 提取功能切片、验收标准、AFK/HITL 标记与前置依赖。`[HITL]` 任务执行到需用户决策的点时暂停询问。
2. **TDD 实现** — 用 `/tdd` 逐片完成：规划 → RED → GREEN → 下一片。
3. **验证** — 用项目原生 test/type/lint 命令跑完整套件。
4. **自检 + 交接** — 自检是轻量门禁（完整测试/类型/linter 过 + 快速扫重复与命名），然后带**未提交改动**交 `/3-review`，显式传：审查基点（探测 `git symbolic-ref refs/remotes/origin/HEAD`，不写死 `main`）+ 实际 diff 范围、需求来源路径、diff 审查意图。

## 边界

- 本阶段不 `git commit`，不自动进 `/5-git`。
- `/3-review` 裁决 FAIL 时逐条修复后复评（回环规则见 `/3-review`）。

## 完成标准

- 按 `/tdd` 完成红-绿-重构，测试/类型/linter 全过。
- 改动未提交，已带审查基点、需求来源、diff 意图交 `/3-review`。

## 详细规则参考

- `/tdd`（canonical `vocabulary/tdd`）：红-绿-重构循环与测试纪律
