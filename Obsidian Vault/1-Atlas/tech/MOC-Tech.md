---
title: "MOC-Tech"
aliases: ["技术领域总览", "技术索引"]
tags:
  - type/moc
  - domain/tech
created: 2026-05-26
updated: 2026-05-26
status: active
---

# MOC-Tech

> 技术领域总览，聚合 AI 工具链、编程语言、开发实践等子领域的知识地图。

## 子领域

### 🛠️ 开发工具

- [[MOC-Tech Tools]] — Claude Code 生态、IDE 集成、模型切换、技能管理

### 🤖 AI 与技能

- [[Grill-Me 技能介绍与使用]] — 交互式需求拷问技能，通过追问澄清需求
- [[my-skills 开发工作流技能体系]] — 全流程标准化开发技能链

### 🐍 Python

- [[PyCharm 添加 Conda 环境报错 lateinit property 解决方案]] — PyCharm Conda 兼容性问题修复

## 相关项目

```dataview
TABLE status, deadline
FROM "2-Projects"
WHERE contains(tags, "domain/tech")
SORT deadline ASC
```

## 最近更新

```dataview
TABLE updated, confidence
FROM "4-Resources/tech"
SORT updated DESC
LIMIT 10
```
