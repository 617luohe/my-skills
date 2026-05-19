---
title: "Cursor 中配置 Claude Code 插件"
aliases: ["Cursor Claude Code 集成", "Cursor IDE 配置"]
tags:
  - type/resource
  - domain/tech/tools
created: 2026-05-18
updated: 2026-05-18
status: published
confidence: seed
source: ""
---

# Cursor 中配置 Claude Code 插件

> 一句话定义：在 Cursor 编辑器中安装和配置 Claude Code 扩展，使 Cursor 获得完整的 Agent 编程能力。

## 概述

Cursor 基于 VS Code 内核，原生兼容 VS Code 扩展市场。Claude Code 提供了官方 VS Code 扩展，可以直接在 Cursor 中安装使用。本文记录三种配置方式及其适用场景。

## 方式一：扩展市场直接安装（推荐）

Cursor 完全兼容 VS Code 扩展，直接安装最省事。

### 安装步骤

1. 打开 Cursor，按 `Ctrl+Shift+X` 打开扩展面板
2. 搜索 **"Claude Code"**，找到 Anthropic 官方发布的扩展
3. 点击 **Install**，安装完成后重启 Cursor
4. 左侧栏出现 Claude Code 图标，点击使用 Anthropic 账号登录

### 打开面板

| 方式 | 操作 |
|------|------|
| 编辑器工具栏 | 点击右上角 `···` → **Claude Code: Open** |
| 命令面板 | `Ctrl+Shift+P` → 搜索 "Claude Code: Open" |
| 快捷键 | `Ctrl+Esc`（Windows）/ `Cmd+Esc`（Mac） |

---

## 方式二：VSIX 手动安装

当 Claude Code 未能自动识别 Cursor 作为兼容 IDE 时，通过 VSIX 文件手动安装。

### 确认 Claude Code 已安装

```bash
claude
# 在会话中输入：
/doctor
# 预期输出：You are running Claude Code from your local installation
```

### 手动安装扩展

```bash
# 通过命令行安装
cursor --install-extension ~/.claude/local/node_modules/@anthropic-ai/claude-code/vendor/claude-code.vsix
```

或者在 Cursor 中操作：
1. `Ctrl+Shift+P` → **Extensions: Install from VSIX...**
2. 选择 `~/.claude/local/` 目录下的 `claude-code.vsix` 文件

安装后运行 `claude`，输入 `/ide` 确认 Cursor 已被检测到。

---

## 方式三：MCP Server 集成

通过 MCP 协议让 Cursor 的 AI 调用 Claude Code 的能力，适合团队协作和权限控制。

### 配置 MCP

在 `~/.cursor/mcp.json` 中添加：

```json
{
  "mcpServers": {
    "claude-code": {
      "type": "stdio",
      "command": "claude",
      "args": ["--mcp"]
    }
  }
}
```

### 带权限控制的配置

```json
{
  "mcpServers": {
    "claude-code": {
      "type": "stdio",
      "command": "claude",
      "args": ["--mcp", "--allowedTools", "Read,Write,Bash(npm test:*)"]
    }
  }
}
```

保存后重启 Cursor 即生效。

---

## 环境变量配置

### 用户级（~/.claude/settings.json）

```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "your-api-token",
    "ANTHROPIC_BASE_URL": "https://api.anthropic.com"
  }
}
```

### 项目级（.claude/settings.local.json）

```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "your-api-token",
    "ANTHROPIC_BASE_URL": "https://api.anthropic.com"
  }
}
```

> 项目级配置优先级高于用户级。`.settings.local.json` 适合存放个人敏感信息，建议加入 `.gitignore`。

---

## 配置 Skills

```bash
# 1. 克隆官方 skills 仓库
git clone https://github.com/anthropics/skills.git

# 2. 将需要的 skill 复制到配置目录
mkdir -p ~/.claude/skills
cp -r skills/pdf ~/.claude/skills/

# 3. 重启 Claude Code 面板，输入 / 即可看到可用 skills
```

也可使用 Skills Manager 进行统一的 skills 管理。

---

## Cursor 内置 AI vs Claude Code 扩展

| 特性 | Cursor 内置 AI | Claude Code 扩展 |
|------|---------------|-----------------|
| 工作模式 | 内联补全 + 对话 | 完整 Agent（自主读写文件、执行命令） |
| 代码修改 | 单文件内联编辑 | 跨文件自主编辑，支持 Diff 审查 |
| 终端操作 | 不直接操作终端 | 可运行终端命令 |
| 上下文 | 手动选择 | 自动分析整个代码库 |
| 权限 | 无分级 | 多级权限（Ask / Plan / Auto） |

两者互不冲突，建议同时使用，各取所长。

---

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| 扩展安装后侧边栏空白 | 在扩展设置中设置 `claude-code.apiVersion` 为 `2026-03`，或执行 `Developer: Reload Window` |
| 连接失败 | 确认 `~/.claude/settings.json` 中环境变量正确，API 令牌有效 |
| Claude Code 图标不出现 | 确保已打开一个文件（仅打开文件夹不够），重启 Cursor 或 Reload Window |
| 使用代理服务 | 修改 `ANTHROPIC_BASE_URL` 为代理地址，配合 CC Switch 一键切换 |

## 与其他概念的关系

- [[Claude Code Windows 安装与配置]] — 前置依赖，必须先安装 Claude Code CLI
- [[CC Switch 配置与使用]] — 可在 Cursor 中配合 CC Switch 切换模型供应商
- [[Skills Manager 技能管理]] — 管理 Cursor + Claude Code 的 skills

## 延伸阅读

- [[Cursor 编辑器使用技巧]]
- [[MCP 协议介绍与配置]]
