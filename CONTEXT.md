# My Skills Library

个人技能库；My Note 子域负责将外部资料整理并发布到启动时解析并锁定的个人知识库。技能内容通过镜像同步分发到外部配置仓库副本。

## Language

**Noteall**:
My Note 唯一面向用户的知识库入口，接收本机路径、URL、自由文本和处理倾向，并编排完整流水线。
_Avoid_: 路由器、子命令集合

**所选知识库（Selected Vault）**:
Noteall 按 `references/config.yaml` 在当前 Vault 与配置默认 Vault 之间解析一次并锁定的 Obsidian Vault。路径或 `.obsidian/` 校验失败时停止；后续阶段不得重新解析或切换。
_Avoid_: 固定知识库、阶段间回退

**收录（Intake）**:
解析输入与处理倾向、验证所选知识库前置条件，并将本机文件的副本或 URL/文本来源记录带入整理阶段。

**整理（Curate）**:
把已收录来源转换为目标笔记形态，执行结构化、去重、链接、索引和 Vault 内原始副本归档。

**发布（Publish）**:
将一次成功流水线拥有的改动受控提交并同步到所选知识库 Git 远端。这里的发布不表示公开发布文章。
_Avoid_: 文章发布、通用 Git 操作

**处理倾向（Processing Intent）**:
用户对资料处理方式的自然语言要求。它优先于自动推断，但不能覆盖所选知识库、干净工作区、受控暂存和冲突停止等安全不变量。

**处理 Profile**:
描述会议、阅读、日记、文章等内容类型差异的模板或规则集合；它复用统一流水线，不拥有独立的摄入、归档或发布流程。
_Avoid_: 顶层路由 Skill

**维护模式（Maintenance）**:
Noteall 收到批量整理、索引更新、MOC 审计或文件整理等维护倾向时执行的流程变体：跳过 Intake，直接执行 Curate 的维护步骤并进入 Publish。
_Avoid_: 独立的批量/索引/整理 Skill 入口

**内部 Worker**:
仅由 Noteall 调度、承担独立且可复用职责的 My Note skill，不是用户入口。

**流水线拥有路径（Owned Path）**:
本次 Noteall 运行创建或修改并显式记录的所选知识库路径集合；Publish 只能暂存这些路径。
_Avoid_: 整个工作区、`git add .`

**遗留提交（Pending Push）**:
先前 Noteall 流水线已在所选知识库本地成功提交、但尚未推送到跟踪远端的提交。下一次新收录前优先重试推送。

**技能清单（Skills Manifest）**:
`skills-manifest.yaml`，声明每个技能的名称、路径、调用方式与分发属性（`sync: true`）的唯一权威文件。

**镜像同步（Sync）**:
依据技能清单单向分发到同步目标。机制与路径见 [README §分发与部署](README.md#分发与部署)。

**来源笔记（Source Note）**:
记录外部知识来源（书/文章/视频/课程/文档）元数据与学习心得的笔记，位于所选知识库 7-Sources/ 的领域文件夹内。
_Avoid_: 原始文件、归档原件

**概念笔记（Concept Note）**:
从来源笔记提取、承载单一概念的原子笔记，位于 4-Resources/，通过 wikilink 与来源笔记互链。
_Avoid_: 知识点、笔记本体

**领域（Domain）**:
知识的主题分类维度，以 frontmatter `domain/xxx` 标签表达，映射到 1-Atlas 的领域 MOC 与 7-Sources 的领域文件夹。
_Previously ambiguous_: "主题/分类"在索引与文件夹命名中混用

**领域文件夹（Domain Folder）**:
7-Sources/ 内按领域组织的子文件夹，是来源笔记与归档原件的统一落位；项目型来源可保留独立项目文件夹。
_Previously ambiguous_: 用户口语 "source 文件夹" 指 7-Sources/ 本身

**归档原件（Archived Original）**:
收录时复制到 raw/ 的原始文件，整理完成后移入 7-Sources/ 领域文件夹，作为来源笔记对应的原始载体。

**目录索引（Folder INDEX）**:
每个一级文件夹的 `_INDEX.md`，回答"这个文件夹里有什么"的结构性导航；索引维护只更新 `INDEX-KEEPER-MANAGED` 标记区域，`<!-- MANUAL -->...<!-- /MANUAL -->` 区域完全不碰。
_Avoid_: 索引文件、导航文件

**领域 MOC（Domain MOC）**:
1-Atlas/ 中按领域组织的概念导航页，回答"这个领域的知识如何关联"；与目录索引分工。
_Avoid_: 总览页、目录

**双链（Bidirectional Link）**:
来源笔记与概念笔记之间相互引用的 wikilink 关系，双向一致、可反向追踪；Obsidian 打开时据此呈现知识图谱。
_Avoid_: 单向引用、反链（仅 Obsidian 软件内概念）

**级联更新（Cascade Update）**:
笔记增、改、移、删后，对受影响的目录索引、领域 MOC、链接登记等进行的联动修改，保证全库一致性。
_Avoid_: 同步更新、索引刷新

**增量健康检查（Incremental Health Check）**:
发布前对本次流水线拥有路径的轻量检查：结构性违规（frontmatter 枚举/格式、断链）拦截发布，除非 `--allow-issues` 逃生舱显式放行；指标类问题只记录不拦截。全量检查在维护模式执行。
_Avoid_: 全库扫描、无门槛报告

**质量门禁（Quality Gate）**:
发布（Publish）阶段对本次拥有路径执行的结构性校验门槛；校验由 vault_check 的确定性规则执行，违规时发布以退出码 5 停止。
_Avoid_: 语义评审、人工审查

**图谱指标（Graph Metrics）**:
vault_check `--metrics` 输出的量化知识库健康指标（笔记数、边数、孤岛率、有链率、连通分量、断链数、schema 枚举合规），供纵向趋势对比（首次运行=基线快照）。
_Avoid_: 一次性报告

**元数据合规（Frontmatter Compliance）**:
对笔记 frontmatter 的机器校验规则：`confidence`（seed|sapling|evergreen）、`status`（draft|published|archived）、`source` 回链格式（`[[笔记名]]`）、`tags` 前缀（`type/`、`domain/`）与 `domain` 合法领域清单。合法枚举以 vault_check 为机器事实源，noteall 规则文档与 Vault 标签体系引用。
_Avoid_: 自由格式元数据

## Relationships

- Noteall 依次编排收录、整理和发布。
- 处理 Profile 为整理阶段提供内容类型差异。
- 内部 Worker 由 Noteall 调度，可服务一个或多个流水线阶段。
- 维护模式是收录流水线的变体，跳过 Intake，直接执行 Curate 维护步骤并进入 Publish。
- 发布只处理流水线拥有路径，并且授权范围仅限所选知识库。
- 遗留提交必须在新一轮收录开始前完成推送或明确失败停止。
- 镜像同步依据技能清单执行，单向分发（详见 README §分发与部署）。
- 来源笔记与概念笔记通过双链互连；概念笔记由来源笔记派生。
- 领域文件夹承载来源笔记与归档原件，领域 MOC 导航概念笔记，两者通过领域标签关联。
- 级联更新在每次流水线写入后执行，保证目录索引、领域 MOC 与链接登记一致。
- 增量健康检查在发布前执行，拦截结构性违规；逃生舱放行后仍受干净工作区约束。
- 质量门禁以 vault_check 规则校验本次拥有路径；全量健康检查在维护模式执行。
- 图谱指标与元数据合规供纵向趋势对比与机器校验；合法枚举以 vault_check 为准。
