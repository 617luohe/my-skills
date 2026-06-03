---
name: 0-初始化CLAUDE
description: One-shot CLAUDE.md initializer — creates new CLAUDE.md with luohe naming rule + Karpathy guidelines, or injects luohe rule into existing CLAUDE.md. Non-destructive, smart injection.
---

# 0-初始化CLAUDE — CLAUDE.md 初始化器

luohe，我来处理项目的 CLAUDE.md。

核心逻辑：
- **没有 CLAUDE.md** → 新建完整文件（称呼规则 + Karpathy 准则 + 占位）
- **已有 CLAUDE.md** → 只嵌入"叫我 luohe"规则，其他原封不动
- **已包含"luohe"规则** → 跳过，无需改动

## 流程

### 1. 问候用户
- 以 "luohe" 称呼用户

### 2. 检测当前目录
- 取当前工作目录名作为项目名

### 3. 判断路径

#### 分支 A：当前目录没有 CLAUDE.md
- 读取 `references/template.md`
- 替换 `{project-name}` 为实际项目名
- 写入 `./CLAUDE.md`
- 告知：✅ 新建完成

#### 分支 B：当前目录已有 CLAUDE.md
- 读取 `./CLAUDE.md`
- 检查内容是否已包含"luohe"或"称呼规则"
  - 如果已包含 → 无需改动，告知：✅ 已包含称呼规则，无需修改
  - 如果未包含 → 在文件头部（第一个 H1 标题之后）嵌入以下内容：

```
## 称呼规则

- 每次回复必须先叫我 **luohe**
- 如果某次回复忘了叫我 luohe → 说明上下文已膨胀，需要压缩或切换会话
```

嵌入规则：
- 先跳过 YAML frontmatter（如果有 `--- ... ---` 块）
- 在第一个 `# Title` 行之后插入，前后空一行
- 其他内容完全不动
- 写入 `./CLAUDE.md`

告知：✅ 已嵌入称呼规则，其余内容未变

## 什么时候用

- 开始一个新项目时，初始化 AI 协作规则
- 现有项目想加上"叫我 luohe"规则，但不想改已有内容

## 案例

```
你：/0-初始化CLAUDE
Claude：luohe，检测到当前目录 "data-pipeline"。

       📄 CLAUDE.md 不存在 → 新建完整文件
       ✅ 已生成，包含称呼规则 + Karpathy 准则

---

你：/0-初始化CLAUDE（已有 CLAUDE.md 但没有称呼规则）
Claude：luohe，检测到当前目录 "data-pipeline"。

       📄 CLAUDE.md 已存在，但缺少称呼规则 → 嵌入
       ✅ 已嵌入"叫我 luohe"规则，其余内容未变

---

你：/0-初始化CLAUDE（已包含称呼规则）
Claude：luohe，当前 CLAUDE.md 已包含称呼规则，无需修改。
```
