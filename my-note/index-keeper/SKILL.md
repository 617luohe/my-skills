---
name: index-keeper
layer: my-note
description: [内部] 索引维护。自主维护所有一级文件夹 _INDEX.md：增量更新、缺失补全、健康报告。由 noteall 路由器调度。
---

# index-keeper — 索引维护

自主维护每个一级文件夹的 `_INDEX.md`（结构性导航索引，非概念地图）。与 vault-cartographer 分工：INDEX = "文件夹里有什么"，MOC = "概念怎么关联"。

## 一、INDEX 统一结构

每个 `_INDEX.md` 包含：frontmatter → 一句话描述 → 统计区 → 内容导航 → 维护日志。

### 各文件夹导航结构定制

| 文件夹 | 导航内容 |
|--------|----------|
| 0-Inbox/ | 待处理队列表 + 处理统计 |
| 1-Atlas/ | MOC 注册表（按 domain 分组） |
| 2-Projects/ | 项目看板（活跃/暂停/已完成） |
| 3-Areas/ | 责任域仪表盘 |
| 4-Resources/ | 知识领域树（按 domain 分组） |
| 5-Journal/ | 日记结构 + 近期活跃表 |
| 6-People/ | 人物目录（按 relationship 分组） |
| 7-Sources/ | 来源目录（按 source-type 分组） |
| raw/ | 待处理文件表 + 处理统计 |

## 二、工作模式

| 模式 | 行为 |
|------|------|
| 全量更新 | 扫描所有一级文件夹，生成/更新所有 _INDEX.md |
| 增量更新 | 只更新指定文件夹，仅处理变更部分 |
| 健康检查 | 检测缺失 INDEX、失效链接、缺失条目、过期描述 |
| 缺失补全 | 仅为无 _INDEX.md 的文件夹创建初始 INDEX |

### 增量更新自动触发时机
- note-composer 新建笔记后
- batch-curator 批量导入后
- workflow-wrapup 归档后

## 三、安全规则

- `<!-- MANUAL -->...<!-- /MANUAL -->` 区域完全不碰
- 内容导航只增不删（确认失效链接除外）
- 每次修改记录维护日志
- 全量更新前展示变更摘要，确认后写入
- 只读写 `_INDEX.md`，不碰其他文件

## 四、输出

全量/增量更新后输出简短报告：哪些文件夹更新了，哪些条目增加/删除，需关注的问题。

## MUST 规则

1. **MANUAL 区域完全不碰。** 只维护 INDEX-KEEPER-MANAGED 区域。
2. **内容导航只增不删。** 确认失效链接除外。
3. **全量更新前展示变更摘要，确认后写入。**
4. **只读写 _INDEX.md，不碰其他文件。**
