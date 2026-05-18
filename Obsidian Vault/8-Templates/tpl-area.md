---
title: "{{area-name}}"
aliases: ["{{area-alias}}"]
tags:
  - type/area
  - domain/{{domain}}
created: {{date}}
updated: {{date}}
status: active
review-frequency: monthly
last-review: {{date}}
---

# {{area-name}}

> 这是一个需要持续关注的责任域。它没有截止日期，但需要定期回顾。

## 当前状态

（当前的整体状况描述）

## 长期目标

- 目标 1
- 目标 2

## 活跃项目

```dataview
TABLE status, deadline, priority
FROM "2-Projects"
WHERE contains(tags, "domain/{{domain}}") AND status = "active"
SORT priority ASC
```

## 关键指标

| 指标 | 当前值 | 目标值 |
|------|--------|--------|
| 指标1 | - | - |
| 指标2 | - | - |

## 定期回顾

### 最近回顾：{{date}}

- 进展：
- 待改进：
- 下步行动：

## 相关资源

- [[相关资源1]]
- [[相关MOC-1]]
