---
title: "CC Switch 配置与使用"
aliases: ["CC Switch", "Claude Code 模型切换"]
tags:
  - type/resource
  - domain/tech/tools
created: 2026-05-18
updated: 2026-05-18
status: published
confidence: seed
source: "https://github.com/farion1231/cc-switch"
---

# CC Switch 配置与使用

> 一句话定义：CC Switch 是一款开源跨平台桌面应用，用于统一管理和一键切换 Claude Code、Codex、Gemini CLI 等 AI 编程 CLI 工具的供应商/模型配置。

## 概述

在日常使用 Claude Code 时，可能需要在不同模型供应商之间切换（Anthropic 官方、DeepSeek、SiliconFlow、智谱 GLM 等）。手动修改 JSON 配置繁琐且容易出错。CC Switch 提供了图形化界面来管理这些配置，一键完成切换。

- **GitHub 仓库**：https://github.com/farion1231/cc-switch
- **支持工具**：Claude Code、Codex、Gemini CLI、OpenCode、OpenClaw
- **预设供应商**：50+ 模型供应商预设

## 前置条件

- **Node.js** ≥ 18
- **Git for Windows** 已安装
- **Claude Code** 已安装：`npm install -g @anthropic-ai/claude-code`

## Windows 安装

### 方式一：MSI 安装包（推荐）

1. 打开 Releases 页面：https://github.com/farion1231/cc-switch/releases
2. 下载最新版 `CC-Switch-vx.x.x-Windows.msi`
3. 双击安装，按向导完成，自动创建桌面快捷方式

### 方式二：绿色便携版

1. 下载 `CC-Switch-vx.x.x-Windows-Portable.zip`
2. 解压到任意目录
3. 双击 `CC-Switch.exe` 运行

## Claude Code 预处理

在配置 CC Switch 之前，需要让 Claude Code 跳过首次登录流程。

编辑 `C:\Users\<用户名>\.claude.json`，确保包含：

```json
{
  "hasCompletedOnboarding": true
}
```

> [!warning] JSON 格式
> 每个字段尾部加英文逗号（最后一个字段除外）。

## 配置模型供应商

### 添加供应商

1. 启动 CC Switch，顶部确认应用为 **Claude**
2. 点击右上角 **+** 按钮添加供应商
3. 在「预设」下拉选择厂商（如 DeepSeek、SiliconFlow、智谱 GLM、通义千问等）
4. 填入 **API Key**
5. 点击保存

### 切换模型

点击供应商卡片上的「**启用**」按钮，即完成切换。Claude Code 支持热重载，无需重启终端。

### 验证

```bash
claude
# 进入会话后输入
/model
```

可查看和切换当前模型。

## 自定义模型配置

在 CC Switch 的 JSON 配置中添加自定义环境变量：

```json
{
  "ANTHROPIC_BASE_URL": "https://api.your-model.com",
  "ANTHROPIC_AUTH_TOKEN": "your-api-key",
  "ANTHROPIC_MODEL": "your-model-name",
  "ANTHROPIC_SMALL_FAST_MODEL": "your-model-name"
}
```

## 配套 CLI 工具

### cc-model-switcher（命令行切换）

```bash
npm install -g cc-model-switcher
cc_switch              # 交互式选择
cc_switch deepseek     # 直接切换到指定模型
cc_switch --list       # 查看所有可用模型
```

配置文件：`C:\Users\<用户名>\.models.json`

### CCSC（会话级隔离）

```bash
npm install -g @terranc/ccsc
ccsc                   # 交互式选择，不影响全局配置
```

CCSC 从 CC Switch 的 SQLite 数据库读取配置，实现会话级切换，其他终端不受影响。

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| 切换后不生效 | Claude Code 支持热重载，如未生效尝试重启终端 |
| 首次启动提示登录 | CC Switch → 设置 → 通用 → 开启「跳过 Claude Code 初次安装确认」 |
| Git Bash 路径错误 | 设置环境变量 `CLAUDE_CODE_GIT_BASH_PATH=C:\Program Files\Git\usr\bin\bash.exe` |
| SmartScreen 拦截 | 点击「更多信息」→「仍要运行」 |
| DeepSeek V4 Pro 模型名 | 精确名称为 `deepseek-v4-pro[1m]`，含后缀 `[1m]` |

## 与其他概念的关系

- [[Claude Code Windows 安装与配置]] — 前置依赖
- [[Cursor 中配置 Claude Code 插件]] — CC Switch 切换的模型同样影响 Cursor 中的 Claude Code
- [[Skills Manager 技能管理]] — 配合 skills 管理，形成完整的 Claude Code 工作环境

## 延伸阅读

- [[DeepSeek API 接入指南]]
- [[SiliconFlow API 接入指南]]
