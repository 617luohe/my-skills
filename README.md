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
├── 0-启动/ ~ 9-最后整理/        — 阶段 0~9 开发流程
├── 0--*/                        — 阶段 0 扩展能力
├── multi-worker/                — 并行开发编排器（实验性）
├── tools--*/                    — 工具类 skills（11 个，host-provided）
└── scripts/                     — manifest 解析与精确镜像部署脚本
```

## 调用分类

- **仅用户调用**：`0-询问luohe`、`0-启动`、`1-规划`、`8-版本管理`、`9-最后整理`、`multi-worker`、`0--neat-freak`、`0--dialectic`。只能由用户显式输入调用。
- **允许模型调用**：`2-分析`、`3-原型`、`4-开发`、`5-检查`、`6-优化`、`7-调试`、`0--claude`、`0--laoyoutiao`、`0--tokenless`。模型可按描述自动调用，用户也可显式调用。
- **vocabulary 层**：`grilling`、`domain-modeling`、`tdd`、`code-review`、`diagnosing-bugs`。被其他技能调用，不直接暴露给用户。

## 核心优化（2026-07-26）

### 提取 vocabulary 层（可复用核心）

| 技能 | 职责 | 被谁调用 |
|---|---|---|
| **grilling** | 询问循环（批量/逐步模式、事实自查、决策推荐） | `/1-规划`、`/6-优化` |
| **domain-modeling** | 领域建模（维护 CONTEXT.md、ADR、术语锐化） | `/1-规划` |
| **tdd** | TDD 循环（红-绿-重构、测试策略、编码准则） | `/4-开发`、`/multi-worker` |
| **code-review** | 代码审查（Standards + Spec 双轴、并行子代理） | `/4-开发`、`/5-检查`、`/multi-worker` |
| **diagnosing-bugs** | Bug 诊断（六阶段：构建回路→复现→假设→验证→修复→清理） | `/7-调试` |

**收益**：
- 阶段技能从 150+ 行简化到 30-80 行（委托到 vocabulary）
- 核心逻辑可复用（如 `grilling` 被多个技能调用）
- 边界清晰（vocabulary = 可复用层，阶段技能 = 编排入口）

### 简化阶段技能（委托编排）

| 技能 | 优化前 | 优化后 | 变化 |
|---|---|---|---|
| **1-规划** | 150+ 行（6 个子阶段内联） | 80 行（委托 grilling + domain-modeling） | ↓ 47% |
| **4-开发** | 80 行（TDD 流程内联） | 60 行（委托 tdd + code-review） | ↓ 25% |
| **5-检查** | 100 行（审查逻辑内联） | 50 行（委托 code-review） | ↓ 50% |
| **7-调试** | 100 行（诊断流程内联） | 50 行（委托 diagnosing-bugs） | ↓ 50% |

### 创建路由器（统一入口）

**0-询问luohe** — 中文版 ask-matt，包含：
- 主流程：想法 → 交付
- 上游：陌生代码、难搞 bug、代码腐烂
- 支撑层：初始化、压缩、整理、洁癖审查
- 快速判断表（15 种常见情况）

**替代原 use-skills**，指向更新到 CLAUDE.md 工作流路由表。

## 开发流程 Skills（阶段 0~9）

| # | 技能 | 职责 | 委托到 |
|---|---|---|---|
| 0 | **询问luohe** (`0-询问luohe`) | 路由器 — 不知道用哪个技能？问我 | - |
| 0 | **初始化CLAUDE** (`0--claude`) | 一键生成 CLAUDE.md | - |
| 0 | **启动** (`0-启动`) | 新项目脚手架 | - |
| 0 | **洁癖审查** (`0--neat-freak`) | 知识库洁癖审查 | - |
| 0 | **Tokenless** (`0--tokenless`) | 超压缩沟通模式 | - |
| 1 | **规划** (`1-规划`) | 方案设计与任务拆解 | `vocabulary/grilling` + `vocabulary/domain-modeling` |
| 2 | **分析** (`2-分析`) | 代码理解与概览 | - |
| 3 | **原型** (`3-原型`) | 快速原型验证 | - |
| 4 | **开发** (`4-开发`) | TDD 编码实现 | `vocabulary/tdd` + `vocabulary/code-review` |
| 5 | **检查** (`5-检查`) | 代码审查与验收 | `vocabulary/code-review` |
| 6 | **优化** (`6-优化`) | 重构与架构改进 | - |
| 7 | **调试** (`7-调试`) | 结构化调试 | `vocabulary/diagnosing-bugs` |
| 8 | **版本管理** (`8-版本管理`) | Git 版本控制 | - |
| 9 | **最后整理** (`9-最后整理`) | 会话收尾与沉淀 | - |

## 独立方法论 Skills

| 技能 | 职责 |
|---|---|
| **辩证矛盾分析法** (`0--dialectic`) | 六步法分析复杂问题、制定战略决策 |
| **老油条** (`0--laoyoutiao`) | Python 交付节奏管理（个人定制） |
| **multi-worker** (`multi-worker`) | 并行开发编排器（实验性） |

## 工具类 Skills

| 目录 | 调用名 | 职责 |
|---|---|---|
| `tools--前端设计` | `/tools--前端设计` | 生产级前端界面设计与实现 |
| `tools--图表生成` | `/tools--图表生成` | 图表和信息图生成 |
| `tools--幻灯片生成` | `/tools--幻灯片生成` | 演示文稿创建与编辑 |
| `tools--技能工坊` | `/tools--技能工坊` | 创建、评估和改进 skills |
| `tools--数据可视化` | `/tools--数据可视化` | 图表、仪表盘与配色规范 |
| `tools--文档生成` | `/tools--文档生成` | Word 文档创建与编辑 |
| `tools--智能搜索` | `/tools--智能搜索` | 多源智能检索 |
| `tools--深度研报生成` | `/tools--深度研报生成` | 深度研究与研报生成 |
| `tools--画布设计` | `/tools--画布设计` | 画布式视觉设计 |
| `tools--网页测试` | `/tools--网页测试` | Web 应用交互测试 |
| `tools--表格生成` | `/tools--表格生成` | Excel 表格创建与分析 |

> 11 个 `tools--*` 目录在 `skills-manifest.yaml` 中标记为 `host-provided`、`sync: false`；本仓库保留其参考/封装源码，但同步脚本不复制也不修改它们的行为。

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

同步后的三个目标是**完整镜像**：脚本先删除每个已存在目标目录下的全部子项，再仅复制 manifest 发布的 17 个核心 skills + 5 个 vocabulary 技能。目标根不存在时只警告，不创建未知父目录。

发布成员与版本的唯一来源是仓库根 `skills-manifest.yaml`：`schema_version: 1`、`repository_version: 1.0.0`。其中 17 个 `distribution: synchronized` 条目构成正式发布集；11 个 `distribution: host-provided` 工具条目只记录宿主提供关系；5 个 `layer: vocabulary` 条目是可复用核心。`scripts/skill_manifest.py` 使用 Python 标准库和受限 YAML 解析器读取该文件，无 PyYAML 依赖；不再维护第二份手写同步映射。

`-DryRun` 会逐项输出 `REMOVE` 和 `COPY`，但不改磁盘。正式运行会对 `.claude/skills/`、`.cursor/skills/`、`.codex/skills/` 执行精确镜像。

## 治理验证

验证源码治理规则（默认不检查部署目录）：

```bash
python scripts/validate_skills.py
python scripts/validate_skills.py --json
```

验证父目录下 `.claude/.cursor/.codex` 的 skill 名称和内容哈希与源码完全一致：

```bash
python scripts/validate_skills.py --check-deployments
```

运行标准库 `unittest` 测试：

```bash
python -m unittest discover -s tests -v
```

警告不影响退出码；治理错误返回非零退出码。CI 只验证独立源码，不依赖宿主部署目录，也不运行行为模型评测。
