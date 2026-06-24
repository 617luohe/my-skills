---
name: tools--技能工坊
description: 创建新 skills、修改和优化已有 skills、评估 skill 性能。当用户想"做一个skill"、"写个skill"、"优化这个skill"、"这个skill触发不准"、"运行评测"、"benchmark 这个 skill"时触发。也用于从已有工作流提取为可复用 skill。
---

# 技能工坊

创建新 skills 并迭代优化的完整工具链。

## 流程

```
明确意图 → 访谈调研 → 写 SKILL.md → 写测试用例 → 跑评测 → 迭代优化 → 描述优化
```

### 1. 捕捉意图
- 这个 skill 要让 Claude 能做什么？
- 什么时候触发？（什么用户表达/上下文）
- 期望的输出格式？
- 是否需要测试用例？（文件转换、数据提取、代码生成、固定流程 → 需要；写作风格、艺术 → 通常不需要）

### 2. 访谈与调研
- 主动追问边界情况、输入/输出格式、示例文件、成功标准、依赖关系
- 利用 MCP 并行搜索文档、找相似 skill、查最佳实践

### 3. 写 SKILL.md
必填字段：
- **name**：skill 标识
- **description**：这是主要的触发机制。**要写得"pushy"**——内容要过触发，而不是等用户精确说出关键词。包含 skill 做什么 + 什么时候用。例如不说"构建仪表板"而说"当用户提到仪表板、数据可视化、内部指标或想展示公司数据时，务必使用此 skill，即使没有明确说'仪表板'这个词。"
- **compatibility**：需要的工具、依赖（可选，很少需要）
- **正文**：skill 指令

标准目录结构：
```
skill-name/
├── SKILL.md（必需）
│   ├── YAML frontmatter（name, description 必需）
│   └── Markdown 指令
└── 捆绑资源（可选）
    ├── scripts/
    ├── references/
    └── templates/
```

### 4. 评测与迭代
- 创建测试 prompt
- 跑 Claude-with-skill 测试
- 定性评估（看结果）+ 定量评估（跑 benchmark）
- 根据反馈重写 skill
- 扩大测试集，大规模再跑

### 5. 描述优化
- 用 description improver 脚本优化触发准确性
- 确保 description 足够"pushy"避免 undertrigger

## 参考原始 skill

基于 [anthropics/skills@skill-creator](https://github.com/anthropics/skills)，完整文件位于 `reference-skills/skill-creator/`。
