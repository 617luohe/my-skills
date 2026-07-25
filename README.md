# My Skills Library

个人 skills 开发目录。每个 skill 独立文件夹，写好后可部署到 `.claude/skills/`。

📖 **使用说明书**：[USAGE.md](USAGE.md) — 每个技能的场景描述 + 案例演示。

## 目录结构

```
my-skills/
├── README.md / USAGE.md  — 索引与调用示例
├── 0-启动/ ~ 9-最后整理/ — 阶段 0~9 开发流程
├── 0--*/                 — 阶段 0 扩展能力
├── multi-worker/         — 内置 Agent 并行开发入口（先检查 Agent 配置）
├── use-skills/           — 智能调度器入口
├── tools--*/             — 工具类 skills
└── scripts/              — manifest 解析与精确镜像部署脚本
```

## 调用分类

- **仅用户调用**：`0-启动`、`1-规划`、`8-版本管理`、`9-最后整理`、`use-skills`、`0--neat-freak`、`0--dialectic`。只能由用户显式输入 canonical 名称调用。
- **允许模型调用**：`2-分析`、`3-原型`、`4-开发`、`5-检查`、`6-优化`、`7-调试`、`0--claude`、`0--laoyoutiao`、`0--tokenless`、`multi-worker`。模型可按描述自动调用，用户也可显式调用。

> `multi-worker` 仅在已有清晰开发/设计文档，且确有可独立并行的开发任务时自动调用；缺少任一条件都不触发。

## 开发流程 Skills（阶段 0~9）

| # | 技能 | 合并来源 | 职责 |
|---|---|---|---|
| 0 | **初始化CLAUDE** (`0--claude`) | 新增 | 一键生成 CLAUDE.md：称呼规则 + Karpathy 准则 + 上下文健康检查 |
| 0 | **启动** | 配置环境 + 技能初始化 + 项目脚手架 | 新建项目：目录结构 → uv 环境 → pre-commit → 任务配置 |
| 0 | **洁癖审查** (`0--neat-freak`) | 新增 | 知识库洁癖审查 — 校准全局文档↔代码、尺寸体检、记忆毕业、消矛盾（减法/校准；本次会话沉淀交给 9-最后整理） |
| 0 | **Tokenless** (`0--tokenless`) | [caveman](../reference-skills/caveman/) | 超压缩沟通模式 — 删除填充语和客套，保留完整技术准确性与清晰度例外 |
| 1 | **规划** | 批量 grilling + 接口设计 + CONTEXT.md + 输出PRD + 拆解任务 | 默认集中询问同类独立决策；用户要求逐步时一次一问，确认共识后产出规划 |
| 2 | **分析** | 代码概览 | 查看不熟悉的代码，输出模块地图和数据流 |
| 3 | **原型** | 快速原型验证 | 用一次性代码验证设计决策，然后进入正式开发 |
| 4 | **开发** | TDD开发 + 编程准则 | 红-绿-重构，按准则写代码 |
| 5 | **检查** | 代码审查 + 验收反馈 | 审查代码质量 + 报告 bug |
| 6 | **优化** | 重构计划 + 架构改进 | 发现耦合点，做重构计划 |
| 7 | **调试** | 调试诊断 | 结构化排查 bug |
| 8 | **版本管理** | 新增（git 全流程） | 本地 git 版本管理，按需连接 GitHub |
| 9 | **最后整理** | 会话交接 + 修改总结 + 经验沉淀 + 结构整理 + 安全护栏 | 会话收尾：沉淀本次产出、清临时文件、交接、确认护栏（加法；全局同步交给 0--neat-freak） |

## 独立方法论 Skills

| 技能 | 来源 | 职责 |
|---|---|---|
| **辩证矛盾分析法** (`0--dialectic`) | 新增 | 哲学方法论 — 六步法分析复杂问题、制定战略决策 |
| **老油条** (`0--laoyoutiao`) | 新增 | Python 交付节奏管理 — 优先复用项目已有交付开关框架，无现成机制时回退到 branch_config.json，逐步向甲方展示优化成果 |
| **use-skills** | 智能调度器（入口） | 自然语言需求 → 自动匹配并执行对应技能 |
| **multi-worker** | 新增（多 Agent 入口） | 基于设计文档拆分独立任务，先核验 Agent 配置，再用独立 worktree 并行开发、审查和合并 |

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

同步后的三个目标是**完整镜像**：脚本先删除每个已存在目标目录下的全部子项，再仅复制 manifest 发布的 17 个核心 skills。目标根不存在时只警告，不创建未知父目录。

发布成员与版本的唯一来源是仓库根 `skills-manifest.yaml`：`schema_version: 1`、`repository_version: 1.0.0`。其中 17 个 `distribution: synchronized` 条目构成正式发布集；11 个 `distribution: host-provided` 工具条目只记录宿主提供关系。`scripts/skill_manifest.py` 使用 Python 标准库和受限 YAML 解析器读取该文件，无 PyYAML 依赖；不再维护第二份手写同步映射。

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
