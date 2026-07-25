---
name: multi-worker
description: 并行开发编排 — 读设计文档 → 拆解独立子任务 → git 基线+独立分支 → spawn 多个 worker agent 并行开发 → 收集审查 → 合并。触发词：并行开发、multi-worker、分头开发、多路并行、同时开发、并行实现、多 worker。
---

# multi-worker — 并行开发编排

将一个设计文档拆成 N 个独立子任务，每个子任务在独立的 git 分支上并行开发，完成后合并回集成分支。主 session 只做管控。

## 适用场景

- AI 已分析出多个优化方向，都想要
- 主 AI 已留下设计文档，需要并行实现
- 多个模块彼此独立，可以同时开工
- 不想让一个 agent 的上下文被其他任务污染

## 不适用

- 任务有强依赖关系（A 完成后 B 才能开始）→ 先用 `/1-规划` 拆解，再按依赖顺序逐项执行
- 还不确定要做什么 → 先用 `/1-规划` 出设计文档

## MUST 规则

1. **必须有设计文档。** 用户提供路径或直接粘贴。没有文档不进入拆解。
2. **子任务必须独立。** 不能有代码依赖。有依赖的拆成一组或标注顺序。
3. **派发前必须检查 Agent 配置。** 枚举项目级和用户级 Agent 定义，确认开发 worker 的名称、工具权限、模型和 worktree 能力；配置缺失或不兼容时停止并报告，不得直接派发或静默降级。
4. **开发前必做版本控制。** 先确认工作区干净 → 创建集成分支 → 每个任务独立开发分支。不跳过。
5. **每个 worker 干净上下文 + 独立分支。** 只传 3 样东西：任务描述 + 相关文件路径 + 项目约束。不传对话历史。
6. **全部并行派发。** 所有 worker 同时启动，不排队等。
7. **结果逐项审查。** 每个 worker 产出都要过一遍：测试通过、类型安全、lint 干净。
8. **通过后合并。** 审查通过的 worker 分支合并回集成分支。失败的单独处理。
9. **主 session 不参与开发。** 只做管控：拆解、版本控制、派发、审查、合并、报告。

## 执行流程

### 阶段 1 — 接收设计文档

用户提供设计文档（文件路径或直接粘贴内容）。

如果是文件路径：
- 读取文件内容
- 确认文档包含：目标描述、模块划分、接口约定、验收标准

如果文档信息不完整 → 追问补全后再进入阶段 2。

### 阶段 2 — 拆解子任务

基于设计文档，拆成 2-5 个独立子任务。每个子任务：

```json
{
  "task_id": "T1",
  "slug": "wc-tool",
  "title": "字数统计器",
  "description": "做什么、怎么做、边界在哪",
  "files": ["需要修改/创建的文件列表"],
  "context": "只传必要背景：项目类型+关键依赖+相关接口",
  "acceptance": ["可验证的完成标准"]
}
```

**拆解原则**：
- 垂直切片优先：每个任务穿通一层（schema → 逻辑 → 测试）
- 无代码依赖：两个任务不能改同一文件
- 粒度适中：每个任务 30min-2h 能完成
- 每个任务生成唯一 slug（英文短名，用于分支名）

拆完后展示给用户确认：

```
📋 并行开发计划

设计文档：docs/design-text-tools.md
子任务数：3

| # | 任务 | 分支 | 涉及文件 |
|---|------|------|----------|
| T1 | 字数统计器 | feat/multi-worker/T1-wc-tool | text_tools/wc.py, tests/test_wc.py |
| T2 | JSON美化器 | feat/multi-worker/T2-fmt | text_tools/fmt.py, tests/test_fmt.py |
| T3 | 行号添加器 | feat/multi-worker/T3-nl | text_tools/nl.py, tests/test_nl.py |

基线分支：feat/multi-worker-text-tools-20260724
```

确认开始并行开发？[Y / 调整 / 取消]

### 阶段 3 — Agent 配置与版本控制准备（CRITICAL）

用户确认后，必须先检查 Agent 配置，再完成 git 操作；两者都通过后才能派发 worker。

#### 3a — 检查 Agent 配置

1. 枚举项目级和用户级 Agent 配置目录（以当前宿主实际配置路径为准）。
2. 读取可用 Agent 定义，核对：名称、工具权限、模型、是否支持 `worktree` 隔离。
3. 优先选择已配置的开发 worker；不得假定 `worker-dev` 一定存在。
4. 未找到合适配置、权限不足或不支持隔离 → 停止流程，报告缺口和建议配置，不得直接调用 Agent。
5. 把确认后的 Agent 名称和关键能力写入并行开发计划，供审查时核对。

#### 3b — 检查工作区

```bash
git status --porcelain
```

- 有未提交变更 → 提示用户先提交或暂存，暂停流程
- 工作区干净 → 继续

#### 3c — 创建集成分支（基线）

```bash
git checkout -b feat/multi-worker-<project-slug>-<YYYYMMDD>
```

这是最终合并的目标分支。所有 worker 分支都从此分叉。

#### 3d — 为每个任务创建开发分支

```bash
git checkout -b feat/multi-worker/<T1-slug> feat/multi-worker-<project-slug>-<YYYYMMDD>
git checkout feat/multi-worker-<project-slug>-<YYYYMMDD>   # 回到基线
git checkout -b feat/multi-worker/<T2-slug> feat/multi-worker-<project-slug>-<YYYYMMDD>
git checkout feat/multi-worker-<project-slug>-<YYYYMMDD>   # 回到基线
...
```

最终当前分支回到基线 `feat/multi-worker-<project-slug>-<YYYYMMDD>`。

**分支命名规范**：
- 集成分支：`feat/multi-worker-<project-slug>-<YYYYMMDD>`
- 开发分支：`feat/multi-worker/<T{N}>-<task-slug>`

完成后输出：

```
🔀 版本控制就绪

集成分支：feat/multi-worker-text-tools-20260724
开发分支：
  feat/multi-worker/T1-wc-tool → T1 字数统计器
  feat/multi-worker/T2-fmt     → T2 JSON美化器
  feat/multi-worker/T3-nl      → T3 行号添加器

开始并行派发 worker...
```

### 阶段 4 — 并行派发

一次性 spawn 所有 worker agent。每个 worker：

1. **Agent 类型**：使用阶段 3 已核验的开发 worker 配置；禁止硬编码未验证的 `worker-dev`，也禁止静默回退到 `general-purpose`
2. **隔离模式**：`worktree`（基于自己的开发分支创建独立工作区）
3. **Prompt 内容**：只传任务 JSON + 分支信息 + 项目约束

**Worker prompt 模板**：

```
你是独立开发 agent。在专属 git 分支上完成一个任务。

## Git 分支
你工作在分支 `{branch_name}` 上，基于集成分支 `{base_branch}` 分叉。
所有改动提交到此分支。

## 任务
{任务 JSON}

## 项目约束
- 语言：Python 3
- 测试框架：pytest
- 类型检查：mypy
- Lint：ruff
- 代码风格：遵循现有项目风格

## 要求
1. TDD：先写测试，再实现
2. 只改 task.files 中列出的文件
3. 完成后运行 pytest + mypy + ruff
4. 所有改动 git add + git commit（commit message 包含 task_id）
5. 输出结构化结果
```

**并行派发**：所有 worker 同时启动，不等待。用 Agent 工具的 `run_in_background: true`。

### 阶段 5 — 收集与审查

所有 worker 完成后，逐项审查：

1. **测试通过**：pytest 全部通过
2. **类型安全**：mypy 无新错误
3. **Lint 干净**：ruff 无新警告
4. **符合设计**：产出与设计文档一致
5. **分支干净**：git status 确认无未提交变更

审查结果表：

```
| 任务 | 分支 | 状态 | 测试 | mypy | ruff | 提交 |
|------|------|------|------|------|------|------|
| T1 字数统计器 | feat/multi-worker/T1-wc-tool | ✅ done | 5/5 | clean | clean | abc1234 |
| T2 JSON美化器 | feat/multi-worker/T2-fmt     | ✅ done | 8/8 | clean | clean | def5678 |
| T3 行号添加器 | feat/multi-worker/T3-nl      | ❌ failed | 3/5 | clean | 2 warn | — |
```

### 阶段 6 — 合并

对审查通过的 worker 分支，逐一合并到集成分支：

```bash
git checkout <base_branch>
git merge feat/multi-worker/<T{N}>-<slug> --no-ff -m "merge: <task_title>"
```

合并策略：
- 每个通过的分支独立 merge（`--no-ff` 保留分支痕迹）
- 有冲突 → 暂停，报告冲突文件和冲突内容，人工处理
- 全部无冲突合并完成 → 继续

合并结果：

```
🔀 合并完成

集成分支：feat/multi-worker-text-tools-20260724
已合并：
  ✅ feat/multi-worker/T1-wc-tool — 字数统计器
  ✅ feat/multi-worker/T2-fmt     — JSON美化器
未合并：
  ❌ feat/multi-worker/T3-nl      — 审查未通过，需修复后单独合并
```

### 阶段 7 — 处理失败

对失败的 worker：
- **首次失败**：读失败原因 + git log 查看分支状态 → 给 1 次修复机会（重新 spawn 在同一分支上继续）
- **再次失败**：报告用户，标记该分支为需要人工处理，不阻塞其他分支合并
- **合并冲突**：两个 worker 意外改了同一文件 → 暂停合并，展示冲突内容，人工处理

### 阶段 8 — 收尾

全部通过后输出汇总：

```
✅ 并行开发完成

设计文档：docs/design-text-tools.md
总任务数：3 | 通过：3 | 失败：0

集成分支：feat/multi-worker-text-tools-20260724
开发分支（已合并）：
  feat/multi-worker/T1-wc-tool
  feat/multi-worker/T2-fmt
  feat/multi-worker/T3-nl

产出物：
- text_tools/wc.py（新增）
- text_tools/fmt.py（新增）
- text_tools/nl.py（新增）
- tests/test_wc.py（新增）
- tests/test_fmt.py（新增）
- tests/test_nl.py（新增）

下一步：git checkout feat/multi-worker-text-tools-20260724 查看完整结果
         确认无误后合并到主分支
```

## 触发方式

```
/multi-worker <设计文档路径>
```

或自然语言：
- "并行开发这些模块：..."
- "分头实现以下任务：..."
- "同时开发：..."
- "把设计文档里的任务并行做了"

## 分支策略总结

```
main / master
  └── feat/multi-worker-<project>-<date>     ← 集成分支（基线）
        ├── feat/multi-worker/T1-<slug>      ← Worker 1 独占
        ├── feat/multi-worker/T2-<slug>      ← Worker 2 独占
        └── feat/multi-worker/T3-<slug>      ← Worker 3 独占
              ↓ 审查通过后 merge --no-ff
        feat/multi-worker-<project>-<date>   ← 合并回基线
              ↓ 最终确认后
        main / master                        ← 合入主分支
```

## 与现有技能的关系

| 场景 | 用 |
|------|-----|
| 设计文档已有，多个独立任务 → 并行开发 | `/multi-worker` |
| 需要从头规划 → 设计文档 → 并行开发 | `/1-规划` → `/multi-worker` |
| 任务有依赖，必须顺序执行 | `/1-规划` 拆解后按依赖顺序逐项执行 |
| 版本控制相关操作 | `/8-版本管理`（multi-worker 内部调用 git 命令） |

## 边缘情况

**工作区不干净**：提示用户 `git status` 输出，要求先处理（commit / stash / clean）。不自动 stash。

**设计文档不完整**：追问补全。至少需要：目标、范围、接口约定。

**子任务 > 5 个**：拆成多批，每批 ≤ 5 个同时跑。每批创建独立集成分支（`feat/multi-worker-<project>-batch1-<date>`）。先跑第一批，合并后再第二批。

**所有 worker 都失败**：检查是否是设计文档本身有问题。向用户报告，集成分支保留为空（仅有 git 初始化），等待修正设计后重跑。

**合并冲突**：两个 worker 意外修改同一文件 → 报告冲突文件和 diff，标记该批合并暂停，人工处理。

**Worker 超时**：默认超时 10 分钟。超时的 worker 标记失败，不重试。用户可手动 `git checkout <worker-branch>` 继续开发。

**部分合并失败**：已合并的分支不回滚。未合并的保留在开发分支上，用户可手动处理。
