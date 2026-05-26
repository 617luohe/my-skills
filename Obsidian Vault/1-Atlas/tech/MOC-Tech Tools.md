---
title: "MOC-Tech Tools"
aliases: ["技术工具索引", "AI 开发工具"]
tags:
  - type/moc
  - domain/tech/tools
created: 2026-05-26
updated: 2026-05-26
status: active
---

# MOC-Tech Tools

> AI 编程工具链与辅助开发工具的知识地图，涵盖 Claude Code 生态、模型切换、技能管理、IDE 集成等。

## Claude Code 生态

- [[Claude Code Windows 安装与配置]] — Windows 系统从零安装 Claude Code CLI 的完整步骤
- [[CC Switch 配置与使用]] — 一键切换 Claude Code 供应商/模型的开源桌面应用
- [[Skills Manager 技能管理]] — 跨 15+ AI 工具的 Agent Skills 统一管理平台
- [[my-skills 开发工作流技能体系]] — 全生命周期 Claude Code 技能链，串联需求到收尾

## IDE 集成

- [[Cursor 中配置 Claude Code 插件]] — 三种方式在 Cursor 中集成 Claude Code 扩展

## 子主题

### 环境与部署

- Claude Code CLI 安装与认证
- 使用 CC Switch 切换模型供应商
- 使用 Skills Manager 部署技能

### 技能开发

- 通过 my-skills 体系实现标准化开发工作流
- Skills 的跨工具同步与版本管理

## 相关项目

```dataview
TABLE status, deadline
FROM "2-Projects"
WHERE contains(tags, "domain/tech/tools")
SORT deadline ASC
```

## 延伸阅读

- [[MOC-Tech]] — 技术领域总览

## 待探索

- [ ] Cursor 内置 AI 与 Claude Code 扩展的深度对比
- [ ] MCP 协议的高级配置
- [ ] 更多 AI 编程工具的接入（Codex、Gemini CLI、Windsurf）

## 最近更新

```dataview
TABLE updated, confidence
FROM "4-Resources/tech/tools"
SORT updated DESC
LIMIT 10
```
