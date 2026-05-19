---
title: "Skills Manager 技能管理"
aliases: ["skills-manager", "技能管理器", "xingkongliang"]
tags:
  - type/resource
  - domain/tech/tools
created: 2026-05-18
updated: 2026-05-18
status: published
confidence: seed
source: "https://github.com/xingkongliang/skills-manager"
---

# Skills Manager 技能管理

> 一句话定义：Skills Manager 是一个跨平台桌面应用，用于统一管理跨 15+ AI 编程工具的 Agent Skills，支持安装、同步、分组、版本控制和多工具部署。

## 概述

Skills Manager（作者 xingkongliang / @JayTL00）解决了 AI 编程工具生态中 skills 分散管理的问题。不同的 AI 工具（Claude Code、Cursor、Codex、Gemini CLI 等）各有自己的 skills 目录和格式，手动同步耗时且容易出错。Skills Manager 提供统一的中央管理界面，一键同步到所有目标工具。

- **GitHub 仓库**：https://github.com/xingkongliang/skills-manager
- **技术栈**：Rust 后端 + React 19 + Tauri 2 桌面应用
- **许可协议**：MIT
- **支持工具数**：15+ 种 AI 编程工具

## 核心功能

### 统一技能库

中央技能目录 `~/.skills-manager`，支持从多种来源安装技能：
- **Git 仓库**：直接从 GitHub URL 安装
- **本地文件夹**：导入本地已有的技能
- **归档文件**：从 .zip / .tar.gz 安装
- **专用市场**：浏览和安装市场中的技能

### 多工具同步

通过符号链接或文件复制，跨以下工具同步技能：
Claude Code、Cursor、GitHub Copilot、Codex、Gemini CLI、Windsurf、Aider、OpenCode、OpenClaw 等 15+ 种。

### 项目级管理

可在项目的 `.claude/skills/` 目录管理技能，并与中央库双向同步。项目特有技能不会污染全局配置。

### 场景分组与即时切换

将技能分组为「场景」（Scenario），例如：
- **日常开发**：note-composer、info-digester
- **代码审查**：security-review、simplify
- **文档写作**：doc-coauthoring、obsidian-markdown

一键切换场景，自动启用/禁用对应技能组。

### 标签与过滤

支持为技能添加标签，通过标签快速过滤和查找。例如 `#p0`、`#writing`、`#code-review`。

### 文档预览

内置技能文档预览，无需打开文件即可查看 SKILL.md 内容。

### Git 版本控制

可选的 Git 备份功能，追踪技能变更历史。

## Windows 安装

### 前置条件

- Windows 10 或更高版本
- Claude Code 已安装
- Git 已安装

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/xingkongliang/skills-manager.git
cd skills-manager

# 2. 安装依赖
npm install

# 3. 启动开发模式（或构建发布版本）
npm run tauri dev

# 构建发布版本
npm run tauri build
```

构建完成后，在 `src-tauri/target/release/` 下找到 `.msi` 安装包。

### 首次配置

1. 启动 Skills Manager
2. 设置中央目录：默认 `~/.skills-manager`
3. 添加目标工具：选择你使用的 AI 工具（Claude Code、Cursor 等）
4. 工具会自动检测每个工具的 skills 目录位置

## 基本工作流

### 安装一个 Skill

```
1. 点击「添加技能」→ 选择来源（Git / 本地 / 市场）
2. 输入 GitHub URL 或选择本地路径
3. Skills Manager 自动解析 SKILL.md 元数据
4. 确认安装 → 自动同步到所有目标工具
```

### 创建场景

```
1. 点击「场景管理」→ 「新建场景」
2. 命名场景（如"日常写作"）
3. 勾选该场景需要启用的技能
4. 保存
```

### 同步到项目

```
1. 打开目标项目
2. 在 Skills Manager 中选择该项目
3. 选择要同步的技能 → 点击「同步到项目」
4. 技能的符号链接/副本写入项目 .claude/skills/
```

## 同类工具对比

| 工具 | 类型 | 支持工具数 | 特点 |
|------|------|-----------|------|
| **Skills Manager** (xingkongliang) | 桌面 GUI | 15+ | 场景分组、市场支持、Git 备份 |
| **skills-manage** (iamzhihuix) | 桌面 GUI | 20+ | Collections 组织、双语 UI |
| **skill-manager** (omrikais) | CLI (`sm`) | 2 | 符号链接部署、TUI 界面、MCP 服务器 |
| **Khazix 三件套** | CLI | 3+ | GitHub 导入、身份 ID、经验进化 |

### 选择建议

- **日常使用 + 多工具**：Skills Manager（桌面 GUI，操作直观）
- **极简 CLI 用户**：omrikais/skill-manager（命令 `sm`，轻量高效）
- **需要自动迭代进化**：Khazix-Skills 三件套（基于对话经验自动优化）

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| 技能同步后不生效 | 重启目标 AI 工具，确认 symlink 路径正确 |
| Tauri 构建失败 | 确保已安装 Rust 工具链（`rustup`）和 VS Build Tools |
| Git 克隆速度慢 | 设置代理或使用国内镜像 |
| 技能冲突 | 中央库优先于项目级，项目级同名技能会覆盖中央库配置 |

## 与其他概念的关系

- [[Claude Code Windows 安装与配置]] — 前置依赖
- [[Cursor 中配置 Claude Code 插件]] — Skills Manager 可管理的目标工具之一
- [[CC Switch 配置与使用]] — 模型切换 + 技能管理 = 完整 Claude Code 工作环境
- [[知识库体系设计]] — Skills Manager 可管理本知识库创建的 8 个自定义技能

## 技能管理最佳实践

### 目录结构约定

```
~/.skills-manager/          # 中央技能库
├── note-composer/          # 自定义技能
├── info-digester/
├── vault-wizard/
└── ...

项目/.claude/skills/        # 项目级技能
├── note-composer -> ../../.skills-manager/note-composer  # 符号链接
```

### 版本管理

- 所有 skill 通过 Git 仓库管理版本
- 在 SKILL.md 的 frontmatter 中标注版本号
- 使用 Skills Manager 的 Git 备份功能自动记录变更

### 场景模板推荐

| 场景名 | 包含技能 | 用途 |
|--------|---------|------|
| 知识库写作 | note-composer, note-polisher, vault-wizard | 日常笔记撰写 |
| 内容消化 | info-digester, reading-digester, concept-atomizer | 外部内容处理 |
| 知识库维护 | vault-cartographer, note-polisher | 定期审计和维护 |
| 会议记录 | meeting-minutes | 会议场景 |
| 全功能 | 以上全部 | 不确定时使用 |

## 延伸阅读

- [[Claude Code Skills 开发指南]]
- [[Tauri 2 桌面应用开发]]
