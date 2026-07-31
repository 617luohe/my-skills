# My Skills Library

个人 skills 开发目录。每个 skill 独立文件夹，写好后可部署到 `.claude/skills/`。

📖 **使用说明书**：[USAGE.md](USAGE.md) — 每个技能的场景描述 + 案例演示。
🧭 **路由器**：`/0-询问luohe` — 不知道用哪个技能？直接问路由器。

## 目录结构

```
my-skills/
├── README.md / USAGE.md         — 索引与调用示例
├── 0-询问luohe/                 — 技能路由器（唯一入口）
├── vocabulary/                   — 可复用核心循环（被其他技能调用）
│   ├── grilling/                — 询问循环
│   ├── domain-modeling/         — 领域建模
│   ├── tdd/                     — TDD 循环
│   ├── code-review/             — 代码审查
│   └── diagnosing-bugs/         — Bug 诊断
├── my-note/                      — 知识管理技能体系（类比 vocabulary 层）
│   ├── noteall/                 — 唯一入口（三阶段流水线编排）
│   └── vault-publisher/         — 内部 Worker（固定 Vault 发布）
├── 0-启动/ ~ 6-最后整理/        — 阶段 0~6 开发流程
├── 0--*/                        — 阶段 0 扩展能力
├── multi-worker/                — 并行开发编排器（实验性）
└── scripts/                     — manifest 解析与受管技能部署脚本
```

## 命名规范

所有技能命名遵循以下约定：

| 类型 | 命名格式 | 示例 | 说明 |
|---|---|---|---|
| **阶段技能** | `N-中文名称` | `0-启动`、`1-规划`、`2-开发` | N 为阶段编号 0-6 |
| **扩展能力** | `0--英文名称` | `0--claude`、`0--laoyoutiao` | 双连字符标识阶段 0 扩展 |
| **路由器** | `0-询问luohe` | `0-询问luohe` | 唯一入口，独立前缀 |
| **vocabulary 层** | `vocabulary/英文名称` | `vocabulary/grilling` | 可复用核心，不直接调用 |
| **my-note 层** | `my-note/英文名称` | `my-note/noteall`、`my-note/vault-publisher` | 知识管理层，noteall 为唯一用户入口 |
| **独立方法论** | `英文或中文名称` | `multi-worker` | 不属于主流程的独立技能 |

**命名约束**：
- 阶段技能必须以 `N-` 开头（N=0-6），后接中文名称
- 扩展能力必须以 `0--` 开头，后接英文名称（双连字符区分单连字符阶段）
- vocabulary 层必须位于 `vocabulary/` 子目录下，使用英文名称
- 禁止在非阶段技能中使用 `N-` 格式（避免与阶段编号冲突）

## 调用分类

- **仅用户调用**：`0-询问luohe`、`0-启动`、`1-规划`、`5-版本管理`、`6-最后整理`、`multi-worker`、`0--neat-freak`、`0--dialectic`。只能由用户显式输入调用。
- **允许模型调用**：`2-开发`、`3-检查`、`4-调试`、`0--claude`、`0--laoyoutiao`、`0--tokenless`。模型可按描述自动调用，用户也可显式调用。
- **vocabulary 层**：`grilling`、`domain-modeling`、`tdd`、`code-review`、`diagnosing-bugs`。被其他技能调用，不直接暴露给用户。
- **my-note 层**：`noteall` 为唯一用户入口（三阶段流水线）；`vault-publisher` 为内部 Worker（model-invoked，由 noteall 调度），不直接暴露给用户。

## 核心优化（2026-07-26）

### 提取 vocabulary 层（可复用核心）

| 技能 | 职责 | 被谁调用 |
|---|---|---|
| **grilling** | 询问循环（批量/逐步模式、事实自查、决策推荐） | `/1-规划` |
| **domain-modeling** | 领域建模（维护仅含术语的 CONTEXT.md、独立 ADR、术语锐化） | `/1-规划` |
| **tdd** | TDD 循环（红-绿-重构、按行为风险确定测试、编码准则） | `/2-开发`、`/multi-worker` |
| **code-review** | 代码审查（Standards + Spec 双轴、并行子代理） | `/3-检查`、`/multi-worker` |
| **diagnosing-bugs** | Bug 诊断（六阶段：可比较观测→复现→假设→验证→修复→清理） | `/4-调试` |

**收益**：
- 阶段技能从 150+ 行简化到 30-80 行（委托到 vocabulary）
- 核心逻辑可复用（如 `grilling` 被多个技能调用）
- 边界清晰（vocabulary = 可复用层，阶段技能 = 编排入口）

### 简化阶段技能（委托编排）

| 技能 | 优化前 | 优化后 | 变化 |
|---|---|---|---|
| **1-规划** | 150+ 行（6 个子阶段内联） | 80 行（委托 grilling + domain-modeling） | ↓ 47% |
| **2-开发** | 80 行（TDD 流程内联） | 60 行（委托 tdd + code-review） | ↓ 25% |
| **3-检查** | 100 行（审查逻辑内联） | 50 行（委托 code-review） | ↓ 50% |
| **4-调试** | 100 行（诊断流程内联） | 50 行（委托 diagnosing-bugs） | ↓ 50% |

### 创建路由器（统一入口）

**0-询问luohe** — 中文版 ask-matt，包含：
- 主流程：想法 → 交付
- 上游：陌生代码只读调查后按结果进入规划、检查或调试；代码腐烂明确进入架构评估
- 支撑层：初始化、压缩、整理、洁癖审查
- 快速判断表（含一次性调查、原型验证和架构评估路径）

路由器同步到 CLAUDE.md 工作流路由表。

## 开发流程 Skills（阶段 0~6）

| # | 技能 | 职责 | 委托到 |
|---|---|---|---|
| 0 | **询问luohe** (`0-询问luohe`) | 路由器 — 不知道用哪个技能？问我 | - |
| 0 | **初始化CLAUDE** (`0--claude`) | 一键生成 CLAUDE.md | - |
| 0 | **启动** (`0-启动`) | 新项目最小脚手架（结构 + git + uv） | - |
| 0 | **洁癖审查** (`0--neat-freak`) | 知识库洁癖审查 | - |
| 0 | **Tokenless** (`0--tokenless`) | 超压缩沟通模式 | - |
| 1 | **规划** (`1-规划`) | 方案设计与任务拆解 | `vocabulary/grilling` + `vocabulary/domain-modeling` |
| 2 | **开发** (`2-开发`) | TDD 编码实现与自检；按行为风险决定自动化回归测试并记录例外验证证据 | `vocabulary/tdd` |
| 3 | **检查** (`3-检查`) | 由输入契约路由正式 Review、只建单、架构评估或根因修复；Review 输出 PASS/PASS WITH WARNINGS/FAIL | `vocabulary/code-review` |
| 4 | **调试** (`4-调试`) | 结构化调试；以可比较观测信号启动调查，并以稳定或统计可信复现验收修复 | `vocabulary/diagnosing-bugs` |
| 5 | **版本管理** (`5-版本管理`) | Git 版本控制 | - |
| 6 | **最后整理** (`6-最后整理`) | 会话收尾与沉淀 | - |

## 独立方法论 Skills

| 技能 | 职责 |
|---|---|
| **辩证矛盾分析法** (`0--dialectic`) | 六步法分析复杂问题、制定战略决策 |
| **老油条** (`0--laoyoutiao`) | Python 交付节奏管理（个人定制） |
| **leader** (`leader`) | 一句话想法 → agent 可独立执行的任务书 |
| **multi-worker** (`multi-worker`) | 并行开发编排器（实验性） |

## 知识管理 Skills（my-note 体系）

> 从 Obsidian vault 知识库技能体系提炼。`noteall` 为唯一用户入口，编排三阶段流水线；`vault-publisher` 为内部发布 Worker。

### 流水线概览

```
Intake → Curate → Publish（维护模式跳过 Intake）
```

| 技能 | 职责 | 阶段 |
|---|---|---|
| **noteall** (`my-note/noteall`) | 唯一入口：输入识别 + 处理倾向 + 三阶段编排 / 维护模式 | 入口 |
| **vault-publisher** (`my-note/vault-publisher`) | 固定 Vault 受控发布：校验、同步、受控暂存、commit、push | Publish |

- 内容类型差异（会议/阅读/日记/文章）由 noteall `references/profiles.yaml` 承担，不再各自为独立技能。
- 维护能力（批量/索引/MOC/文件整理）走 noteall 维护模式（`references/maintain.md`）。
- Git 收尾由 vault-publisher 确定性脚本完成，模型不自由组合 Git 命令。

## 部署方法

将 `my-skills/<skill-name>/` 复制到 `.claude/skills/<skill-name>/` 即可使用。

**一键同步**（推荐）：在项目根 `skills工程/` 下执行：

```powershell
.\my-skills\scripts\sync-skills.ps1
```

预览不写盘：

```powershell
.\my-skills\scripts\sync-skills.ps1 -DryRun
```

同步只管理本仓库拥有的技能，不会清空 `.claude/skills/`、`.cursor/skills/` 或 `.codex/skills/` 根目录。每个目标根会维护 `.my-skills-managed.json`，记录上一次成功同步时由本仓库管理的 skill 名称：

- 上次受管、但已不在当前 manifest 发布集中的名称会显示为 `REMOVE MANAGED` 并被删除；受管的当前名称会显示为 `UPDATE`，新名称显示为 `ADD`。
- 不在该清单中的现有目录永远不会被删除或覆盖。如果当前发布名称与这种目录同名，脚本会显示 `CONFLICT`、停止且不写入任何目标。
- 确认要由本仓库接管同名目录时，必须显式授权：

  ```powershell
  .\my-skills\scripts\sync-skills.ps1 -TakeOwnership
  ```

`-DryRun` 会准确输出 `ADD`、`UPDATE`、`REMOVE MANAGED` 和 `CONFLICT`，且不改磁盘。正式同步先为**所有**目标完成复制暂存；随后对每个宿主目标把将变更的受管目录和旧状态文件同卷重命名到私有 backup，再移入新内容并发布新状态。状态发布采用旧状态先重命名到 backup、再移动新状态的方式，不存在先删除旧状态的窗口。任一步失败会删除该目标及此前已提交目标的新内容，并恢复其旧目录和旧状态；若恢复本身失败，会汇总报告并保留 backup 现场。此补偿机制尽力恢复跨 `.claude`、`.cursor`、`.codex` 的一致性，但文件系统崩溃或恢复操作失败时不能保证严格全局原子性。目标根不存在时只警告，不创建未知父目录。

发布成员与版本的唯一来源是仓库根 `skills-manifest.yaml`：`schema_version: 1`、`repository_version: 1.0.0`。其中 19 个 `distribution: synchronized` 条目构成正式发布集；5 个 `layer: vocabulary` 条目是可复用核心。`scripts/skill_manifest.py` 使用 Python 标准库和受限 YAML 解析器读取该文件，无 PyYAML 依赖；不再维护第二份手写同步映射。

## 治理验证

验证源码治理规则（默认不检查部署目录）：

```bash
python scripts/validate_skills.py
python scripts/validate_skills.py --json
```

验证父目录下 `.claude/.cursor/.codex` 的受管清单和受管内容与源码一致，忽略未受管的额外技能：

```bash
python scripts/validate_skills.py --check-deployments
```

警告不影响退出码；治理错误返回非零退出码。CI 只运行 `python scripts/validate_skills.py` 静态治理验证，不依赖宿主部署目录。
