---
title: "MOC-{{title}}"
aliases: ["{{title}} 索引"]
tags:
  - type/moc
  - domain/{{domain}}
created: {{date}}
updated: {{date}}
status: active
---

# MOC-{{title}}

> 这是关于 **{{title}}** 的知识地图，汇集了该领域的所有核心概念、项目和相关资源。

## 核心概念

- [[概念A]] — 一句话描述
- [[概念B]] — 一句话描述

## 子主题

### {{子主题1}}

- [[相关笔记1]]
- [[相关笔记2]]

### {{子主题2}}

- [[相关笔记3]]
- [[相关笔记4]]

## 相关项目

```dataview
TABLE status, deadline
FROM "2-Projects"
WHERE contains(tags, "domain/{{domain}}")
SORT deadline ASC
```

## 延伸阅读

- [[相关MOC-1]]
- [[相关MOC-2]]

## 待探索

- [ ] 尚需覆盖的主题
- [ ] 需要深入研究的领域

## 最近更新

```dataview
TABLE updated, confidence
FROM "4-Resources"
WHERE contains(tags, "domain/{{domain}}")
SORT updated DESC
LIMIT 10
```
