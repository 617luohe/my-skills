# My Skills Library

个人技能库；My Note 子域负责将外部资料整理并发布到固定个人知识库。

## Language

**Noteall**:
My Note 唯一面向用户的知识库入口，接收本机路径、URL、自由文本和处理倾向，并编排完整流水线。
_Avoid_: 路由器、子命令集合

**固定知识库（Fixed Vault）**:
Noteall 唯一允许写入和执行发布操作的 Obsidian Vault：`C:\Users\Administrator\Documents\Obsidian Vault`。路径或 `.obsidian/` 校验失败时停止，不回退到当前工作目录。
_Avoid_: 默认知识库探测、当前 Vault

**收录（Intake）**:
解析输入与处理倾向、验证固定知识库前置条件，并将本机文件的副本或 URL/文本来源记录带入整理阶段。

**整理（Curate）**:
把已收录来源转换为目标笔记形态，执行结构化、去重、链接、索引和 Vault 内原始副本归档。

**发布（Publish）**:
将一次成功流水线拥有的改动受控提交并同步到固定知识库 Git 远端。这里的发布不表示公开发布文章。
_Avoid_: 文章发布、通用 Git 操作

**处理倾向（Processing Intent）**:
用户对资料处理方式的自然语言要求。它优先于自动推断，但不能覆盖固定知识库、干净工作区、受控暂存和冲突停止等安全不变量。

**处理 Profile**:
描述会议、阅读、日记、文章等内容类型差异的模板或规则集合；它复用统一流水线，不拥有独立的摄入、归档或发布流程。
_Avoid_: 顶层路由 Skill

**维护模式（Maintenance）**:
Noteall 收到批量整理、索引更新、MOC 审计或文件整理等维护倾向时执行的流程变体：跳过 Intake，直接执行 Curate 的维护步骤并进入 Publish。
_Avoid_: 独立的批量/索引/整理 Skill 入口

**内部 Worker**:
仅由 Noteall 调度、承担独立且可复用职责的 My Note skill，不是用户入口。

**流水线拥有路径（Owned Path）**:
本次 Noteall 运行创建或修改并显式记录的固定知识库路径集合；Publish 只能暂存这些路径。
_Avoid_: 整个工作区、`git add .`

**遗留提交（Pending Push）**:
先前 Noteall 流水线已在固定知识库本地成功提交、但尚未推送到跟踪远端的提交。下一次新收录前优先重试推送。

## Relationships

- Noteall 依次编排收录、整理和发布。
- 处理 Profile 为整理阶段提供内容类型差异。
- 内部 Worker 由 Noteall 调度，可服务一个或多个流水线阶段。
- 维护模式是收录流水线的变体，跳过 Intake，直接执行 Curate 维护步骤并进入 Publish。
- 发布只处理流水线拥有路径，并且授权范围仅限固定知识库。
- 遗留提交必须在新一轮收录开始前完成推送或明确失败停止。
