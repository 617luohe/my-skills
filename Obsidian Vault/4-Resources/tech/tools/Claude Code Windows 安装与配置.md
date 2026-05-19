---
title: "Claude Code Windows 安装与配置"
aliases: ["Claude Code setup", "Windows 环境配置"]
tags:
  - type/resource
  - domain/tech/tools
created: 2026-05-18
updated: 2026-05-18
status: published
confidence: seed
---

# Claude Code Windows 安装与配置

> 一句话定义：在 Windows 系统上从零安装、配置并启动 Claude Code CLI 的完整操作步骤。

## 概述

Claude Code 是 Anthropic 推出的命令行 AI 编程助手。本文记录 Windows 环境下的完整安装链路，包括 Node.js 环境准备、镜像加速、认证配置和模型切换。

## 环境准备

### Node.js 版本检查
```bash
node -v
```
要求 Node.js 18+，如未安装则先去 [nodejs.org](https://nodejs.org) 下载 LTS 版本。

### npm 版本检查
```bash
npm -v
```
Node.js 自带 npm，此步仅确认可用。

### npm 国内镜像（可选但推荐）
```bash
npm config set registry https://registry.npmmirror.com/
```
设置淘宝/阿里镜像源，显著提升国内下载速度。

### Git 版本检查
```bash
git -v
```
Claude Code 的部分功能（如版本对比、分支操作）依赖 Git。

## 安装 Claude Code

### 安装命令
```bash
npm install -g @anthropic-ai/claude-code
```

### 验证安装
```bash
claude --version
```
输出版本号即安装成功。

## 启动与认证

### 启动
```bash
claude
```
首次启动会自动引导认证流程。

### 认证配置（.claude.json）

Claude Code 的用户配置存储在 `~/.claude.json` 中。关键配置项：

```json
{
  "hasCompletedOnboarding": true
}
```

> [!warning] JSON 格式注意
> 每个字段尾部需加英文逗号（最后一个字段除外），否则 JSON 解析失败。

## 模型切换

### 查看/切换模型
```
/model
```
在 Claude Code 对话中直接输入 `/model` 即可查看和切换可用模型。

### DeepSeek V4 Pro 模型名称
```
deepseek-v4-pro[1m]
```
精确模型名包含 `[1m]` 后缀，切换时需完整输入。

## 安装链路总结

```
node -v          → 确认 Node.js ≥ 18
npm -v           → 确认 npm 可用
npm config set   → 设置国内镜像（可选）
git -v           → 确认 Git 可用
npm install -g   → 安装 Claude Code
claude --version → 验证安装
claude           → 启动并完成认证
/model           → 切换模型
```

## 常见问题

### 网络代理
如果位于防火墙/代理后：
```bash
set HTTPS_PROXY=http://proxy:port
set HTTP_PROXY=http://proxy:port
```

### SSL/TLS 推送到 GitHub 失败
Windows 下 Git 推送到 GitHub 可能遇到 `schannel` SSL 错误：
```bash
git config --global http.sslBackend openssl
```

### 权限弹窗
首次使用时 Windows Defender 或企业安全策略可能拦截网络访问，需在防火墙中添加例外。

## 参考来源

- Claude Code 官方文档
- 实测环境：Windows 10 IoT Enterprise LTSC 2021 + Git Bash

## 延伸阅读

- [[开发环境搭建]]
- [[终端工具配置]]
- [[知识库体系设计]]
