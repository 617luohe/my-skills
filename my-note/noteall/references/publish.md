# Publish — 发布阶段

职责：把本次流水线拥有的改动受控提交并同步到固定 Vault 的 Git 远端。这里的"发布"指发布到个人知识库远端，不表示公开发布文章。

## Step 1 — 校验本次改动

- 收集 owned paths：本次流水线创建/修改的 Vault 内路径清单（笔记、索引、归档副本）。
- 基本完整性：笔记 frontmatter 完整、无空文件。
- 无任何 owned paths → 不提交、不调用脚本。

## Step 2 — 调用 vault-publisher

执行确定性脚本，模型不自由组合 Git 命令：

```
python my-note/vault-publisher/scripts/publish_vault.py \
  --vault {vault_path} \
  --paths {owned_path1} {owned_path2} ... \
  --message "notes(<type>): ingest <normalized-title>"
```

- 单条：`notes(<type>): ingest <normalized-title>`
- 批量：`notes(batch): curate <count> sources`
- `<type>` 为 profile/类型（meeting/reading/journal/article/resource/note 等）。
- 提交信息不含敏感正文。

## Step 3 — 报告结果

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
