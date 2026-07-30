---
name: noteall
layer: my-note
description: 知识库流程路由器。NL解析意图→提取参数→路由到对应流程。主流程：Intake→Compose→Polish→Index。触发：note、笔记、写、创建、记录、整理、noteall、知识库。
disable-model-invocation: false
---

# noteall — 知识库流程路由器

合并了 note（NL入口）和 noteall（流程路由）。主流程：**Intake → Compose → Polish → Index**。

## 〇、环境检测（每次启动首步）

1. **检测 `.obsidian/` 目录** — 存在于当前工作目录 → **Vault 模式**
2. **无 `.obsidian/`** → 读取 `./CLAUDE.md` 中 `## 默认知识库` 的 `默认知识库路径` → **外部项目模式**
3. **无配置** → 询问用户指定知识库路径

**路径映射**（外部项目模式下，vault = 默认知识库路径）：

| 原相对路径 | 映射为 |
|-----------|--------|
| `0-Inbox/` ~ `7-Sources/` | `{vault}/0-Inbox/` ~ `{vault}/7-Sources/` |
| `raw/` | `{vault}/raw/` |

Wikilink 搜索范围始终为 vault 目录；INDEX/MOC 操作也在 vault 内进行。

## 一、NL 入口 → 场景路由

| 信号词 | 路由 | 提取参数 |
|--------|------|----------|
| URL/http/www | `/my-note/info-digester` | URL, depth(默认detailed) |
| 日记/今天/早上/晚间/收尾/反思 | `/my-note/daily-concierge` | 日期, 模式 |
| 周回顾/月回顾 | `/my-note/daily-concierge` 周期模式 | 周期类型 |
| 写长文/教程/综述/深度文章 | `/my-note/article-writer` | 主题, 领域 |
| 笔记/概念/知识点/写一篇 | `/my-note/note-composer` | 主题, 类型, domain |
| 会议/开会/讨论/纪要 | `/my-note/meeting-minutes` | 主题, 日期, 参会者 |
| 书/读书/阅读 | `/my-note/reading-digester` | 书名, 操作类型 |
| 批量/导入/curate | `/my-note/batch-curator` | 文件夹路径 |
| raw/原始数据/处理文件 | `/my-note/raw-ingester` | 文件路径, 产出类型 |
| 拆解/原子化/atomize | `/my-note/concept-atomizer` | 目标笔记 |
| 润色/优化/修一下 | `/my-note/note-polisher` | 目标笔记 |
| 索引/INDEX/更新导航 | `/my-note/index-keeper` | 全量/增量/健康检查 |
| MOC/审计/图谱/链接健康 | `/my-note/vault-cartographer` | 检查类型 |
| 文件整理/归类/文件乱了 | `/my-note/file-organizer` | 目标目录 |
| 归档/收尾/wrapup/cleanup | `/my-note/workflow-wrapup` | 目标项目 |

多信号同时出现时，越具体越优先。URL 和 raw/ 路径自动优先识别。

## 二、工作流路由

### ① Intake（内容进入）

| 来源 | 路由 | 产出 |
|------|------|------|
| URL/网页/PDF/文本 | `/my-note/info-digester` | 7-Sources/ |
| raw/ 中的文件 | `/my-note/raw-ingester` 盘问→路由 | 取决于结果 |
| 零散想法 | 捕获到 0-Inbox/ | 0-Inbox/ |

### ② Compose（撰写笔记）

| 场景 | 路由 | 目录 |
|------|------|------|
| 知识概念/MOC/项目/人物 | `/my-note/note-composer` | 按类型分目录 |
| 深度长文（2000+字） | `/my-note/article-writer` | 4-Resources/ |
| 会议纪要 | `/my-note/meeting-minutes` | 2-Projects/{项目}/notes/ |

### ③ Polish（提升质量）

| 场景 | 路由 |
|------|------|
| 单篇润色 | `/my-note/note-polisher` |
| 长笔记拆原子 | `/my-note/concept-atomizer` |
| 批量审计 | `/my-note/note-polisher` batch mode |

### ④ Index（维护导航）

| 场景 | 路由 |
|------|------|
| MOC 生成/更新 | `/my-note/vault-cartographer` |
| INDEX 维护 | `/my-note/index-keeper` |
| 收尾归档 | `/my-note/workflow-wrapup` |

## 三、分支决策

| 场景 | 判断 | 路由 |
|------|------|------|
| 深度研究+长篇写作 | 需要研究→大纲→撰写→修订 | `/my-note/article-writer` |
| 大量文件批量导入 | raw/ 有 ≥5 个文件 | `/my-note/batch-curator` |
| 阅读场景 | 读书/文章 | `/my-note/reading-digester` |
| 文件组织混乱 | 错位/命名/重复 | `/my-note/file-organizer` |
| 时间管理 | 日记/周记/月记 | `/my-note/daily-concierge` |

## 四、时间维度触发

| 时机 | 链路 |
|------|------|
| 早晨 | `/my-note/daily-concierge` 创建日记 → 拉取待办 |
| 晚间 | `/my-note/daily-concierge` 晚间反思 → 清空 Inbox |
| 周末 | `/my-note/daily-concierge` 周回顾 → `/my-note/vault-cartographer` → `/my-note/note-polisher` |
| 月末 | `/my-note/daily-concierge` 月回顾 → `/my-note/vault-cartographer` 全量 → `/my-note/index-keeper` 全量 |

## 五、维护触发

| 信号 | 链路 |
|------|------|
| 知识库混乱 | `/my-note/vault-cartographer` 审计 → `/my-note/file-organizer` → `/my-note/index-keeper` |
| raw/ 积压 | `/my-note/batch-curator` |
| 新增大批笔记 | `/my-note/index-keeper` 增量更新 |
| 项目完成 | `/my-note/workflow-wrapup` → `/my-note/index-keeper` 更新 |

## 六、快捷穿透

用户可提供精确指令直接穿透到具体技能：
- `note 消化 {URL}` → `/my-note/info-digester`
- `note 写关于{主题}的笔记` → `/my-note/note-composer`
- `note 批量整理 raw/` → `/my-note/batch-curator`
- `note 处理 raw/{路径}` → `/my-note/raw-ingester`

## 七、外部项目透明路由

在非 vault 项目中调用时，自动执行环境检测（§〇），所有文件操作以默认知识库为根。信号词：`保存到知识库`、`记到默认知识库`、`笔记同步到 vault`。

## 八、原则

- 一次一步，确认后执行，允许跳转
- 大规模操作（batch-curator/全量索引）建议独立对话
- 每次摄入完成 → `/my-note/workflow-wrapup` 归档
- 完全无匹配 → 展示路由表，盘问确认
- 多义输入 → 按更具体场景优先，盘问确认

## MUST 规则

1. **每次启动必须执行环境检测（§〇）。** 不确定路径时先确认再操作。
2. **路由前必须提取完整参数。** URL/路径优先识别；参数不足时分步盘问（每次一问）。
3. **外部项目模式下文件操作以默认知识库为根。** 不污染当前项目目录。
4. **中途取消（"算了"/"取消"）→ 退出不路由。**
