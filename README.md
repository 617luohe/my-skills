# My Skills Library

个人 skills 开发目录。每个 skill 独立文件夹，写好后可部署到 `.claude/skills/`。

📖 **使用说明书**：[USAGE.md](USAGE.md) — 每个技能的场景描述 + 案例演示。

## 目录结构

```
my-skills/
├── README.md / USAGE.md  — 索引与调用示例
├── 0-启动/ ~ 9-最后整理/ — 阶段 0~9 开发流程
├── 0--*/                 — 阶段 0 扩展能力
├── use-skills/           — 智能调度器入口
├── tools--*/             — 工具类 skills
└── scripts/              — 部署脚本与映射
```

## 开发流程 Skills（阶段 0~9）

| # | 技能 | 合并来源 | 职责 |
|---|---|---|---|
| 0 | **初始化CLAUDE** (`0--claude`) | 新增 | 一键生成 CLAUDE.md：称呼规则 + Karpathy 准则 + 上下文健康检查 |
| 0 | **启动** | 配置环境 + 技能初始化 + 项目脚手架 | 新建项目：目录结构 → uv 环境 → pre-commit → 任务配置 |
| 0 | **构建索引** (`0--graphify`) | [graphify](https://github.com/safishamsi/graphify) | 将代码/文档/媒体构建为可查询知识图谱（graphify-out/） |
| 0 | **洁癖审查** (`0--neat-freak`) | 新增 | 知识库洁癖审查 — 校准全局文档↔代码、尺寸体检、记忆毕业、消矛盾（减法/校准；本次会话沉淀交给 9-最后整理） |
| 0 | **Tokenless** (`0--tokenless`) | [caveman](../reference-skills/caveman/) | 超压缩沟通模式 — 删除填充语和客套，保留完整技术准确性与清晰度例外 |
| 1 | **规划** | 方案追问 + 接口设计 + 领域术语 + 输出PRD + 拆解任务 | 写代码前理清方案，输出 PRD 和任务清单 |
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
| **辩证矛盾分析法** | 新增 | 哲学方法论 — 六步法分析复杂问题、制定战略决策 |
| **老油条** | 新增 | Python 交付节奏管理 — branch_config.json 驱动模块实现选择，逐步向甲方展示优化成果 |
| **use-skills** | 智能调度器（入口） | 自然语言需求 → 自动匹配并执行对应技能 |
| **自动迭代** | 新增（编排层） | 多轮闭环编排 — 五阶段 PDCA 自动推进任务链，门禁驱动直到闭环或跳出，主控+工人模式防上下文膨胀 |
| **Agent 统筹** (`0--Agent统筹`) | [fable-the-boss](../reference-skills/fable-the-boss/) 中文化整合 | 统一组织、分工、调度和验收 Codex、Cursor 等外部智能体 |

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

> 工具目录是本仓库的参考/封装源码，当前不在 `scripts/sync-map.json` 的一键同步范围；部署由宿主环境的同名 skill 提供。

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

同步范围由 `scripts/sync-map.json` 决定；当前包括 10 个阶段 skills 与 9 个完整名称 skills，共 19 个。目标为 `.claude/skills/`、`.cursor/skills/`、`.codex/skills/`。阶段 1~9 保留完整中文目录名，阶段 0 扩展保留 `0--*` 前缀。
