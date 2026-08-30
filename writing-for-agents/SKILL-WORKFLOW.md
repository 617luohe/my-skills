# SKILL-WORKFLOW.md — 我方定制工作流

主文 [SKILL.md](SKILL.md) 是通用写作参考；本文件是 luohe 在本仓库落地时的定制工作流（disclosed reference，指针触发才读）。

## 触发（何时用）

- 新建或修改 skill
- 优化 skill description / 触发词
- 生成或修改 CLAUDE.md、路由表
- 校准任何 agent 消费的文档

## 写作流程

1. **抓意图** — 对话历史已含工作流则先提取，再补缺口；用户确认后继续
2. **定触发分支** — 列出文档处理的各个分支，写 description（context pointer）
3. **写正文** — steps + 每步完成标准 + leading words 锚定
4. **渐进披露** — 分支性/参考性内容推到指针后
5. **过闸** — validate_skills.py：size ≤200/500、frontmatter 三处一致（manifest/frontmatter/openai.yaml）、命名规范、link 与 skill-reference 检查

## 完成条件

- [ ] description 有清晰触发分支，一个分支一个触发词，无同义词堆叠
- [ ] 每步/每段有可检查的完成标准，无模糊边界
- [ ] 无 no-op 句、无重复含义（单一事实源）
- [ ] 需要的 reference 已披露到指针后，顶层可读
- [ ] validate_skills.py 通过

## 与其它技能的关系

- **skill-creator**（已部署）— 外层迭代循环：草稿 → 评测 → 改写。本技能管内层写作质量，两者接力
- **`0-claude`** — 生成 CLAUDE.md 时参考本技能原则
- **`0-neat-freak`** — 校准知识库文档时应用 pruning 原则
- 新建技能时：先走本技能写，再用 skill-creator 评测迭代
