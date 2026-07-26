---
name: multi-worker
description: Orchestrate parallel implementation only when BOTH a clear existing development or design document defines the work AND the work contains genuinely independent development tasks. Use for parallel development when both conditions hold; otherwise use planning or sequential development instead.
disable-model-invocation: true
experimental: true
---

# multi-worker — 并行开发编排器

基于设计文档拆分独立任务，检查 Agent 配置，用独立 worktree 并行开发、审查和合并。

**实验性功能** — 需要完整设计文档 + 独立子任务 + Agent 配置验证。

## 与主流程的关系

- **主流程**：`/1-规划` → **串行** `/4-开发`（安全，默认）
- **加速分支**：`/1-规划` → **multi-worker** → **并行** `/4-开发`（高风险，需要明确条件）

## 前置条件（全部满足才用）

1. `/1-规划` 已产出完整设计文档（目标、模块划分、接口约定、验收标准）
2. 任务可拆为 2-5 个互不修改同一文件的独立子任务
3. Agent 配置已验证（名称、权限、模型、worktree 能力）
4. 工作区干净（无未提交变更）

## 何时不用

- **任务有依赖**（A 的输出是 B 的输入）→ 串行 `/4-开发`
- **设计文档不完整** → 先补完 `/1-规划`
- **只有 1 个任务** → 直接 `/4-开发`
- **任务会修改同一文件** → 串行 `/4-开发`

## 流程

### 1. 读取设计文档
从 `/1-规划` 产出的 PRD 文档中提取：
- 目标描述
- 模块划分
- 接口约定
- 验收标准

如果文档信息不完整 → 追问补全。

### 2. 拆解独立子任务
调用 `/1-规划` 的任务拆解能力（阶段 5），生成 2-5 个独立子任务。

每个子任务包含：
- **Task ID** — T001, T002, ...
- **Title** — 简短标题
- **Description** — 要实现的功能切片
- **Files** — 需要修改/创建的文件列表
- **Acceptance Criteria** — 验收标准
- **Depends On** — 前置任务 ID（如果有）

**拆解原则**：
- 垂直切片优先：每个任务穿通一层（schema → 逻辑 → 测试）
- 无代码依赖：两个任务不能改同一文件
- 粒度适中：每个任务 30min-2h 能完成

展示给用户确认：
```
📋 并行开发计划

设计文档：docs/design-text-tools.md
子任务数：3

| # | 任务 | 分支 | 涉及文件 |
|---|------|------|----------|
| T1 | 字数统计器 | feat/multi-worker/T1-wc-tool | text_tools/wc.py, tests/test_wc.py |
| T2 | JSON美化器 | feat/multi-worker/T2-fmt | text_tools/fmt.py, tests/test_fmt.py |
| T3 | 行号添加器 | feat/multi-worker/T3-nl | text_tools/nl.py, tests/test_nl.py |

确认后将并行派发 3 个 worker，每个独立分支和 worktree。
```

### 3. 检查 Agent 配置（门禁）
枚举项目级和用户级 Agent 配置：
- 读取 `.claude/agents.yaml`、`.cursor/agents.yaml`、`.codex/agents.yaml`
- 确认开发 worker 的：
  - 名称（如 `worker-dev`）
  - 工具权限（Read、Write、Edit、Bash、pytest）
  - 模型（通常继承主会话模型）
  - worktree 能力（`isolation: worktree`）

**配置缺失或不兼容时停止并报告**：
```
❌ Agent 配置不满足并行开发要求：

- 未找到 worker-dev Agent 定义
- 或 worker-dev 缺少 worktree 隔离能力

建议：
1. 创建 .claude/agents.yaml 并定义 worker-dev
2. 或使用串行 /4-开发（安全默认）

是否继续串行开发？
```

**不得直接使用通用 Agent**，也不得静默回退。

### 4. Git 基线与任务分支
确认工作区干净：
```bash
git status --porcelain
```

创建集成分支：
```bash
git checkout -b feat/multi-worker-integration
```

为每个任务创建独立分支和 worktree：
```bash
git worktree add ../worktree-T1 -b feat/multi-worker/T1-wc-tool
git worktree add ../worktree-T2 -b feat/multi-worker/T2-fmt
git worktree add ../worktree-T3 -b feat/multi-worker/T3-nl
```

### 5. 并行派发
全部并行启动（不排队），每个 worker：
- 运行在独立 worktree
- 使用配置的开发 Agent（如 `worker-dev`）
- 调用 `/4-开发` 执行任务
- 传入：任务描述 + 验收标准 + 项目约束（不传对话历史）

```bash
# 伪代码
parallel_agents = []
for task in tasks:
    agent = Agent(
        prompt=f"执行任务 {task.id}: {task.description}\n验收标准: {task.acceptance}",
        agentType="worker-dev",
        isolation="worktree",
        label=f"worker-{task.id}"
    )
    parallel_agents.append(agent)

results = await Promise.all(parallel_agents)
```

### 6. 逐项验收
每个 worker 完成后，运行验收检查：
- 调用 `/vocabulary/code-review` 审查代码
- 运行 `pytest` 确认测试通过
- 运行 `mypy` 或 `ruff` 确认类型和 lint
- 检查验收标准是否满足

审查通过 → 标记为 ✅ 可合并
审查失败 → 标记为 ❌ 需修复，给出修复建议

### 7. 合并到集成分支
逐个合并通过验收的分支：
```bash
git checkout feat/multi-worker-integration
git merge --no-ff feat/multi-worker/T1-wc-tool
git merge --no-ff feat/multi-worker/T2-fmt
git merge --no-ff feat/multi-worker/T3-nl
```

清理 worktree：
```bash
git worktree remove ../worktree-T1
git worktree remove ../worktree-T2
git worktree remove ../worktree-T3
```

### 8. 最终报告
```
✅ 并行开发完成

集成分支：feat/multi-worker-integration
任务完成：3/3
- ✅ T1: 字数统计器（通过验收）
- ✅ T2: JSON美化器（通过验收）
- ✅ T3: 行号添加器（通过验收）

下一步：
- 运行完整测试套件确认集成
- 合并到 main 或创建 PR
```

## MUST 规则

1. **必须有设计文档。** 没有文档不进入拆解。
2. **子任务必须独立。** 不能修改同一文件。
3. **派发前必须检查 Agent 配置。** 配置缺失或不兼容时停止并报告，不得直接派发或静默降级。
4. **开发前必做版本控制。** 先确认工作区干净 → 创建集成分支 → 每个任务独立分支。
5. **每个 worker 干净上下文 + 独立分支。** 只传任务描述、验收标准、项目约束。
6. **全部并行派发。** 所有 worker 同时启动，不排队。
7. **结果逐项审查。** 每个 worker 产出都要过验收。
8. **通过后合并。** 审查通过的分支合并回集成分支。
9. **主 session 不参与开发。** 只做管控：拆解、版本控制、派发、审查、合并、报告。

## 与其他技能的关系

- **输入** — `/1-规划` 产出的设计文档（PRD）
- **调用** — `/1-规划`（任务拆解）→ N × `/4-开发`（并行）→ N × `/vocabulary/code-review`（验收）
- **输出** — 集成分支（所有任务合并后的代码）→ `/8-版本管理`（可选 PR）
