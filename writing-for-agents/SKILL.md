---
name: writing-for-agents
description: 写给 agent 的文档写作规范。触发：改技能、优化触发词、写或更新 CLAUDE.md、路由表。
disable-model-invocation: false
---

# Writing for Agents — 写给 agent 的文档

写任何 agent 消费的文档——skill、CLAUDE.md、被指针引用的参考文件。包装不同，写作相同：让 agent 每次跑**同一过程**，而非产出同一输出。

## 触发（何时用）

- 新建或修改 skill
- 优化 skill description / 触发词
- 生成或修改 CLAUDE.md、路由表
- 校准任何 agent 消费的文档

## 七个杠杆

### 1. Context pointer — 描述即指针

description 是常驻指针，其**措辞**（而非目标）决定 agent 何时取到材料：

- **前置触发词**：每个触发分支一个词，同义词合并（"归档"/"收尾" 是同一分支，只留一个）
- **一个分支一个触发**：不同分支才新增触发词
- **不写身份**：body 已表达的，指针不再重复

### 2. 完成标准（completion criteria）

每步以可检查的完成条件收尾，两个属性：

- **clarity（清晰）**：能分辨完成/未完成。模糊边界（"理解达成"）诱发**提前完成**——注意力滑向"做完了"
- **demand（要求）**：要求到什么程度。"每个模块都核对到" 比 "产出一份清单" 逼出更多 legwork

最强的标准：既可检查又穷尽。先锐化边界；确实模糊再拆文档序列。

### 3. Leading words — 单 token 锚点

用预训练已有的词锚定一段行为，重复 token 不重复句子（`tight`、`red`）。造词要付定义 token 的成本，先找现成词。三处写三遍的同义短语 → 收成一个 token。

### 4. 信息层级 + 渐进披露

材料按 agent 需要的紧急度分层：

1. **in-file step** — 主层：按序做什么
2. **in-file reference** — 按需查：规则/定义（平级集合是正当布局，不是坏味道）
3. **disclosed reference** — 推出去，指针触发才加载

**渐进披露** = 往下移：分支性内容披露到指针后，顶层保持可读。inline 每分支都要用的，指针只放部分分支才用的。

### 5. 两种 load — 常驻成本与记忆成本

- **context load**：常驻材料的 token/注意力成本，不触发也付
- **cognitive load**：人的记忆成本——知道哪些文档存在、何时取

只有指针触达的材料逃 context load（代价是指针那一行）；完全无指针的材料全靠 cognitive load。

### 6. 否定转向

禁止式措辞把禁语拖进上下文，让禁语更可用（"别想大象"满脑都是大象）。写**正向目标**（"写一行注释"而非"别写长注释"）。禁令只作为无法正向表达的硬护栏保留，且要配正向目标。

### 7. Pruning — 删减纪律

- **单一事实源**：一个含义只在一处，改行为是一处编辑
- **环境即事实源**：能被查找的（package.json、config、`--help`）不缓存；文档只记查找不到的东西（不成文约定、选择理由、坑）
- **no-op 删整句**：默认就遵守的指令是空转，删整句不删词
- **relevance**：每行仍对该文档的职责有用；随时间过期即删

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
