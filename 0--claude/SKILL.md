---
name: 0--claude
description: One-shot CLAUDE.md initializer — creates a new CLAUDE.md from the single-source template (称呼规则 + Caveman 简洁规则 + Karpathy 编码准则 + 工作流路由 + 支撑层), or injects only the missing rule blocks into an existing CLAUDE.md. Non-destructive, structural detection (no fuzzy string matching). 触发词：初始化CLAUDE、创建CLAUDE.md、CLAUDE规则、caveman、karpathy、工作流路由。
---

# 0--claude — CLAUDE.md 初始化器

luohe，我来处理项目的 CLAUDE.md。

**唯一数据源**：所有规则块的正文只存在于 `references/template.md`。本 SKILL.md 不再内联任何规则正文——读模板、切块、注入，改规则只改模板一处。

核心逻辑：
- **没有 CLAUDE.md** → 用 template.md 新建完整文件
- **已有 CLAUDE.md** → 结构化检测四个规则块，缺失则从模板切出对应块注入，已有则跳过
- **四个块都在** → 告知无需改动，不写文件

## MUST 规则

1. **模板是唯一源。** 规则正文一律从 `references/template.md` 读取，禁止在别处（含本文件）复制粘贴规则文字。
2. **非破坏式注入。** 已有内容一字不动，只在缺失位置嵌入。
3. **结构化检测，不做模糊匹配。** 按 H2 标题精确匹配判断块是否存在（见下表），不靠 grep 关键词。
4. **已有则跳过。** 块都在 → 告知无需改动，不写文件。

## 规则块清单（H2 标题即结构标记）

| 块 | 检测标记（精确 H2） | 注入内容来源 |
|---|---|---|
| 称呼规则 | `## 称呼规则` | template.md 同名 H2 段 |
| Caveman 简洁规则 | `## Caveman 简洁规则` | template.md 同名 H2 段 |
| Karpathy 编码准则 | `## Karpathy 编码准则` | template.md 同名 H2 段 |
| 工作流路由 | `## 工作流路由` | template.md 的 `## 工作流路由` + 紧随的 `## 支撑层` 两段 |

检测按整行 H2 标题匹配。标题被改写（如加了后缀）视为"缺失"是可接受的——用户可手动合并，本 skill 不猜测同义标题。

## 流程

### 1. 问候 + 取项目名

以 "luohe" 称呼用户；取当前工作目录名作为 `{project-name}`。

### 2. 判断路径

#### 分支 A：无 CLAUDE.md

1. 读 `references/template.md`
2. 把标题行 `# {project-name}` 的占位替换为实际项目名
3. 写入 `./CLAUDE.md`
4. 告知：✅ 新建完成（称呼规则 + Caveman + Karpathy + 工作流路由 + 支撑层）

#### 分支 B：已有 CLAUDE.md

1. 读 `./CLAUDE.md` 与 `references/template.md`
2. 按上表逐块检测 H2 标题是否存在
3. 对每个缺失块：从 template.md 切出该 H2 段的完整正文（从 H2 行到下一个 H2 前），保持原文
4. 在第一个 `# Title` 之后按序注入缺失块（跳过 YAML frontmatter），块间空一行，顺序：称呼规则 → Caveman → Karpathy → 工作流路由(+支撑层)
5. 其他内容完全不动，写入 `./CLAUDE.md`
6. 告知：缺了哪些、注入了哪些、哪些已有

## 什么时候用

- 新项目开张，初始化 AI 协作规则（含工作流路由，用户提需求即自动进环）
- 现有项目补齐缺失规则块，不动已有内容

## 案例

```
你：/0--claude（无 CLAUDE.md）
Claude：luohe，当前目录 "data-pipeline"。
       📄 无 CLAUDE.md → 按模板新建
       ✅ 已生成：称呼规则 + Caveman + Karpathy + 工作流路由 + 支撑层

---

你：/0--claude（只缺 Karpathy + 工作流路由）
Claude：luohe，当前目录 "data-pipeline"。
       检测：称呼规则 ✓、Caveman ✓、Karpathy ✗、工作流路由 ✗
       ✅ 已从模板注入 Karpathy 编码准则 + 工作流路由(+支撑层)

---

你：/0--claude（块都在）
Claude：luohe，当前 CLAUDE.md 四个规则块齐全，无需修改。
```

## 完成后

新项目一般刚跑过 `/0-启动`。规则就位后，用户直接说需求即按工作流路由进环——中大功能默认 `/1-规划`。
