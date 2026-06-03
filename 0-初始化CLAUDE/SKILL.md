---
name: 0-初始化CLAUDE
description: One-shot CLAUDE.md initializer — generates project CLAUDE.md with luohe naming rule, context health check, and Karpathy coding guidelines. Use when starting a new project or resetting AI collaboration rules.
---

# 0-初始化CLAUDE — CLAUDE.md 初始化器

luohe，我来帮你一键生成项目的 CLAUDE.md。

生成的文件包含：
- **称呼规则** — 每次回复叫你 "luohe"，漏了说明上下文需要压缩/切换
- **Karpathy 编码准则** — 先想后写 / 简洁优先 / 外科手术式改动 / 目标驱动
- **项目信息 + 命令速查** — 占位符，生成后可按需补充

## 流程

### 1. 问候用户
- 以 "luohe" 称呼用户（本 skill 的核心规则在生成前就要遵守）

### 2. 检测当前目录
- 取当前工作目录名作为项目名
- 填入 template.md 的 `{project-name}` 占位符

### 3. 备份已有 CLAUDE.md（如有）
- 如果 `./CLAUDE.md` 已存在 → 复制为 `./CLAUDE.md.bak`
- 告知用户已备份

### 4. 生成 CLAUDE.md
- 读取 `references/template.md`
- 替换 `{project-name}` 为实际项目名
- 写入当前目录 `./CLAUDE.md`

### 5. 输出结果
- 告知已生成，展示内容概要
- 提醒用户可以在"项目信息"和"命令速查"部分补充内容

## 什么时候用

- 开始一个新项目时，初始化 AI 协作规则
- 现有项目的 CLAUDE.md 需要重置或更新
- AI 回复质量下降，怀疑是 CLAUDE.md 规则不清晰导致

## 案例

```
你：帮我初始化这个项目的 CLAUDE 文件
Claude：luohe，好的。检测到当前目录为 "data-pipeline"，
       将以此作为项目名生成 CLAUDE.md。
       已有 CLAUDE.md → 已备份为 CLAUDE.md.bak
       ✅ CLAUDE.md 已生成，包含称呼规则 + Karpathy 准则。
       可在"项目信息"和"命令速查"部分补充项目特定内容。
```
