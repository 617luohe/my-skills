# Curate — 整理阶段

职责：把已收录来源转换为目标笔记形态，结构化、去重、链接、索引，并归档 Vault 内原始副本。内容类型差异读取 `profiles.yaml`。

## Step 1 — 判断笔记形态与目录

按处理倾向 → profile（`profiles.yaml`）→ 类型信号词推断，确定类型与目录：

| 信号词 | 类型 | 目录 |
|--------|------|------|
| 索引/概览/MOC | MOC | 1-Atlas/ |
| 项目/计划/方案 | Project | 2-Projects/ |
| 日常/习惯/财务 | Area | 3-Areas/ |
| 概念/术语 | Resource | 4-Resources/ |
| 日记/周记/月记 | Journal | 5-Journal/ |
| 人/联系 | Person | 6-People/ |
| 书/文章/论文/视频 | Source | 7-Sources/ |
| 会议/讨论/访谈 | Meeting | 2-Projects/{project}/notes/ |

默认 Resource。不确定时一次一问确认。

## Step 2 — 去重检测（写入前）

按标题/来源 URL/相似度检测重复：
- 无重复 → 新建。
- 有重复 → 询问**更新 / 另存 / 跳过**，绝不静默覆盖。

## Step 3 — 生成笔记

1. 按 profile/类型加载模板，填充结构化内容。
2. 提取关键词 → 搜索 Vault 已有笔记 → 首次出现自然嵌入 `[[wikilink]]`；未匹配的放"## 相关笔记"。
3. Frontmatter 必填：`title`、`tags`（type/ + domain/）、`created`、`updated`、`status: draft`。
4. 格式规范：`#` 层级不跳级、`-` 列表、callout 标准语法、中英文间留空格。
5. 写入前预览确认；AI 推测标注 `> [!ai-guess]`。

## Step 4 — 索引更新

更新相关文件夹 `_INDEX.md`（增量）：
- 只维护 INDEX-KEEPER-MANAGED 区域；`<!-- MANUAL -->...<!-- /MANUAL -->` 完全不碰。
- 内容导航只增不删（确认失效链接除外）。
- 修改后记录维护日志。

## Step 5 — 归档原始副本

Vault 内 `raw/` 的原始副本 → 归档到 `7-Sources/{project}/{subdir}/{file}`：
- 目标目录不存在 → 询问是否创建。
- 同名冲突 → 询问覆盖/重命名。
- 归档后 raw/ 空 → 提示。

## 处理模式

| 模式 | 触发 | 行为 |
|------|------|------|
| compose | 默认 | 创建/更新/展开笔记 |
| polish | "润色/优化" | 改写已有笔记；更新模式展示 diff，确认后写入 |
| atomic | "拆解/原子化" | 长笔记拆为原子概念，建立互链，可选生成 MOC |

## MUST 规则

1. **重复检测在写入前。** 有重复必须询问，不静默覆盖。
2. **创建前确认类型与领域。** 不确定不猜测。
3. **更新模式展示 diff，确认后写入。** 不静默修改、不删除已有内容。
4. **MANUAL 区域不碰。** 索引只增不删。
