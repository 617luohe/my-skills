---
name: 0--claude
description: 初始化或修复 CLAUDE.md 小内核（工作哲学、记忆约定）。触发：新项目协作规则、初始化 CLAUDE、补齐规则块。
disable-model-invocation: false
---

# 0--claude — CLAUDE.md 初始化器

luohe，我来处理项目的 CLAUDE.md。

**职责**：CLAUDE.md 只常驻最小内核（工作哲学 + 记忆约定），不含路由表；完整技能路由由 `0-询问luohe/SKILL.md` 独占。

**唯一模板源**：`references/template.md`。改规则正文只改模板一处。

## MUST 规则

1. **模板是唯一源** — 正文从 `references/template.md` 读取。
2. **非破坏式注入** — 缺失块才注入，已有用户内容不动。
3. **结构化检测** — 按 H2 精确匹配（见下表）。
4. **Fat 收敛** — 删除模板外的块：`## 称呼规则`、`## 路由入口`、`## 本项目配置`、`## 工作流路由`、`## 支撑层`；旧版详细格式（Caveman/Karpathy/Vercel 子节）的 `## 工作哲学` 替换为新精简版。

## 规则块清单

| 块       | 检测 H2       | 说明                      |
| -------- | ------------- | ------------------------- |
| 工作哲学 | `## 工作哲学` | 称呼 + 五条原则平铺       |
| 记忆约定 | `## 记忆约定` | 触发/写入/检索/边界       |

## 流程

### 1. 问候 + 取项目名

称呼 luohe；取当前目录名替换 `{project-name}`。

### 2. 判断路径

#### 分支 A：无 CLAUDE.md

读 template → 替换项目名 → 写入 `./CLAUDE.md` → 可选写 AGENTS 指针（[references/agents-pointer.md](references/agents-pointer.md)）。

#### 分支 B：已有 CLAUDE.md

1. Fat 收敛：删除模板外块（`## 称呼规则`、`## 路由入口`、`## 本项目配置`、`## 工作流路由`、`## 支撑层`）
2. 旧版详细格式的 `## 工作哲学`（含 Caveman/Karpathy/Vercel 子节）→ 替换为新精简版
3. 按上表检测缺失块 → 从 template 切出并注入（顺序：工作哲学 → 记忆约定）
4. 两块齐全且无 Fat 残留 → 可告知无需改动

## 什么时候用

- 新项目开张（通常接在 `/0-启动` 之后）
- 补齐缺失规则块，或从 Fat 版（含路由镜像表 / 旧版详细格式）收敛

## 完成后

用户直接说需求；完整路由只见 `/0-询问luohe`。
