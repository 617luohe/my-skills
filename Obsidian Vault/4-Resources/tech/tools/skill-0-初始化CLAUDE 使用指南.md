---
title: "skill-0-初始化CLAUDE 使用指南"
aliases: ["初始化CLAUDE指南"]
tags:
  - type/resource
  - domain/tech/tools
  - topic/skills-guide
created: 2026-06-18
status: published
confidence: sprout
source: "https://github.com/617luohe/my-skills"
skill: "0-初始化CLAUDE"
---

# 0-初始化CLAUDE — CLAUDE.md 初始化器

> 一句话：一键生成或注入 CLAUDE.md，确保 AI 每次回复都叫你 luohe，并遵循 Karpathy 编码准则。

## 什么时候用

| 场景 | 说明 |
|------|------|
| 新项目启动后 | 0-启动 建好项目骨架后，立即初始化 CLAUDE.md |
| 接手已有项目 | 项目已有 CLAUDE.md 但没有称呼规则，注入一段而不动其他内容 |
| 重置 AI 协作规则 | 想用标准模板替换旧的 CLAUDE.md |

**不适用**：项目已有完整的 CLAUDE.md 且已包含 luohe 称呼规则——此时技能检测到后会跳过，不做任何修改。

## 工作流程

```
检测当前目录 CLAUDE.md
  │
  ├── 不存在 → 读取 references/template.md → 替换项目名 → 写入新文件
  │
  ├── 存在但无称呼规则 → 在第一个标题后注入 luohe 规则 → 不动其他内容
  │
  └── 存在且已有规则 → 跳过，告知无需修改
```

## 案例演示

### 案例 1：新项目——全量生成

```
用户：/0-初始化CLAUDE

Claude：luohe，检测到当前目录 "data-pipeline"。

       📄 CLAUDE.md 不存在 → 新建完整文件

       ✅ 已生成 CLAUDE.md，包含：
       - 称呼规则（每次回复叫我 luohe）
       - Karpathy 编码准则（先想后写 / 简洁优先 / 手术刀式改动 / 目标驱动）
       - 项目信息占位 + 命令速查占位

       你可以在"项目信息"和"命令速查"部分补充项目特定内容。
```

生成的 CLAUDE.md 内容示例：

```markdown
# data-pipeline

## 称呼规则

- 每次回复必须先叫我 **luohe**
- 如果某次回复忘了叫我 luohe → 说明上下文已膨胀，需要压缩或切换会话

## Karpathy 编码准则

### 1. 先想后写
- 明确假设，不确定就问
- 如果有多种解读，列出而不是暗中选一个
- 如果有更简单的方案，说出来

### 2. 简洁优先
- 只写解决问题的最小代码
- 不需要的功能不加、只用一个地方的抽象不做

### 3. 手术刀式改动
- 只动必须动的代码
- 不改没坏的东西
- 匹配现有风格

### 4. 目标驱动
- 每个任务转化为可验证的目标

## 项目信息

（在此补充项目简介、技术栈、目录结构等）

## 命令速查

（在此补充常用命令，如 dev / build / test / deploy 等）
```

### 案例 2：已有项目——精准注入

```
用户：/0-初始化CLAUDE

Claude：luohe，检测到当前目录 "payment-service"。

       📄 CLAUDE.md 已存在，但缺少称呼规则 → 嵌入

       原文件：
       # payment-service
       ## 技术栈
       ...

       注入后：
       # payment-service
       
       ## 称呼规则
       - 每次回复必须先叫我 **luohe**
       ...

       ## 技术栈
       ...（后续内容完全未变）

       ✅ 已嵌入称呼规则，其余内容未变。
```

### 案例 3：无需修改——智能跳过

```
用户：/0-初始化CLAUDE

Claude：luohe，当前 CLAUDE.md 已包含称呼规则，无需修改。
```

## 注意事项

- 已有 CLAUDE.md 时**只注入 luohe 规则，不动其他内容**——不会破坏你手动添加的项目信息
- 如果 CLAUDE.md 有 YAML frontmatter（`--- ... ---`），注入时会跳过 frontmatter 块
- 模板文件位于 `references/template.md`，部署技能时需一起复制

## 相关技能

- [[skill-0-启动 使用指南]] — 先搭项目骨架，再初始化 CLAUDE
- [[skill-9-最后整理 使用指南]] — 收尾时会同步 CLAUDE.md 与代码
