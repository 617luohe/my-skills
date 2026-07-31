---
name: vault-publisher
layer: my-note
description: [内部] 固定 Vault 的发布阶段。校验、受控暂存、commit、sync、push。仅由 noteall 编排调度，不可独立触发。
disable-model-invocation: false
---

# vault-publisher — 固定 Vault 发布（内部 Worker）

承担 noteall 流水线的 Publish 阶段：把本次流水线拥有的改动受控提交并同步到固定 Vault 远端。只接受 noteall 调度，不接收用户直接调用。

## 职责

1. 校验固定 Vault 与 Git 前置状态。
2. 同步远端（快进 / 干净自动合并 / 冲突停止）。
3. 只暂存本次 owned paths，commit，push。
4. 报告 commit hash、push 状态与失败恢复建议。

## 调用契约

noteall 通过 `references/publish.md` 以脚本方式调用，模型不自由组合 Git 命令：

```
python my-note/vault-publisher/scripts/publish_vault.py \
  --vault {vault_path} \
  --paths {owned_path1} {owned_path2} ... \
  --message "notes(<type>): ingest <normalized-title>"
```

参数含义：
- `--vault`：固定 Vault 路径（来自 noteall `references/config.yaml`）。
- `--paths`：本次流水线创建的 Vault 内路径（相对 Vault）。
- `--message`：提交信息。单条 `notes(<type>): ingest <title>`；批量 `notes(batch): curate <count> sources`。

## 退出码语义

| 码 | 含义 | noteall 处理 |
|----|------|--------------|
| 0 | 发布成功 / 无变更 | 报告结果 |
| 2 | 前置失败（Vault 无效 / 存在非 owned 改动） | 停止，提示用户先清理 |
| 3 | 远端合并冲突 | 停止，报告冲突文件，不自动解决 |
| 4 | push 失败 | 保留本地提交，报告 hash，下次先补推 |

## MUST 规则

1. **仅由 noteall 编排调度。** 不独立触发、不向用户暴露。
2. **只暂存 owned paths。** 不用 `git add .`。
3. **无实际变更不创建空提交。**
4. **冲突不自动解决。** 停止并报告。
5. **push 失败不回滚本地提交。** 保留 hash 并报告。
6. **Vault 工作区存在非 owned 改动 → 立即停止。**
