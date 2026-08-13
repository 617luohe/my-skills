# Publish — 发布阶段

职责：把本次流水线拥有的改动受控提交并同步到本次所选 Vault 的 Git 远端。这里的"发布"指发布到个人知识库远端，不表示公开发布文章。

## Step 1 — 校验本次改动

- 收集 owned paths：本次流水线创建/修改的 Vault 内路径清单（笔记、索引、归档副本）。
- 基本完整性：笔记 frontmatter 完整、无空文件。
- 无任何 owned paths → 不提交、不调用脚本。

## Step 2 — 增量健康检查

对**本次变更影响面**做轻量检查（由 index-keeper 健康检查模式执行），输出报告：

| 检查项         | 方法                                                              |
| -------------- | ----------------------------------------------------------------- |
| 断链           | 变更涉及的新/改 wikilink 是否有对应笔记（排除有意占位）           |
| 孤岛           | 本次新建笔记是否有入链；来源↔概念双链是否成对                     |
| INDEX 缺失条目 | 新建/移动文件是否已在所在文件夹 `_INDEX.md`（含领域 `_INDEX.md`） |
| 统计过期       | 受影响 `_INDEX.md` 的统计值是否与实际文件数一致                   |

- 发现问题 → 先修复可自动修复项（补 INDEX 条目、更新统计），再输出剩余项。
- **不阻塞发布**：剩余问题写入报告随 Step 4 输出；严重问题（大量断链）提示用户是否继续。

## Step 3 — 调用 vault-publisher

执行确定性脚本，模型不自由组合 Git 命令：

```
python my-note/vault-publisher/scripts/publish_vault.py \
  --vault {selected_vault} \
  --paths {owned_path1} {owned_path2} ... \
  --message "notes(<type>): ingest <normalized-title>"
```

- 单条：`notes(<type>): ingest <normalized-title>`
- 批量：`notes(batch): curate <count> sources`
- `<type>` 为 profile/类型（meeting/reading/journal/article/resource/note 等）。
- 提交信息不含敏感正文。

**质量门禁（脚本内置）**：publish_vault.py 在提交前对本次 owned paths 做结构性校验（frontmatter 枚举/格式合规、目录必填字段完整含 source 回链、断链检出），违规时退出码 `5` 拦截发布并打印违规清单；`--allow-issues` 逃生舱可显式放行（绕过时打印警告）。孤儿/重复/索引过期类不拦截（报告随 Step 4 输出）；完全无 frontmatter 的文件不拦截。结构性违规必须先修复或显式逃生，不得静默放行。

## Step 4 — 报告结果

向用户输出：

- 写入位置（笔记/索引/归档文件）
- 处理摘要
- commit hash、push 状态
- 失败时：保留的本地提交 hash + 失败原因 + 恢复建议

## MUST 规则

1. **只暂存 owned paths。** 不用 `git add .`，不暂存本次无关的 Vault 改动。
2. **无实际变更不创建空提交。**
3. **冲突不自动解决。** 脚本停止并报告冲突文件。
4. **push 失败不回滚本地提交。** 保留 hash 并报告，下次先补推。
