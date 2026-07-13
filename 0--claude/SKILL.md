---
name: 0--claude
description: One-shot CLAUDE.md initializer — creates new CLAUDE.md with luohe naming rule + Caveman brevity rules + Karpathy coding guidelines + workflow routing (按规模分档 + 支撑层触发表), or injects missing rules into existing CLAUDE.md. Non-destructive, smart injection. 触发词：初始化CLAUDE、创建CLAUDE.md、CLAUDE规则、caveman、karpathy、工作流路由。
---

# 0--claude — CLAUDE.md 初始化器

luohe，我来处理项目的 CLAUDE.md。

核心逻辑：
- **没有 CLAUDE.md** → 新建完整文件（称呼规则 + Caveman 简洁规则 + Karpathy 编码准则 + 工作流路由 + 占位）
- **已有 CLAUDE.md** → 检测三个规则块，缺失则注入，已有则跳过
- **三个规则都已存在** → 跳过，无需改动

## 流程

## MUST 规则

1. **非破坏式注入。** 已有内容完全不动，只在缺失位置嵌入。
2. **三个规则块按优先级注入。** 称呼规则 → Caveman 规则 → Karpathy 准则 → 工作流路由。
3. **已有则跳过。** 规则都已存在 → 告知无需改动，不写文件。

### 1. 问候用户
- 以 "luohe" 称呼用户

### 2. 检测当前目录
- 取当前工作目录名作为项目名

### 3. 判断路径

#### 分支 A：当前目录没有 CLAUDE.md
- 读取 `references/template.md`
- 替换 `{project-name}` 为实际项目名
- 写入 `./CLAUDE.md`
- 告知：✅ 新建完成（包含称呼规则 + Caveman 简洁规则 + Karpathy 编码准则 + 工作流路由 → /1-规划）

#### 分支 B：当前目录已有 CLAUDE.md
- 读取 `./CLAUDE.md`
- 检测三个规则块 + 工作流路由是否已存在：
  - **称呼规则**：搜索 "luohe" 或 "称呼规则"
  - **Caveman 简洁规则**：搜索 "caveman" 或 "简洁规则"
  - **Karpathy 编码准则**：搜索 "Karpathy" 或 "编码准则"
  - **工作流路由**：搜索 "工作流路由" 或 "/1-规划"
- 对每个缺失的规则块，在文件头部（第一个 H1 标题之后）嵌入

**称呼规则块**（缺失时注入）：
```
## 称呼规则

- 每次回复必须先叫我 **luohe**
- 如果某次回复忘了叫我 luohe → 说明上下文已膨胀，需要压缩或切换会话
```

**Caveman 简洁规则块**（缺失时注入）：
```
## Caveman 简洁规则

- **先说结论**：回复第一句给答案，细节和理由按需补充
- **简化思考**：内部推理聚焦关键决策点，跳过显而易见的推导
- **短句优先**：一句话能说清不分三句，不罗列不铺陈
- **不过度简化**：保持可理解，关键步骤和边界条件必须说清
```

**Karpathy 编码准则块**（缺失时注入）：
```
## Karpathy 编码准则

### 1. 先想后写
- 明确假设，不确定就问
- 如果有多种解读，列出而不是暗中选一个
- 如果有更简单的方案，说出来
- 不清晰就停下来，指出哪里模糊

### 2. 简洁优先
- 只写解决问题的最小代码，不写猜测性代码
- 不需要的功能不加、只用一个地方的抽象不做、没要求的灵活性不搞
- 如果写了 200 行但 50 行能搞定，重写

### 3. 外科手术式改动
- 只动必须动的代码，不"改进"旁边的代码
- 不改没坏的东西
- 匹配现有风格
- 自己产生的垃圾自己清理（无用的 import、变量等）

### 4. 目标驱动
- 每个任务转化为可验证的目标
- 多步骤任务先列计划再动手
```

**工作流路由块**（缺失时注入，与 `references/template.md` 保持一致）：
```
## 工作流路由

直接说需求，AI 按规模选路径，无需报技能名。拿不准用 `/use-skills <需求>`（自动匹配）；放手全自动用 `/0--auto-iteration <目标>`。

| 任务规模 | 路径 |
|---|---|
| **小改动 / bug**（单行、拼写、已定位 fix） | 直接改 →（需查根因 `/7-调试`）→ `/8-版本管理` |
| **中大功能**（新功能、多模块、方案不定） | `/1-规划` →（存疑 `/3-原型`）→ `/4-开发` → `/5-检查` →（有 bug `/7-调试`）→ `/8-版本管理` → `/9-最后整理` |
| **接手陌生项目** | `/0--graphify` 建索引 → `/2-分析` 看结构 → 再进上面的环 |
| **不确定复杂度** | 说明判断依据，默认先 `/1-规划` |

**铁律**：先想后写（Karpathy 准则 1）——没有方案共识不写复杂代码。

## 支撑层（不进主线，按信号触发）

| 信号 | 技能 |
|---|---|
| 新项目开张 | `/0-启动` + `/0--claude` |
| 工具输出太大 / token 紧张 | `/0--headroom-compress` |
| 反复同类报错 | `/0--headroom-learn` |
| 收尾、沉淀本次会话产出、清临时文件 | `/9-最后整理` |
| 全局文档↔代码洁癖同步、防记忆膨胀 | `/0--neat-freak` |
| 复杂问题拿不准方向 | `/0--dialectic` |
```

嵌入规则：
- 先跳过 YAML frontmatter（如果有 `--- ... ---` 块）
- 在第一个 `# Title` 行之后插入，前后空一行
- 多个规则块都缺失时，顺序：称呼规则 → Caveman 规则 → Karpathy 准则 → 工作流路由
- 其他内容完全不动
- 写入 `./CLAUDE.md`

告知：
- 概述缺了哪些、注入了哪些、哪些已有
- 示例：✅ 已嵌入称呼规则 + Caveman 规则；Karpathy 准则已存在

## 什么时候用

- 开始一个新项目时，初始化 AI 协作规则（含工作流路由 → 用户提需求自动触发 /1-规划）
- 现有项目想补上缺失的规则块（称呼 / Caveman / Karpathy），不想改已有内容

## 案例

```
你：/0--claude（无 CLAUDE.md）
Claude：luohe，检测到当前目录 "data-pipeline"。

       📄 CLAUDE.md 不存在 → 新建完整文件
       ✅ 已生成，包含称呼规则 + Caveman 简洁规则 + Karpathy 编码准则 + 工作流路由 → /1-规划

---

你：/0--claude（已有 CLAUDE.md，规则全缺）
Claude：luohe，检测到当前目录 "data-pipeline"。

       📄 CLAUDE.md 已存在，缺少全部规则 → 嵌入
       ✅ 已嵌入称呼规则 + Caveman 简洁规则 + Karpathy 编码准则 + 工作流路由

---

你：/0--claude（只缺 Karpathy + 工作流路由）
Claude：luohe，检测到当前目录 "data-pipeline"。

       📄 称呼规则已有 ✓，Caveman 已有 ✓，Karpathy 缺失，工作流路由缺失
       ✅ 已嵌入 Karpathy 编码准则 + 工作流路由

---

你：/0--claude（规则全有）
Claude：luohe，当前 CLAUDE.md 已包含所有规则，无需修改。
```
